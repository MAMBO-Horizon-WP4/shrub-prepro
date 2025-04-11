# Shrub Samples Pre-Processing

This repository contains scripts for pre-processing geospatial data, specifically for:
- Creating binary masks from shapefiles.
- Combining RGB imagery with DSM data into processed samples.
- Generating rotated versions of processed images.

## Installation

1. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install in development mode:
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
└── src
    ├── __init__.py
    ├── run_pipeline.py
    ├── shrub_prepro
    │   ├── cli.py
    │   ├── __init__.py
    │   ├── io
    │   │   ├── __init__.py
    │   │   └── s3.py
    │   └── processing
    │       ├── __init__.py
    │       ├── raster.py
    │       └── transform.py
├── tests/
├── .gitignore
├── README.md
├── requirements.txt
```

## How to Use
1. Place input files in `data/input/` or use S3 paths:
    - RGB raster
    - Polygons shapefile
2. Run the pipeline using the CLI:
```bash
shrub-prepro \
    --input-raster s3://bucket/path/to/rgb.tif \
    --input-polygons s3://bucket/path/to/shrubs.shp \
    --output-dir data/output \
    --label rgb
```
3. Outputs will be saved in `data/output/`:
    - Image files with individual shrubs (images)
    - Binary masks with pixels belonging to shrubs (samples)

## Development

Run tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=shrub_prepro
```

## License
MIT License
