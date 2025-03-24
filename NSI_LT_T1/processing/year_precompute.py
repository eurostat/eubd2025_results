# precompute.py
import geopandas as gpd
import pandas as pd
import numpy as np
import xarray as xr
from shapely.geometry import Point, Polygon

# 1. Read the shapefile and filter to your country of interest (using EPSG:4326)
nuts = gpd.read_file("NUTS_RG_01M_2021_3035.shp.zip").to_crs(epsg=4326)

# Use your country code, for example, "LT" for Lithuania.
country_code = "PL"
country_gdf = nuts[nuts["CNTR_CODE"] == country_code]
# Combine all geometries into a single polygon
country_polygon = country_gdf.unary_union

# 2. Load the NetCDF file containing temperature data
ds = xr.open_dataset("avg_temp_pl_2023_2024.nc")

# Print dataset keys (for debugging purposes)
print("Dataset details:")
print(ds)
print("\nData variables:")
print(list(ds.data_vars))
print("\nCoordinates:")
print(list(ds.coords))

# 3. Convert the dataset to a DataFrame and rename columns
df_temp = ds.to_dataframe().reset_index()
print("\nDataFrame columns:")
print(df_temp.columns)

df_temp.rename(
    columns={
        "t": "time",        # rename time coordinate from 't' to 'time'
        "x": "longitude",   # rename x to longitude
        "y": "latitude",    # rename y to latitude
        "LST": "value"      # rename LST to value
    },
    inplace=True
)

# Convert 'time' to datetime (if not already) and extract year and month
df_temp["time"] = pd.to_datetime(df_temp["time"])
df_temp["year"] = df_temp["time"].dt.year
df_temp["month"] = df_temp["time"].dt.month

# Convert coordinates and temperature values to float and adjust units (Kelvin -> Celsius)
df_temp["longitude"] = df_temp["longitude"].astype(float)
df_temp["latitude"]  = df_temp["latitude"].astype(float)
df_temp["value"]     = df_temp["value"].astype(float) - 273.15

# 4. Create a GeoDataFrame of temperature points
gdf_points = gpd.GeoDataFrame(
    df_temp,
    geometry=[Point(lon, lat) for lon, lat in zip(df_temp["longitude"], df_temp["latitude"])],
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
            (x,               y),
            (x+cell_size_deg, y),
            (x+cell_size_deg, y+cell_size_deg),
            (x,               y+cell_size_deg)
        ])
        grid_polygons.append(poly)

grid = gpd.GeoDataFrame(geometry=grid_polygons, crs="EPSG:4326")
grid.reset_index(inplace=True)
grid.rename(columns={"index": "grid_id"}, inplace=True)

# Clip grid cells to the country boundary
grid = gpd.clip(grid, country_polygon)

# 6. For each unique period (year and month), perform spatial join and aggregate the temperature values
for (year, month), group in gdf_points_filtered.groupby(["year", "month"]):
    # Spatial join: assign each point to a grid cell
    joined = gpd.sjoin(group, grid, how="left", predicate="within")
    # Aggregate by grid cell (computing the mean temperature)
    aggregated = joined.groupby("grid_id")["value"].mean()
    
    # Map the aggregated temperature back to the grid
    grid_period = grid.copy()
    grid_period["mean_val"] = grid_period["grid_id"].map(aggregated)
    
    # Save the aggregated grid to a GeoJSON file, including year and month in the filename
    filename = f"grid_aggregated_{country_code}_{year}_{month:02d}.geojson"
    grid_period.to_file(filename, driver="GeoJSON")
    print(f"Saved aggregated grid for {year}-{month:02d} to {filename}.")

print("Precomputation complete.")
