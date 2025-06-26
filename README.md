# Shrub Samples Pre-Processing

This repository provides a Python package and CLI for pre-processing geospatial data, specifically for:
- Creating binary masks from shapefiles.
- Combining RGB imagery with DSM data into processed samples.
- Generating rotated versions of processed images.
- Supporting both local and S3 input data.

## Installation

1. Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

2. Install the package in development mode with all dev dependencies:
    ```bash
    pip install -e ".[dev]"
    ```

## Folder Structure

```
shrub-prepro/
│
├── data/
│   ├── input/
│   └── output/
│       ├── samples/
│       └── images/
├── scripts/
│   └── create_test_samples.py
├── src/
│   ├── __init__.py
│   ├── run_pipeline.py
│   └── shrub_prepro/
│       ├── __init__.py
│       ├── cli.py
│       ├── images.py
│       ├── io.py
│       └── processing/
│           ├── __init__.py
│           ├── raster.py
│           └── transform.py
├── tests/
│   └── test_pipeline.py
├── .github/
│   └── workflows/
│       └── tests.yml
├── .gitignore
├── README.md
├── pyproject.toml
```

## Usage

You can run the main pipeline from the command line, using either local or S3 paths for input:

```bash
shrub-prepro \
    --input-raster s3://bucket/path/to/rgb.tif \
    --input-polygons s3://bucket/path/to/shrubs.shp \
    --output-dir data/output \
    --label rgb
```

Outputs will be saved in `data/output/`:
- Image files with individual shrubs (images)
- Binary masks with pixels belonging to shrubs (samples)

### Creating Test Samples from S3

To generate small test samples from large S3 datasets for local testing:

```bash
python scripts/create_test_samples.py \
    --s3-raster s3://bucket/path/to/rgb.tif \
    --s3-polygons s3://bucket/path/to/shrubs.shp \
    --output-dir tests/data
```

## Development

- Run tests:
    ```bash
    pytest
    ```

- Run tests with coverage:
    ```bash
    pytest --cov=shrub_prepro
    ```

- Lint the code:
    ```bash
    black --check src tests
    isort --check-only src tests
    ```

## Continuous Integration

- GitHub Actions workflow runs on every push and pull request:
    - Lints the code with `black` and `isort`
    - Runs all tests with coverage
    - Uploads the coverage report as an artifact

## License

MIT License
