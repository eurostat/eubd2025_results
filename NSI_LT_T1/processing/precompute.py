# precompute.py
import geopandas as gpd
import pandas as pd
import numpy as np
import xarray as xr
from shapely.geometry import Point, Polygon

# 1. Read shapefile (EPSG:4326) or reproject as needed
nuts = gpd.read_file("NUTS_RG_01M_2021_3035.shp.zip").to_crs(epsg=4326)

country_code = "PL"
country_gdf = nuts[nuts["CNTR_CODE"] == country_code]
country_polygon = country_gdf.union_all()

# 2. Load NetCDF
ds = xr.open_dataset("avg_temp_pl_jan_feb.nc")  # or "raw_lt_temp.nc"
df_temp = ds.to_dataframe().reset_index()

df_temp.rename(
    columns={"x": "longitude", "y": "latitude", "LST": "value"},
    inplace=True
)
df_temp["longitude"] = df_temp["longitude"].astype(float)
df_temp["latitude"]  = df_temp["latitude"].astype(float)
df_temp["value"]     = df_temp["value"].astype(float)

# Kelvin -> Celsius
df_temp["value"] = df_temp["value"] - 273.15

# Make point GDF
from shapely.geometry import Point
gdf_points = gpd.GeoDataFrame(
    df_temp,
    geometry=[Point(lon, lat) for lon, lat in zip(df_temp["longitude"], df_temp["latitude"])],
    crs="EPSG:4326"
)

# Filter to country boundary
gdf_points_filtered = gdf_points[gdf_points.within(country_polygon)]

# Build the grid
minx, miny, maxx, maxy = gdf_points_filtered.total_bounds
cell_size_deg = 0.1
xs = np.arange(minx, maxx, cell_size_deg)
ys = np.arange(miny, maxy, cell_size_deg)

grid_polygons = []
for x in xs:
    for y in ys:
        poly = Polygon([
            (x,               y),
            (x+cell_size_deg, y),
            (x+cell_size_deg, y+cell_size_deg),
            (x,               y+cell_size_deg)
        ])
        grid_polygons.append(poly)

grid = gpd.GeoDataFrame(geometry=grid_polygons, crs="EPSG:4326")
grid.reset_index(inplace=True)
grid.rename(columns={"index": "grid_id"}, inplace=True)

# Clip squares to country
grid = gpd.clip(grid, country_polygon)

# Spatial join & aggregate
joined = gpd.sjoin(gdf_points_filtered, grid, how="left", predicate="within")
aggregated = joined.groupby("grid_id")["value"].mean()

grid["mean_val"] = grid["grid_id"].map(aggregated)

# Now save the final polygons with a mean_val column
# You can write to GeoJSON, shapefile, or GeoPackage, etc.
grid.to_file("grid_aggregated_PL.geojson", driver="GeoJSON")
print("Saved aggregated grid to grid_aggregated.geojson.")
