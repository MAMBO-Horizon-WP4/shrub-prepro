import geopandas as gpd
import rasterio
from rasterio.features import rasterize
from rasterio.mask import mask
from shapely.geometry import box, shape


def clip_raster_to_extent(raster_path, shapefile_path, output_path):
    """Clips a raster to the bounding box of the shapefile's geometries."""
    gdf = gpd.read_file(shapefile_path)
    bbox = gdf.geometry.total_bounds  # [minx, miny, maxx, maxy]
    bbox_geom = [box(*bbox)]

    with rasterio.open(raster_path) as src:
        out_image, out_transform = mask(src, bbox_geom, crop=True)
        out_meta = src.meta.copy()

        # Update metadata with new dimensions and transform
        out_meta.update(
            {
                "height": out_image.shape[1],
                "width": out_image.shape[2],
                "transform": out_transform,
                "dtype": src.meta["dtype"],
            }
        )

        with rasterio.open(output_path, "w", **out_meta) as dest:
            dest.write(out_image)


def create_binary_raster(raster_path, shapefile_path, output_path):
    """Creates a binary raster where 1 indicates the presence of polygons.

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

        with rasterio.open(output_path, "w", **meta) as dst:
            binary = rasterize(
                shapes=shapes,
                out_shape=src.shape,
                transform=src.transform,
                fill=0,
                dtype=rasterio.uint8,
            )
            dst.write(binary, 1)
