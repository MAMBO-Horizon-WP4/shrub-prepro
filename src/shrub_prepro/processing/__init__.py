"""Shrub preprocessing package for handling remote sensing data."""

from shrub_prepro.processing.raster import clip_raster_to_extent, create_binary_raster
from shrub_prepro.processing.transform import process_data

__version__ = "0.1.0"

__all__ = ["clip_raster_to_extent", "create_binary_raster", "process_data"]
