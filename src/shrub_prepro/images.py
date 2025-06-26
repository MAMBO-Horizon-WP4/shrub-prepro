import rasterio
import geopandas as gpd
from rasterio.windows import Window
from shapely.geometry import box
from rasterio.features import rasterize


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
