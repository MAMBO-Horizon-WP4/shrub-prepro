import argparse
from pathlib import Path

from shrub_prepro.processing.raster import clip_raster_to_extent, create_binary_raster
from shrub_prepro.processing.transform import process_data


def main():
    parser = argparse.ArgumentParser(description="Process shrub data from RGB imagery")
    parser.add_argument(
        "--input-raster", required=True, help="S3 path or local path to input raster"
    )
    parser.add_argument(
        "--input-polygons",
        required=True,
        help="S3 path or local path to input polygons",
    )
    parser.add_argument("--output-dir", required=True, help="Output directory (local)")
    parser.add_argument("--label", default="rgb", help="Label for output files")

    args = parser.parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Pipeline steps
    print("Preparing datasets...")
    clipped_raster = output_dir / "clipped_rgb.tif"
    binary_raster = output_dir / "binary_raster.tif"

    clip_raster_to_extent(args.input_raster, args.input_polygons, clipped_raster)
    create_binary_raster(clipped_raster, args.input_polygons, binary_raster)
    process_data(clipped_raster, args.input_polygons, output_dir, label=args.label)


if __name__ == "__main__":
    main()
