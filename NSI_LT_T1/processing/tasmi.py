import os
import geopandas as gpd
import pandas as pd
import numpy as np
import xarray as xr
from shapely.geometry import Point, Polygon
import scipy.spatial

# --- Step 1: Read the NUTS shapefile and reproject to EPSG:4326 ---
# Adjust the path if needed. This file contains country boundaries.
nuts = gpd.read_file("../nuts/NUTS_RG_01M_2021_3035.shp.zip").to_crs(epsg=4326)

# Set the country code (e.g., "LT" for Lithuania)
country_code = "PL"
country_gdf = nuts[nuts["CNTR_CODE"] == country_code]

# Combine all geometries of the country into a single polygon
country_polygon = country_gdf.unary_union

# --- Step 2: Load the TASMI data from a NetCDF file in the /raw folder ---
# The file is assumed to contain variables that can be converted to a DataFrame.
# Adjust the filename if needed.
ds = xr.open_dataset("../raw/cleaned_TASMI_PL.nc")
df_temp = ds.to_dataframe().reset_index()

# Rename columns: assume that the raw data has 'x' and 'y' coordinates which we rename to "longitude" and "lattitude",
# and the data variable is renamed to "tasmi".
df_temp.rename(
    columns={
        "x": "longitude",
        "y": "latitude",
        "tasmi": "tasmi"
    },
    inplace=True
)

# Convert columns to appropriate types.
df_temp["longitude"] = df_temp["longitude"].astype(float)
df_temp["latitude"]  = df_temp["latitude"].astype(float)
df_temp["tasmi"]      = df_temp["tasmi"].astype(float)

# --- Step 3: Create a GeoDataFrame of TASMI points ---
gdf_points = gpd.GeoDataFrame(
    df_temp,
    geometry=[Point(lon, lat) for lon, lat in zip(df_temp["longitude"], df_temp["latitude"])],
    crs="EPSG:4326"
)

# Filter points to only those within the country boundary
gdf_points_filtered = gdf_points[gdf_points.within(country_polygon)]

# --- Step 4: Build a grid over the country extent ---
minx, miny, maxx, maxy = country_polygon.bounds
cell_size_deg = 0.05  # Define grid cell size (in degrees)
xs = np.arange(minx, maxx, cell_size_deg)
ys = np.arange(miny, maxy, cell_size_deg)

grid_polygons = []
for x in xs:
    for y in ys:
        poly = Polygon([
            (x, y),
            (x + cell_size_deg, y),
            (x + cell_size_deg, y + cell_size_deg),
            (x, y + cell_size_deg)
        ])
        grid_polygons.append(poly)

grid = gpd.GeoDataFrame(geometry=grid_polygons, crs="EPSG:4326")
grid.reset_index(inplace=True)
grid.rename(columns={"index": "grid_id"}, inplace=True)

# Clip the grid cells so they only cover the area within the country
grid = gpd.clip(grid, country_polygon)

# --- Step 5: Spatial join and aggregation ---
# Join the TASMI points with the grid and compute the mean TASMI value per grid cell.
joined = gpd.sjoin(gdf_points_filtered, grid, how="left", predicate="within")
aggregated = joined.groupby("grid_id")["tasmi"].mean()
grid["mean_tasmi"] = grid["grid_id"].map(aggregated)

# --- Step 6: Handle missing values via nearest-neighbor interpolation ---
# Compute centroids for each grid cell.
grid["centroid"] = grid.geometry.centroid
grid["centroid_x"] = grid.centroid.x
grid["centroid_y"] = grid.centroid.y

# Identify grid cells with missing mean_tasmi values.
missing = grid["mean_tasmi"].isnull()
if missing.any():
    # Coordinates of cells with known values.
    known_points = grid.loc[~missing, ["centroid_x", "centroid_y"]].values
    known_values = grid.loc[~missing, "mean_tasmi"].values
    # Coordinates of cells with missing values.
    unknown_points = grid.loc[missing, ["centroid_x", "centroid_y"]].values

    # Build a KDTree from known points and query for the nearest neighbor for each unknown cell.
    tree = scipy.spatial.cKDTree(known_points)
    distances, indices = tree.query(unknown_points, k=1)

    # Fill missing values with the nearest known value.
    grid.loc[missing, "mean_tasmi"] = known_values[indices]

# If any cells are still null, fill with the overall mean.
if grid["mean_tasmi"].isnull().any():
    overall_mean = grid["mean_tasmi"].mean()
    grid["mean_tasmi"] = grid["mean_tasmi"].fillna(overall_mean)

# Optionally remove temporary centroid columns.
grid = grid.drop(columns=["centroid", "centroid_x", "centroid_y"])

# --- Step 7: Save the final aggregated grid to a GeoJSON file ---
output_file = f"grid_aggregated_{country_code}.geojson"
grid.to_file(output_file, driver="GeoJSON")
print(f"Saved aggregated grid to {output_file}.")
