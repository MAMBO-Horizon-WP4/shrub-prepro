import rasterio
from rasterio.features import rasterize
from rasterio.mask import mask
from rasterio.windows import Window
import geopandas as gpd
from shapely.geometry import shape, box
import numpy as np
from scipy.ndimage import zoom
from PIL import Image
import os
from tqdm import tqdm


def clip_raster_to_extent(raster_path, shapefile_path, output_path):
    """
    Clips a raster to the bounding box of the shapefile's geometries.

    Parameters:
        raster_path (str): Path to the input raster file.
        shapefile_path (str): Path to the shapefile with polygons.
        output_path (str): Path to save the clipped raster.
    """
    gdf = gpd.read_file(shapefile_path)
    bbox = gdf.geometry.total_bounds  # [minx, miny, maxx, maxy]
    bbox_geom = [box(*bbox)]

    with rasterio.open(raster_path) as src:
        out_image, out_transform = mask(src, bbox_geom, crop=True)
        out_meta = src.meta.copy()

        # Update metadata with new dimensions and transform
        out_meta.update({
            "height": out_image.shape[1],
            "width": out_image.shape[2],
            "transform": out_transform,
            "dtype": src.meta["dtype"],
        })

        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(out_image)


def create_binary_raster(raster_path, shapefile_path, output_path):
    """
    Creates a binary raster where 1 indicates the presence of polygons.

    Parameters:
        raster_path (str): Path to the input raster file.
        shapefile_path (str): Path to the shapefile.
        output_path (str): Path to save the binary raster.
    """
    with rasterio.open(raster_path) as src:
        meta = src.meta.copy()
        meta.update(dtype=rasterio.uint8, count=1)

        gdf = gpd.read_file(shapefile_path)
        shapes = [(shape(geom), 1) for geom in gdf.geometry]

        with rasterio.open(output_path, 'w', **meta) as dst:
            binary = rasterize(shapes=shapes, out_shape=src.shape, transform=src.transform, fill=0, dtype=rasterio.uint8)
            dst.write(binary, 1)


def process_data(raster_path, shapefile_path, output_dir, label, window_size=512, rotate_angles=[90, 180, 270]):
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
    # Open the raster and shapefile
    with rasterio.open(raster_path) as src:
        gdf = gpd.read_file(shapefile_path)

        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Process each polygon
        for i, row in tqdm(enumerate(gdf.iterrows()), total=len(gdf), desc="Processing Samples"):
            geom = shape(row[1].geometry)
            center_x, center_y = geom.centroid.x, geom.centroid.y
            row_col = src.index(center_x, center_y)

            half_size = window_size // 2
            window = Window(row_col[1] - half_size, row_col[0] - half_size, window_size, window_size)

            # Read the data within the window
            try:
                window_data = src.read(window=window)
            except ValueError:
                print(f"Skipping polygon {i} as it is out of bounds.")
                continue

            # Save the original window
            transform = rasterio.windows.transform(window, src.transform)
            meta = src.meta.copy()
            meta.update({
                "height": window_data.shape[1],
                "width": window_data.shape[2],
                "transform": transform
            })

            original_path = os.path.join(output_dir, f"{label}_{i}_rot0.tif")
            with rasterio.open(original_path, "w", **meta) as dst:
                dst.write(window_data)

            # Generate rotated versions
            for angle in rotate_angles:
                img = Image.fromarray(np.moveaxis(window_data, 0, -1))  # Convert to HWC
                rotated = img.rotate(angle, expand=True)
                rotated_data = np.moveaxis(np.array(rotated), -1, 0)  # Convert back to CHW

                rotated_path = os.path.join(output_dir, f"{label}_{i}_rot{angle}.tif")
                with rasterio.open(rotated_path, "w", **meta) as dst:
                    dst.write(rotated_data)
