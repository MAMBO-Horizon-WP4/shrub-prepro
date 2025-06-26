from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
import rasterio
from shapely.geometry import Polygon

from shrub_prepro import images


@pytest.fixture
def test_data_dir():
    """Create and return test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture
def sample_raster(tmp_path):
    """Create a small test raster."""
    raster_dir = tmp_path / "input"
    raster_dir.mkdir(parents=True, exist_ok=True)
    raster_path = raster_dir / "sample.tif"

    # Create 10x10 RGB raster
    with rasterio.open(
        raster_path,
        "w",
        driver="GTiff",
        height=10,
        width=10,
        count=3,
        dtype=rasterio.uint8,
        crs="EPSG:4326",
        transform=rasterio.transform.from_bounds(0, 0, 1, 1, 10, 10),
    ) as dst:
        # Fill with random data
        data = np.random.randint(0, 255, size=(3, 10, 10), dtype=np.uint8)
        dst.write(data)

    return raster_path


@pytest.fixture
def sample_polygons(tmp_path):
    """Create a small test shapefile."""
    poly_dir = tmp_path / "input"
    poly_dir.mkdir(parents=True, exist_ok=True)

    polygon = Polygon([(0.2, 0.2), (0.8, 0.2), (0.8, 0.8), (0.2, 0.8)])
    gdf = gpd.GeoDataFrame({"geometry": [polygon]}, crs="EPSG:4326")

    output_path = poly_dir / "sample.shp"
    gdf.to_file(output_path)
    return output_path


@pytest.fixture(autouse=True)
def cleanup(test_data_dir):
    """Clean up test files after each test."""
    yield
    # Comment out during test development to inspect outputs
    for file in test_data_dir.glob("*"):
        file.unlink()


def test_patch_window(sample_polygons, sample_raster):
    """Test that patch_window returns a valid rasterio window."""
    gdf = gpd.read_file(sample_polygons)
    with rasterio.open(sample_raster) as img:
        window = images.patch_window(gdf.geometry.iloc[0], img, patch_size=6)
        assert isinstance(window, rasterio.windows.Window)
        # The window should be the requested size
        assert window.width == 6
        assert window.height == 6


def test_shrub_labels_in_window(sample_polygons, sample_raster):
    """Test that shrub_labels_in_window returns intersecting geometries."""
    gdf = gpd.read_file(sample_polygons)
    with rasterio.open(sample_raster) as img:
        window = images.patch_window(gdf.geometry.iloc[0], img, patch_size=10)
        intersecting = images.shrub_labels_in_window(gdf.geometry, window, img)
        assert isinstance(intersecting, gpd.GeoSeries)
        # Should not be empty for this synthetic data
        assert not intersecting.empty


def test_label_patch_with_window(sample_polygons, sample_raster):
    """Test that label_patch_with_window returns a correct rasterized array."""
    gdf = gpd.read_file(sample_polygons)
    with rasterio.open(sample_raster) as img:
        window = images.patch_window(gdf.geometry.iloc[0], img, patch_size=10)
        intersecting = images.shrub_labels_in_window(gdf.geometry, window, img)
        arr = images.label_patch_with_window(intersecting, window, img)
        assert isinstance(arr, np.ndarray)
        assert arr.shape == (10, 10)
        # Should contain the default value (255) and possibly 0
        assert np.any(arr == 255)
