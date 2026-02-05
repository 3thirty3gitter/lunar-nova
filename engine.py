import os
import sys
import torch
import numpy as np
from PIL import Image
import rembg
import logging

# Add TripoSR repo to path so imports work
current_dir = os.path.dirname(os.path.abspath(__file__))
triposr_dir = os.path.join(current_dir, "TripoSR")
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
        """Loads and pre-processes image (bg removal, resizing)"""
        if isinstance(input_image_path, str):
            image = Image.open(input_image_path)
        else:
            image = input_image_path # Assume PIL image already

        # Remove background
        image = remove_background(image, self.rembg_session)
        image = resize_foreground(image, 0.85)
        
        # Prepare for model
        image = np.array(image).astype(np.float32) / 255.0
        image = image[:, :, :3] * image[:, :, 3:4] + (1 - image[:, :, 3:4]) * 0.5
        image = Image.fromarray((image * 255.0).astype(np.uint8))
        return image

    def generate(self, image_path, output_dir):
        """Generates 3D model from image"""
        os.makedirs(output_dir, exist_ok=True)
        
        processed_image = self.preprocess_image(image_path)
        
        # Run inference
        with torch.no_grad():
            scene_codes = self.model([processed_image], device=self.device)
        
        # Export meshes
        # Lowering threshold back to 30.0 for more volume/stability
        meshes = self.model.extract_mesh(scene_codes, has_vertex_color=True, resolution=512, threshold=30.0)
        
        output_files = []
        for i, mesh in enumerate(meshes):
            # Apply Laplacian smoothing to remove marching cubes artifacts
            try:
                import trimesh.smoothing
                # Moderate smoothing to keep the shape but lose the noise
                trimesh.smoothing.filter_laplacian(mesh, iterations=15, lamb=0.1)
            except Exception as e:
                print(f"Smoothing failed: {e}")

            save_path = os.path.join(output_dir, f"model_{i}.glb")
            mesh.export(save_path)
            output_files.append(save_path)
            
        return output_files[0] if output_files else None

# Singleton instance
engine = None

def get_engine():
    global engine
    if engine is None:
        engine = Local3DEngine()
    return engine
