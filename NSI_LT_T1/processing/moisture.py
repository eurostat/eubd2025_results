# precompute_soil_moisture.py
import geopandas as gpd
import pandas as pd
import numpy as np
import xarray as xr
from shapely.geometry import Point, Polygon
import scipy.spatial  # for nearest-neighbor interpolation

# 1. Read the shapefile and filter to your country of interest (using EPSG:4326)
nuts = gpd.read_file("../nuts/NUTS_RG_01M_2021_3035.shp.zip").to_crs(epsg=4326)

# Use your country code, e.g., "LT" for Lithuania
country_code = "PL"
country_gdf = nuts[nuts["CNTR_CODE"] == country_code]

# Use union_all() if available, else fallback to unary_union.
try:
    country_polygon = country_gdf.geometry.union_all()
except AttributeError:
    country_polygon = country_gdf.unary_union

# 2. Load the NetCDF file containing soil moisture data
#    (Adjust the file path as needed)
ds = xr.open_dataset("../raw/Poland_SoilMoisture_2023_2024.nc")

print("Dataset details:")
print(ds)
print("\nData variables:")
print(list(ds.data_vars))
print("\nCoordinates:")
print(list(ds.coords))

# 3. Convert the dataset to a DataFrame and rename columns as needed
df_sm = ds.to_dataframe().reset_index()
print("\nDataFrame columns:")
print(df_sm.columns)

# Multiply SM by 100 to convert from fraction to percentage
df_sm["value"] = df_sm["sm"].astype(float) * 100.0

# Create 'year' and 'month' columns from the 'time' coordinate
df_sm["year"] = pd.to_datetime(df_sm["time"]).dt.year
df_sm["month"] = pd.to_datetime(df_sm["time"]).dt.month

# Rename lat/lon to latitude/longitude for consistency
df_sm.rename(columns={"lat": "latitude", "lon": "longitude"}, inplace=True)

# 4. Create a GeoDataFrame of SM points
gdf_points = gpd.GeoDataFrame(
    df_sm,
    geometry=[Point(lon, lat) for lon, lat in zip(df_sm["longitude"], df_sm["latitude"])],
    crs="EPSG:4326"
)

# Filter points to only those within the country boundary
gdf_points_filtered = gdf_points[gdf_points.within(country_polygon)]

# 5. Build a grid over the entire country extent
minx, miny, maxx, maxy = country_polygon.bounds  # full extent of the country
# minx, miny, maxx, maxy = gdf_points_filtered.total_bounds
cell_size_deg = 0.1  # Adjust grid cell size as needed
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

# Clip grid cells to the country boundary
grid = gpd.clip(grid, country_polygon)

# 6. For each unique (year, month), perform a spatial join, aggregate SM% values, and fill nulls
for (year, month), group in gdf_points_filtered.groupby(["year", "month"]):
    # Spatial join: assign each point to a grid cell
    joined = gpd.sjoin(group, grid, how="left", predicate="within")
    
    # Aggregate by grid cell (computing the mean SM% value)
    aggregated = joined.groupby("grid_id")["value"].mean()
    
    # Map the aggregated SM% back to the grid
    grid_period = grid.copy()
    grid_period["mean_val"] = grid_period["grid_id"].map(aggregated)
    
    # --- Handle null values via nearest-neighbor interpolation ---
    # Compute centroids for each grid cell
    grid_period["centroid"] = grid_period.geometry.centroid
    grid_period["centroid_x"] = grid_period.centroid.x
    grid_period["centroid_y"] = grid_period.centroid.y
    
    # Identify cells with missing values
    missing = grid_period["mean_val"].isnull()
    if missing.any():
        # Coordinates of cells with known values
        known_points = grid_period.loc[~missing, ["centroid_x", "centroid_y"]].values
        known_values = grid_period.loc[~missing, "mean_val"].values
        
        # Coordinates of cells with missing values
        unknown_points = grid_period.loc[missing, ["centroid_x", "centroid_y"]].values
        
        # Build a KDTree from known points and query for the nearest neighbor of each unknown cell
        tree = scipy.spatial.cKDTree(known_points)
        distances, indices = tree.query(unknown_points, k=1)
        
        # Fill missing values with the nearest known value
        grid_period.loc[missing, "mean_val"] = known_values[indices]
    
    # Final pass: if any cells are still null, fill with overall mean of the region
    if grid_period["mean_val"].isnull().any():
        overall_mean = grid_period["mean_val"].mean()
        grid_period["mean_val"] = grid_period["mean_val"].fillna(overall_mean)
    
    # Remove temporary centroid columns
    grid_period = grid_period.drop(columns=["centroid", "centroid_x", "centroid_y"])
    
    # Save the aggregated grid to a GeoJSON file, including year and month in the filename
    filename = f"grid_soil_moisture_{country_code}_{year}_{month:02d}.geojson"
    grid_period.to_file(filename, driver="GeoJSON")
    print(f"Saved aggregated soil moisture grid for {year}-{month:02d} to {filename}.")

print("Precomputation complete.")
