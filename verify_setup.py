
import os
import sys
import traceback

print("Starting verification...")

try:
    print("Importing engine...")
    from engine import Local3DEngine
    
    print("Initializing Engine (this might download weights)...")
    engine = Local3DEngine()
    
    print("Engine initialized.")
    
    # Test generation
    input_image = os.path.join("TripoSR", "examples", "chair.png")
    output_dir = "test_output"
    os.makedirs(output_dir, exist_ok=True)
    
    if os.path.exists(input_image):
        print(f"Generating from {input_image}...")
        output_path = engine.generate(input_image, output_dir)
        print(f"Generation successful! Output: {output_path}")
    else:
        print(f"Warning: {input_image} not found, skipping generation test.")

except Exception as e:
    print("Verification Failed!")
    traceback.print_exc()

print("Verification complete.")
