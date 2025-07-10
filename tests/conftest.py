import pytest
import numpy as np
import rasterio
from rasterio.transform import from_bounds
import geopandas as gpd
from shapely.geometry import Polygon


@pytest.fixture
def sample_raster(tmp_path):
    """Create a 3-band 20x20 raster with realistic UTM bounds."""
    raster_path = tmp_path / "sample.tif"
    width = height = 20
    # Use UTM coordinates (meters), e.g., somewhere in central Europe
    bounds = (500000, 0, 502000, 2000)  # left, bottom, right, top
    transform = from_bounds(*bounds, width, height)
    data = np.random.randint(0, 255, size=(3, height, width), dtype=np.uint8)
    with rasterio.open(
        raster_path,
        "w",
        driver="GTiff",
        height=height,
        width=width,
        count=3,
        dtype=np.uint8,
        crs="EPSG:32633",  # UTM zone 33N
        transform=transform,
    ) as dst:
        dst.write(data)
    return raster_path


@pytest.fixture
def sample_polygons(tmp_path):
    """Create a GeoDataFrame with a few polygons within the raster bounds (UTM meters)."""
    # These polygons are within the (500000,0)-(502000,2000) bounds
    polys = [
        Polygon([(500100, 1100), (500300, 1100), (500300, 1300), (500100, 1300)]),
        Polygon([(501000, 1000), (501200, 1000), (501200, 1200), (501000, 1200)]),
        Polygon([(500400, 1600), (500600, 1600), (500600, 1800), (500400, 1800)]),
    ]
    gdf = gpd.GeoDataFrame({"geometry": polys}, crs="EPSG:32633")
    poly_path = tmp_path / "sample_polygons.gpkg"
    gdf.to_file(poly_path, driver="GPKG")
    return poly_path
