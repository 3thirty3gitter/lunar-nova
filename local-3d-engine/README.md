# Local 3D Engine

This is a local AI engine for generating 3D models from images using [TripoSR](https://github.com/VAST-AI-Research/TripoSR).

## Setup

1.  Create a virtual environment (recommended).
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *Note: For Windows, `PyMCubes` is used instead of `torchmcubes`.*

## Running the Server

Start the FastAPI server:

```bash
python app.py
```

The server will start at `http://localhost:8000`.
Open this URL in your browser to access the Web UI.

## Usage

1.  Open the Web UI.
2.  Upload an image (remove background preferred, but the engine handles basic removal).
3.  Click "Generate".
4.  View and download the resulting `.glb` model.

## API

-   `POST /generate`: Upload a file (`file` form-data) to generate a model. Returns the `.glb` file.

## Troubleshooting

-   If CUDA is not available, it will fall back to CPU (slower).
-   Ensure you have the correct PyTorch version for your hardware.
