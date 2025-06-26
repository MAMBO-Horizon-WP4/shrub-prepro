import os
import s3fs
import rasterio
import numpy as np


def get_s3_file(s3_path):
    """
    Open a file from S3 using s3fs.

    Args:
        s3_path (str): S3 path in format 's3://bucket/path/to/file'

    Returns:
        file-like object
    """
    fs = s3fs.S3FileSystem(anon=False)
    return fs.open(s3_path, "rb")


def save_label_patch(
    data: np.ndarray,
    window: rasterio.windows.Window,
    image: rasterio.DatasetReader,
    index: int,
    label: str = "shrubs",
    dir: str = "labels",
) -> None:
    """
    Save a single-channel label patch as a GeoTIFF file.

    Args:
        data (np.ndarray): The label data array to save (2D, single channel).
        window (rasterio.windows.Window): The window in the original image corresponding to this patch.
        image (rasterio.DatasetReader): The source rasterio image object (for metadata).
        index (int): Index for naming the output file.
        label (str, optional): Prefix label for the output filename. Defaults to 'shrubs'.
        dir (str, optional): Directory to save the label patch. Defaults to 'labels'.

    Returns:
        None
    """
    transform = rasterio.windows.transform(window, image.transform)
    meta = image.meta.copy()
    meta.update(
        {
            "height": window.height,
            "width": window.width,
            "transform": transform,
            "count": 1,
        }
    )

    original_path = os.path.join(dir, f"{label}_{index}.tif")
    with rasterio.open(original_path, "w", **meta) as dst:
        dst.write(data, 1)


def save_image_patch(
    window: rasterio.windows.Window,
    image: rasterio.DatasetReader,
    index: int,
    label: str = "shrubs",
    dir: str = "images",
) -> rasterio.DatasetReader:
    """
    Save a multi-channel image patch as a GeoTIFF file.

    Args:
        window (rasterio.windows.Window): The window in the original image corresponding to this patch.
        image (rasterio.DatasetReader): The source rasterio image object (for metadata and reading).
        index (int): Index for naming the output file.
        label (str, optional): Prefix label for the output filename. Defaults to 'shrubs'.
        dir (str, optional): Directory to save the image patch. Defaults to 'images'.

    Returns:
        None
    """
    # Extract the image data for the current patch
    image_patch = image.read(window=window)
    # Save the original window
    transform = rasterio.windows.transform(window, image.transform)
    meta = image.meta.copy()
    meta.update(
        {
            "height": window.height,
            "width": window.width,
            "transform": transform,
        }
    )

    original_path = os.path.join(dir, f"{label}_{index}.tif")
    with rasterio.open(original_path, "w", **meta) as dst:
        dst.write(image_patch)
