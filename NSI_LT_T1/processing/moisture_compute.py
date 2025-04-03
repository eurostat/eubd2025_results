# precompute_moisture.py
import geopandas as gpd
import pandas as pd
import numpy as np
import xarray as xr
from shapely.geometry import Point, Polygon

# 1. Read the shapefile and filter to your country of interest (using EPSG:4326)
nuts = gpd.read_file("../NUTS_RG_01M_2021_3035.shp.zip").to_crs(epsg=4326)

country_code = "LT"
country_gdf = nuts[nuts["CNTR_CODE"] == country_code]
# Combine all geometries into a single polygon
country_polygon = country_gdf.unary_union

# 2. Load the NetCDF file containing soil moisture data
ds = xr.open_dataset("soil_moisture_vwc_lithuania_time_series_2023_2024_s2_adjusted.nc")

print("Dataset details:")
print(ds)
print("\nData variables:")
print(list(ds.data_vars))
print("\nCoordinates:")
print(list(ds.coords))

# 3. Convert the dataset to a DataFrame and rename columns
# (Assuming the dataset contains coordinates 't', 'x', 'y' and the moisture variable 'VWC_percent')
df_moisture = ds.to_dataframe().reset_index()
print("\nDataFrame columns:")
print(df_moisture.columns)

df_moisture.rename(
    columns={
        "t": "time",          # rename time coordinate from 't' to 'time'
        "x": "longitude",     # rename x to longitude
        "y": "latitude",      # rename y to latitude
        "VWC_percent": "value"  # rename VWC_percent to value
    },
    inplace=True
)

# Convert 'time' to datetime and extract year and month
df_moisture["time"] = pd.to_datetime(df_moisture["time"])
df_moisture["year"] = df_moisture["time"].dt.year
df_moisture["month"] = df_moisture["time"].dt.month

# Convert coordinates and moisture values to float (if not already)
df_moisture["longitude"] = df_moisture["longitude"].astype(float)
df_moisture["latitude"]  = df_moisture["latitude"].astype(float)
df_moisture["value"]     = df_moisture["value"].astype(float)

# 4. Create a GeoDataFrame of soil moisture points
gdf_points = gpd.GeoDataFrame(
    df_moisture,
    geometry=[Point(lon, lat) for lon, lat in zip(df_moisture["longitude"], df_moisture["latitude"])],
    crs="EPSG:4326"
)

# Filter points to only those within the country boundary
gdf_points_filtered = gdf_points[gdf_points.within(country_polygon)]

# 5. Build a grid over the country extent
minx, miny, maxx, maxy = gdf_points_filtered.total_bounds
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

# 6. For each unique period (year and month), perform spatial join and aggregate the moisture values
for (year, month), group in gdf_points_filtered.groupby(["year", "month"]):
    # Spatial join: assign each point to a grid cell
    joined = gpd.sjoin(group, grid, how="left", predicate="within")
    # Aggregate by grid cell (computing the mean soil moisture)
    aggregated = joined.groupby("grid_id")["value"].mean()
    
    # Map the aggregated moisture back to the grid
    grid_period = grid.copy()
    grid_period["mean_val"] = grid_period["grid_id"].map(aggregated)
    
    # Save the aggregated grid to a GeoJSON file, including year and month in the filename
    filename = f"grid_aggregated_{country_code}_{year}_{month:02d}.geojson"
    grid_period.to_file(filename, driver="GeoJSON")
    print(f"Saved aggregated grid for {year}-{month:02d} to {filename}.")

print("Precomputation complete.")
