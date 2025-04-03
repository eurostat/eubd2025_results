import os
import geopandas as gpd
import pandas as pd

# Define crop conditions with extended planting months and temperature ranges
crop_conditions = {
    "Winter Wheat": {"planting_month": "09-11", "temp_range": (5, 10)},
    "Spring Wheat": {"planting_month": "03-05", "temp_range": (7, 12)},
    "Winter Barley": {"planting_month": "09-11", "temp_range": (5, 10)},
    "Spring Barley": {"planting_month": "03-04", "temp_range": (7, 12)},
    "Maize": {"planting_month": "05-06", "temp_range": (13, 18)},
    "Sunflower": {"planting_month": "05-06", "temp_range": (15, 20)},
    "Potato": {"planting_month": "03-05", "temp_range": (7, 12)},
    "Rapeseed": {"planting_month": "08-09", "temp_range": (5, 10)},
    "Sugar Beet": {"planting_month": "03-05", "temp_range": (7, 12)},
    "Peas": {"planting_month": "03-05", "temp_range": (5, 10)}
}

# Define ideal soil moisture range for each crop (in % VWC)
ideal_soil_humidity = {
    "Winter Wheat": (20, 25),
    "Spring Wheat": (20, 25),
    "Winter Barley": (20, 25),
    "Spring Barley": (20, 25),
    "Maize": (25, 30),
    "Sunflower": (25, 30),
    "Potato": (25, 30),
    "Rapeseed": (20, 25),
    "Sugar Beet": (20, 25),
    "Peas": (20, 25)
}

country_code = "LT"
years = ["2023", "2024"]

# Define input directories for temperature and moisture files:
temp_dir = "../lts"
moisture_dir = "../moisture_new"

output_dir = "./crop_geojsons"
os.makedirs(output_dir, exist_ok=True)

for crop, conditions in crop_conditions.items():
    planting_value = conditions["planting_month"]
    temp_min, temp_max = conditions["temp_range"]
    moist_min, moist_max = ideal_soil_humidity[crop]
    
    # Determine list of months from planting month value (e.g., "09-11" -> ["09", "10", "11"])
    if "-" in planting_value:
        start, end = planting_value.split("-")
        months = [f"{m:02d}" for m in range(int(start), int(end) + 1)]
    else:
        months = [planting_value]
    
    for year in years:
        for month in months:
            # Build filenames for both temperature and moisture data
            temp_filename = os.path.join(temp_dir, f"grid_aggregated_{country_code}_{year}_{month}.geojson")
            moist_filename = os.path.join(moisture_dir, f"grid_soil_moisture_{country_code}_{year}_{month}.geojson")
            
            if not os.path.exists(temp_filename):
                print(f"Temperature file {temp_filename} not found.")
                continue
            if not os.path.exists(moist_filename):
                print(f"Moisture file {moist_filename} not found.")
                continue
            
            # Read both GeoJSON files
            gdf_temp = gpd.read_file(temp_filename)
            gdf_moist = gpd.read_file(moist_filename)
            
            # Merge on grid_id (assumes both files contain the same grid geometry and "grid_id" field)
            # Here we perform an inner join so that only grid cells present in both files are kept.
            merged = gdf_temp.merge(gdf_moist[["grid_id", "mean_val"]].rename(columns={"mean_val": "mean_moisture"}),
                                     on="grid_id", how="inner")
            # Assume that gdf_temp's "mean_val" holds the temperature (°C)
            merged.rename(columns={"mean_val": "mean_temp"}, inplace=True)
            
            # Filter based on temperature and moisture criteria
            filtered = merged[
                (merged["mean_temp"] >= temp_min) & (merged["mean_temp"] <= temp_max) &
                (merged["mean_moisture"] >= moist_min) & (merged["mean_moisture"] <= moist_max)
            ]
            
            if not filtered.empty:
                output_filename = os.path.join(
                    output_dir,
                    f"grid_{crop.replace(' ', '_')}_{country_code}_{year}_{month}.geojson"
                )
                filtered.to_file(output_filename, driver="GeoJSON")
                print(f"Created file {output_filename}")
            else:
                print(f"No grid cells in {temp_filename} & {moisture_dir} for {crop} meeting criteria: "
                      f"Temp ({temp_min}–{temp_max} °C) and Moisture ({moist_min}–{moist_max} %).")
                
print("Crop condition processing complete.")
