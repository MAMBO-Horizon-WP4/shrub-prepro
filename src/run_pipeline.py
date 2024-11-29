import sys
import os

# Add the parent folder of the scripts directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from src.utils import clip_raster_to_extent, create_binary_raster, process_data
import os

# Paths
input_raster_path = "data/input/rgb_sfm.tif"
input_polygons_path = "data/input/reprojected_yellow_low_shrub.shp"
clipped_raster_path = "data/output/clipped_rgb.tif"
binary_raster_path = "data/output/binary_raster.tif"
mask_output_dir = "data/output/labels"
output_img_dir = "data/output/images"

# Ensure directories exist
os.makedirs(mask_output_dir, exist_ok=True)
os.makedirs(output_img_dir, exist_ok=True)

# Pipeline steps
print("Preparing datasets...")
clip_raster_to_extent(input_raster_path, input_polygons_path, clipped_raster_path)
create_binary_raster(clipped_raster_path, input_polygons_path, binary_raster_path)
process_data(clipped_raster_path, input_polygons_path, output_img_dir, label='rgb')
