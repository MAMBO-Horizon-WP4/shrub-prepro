from pathlib import Path

import geopandas as gpd
import numpy as np
import pytest
import rasterio
from shapely.geometry import Polygon

from shrub_prepro.processing.raster import clip_raster_to_extent, create_binary_raster


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


def test_clip_raster_to_extent(sample_raster, sample_polygons, tmp_path):
    """Test that clipping produces a valid smaller raster."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "clipped.tif"

    clip_raster_to_extent(sample_raster, sample_polygons, output_path)

    with rasterio.open(output_path) as src:
        assert src.shape[0] <= 10  # Should be smaller than original
        assert src.shape[1] <= 10
        assert src.count == 3  # Should maintain RGB channels


def test_create_binary_raster(sample_raster, sample_polygons, tmp_path):
    """Test that binary raster creation produces valid output."""
    output_dir = tmp_path / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "binary.tif"

    create_binary_raster(sample_raster, sample_polygons, output_path)

    with rasterio.open(output_path) as src:
        data = src.read(1)  # Read first band
        assert data.dtype == np.uint8
        assert set(np.unique(data)).issubset({0, 1})  # Should only contain 0s and 1s


@pytest.fixture(autouse=True)
def cleanup(test_data_dir):
    """Clean up test files after each test."""
    yield
    # Comment out during test development to inspect outputs
    for file in test_data_dir.glob("*"):
        file.unlink()
