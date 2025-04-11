"""Create small test samples from S3 data for testing."""

import argparse
from pathlib import Path
import rasterio
import geopandas as gpd
import s3fs


def get_sample_bbox(raster_path: str, max_pixels: int = 1000) -> tuple:
    """
    Generate a sample bbox from COG metadata that will result in a window < max_pixels.

    Args:
        raster_path: S3 path to COG
        max_pixels: Maximum size in pixels for either dimension

    Returns:
        tuple: (minx, miny, maxx, maxy)
    """
    fs = s3fs.S3FileSystem(anon=False)
    with rasterio.open(fs.open(raster_path)) as src:
        # Get full bounds
        bounds = src.bounds
        transform = src.transform

        # Calculate center point
        center_x = (bounds.left + bounds.right) / 2
        center_y = (bounds.bottom + bounds.top) / 2

        # Calculate pixel size
        pixel_width = abs(transform[0])
        pixel_height = abs(transform[4])

        # Calculate bbox size that will give us < max_pixels
        width_meters = pixel_width * max_pixels * 0.9  # 90% of max to be safe
        height_meters = pixel_height * max_pixels * 0.9

        # Create bbox centered on image center
        minx = center_x - (width_meters / 2)
        maxx = center_x + (width_meters / 2)
        miny = center_y - (height_meters / 2)
        maxy = center_y + (height_meters / 2)

        return (minx, miny, maxx, maxy)


def create_test_samples(
    s3_raster: str,
    s3_polygons: str,
    output_dir: Path,
    bbox: tuple = None,
    label: str = "test",
    max_pixels: int = 1000,
):
    """
    Extract small samples from S3 data for testing.

    Args:
        s3_raster: S3 path to raster (e.g. s3://bucket/rgb.tif)
        s3_polygons: S3 path to polygons (e.g. s3://bucket/shrubs.shp)
        output_dir: Local directory to save samples
        bbox: Optional tuple of (minx, miny, maxx, maxy). If None, auto-generated
        label: Label for output files
        max_pixels: Maximum size in pixels for auto-generated bbox
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Auto-generate bbox if not provided
    if bbox is None:
        print("Generating sample bbox from COG metadata...")
        bbox = get_sample_bbox(s3_raster, max_pixels)
        print(f"Generated bbox: {bbox}")

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
        nargs=4,
        type=float,
        help="Optional bounding box: minx miny maxx maxy. If not provided, auto-generated",
    )
    parser.add_argument("--label", default="test", help="Label for output files")
    parser.add_argument(
        "--max-pixels",
        type=int,
        default=1000,
        help="Maximum size in pixels for auto-generated bbox",
    )

    args = parser.parse_args()

    create_test_samples(
        args.s3_raster,
        args.s3_polygons,
        args.output_dir,
        tuple(args.bbox) if args.bbox else None,
        args.label,
        args.max_pixels,
    )


if __name__ == "__main__":
    main()
