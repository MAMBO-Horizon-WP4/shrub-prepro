import os

import geopandas as gpd
import rasterio
from tqdm import tqdm
from pathlib import Path


from shrub_prepro.images import (
    patch_window,
    label_patch_with_window,
    shrub_labels_in_window,
    background_samples,
    background_label,
)
from shrub_prepro.io import save_image_patch, save_label_patch


def process_data(
    raster_path,
    shapefile_path,
    output_dir,
    label,
    window_size=512,
):
    """
    Process a generic raster to extract window-sized outputs around polygon centers.

    Parameters:
        raster_path (str): Path to the input raster file.
        shapefile_path (str): Path to the shapefile containing polygons.
        output_dir (str): Directory to save individual window-sized outputs.
        label (str): Label of the outputs
        window_size (int): Size of the square window to extract (default: 512).
        rotate_angles (list): List of angles (in degrees) to rotate the windows (default: [90, 180, 270]).

    Returns:
        None
    """

    labels_dir = Path(output_dir) / "labels"
    images_dir = Path(output_dir) / "images"
    os.makedirs(labels_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)

    # Open the raster and shapefile
    with rasterio.open(raster_path) as image:
        shrubs = gpd.read_file(shapefile_path)

        for index, shrub in tqdm(
            shrubs.iterrows(), total=len(shrubs), desc="Processing Samples"
        ):
            window = patch_window(shrub.geometry, image, patch_size=window_size)
            labels = shrub_labels_in_window(shrubs, window, image)
            arr = label_patch_with_window(labels, window, image)
            save_image_patch(window, image, index, label=label, dir=images_dir)
            save_label_patch(arr, window, image, index, label=label, dir=labels_dir)

        negative_windows = background_samples(image, shrubs)
        for index, neg_window in enumerate(
            tqdm(negative_windows, total=len(negative_windows))
        ):
            save_image_patch(neg_window, image, index, label="negative", dir="images")

        save_label_patch(
            background_label(), window, image, 0, label="negative", dir="train/labels"
        )
