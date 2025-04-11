"""Create small test samples from S3 data for testing."""

import argparse
from pathlib import Path
import rasterio
import geopandas as gpd
import s3fs
from shapely.geometry import box


def create_test_samples(
    s3_raster: str, s3_polygons: str, output_dir: Path, bbox: tuple, label: str = "test"
):
    """
    Extract small samples from S3 data for testing.

    Args:
        s3_raster: S3 path to raster (e.g. s3://bucket/rgb.tif)
        s3_polygons: S3 path to polygons (e.g. s3://bucket/shrubs.shp)
        output_dir: Local directory to save samples
        bbox: Tuple of (minx, miny, maxx, maxy)
        label: Label for output files
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    bbox_geom = box(*bbox)
    fs = s3fs.S3FileSystem(anon=False)

    # Extract raster window
    print(f"Reading raster window from {s3_raster}")
    with rasterio.open(fs.open(s3_raster)) as src:
        window = rasterio.windows.from_bounds(*bbox, transform=src.transform)
        data = src.read(window=window)
        profile = src.profile.copy()
        profile.update(
            {
                "height": window.height,
                "width": window.width,
                "transform": rasterio.windows.transform(window, src.transform),
            }
        )

    # Save raster sample
    raster_out = output_dir / f"{label}_raster.tif"
    print(f"Saving raster sample to {raster_out}")
    with rasterio.open(raster_out, "w", **profile) as dst:
        dst.write(data)

    # Extract polygons within bbox
    print(f"Reading polygons from {s3_polygons}")
    gdf = gpd.read_file(fs.open(s3_polygons), bbox=bbox)

    # Save polygon sample
    poly_out = output_dir / f"{label}_polygons.shp"
    print(f"Saving {len(gdf)} polygons to {poly_out}")
    gdf.to_file(poly_out)


def main():
    parser = argparse.ArgumentParser(description="Create test samples from S3 data")
    parser.add_argument("--s3-raster", required=True, help="S3 path to raster")
    parser.add_argument("--s3-polygons", required=True, help="S3 path to polygons")
    parser.add_argument("--output-dir", required=True, help="Output directory")
    parser.add_argument(
        "--bbox",
        required=True,
        nargs=4,
        type=float,
        help="Bounding box: minx miny maxx maxy",
    )
    parser.add_argument("--label", default="test", help="Label for output files")

    args = parser.parse_args()

    create_test_samples(
        args.s3_raster, args.s3_polygons, args.output_dir, tuple(args.bbox), args.label
    )


if __name__ == "__main__":
    main()
