import os
import sys
import inspect
import torch
import numpy as np
from PIL import Image
import rembg
import logging

# Add TripoSR repo to path so imports work when the repo is present
current_dir = os.path.dirname(os.path.abspath(__file__))
triposr_dir = os.path.join(current_dir, "TripoSR")
if os.path.isdir(os.path.join(triposr_dir, "tsr")):
    sys.path.append(triposr_dir)

# Now we can import from TripoSR codebase
try:
    from tsr.system import TSR
    from tsr.utils import remove_background, resize_foreground
except ImportError as e:
    print(f"Error importing TripoSR modules: {e}")
    print(f"Make sure the TripoSR repository is cloned into {triposr_dir}")
    raise

class Local3DEngine:
    def __init__(self, device="cuda"):
        self.device = device
        if not torch.cuda.is_available() and device == "cuda":
            print("CUDA not available, falling back to CPU")
            self.device = "cpu"
            
        print(f"Initializing TripoSR on {self.device}...")
        self.model = TSR.from_pretrained(
            "stabilityai/TripoSR",
            config_name="config.yaml",
            weight_name="model.ckpt",
        )
        # Adjust chunk size for VRAM usage (8192 is default)
        self.model.renderer.set_chunk_size(8192)
        self.model.to(self.device)
        
        self.rembg_session = rembg.new_session()
        print("Model initialized.")

    def preprocess_image(self, input_image_path):
        """Loads and pre-processes image (bg removal, resizing)."""
        if isinstance(input_image_path, str):
            image = Image.open(input_image_path)
        else:
            image = input_image_path  # Assume PIL image already

        # Remove background
        image = remove_background(image, self.rembg_session)
        image = resize_foreground(image, 0.85)

        # Prepare for model
        image = np.array(image).astype(np.float32) / 255.0
        image = image[:, :, :3] * image[:, :, 3:4] + (1 - image[:, :, 3:4]) * 0.5
        image = Image.fromarray((image * 255.0).astype(np.uint8))
        return image

    def preprocess_images(self, image_inputs):
        if isinstance(image_inputs, (list, tuple)):
            return [self.preprocess_image(image_input) for image_input in image_inputs]
        return [self.preprocess_image(image_inputs)]

    def _call_model(self, images):
        try:
            params = inspect.signature(self.model.__call__).parameters
        except Exception:
            params = {}

        if "device" in params:
            return self.model(images, device=self.device)
        return self.model(images)

    def _infer_scene_codes(self, images):
        if len(images) == 1:
            return self._call_model(images)

        try:
            return self._call_model(images)
        except TypeError as exc:
            fallback = os.getenv("TRIPOSR_MULTIVIEW_FALLBACK", "error").lower()
            if fallback == "first":
                print("Multi-view not supported, falling back to the first image.")
                return self._call_model([images[0]])
            raise RuntimeError(
                "Multi-view inputs are not supported by this TripoSR build. "
                "Set TRIPOSR_MULTIVIEW_FALLBACK=first to use only the first image."
            ) from exc

    def _get_vertex_colors(self, mesh):
        try:
            colors = np.asarray(mesh.visual.vertex_colors)
        except Exception:
            return None

        if colors.size == 0:
            return None

        if colors.shape[1] >= 3:
            colors = colors[:, :3]
        else:
            return None

        if colors.max() > 1.0:
            colors = colors / 255.0

        return colors.astype(np.float32)

    def _unwrap_uvs_xatlas(self, vertices, faces):
        import xatlas  # type: ignore

        try:
            atlas = xatlas.Atlas()
            mesh_id = atlas.add_mesh(vertices, faces)
            atlas.generate()
            vmapping, indices, uvs = atlas[mesh_id]
        except Exception:
            vmapping, indices, uvs = xatlas.parametrize(vertices, faces)

        vmapping = np.asarray(vmapping, dtype=np.int32)
        indices = np.asarray(indices, dtype=np.int32).reshape(-1, 3)
        uvs = np.asarray(uvs, dtype=np.float32)

        new_vertices = vertices[vmapping]
        return new_vertices, indices, uvs, vmapping

    def _rasterize_texture(self, uvs, faces, colors, texture_size):
        import moderngl  # type: ignore

        ctx = moderngl.create_standalone_context()
        color_tex = ctx.texture((texture_size, texture_size), 4, dtype="f4")
        depth = ctx.depth_renderbuffer((texture_size, texture_size))
        fbo = ctx.framebuffer(color_tex, depth)
        fbo.use()
        ctx.viewport = (0, 0, texture_size, texture_size)
        fbo.clear(0.0, 0.0, 0.0, 0.0)

        ctx.enable(moderngl.DEPTH_TEST)

        program = ctx.program(
            vertex_shader="""
                #version 330
                in vec2 in_uv;
                in vec4 in_color;
                out vec4 v_color;
                void main() {
                    vec2 pos = in_uv * 2.0 - 1.0;
                    gl_Position = vec4(pos.x, pos.y, 0.0, 1.0);
                    v_color = in_color;
                }
            """,
            fragment_shader="""
                #version 330
                in vec4 v_color;
                out vec4 f_color;
                void main() {
                    f_color = v_color;
                }
            """,
        )

        if colors.shape[1] == 3:
            alpha = np.ones((colors.shape[0], 1), dtype=np.float32)
            colors = np.concatenate([colors, alpha], axis=1)

        vertices = np.concatenate([uvs, colors], axis=1).astype(np.float32)
        vbo = ctx.buffer(vertices.tobytes())
        ibo = ctx.buffer(faces.astype(np.int32).tobytes())

        vao = ctx.vertex_array(
            program,
            [(vbo, "2f 4f", "in_uv", "in_color")],
            ibo,
        )
        vao.render()

        data = fbo.read(components=4, dtype="f4", alignment=1)
        image = np.frombuffer(data, dtype=np.float32).reshape((texture_size, texture_size, 4))
        image = np.flipud(image)
        image = np.clip(image * 255.0, 0, 255).astype(np.uint8)
        return Image.fromarray(image, mode="RGBA")

    def _bake_vertex_colors(self, mesh, output_dir, base_name, texture_size=1024):
        import trimesh

        colors = self._get_vertex_colors(mesh)
        if colors is None:
            print("Texture baking skipped: no vertex colors available.")
            return None

        vertices = np.asarray(mesh.vertices, dtype=np.float32)
        faces = np.asarray(mesh.faces, dtype=np.int32)

        new_vertices, new_faces, uvs, vmapping = self._unwrap_uvs_xatlas(vertices, faces)
        new_colors = colors[vmapping]

        texture = self._rasterize_texture(uvs, new_faces, new_colors, texture_size)
        texture_path = os.path.join(output_dir, f"{base_name}_albedo.png")
        texture.save(texture_path)

        baked_mesh = trimesh.Trimesh(vertices=new_vertices, faces=new_faces, process=False)
        baked_mesh.visual = trimesh.visual.texture.TextureVisuals(uv=uvs, image=texture)
        baked_path = os.path.join(output_dir, f"{base_name}_baked.glb")
        baked_mesh.export(baked_path)

        return baked_path

    def generate(
        self,
        image_path,
        output_dir,
        *,
        resolution=512,
        threshold=30.0,
        smoothing_iterations=15,
        smoothing_lambda=0.1,
        texture_bake=False,
    ):
        """Generates 3D model from image."""
        os.makedirs(output_dir, exist_ok=True)

        processed_images = self.preprocess_images(image_path)

        # Run inference
        with torch.no_grad():
            scene_codes = self._infer_scene_codes(processed_images)

        # Export meshes
        meshes = self.model.extract_mesh(
            scene_codes,
            has_vertex_color=True,
            resolution=resolution,
            threshold=threshold,
        )

        output_files = []
        for i, mesh in enumerate(meshes):
            # Apply Laplacian smoothing to remove marching cubes artifacts
            if smoothing_iterations and smoothing_iterations > 0:
                try:
                    import trimesh.smoothing
                    trimesh.smoothing.filter_laplacian(
                        mesh,
                        iterations=smoothing_iterations,
                        lamb=smoothing_lambda,
                    )
                except Exception as e:
                    print(f"Smoothing failed: {e}")

            save_path = os.path.join(output_dir, f"model_{i}.glb")
            mesh.export(save_path)
            final_path = save_path

            if texture_bake:
                baked_path = self._try_texture_bake(mesh, output_dir, base_name=f"model_{i}")
                if baked_path and os.path.exists(baked_path):
                    final_path = baked_path

            output_files.append(final_path)

        return output_files[0] if output_files else None

    def _try_texture_bake(self, mesh, output_dir, base_name="model"):
        """Attempt experimental texture baking if deps are available."""
        try:
            import xatlas  # type: ignore
            import moderngl  # type: ignore
        except Exception:
            print("Texture baking requested but optional deps are missing.")
            return None

        try:
            return self._bake_vertex_colors(mesh, output_dir, base_name)
        except Exception as exc:
            print(f"Texture baking failed: {exc}")
            return None

# Singleton instance
engine = None

def get_engine():
    global engine
    if engine is None:
        engine = Local3DEngine()
    return engine
