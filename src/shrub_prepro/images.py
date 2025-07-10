import rasterio
import geopandas as gpd
from rasterio.windows import Window
from shapely.geometry import box
from rasterio.features import rasterize
import random
import numpy as np
import logging


def patch_window(
    geom: gpd.geoseries.GeoSeries, image: rasterio.DatasetReader, patch_size: int = 512
) -> rasterio.windows.Window:
    """
    Calculate a rasterio window centered on the centroid of a geometry.

    Args:
        geom (gpd.geoseries.GeoSeries): The geometry (typically a shrub polygon) to center the patch on.
        image (rasterio.DatasetReader): The raster image to index into.
        patch_size (int, optional): The size of the patch (in pixels). Defaults to 512.

    Returns:
        rasterio.windows.Window: The window object representing the patch region.
    """

    half_patch = patch_size // 2

    center_x, center_y = geom.centroid.x, geom.centroid.y
    row_col = image.index(center_x, center_y)

    window = Window(
        row_col[1] - half_patch, row_col[0] - half_patch, patch_size, patch_size
    )
    return window


def shrub_labels_in_window(
    geometries: gpd.GeoSeries,
    window: rasterio.windows.Window,
    image: rasterio.DatasetReader,
) -> gpd.GeoSeries:
    """
    Compute the intersection between all shrub geometries and a given window within the image.

    Args:
        geometries (gpd.GeoSeries): Series of shrub geometries.
        window (rasterio.windows.Window): The window within the image to check for intersections.
        image (rasterio.DatasetReader): The raster image (for georeferencing).

    Returns:
        gpd.GeoSeries: Series of geometries intersecting the window, with empty geometries removed.
    """
    transform = rasterio.windows.transform(window, image.transform)
    bounds = rasterio.windows.bounds(window, transform)
    bbox = box(*bounds)
    s = geometries.intersection(bbox)
    out_series = s[~(s.is_empty)]
    return out_series


def label_patch_with_window(
    geoms: gpd.GeoSeries, window: rasterio.windows.Window, image: rasterio.DatasetReader
) -> None:
    """
    Rasterize shrub geometries within a given window to create a label patch.

    Args:
        geoms (gpd.GeoSeries): Shrub geometries to rasterize.
        window (rasterio.windows.Window): The window within the image to rasterize into.
        image (rasterio.DatasetReader): The raster image (for georeferencing).

    Returns:
        np.ndarray: The rasterized label patch as a 2D numpy array.
    """
    transform = rasterio.windows.transform(window, image.transform)
    arr = rasterize(
        geoms.geometry,
        out_shape=(int(window.height), int(window.width)),
        transform=transform,
        default_value=255,
    )
    return arr


def background_samples(
    image: rasterio.io.DatasetReader, shrubs: gpd.GeoDataFrame, window_size: int = 256
) -> list:
    """
    Generate negative samples (background patches) from the image that do not overlap with shrub polygons.

    Parameters:
        image (rasterio.io.DatasetReader): Opened rasterio dataset of the image.
        shrubs (gpd.GeoDataFrame): GeoDataFrame containing shrub polygons.

    Returns:
        list: List of rasterio.windows.Window objects representing negative samples.
    """

    # Get the bounding box of the image
    img_bounds = image.bounds

    # Buffer the shrub polygons slightly to ensure negative windows don't touch them
    shrub_buffer = shrubs.copy()
    # Adjust buffer distance based on your data's CRS units.
    # If it's meters, a small buffer like 1-5 meters is reasonable.
    # If it's degrees, you might need a smaller value or reproject.
    # Assuming CRS is in meters based on the previous context, buffer by 5 meters.
    try:
        shrub_buffer["geometry"] = shrub_buffer.geometry.buffer(5)
    except Exception as e:
        logging.info(
            f"Could not buffer polygons, likely due to CRS or geometry issues: {e}"
        )
        logging.info("Proceeding without buffering, this might lead to minor overlaps.")
        shrub_buffer = shrubs  # Use original shrubs if buffering fails

    shrub_union = shrub_buffer.unary_union

    # Determine the number of negative samples to generate
    num_positive_samples = len(shrubs)
    num_negative_samples = num_positive_samples * 2  # Adjust this ratio as needed

    negative_windows = []  # Set up a list of empty patches

    # Generate random points within the image bounds until we have enough negative windows
    logging.info(f"Attempting to generate {num_negative_samples} negative windows...")
    attempts = 0
    max_attempts = num_negative_samples * 10  # Limit attempts to avoid infinite loops

    while len(negative_windows) < num_negative_samples and attempts < max_attempts:
        # Generate a random point within the image bounds
        rand_x = random.uniform(img_bounds.left, img_bounds.right)
        rand_y = random.uniform(img_bounds.bottom, img_bounds.top)

        # Convert random coordinates to pixel row and column
        try:
            row, col = image.index(rand_x, rand_y)
        except rasterio.errors.CRSError:
            # This can happen if the coordinates are slightly outside valid range due to float precision
            attempts += 1
            continue
        except Exception as e:
            logging.info(f"Error converting coordinates to index: {e}")
            attempts += 1
            continue

        # Create a potential window centered at the random point
        half_patch = window_size // 2
        potential_window = Window(
            col - half_patch, row - half_patch, window_size, window_size
        )

        # Calculate the geographic bounds of the potential window
        window_bounds = rasterio.windows.bounds(potential_window, image.transform)
        window_bbox = box(*window_bounds)

        # Check if the potential window is entirely within the image bounds
        if not box(*img_bounds).contains(window_bbox):
            attempts += 1
            continue

        # Check if the potential window overlaps with any shrub polygon (or buffer)
        # Convert the window bbox to a GeoDataFrame for intersection check
        window_gdf = gpd.GeoDataFrame([1], geometry=[window_bbox], crs=image.crs)

        # Perform the intersection check
        if shrub_union is not None:
            overlap = window_gdf.iloc[0].geometry.intersects(shrub_union)
        else:
            # No shrubs, no overlap to check
            overlap = False

        # If there is no overlap, add the window to our list
        if overlap:
            attempts += 1
            continue

        # Check for more than one distinct pixel value - a lot of our image is nodata
        window_data = image.read(window=potential_window)

        if len(np.unique(window_data)) > 1:
            negative_windows.append(potential_window)

        attempts += 1
    return negative_windows


def background_label(size: int = 256) -> np.ndarray:
    """Return a 2D array of size*size all zeros, for use as a background label (no features)"""
    return np.zeros((size, size), dtype=np.uint8)
