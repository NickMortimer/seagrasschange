import rasterio
from rasterio.features import shapes
import geopandas as gpd
from shapely.geometry import shape

# Step 1: Open GeoTIFF file and read its metadata
with rasterio.open('/media/mor582/Seagate/thailand_2023_11/data_processed/20231122_AN05/DJIP4RTK/AN05-orthophoto.tif') as src:
    # Step 2: Extract the outline (polygon) from the raster
    outline_geom = [shape(geom) for geom, val in shapes(src.read(1), transform=src.transform)]

# Step 3: Convert the outline to a GeoDataFrame
outline_gdf = gpd.GeoDataFrame(geometry=outline_geom)

# Step 4: Save the GeoDataFrame to a shapefile
outline_gdf.to_file('outline.shp')