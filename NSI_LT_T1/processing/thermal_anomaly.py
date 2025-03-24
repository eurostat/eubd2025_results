import geopandas as gpd
import pandas as pd
import numpy as np
import xarray as xr
from shapely.geometry import Point, Polygon
import scipy.spatial  # for nearest-neighbor interpolation

# 1. Read the shapefile and reproject to EPSG:4326 (if needed)
nuts = gpd.read_file("../nuts/NUTS_RG_01M_2021_3035.shp.zip").to_crs(epsg=4326)

country_code = "LT"
country_gdf = nuts[nuts["CNTR_CODE"] == country_code]
# Use union_all() to combine all geometries into a single polygon
country_polygon = country_gdf.union_all()

# 2. Load the NetCDF file containing drought stress index data
ds = xr.open_dataset("../raw/Thermal-Anomaly Soil Moisture Index (TASMI)_LT.nc")
df_temp = ds.to_dataframe().reset_index()

# 3. Rename columns to more descriptive names and convert data types
df_temp.rename(
    columns={"x": "longitude", "y": "latitude", "__xarray_dataarray_variable__": "value"},
    inplace=True
)
df_temp["longitude"] = df_temp["longitude"].astype(float)
df_temp["latitude"]  = df_temp["latitude"].astype(float)
df_temp["value"]     = df_temp["value"].astype(float)

# 4. Create a GeoDataFrame with drought stress points
gdf_points = gpd.GeoDataFrame(
    df_temp,
    geometry=[Point(lon, lat) for lon, lat in zip(df_temp["longitude"], df_temp["latitude"])],
    crs="EPSG:4326"
)

# Filter points to only those within the country boundary
gdf_points_filtered = gdf_points[gdf_points.within(country_polygon)]

# 5. Build the grid over the country extent (using country polygon bounds)
# minx, miny, maxx, maxy = country_polygon.bounds
minx, miny, maxx, maxy = country_polygon.bounds  # <-- Use country polygon bounds

cell_size_deg = 0.05  # each grid cell is 0.1° x 0.1°
xs = np.arange(minx, maxx, cell_size_deg)
ys = np.arange(miny, maxy, cell_size_deg)

grid_polygons = []
for x in xs:
    for y in ys:
        poly = Polygon([
            (x,               y),
            (x + cell_size_deg, y),
            (x + cell_size_deg, y + cell_size_deg),
            (x,               y + cell_size_deg)
        ])
        grid_polygons.append(poly)

grid = gpd.GeoDataFrame(geometry=grid_polygons, crs="EPSG:4326")
grid.reset_index(inplace=True)
grid.rename(columns={"index": "grid_id"}, inplace=True)

# Clip the grid cells so they only cover the area within the country
grid = gpd.clip(grid, country_polygon)

# 6. Spatial join between the points and the grid; then aggregate (mean) values per grid cell
joined = gpd.sjoin(gdf_points_filtered, grid, how="left", predicate="within")
aggregated = joined.groupby("grid_id")["value"].mean()
grid["mean_val"] = grid["grid_id"].map(aggregated)

# --- Handle null values via nearest-neighbor interpolation ---
# Compute centroids for each grid cell.
grid["centroid"] = grid.geometry.centroid
grid["centroid_x"] = grid.centroid.x
grid["centroid_y"] = grid.centroid.y

# Identify cells with missing values.
missing = grid["mean_val"].isnull()
if missing.any():
    # Coordinates of cells with known values
    known_points = grid.loc[~missing, ["centroid_x", "centroid_y"]].values
    known_values = grid.loc[~missing, "mean_val"].values
    # Coordinates of cells with missing values
    unknown_points = grid.loc[missing, ["centroid_x", "centroid_y"]].values

    # Build a KDTree from the known points and query for the nearest neighbor of each unknown cell.
    tree = scipy.spatial.cKDTree(known_points)
    distances, indices = tree.query(unknown_points, k=1)

    # Fill missing values with the nearest known value.
    grid.loc[missing, "mean_val"] = known_values[indices]

# Final pass: if any cells are still null, fill with the overall mean of the region
if grid["mean_val"].isnull().any():
    overall_mean = grid["mean_val"].mean()
    grid["mean_val"] = grid["mean_val"].fillna(overall_mean)

# Optionally, remove temporary centroid columns
grid = grid.drop(columns=["centroid", "centroid_x", "centroid_y"])

# Save the final aggregated grid to a GeoJSON file
grid.to_file("grid_aggregated_LT.geojson", driver="GeoJSON")
print("Saved aggregated grid to grid_aggregated_PL.geojson.")
