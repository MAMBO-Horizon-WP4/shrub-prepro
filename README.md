# Shrub Samples Pre-Processing

This repository contains scripts for pre-processing geospatial data, specifically for:
- Creating binary masks from shapefiles.
- Combining RGB imagery with DSM data into processed samples.
- Generating rotated versions of processed images.

## Folder Structure
```
shrub-prepro/
│
├── data/
│   ├── input/
│   └── output/
│       ├── samples/
│       └── images/
├── src/
│   ├── utils.py              # All utility functions (clipping, rasterizing, processing)
│   └── run_pipeline.py       # Main pipeline script
├── tests/
├── .gitignore
├── README.md
├── requirements.txt
```

## How to Use
1. Place input files in `data/input/`.
    - RGB raster
    - Polygons shapefile
2. Run the pipeline using `run_pipeline.py`.
    - Adjust the names of the files as necessary
3. Outputs will be saved in `data/output/`.
    - Image files with individual shrubs (images)
    - Binary masks with pixels belonging to shrubs (samples)

## License
MIT License
