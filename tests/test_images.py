import numpy as np
import rasterio
import geopandas as gpd
from shrub_prepro import images


def test_patch_window(sample_polygons, sample_raster):
    """Test patch_window returns a valid rasterio window of correct size."""
    gdf = gpd.read_file(sample_polygons)
    with rasterio.open(sample_raster) as img:
        window = images.patch_window(gdf.geometry.iloc[0], img, patch_size=8)
        assert isinstance(window, rasterio.windows.Window)
        assert window.width == 8
        assert window.height == 8


def test_shrub_labels_in_window(sample_polygons, sample_raster):
    """Test shrub_labels_in_window returns intersecting geometries."""
    gdf = gpd.read_file(sample_polygons)
    with rasterio.open(sample_raster) as img:
        window = images.patch_window(gdf.geometry.iloc[0], img, patch_size=10)
        intersecting = images.shrub_labels_in_window(gdf.geometry, window, img)
        assert isinstance(intersecting, gpd.GeoSeries)
        assert not intersecting.empty


def test_label_patch_with_window(sample_polygons, sample_raster):
    """Test label_patch_with_window returns a correct rasterized array."""
    gdf = gpd.read_file(sample_polygons)
    with rasterio.open(sample_raster) as img:
        window = images.patch_window(gdf.geometry.iloc[0], img, patch_size=10)
        intersecting = images.shrub_labels_in_window(gdf.geometry, window, img)
        arr = images.label_patch_with_window(intersecting, window, img)
        assert isinstance(arr, np.ndarray)
        assert arr.shape == (10, 10)
        assert np.any(arr == 255)


def test_background_label():
    """Test background_label returns a zero array of the correct size and type."""
    arr = images.background_label(size=32)
    assert isinstance(arr, np.ndarray)
    assert arr.shape == (32, 32)
    assert np.all(arr == 0)
    assert arr.dtype == np.uint8


def test_background_samples(sample_polygons, sample_raster):
    """Test background_samples returns a list of windows with expected properties."""
    gdf = gpd.read_file(sample_polygons)
    with rasterio.open(sample_raster) as img:
        negatives = images.background_samples(img, gdf, window_size=8)
        assert isinstance(negatives, list)
        assert all(isinstance(w, rasterio.windows.Window) for w in negatives)
        # Each window should be the correct size
        for w in negatives:
            assert w.width == 8
            assert w.height == 8
