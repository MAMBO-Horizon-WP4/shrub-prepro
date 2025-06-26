import argparse
from pathlib import Path
from shrub_prepro.processing import process_data


if __name__ == "__main__":
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
    print("Preparing training data...")

    process_data(args.input_raster, args.input_polygons, output_dir, label=args.label)
