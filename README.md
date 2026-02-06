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

-   `POST /generate`: Upload one or more images (`files` form-data) to generate a model. Returns the `.glb` file.
    - Optional form fields:
        - `resolution`: `256` (fast) or `512` (high). Defaults to `512`.
        - `smoothing`: `none`, `low`, `medium`, or `high`. Defaults to `medium`.
        - `threshold`: float between `15` and `45` (density threshold). Defaults to `30.0`.
        - `texture_bake`: `true` or `false` (experimental). Defaults to `false`.

-   `POST /generate_async`: Upload one or more images to start a background job. Returns `{ job_id, status }`.
    - Optional form fields:
        - `resolution`: `256` (fast) or `512` (high). Defaults to `512`.
        - `smoothing`: `none`, `low`, `medium`, or `high`. Defaults to `medium`.
        - `threshold`: float between `15` and `45` (density threshold). Defaults to `30.0`.
        - `texture_bake`: `true` or `false` (experimental). Defaults to `false`.

-   `GET /status/{job_id}`: Check background job status.

-   `GET /result/{job_id}`: Download the `.glb` when status is `complete`.

-   `GET /jobs`: List recent jobs (default limit 25).

Job history is persisted to `outputs/jobs.json` so recent runs survive restarts.

## Troubleshooting

-   If CUDA is not available, it will fall back to CPU (slower).
-   Ensure you have the correct PyTorch version for your hardware.
