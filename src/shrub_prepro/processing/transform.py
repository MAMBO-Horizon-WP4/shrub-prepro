def process_data(
    raster_path,
    shapefile_path,
    output_dir,
    label,
    window_size=512,
    rotate_angles=[90, 180, 270],
):
    """Process a generic raster to extract window-sized outputs around polygon centers."""
    # ...existing process_data code...
