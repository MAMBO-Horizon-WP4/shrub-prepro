import os

import geopandas as gpd
import rasterio
from tqdm import tqdm
from pathlib import Path


from shrub_prepro.images import (
    patch_window,
    shrub_window,
    shrub_overlaps,
    label_patch_with_window,
    shrub_labels_in_window,
    background_samples,
    background_label,
    is_shrub_huge,
)
from shrub_prepro.io import save_image_patch, save_label_patch
from shrub_prepro.split import test_train_split


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

    # Source of our polygon labels
    shrubs = gpd.read_file(shapefile_path)
    total_shrubs = len(shrubs)

    # Open the raster once, and read small windows from it.
    with rasterio.open(raster_path) as image:
        for index, shrub in tqdm(
            shrubs.iterrows(), total=len(shrubs), desc="Shrub images and labels"
        ):
            windows = []
            # Window defined by the shrub bounds
            shrub_px = shrub_window(shrub, image)
            print(shrub_px.height, shrub_px.width)
            if is_shrub_huge(shrub_px, window_size):
                print("IT'S HUGE!!")
                windows = shrub_overlaps(shrub, image, window_size)
            else:
                windows = [patch_window(shrub.geometry, image, patch_size=window_size)]

            for i, window in enumerate(windows):
                # Naming scheme, track whether a shrub has multi windows
                use_index = f"{index}.{i}"
                labels = shrub_labels_in_window(shrubs, window, image)
                arr = label_patch_with_window(labels, window, image)
                save_image_patch(
                    window, image, use_index, label=label, directory=images_dir
                )
                save_label_patch(
                    arr, window, image, use_index, label=label, directory=labels_dir
                )

        print("Selecting background examples")
        negative_windows = background_samples(
            image, shrubs, window_size=window_size, within_df=True
        )
        for index, neg_window in enumerate(
            tqdm(
                negative_windows,
                total=len(negative_windows),
                desc="Background images and labels",
            )
        ):
            idx = total_shrubs + index
            # Use the same label string as filename; start index after shrubs end
            save_image_patch(neg_window, image, idx, label=label, directory=images_dir)

            save_label_patch(
                background_label(),
                window,
                image,
                idx,
                label=label,
                directory=labels_dir,
            )

    # Finally break this into a dedicated test set the model will never see,
    # And leave the rest for training/validation
    test_train_split(output_dir)
