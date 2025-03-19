import pandas as pd
import os
import zipfile

import geopandas as gpd
import cdsapi
import xarray as xr
import shapefile


def filter_nuts_3(years):
    nuts_2013 = "NUTS_RG_01M_2013_4326"
    nuts_2016 = "NUTS_RG_01M_2016_4326"
    nuts_2021 = "NUTS_RG_01M_2021_4326"
    nuts_names = {
        "2013": nuts_2013,
        "2014": nuts_2013,
        "2015": nuts_2013,
        "2016": nuts_2016,
        "2017": nuts_2016,
        "2018": nuts_2016,
        "2019": nuts_2016,
        "2020": nuts_2016,
        "2021": nuts_2021,
        "2022": nuts_2021,
        "2023": nuts_2021,
        "2024": nuts_2021,
        "2025": nuts_2021
    }

    nuts = {}
    for year in years:
        nuts_name = nuts_names[str(year)]
        nuts_path = f"{nuts_name}.shp"
        nuts_filtered = f"{nuts_name}_filtered.shp"

        filter_shapefile_by_field(nuts_path, nuts_filtered, "LEVL_CODE", 3)

        nuts[str(year)] = nuts_filtered

    return nuts


def perform_spatial_analysis(years, months, nuts):
    for year in years:
        for month in months:
            shapefile_name = get_shapefile_name(year, month)
            shapefile_path = f"{shapefile_name}.shp"
            shapefile_projected = f"{shapefile_name}/{shapefile_name}_projected.shp"

            spj_name = f"{shapefile_name}_spj_nuts3"
            spj_path = f"{spj_name}/{spj_name}.shp"

            output_csv_path = f"summary_stats/summary_stats_{year}_{month}.csv"

            os.makedirs(shapefile_name, exist_ok=True)
            os.makedirs(spj_name, exist_ok=True)
            os.makedirs("summary_stats", exist_ok=True)

            project_to_epsg(shapefile_path, shapefile_projected)

            left_gdf = gpd.read_file(shapefile_projected)
            right_gdf = gpd.read_file(nuts[str(year)])

            joined_result = spatial_join_geopandas(left_gdf, right_gdf, how='inner', predicate='intersects')
            joined_result.to_file(spj_path)

            summarize_shapefile(spj_path, output_csv_path, 'NUTS_ID', ["EXCEED"], ['mean'])


def get_shapefile_name(year, month):
    return f'cams_exceedance_{year}_{month}'


def project_to_epsg(shapefile_path, shapefile_projected):
    gdf = gpd.read_file(shapefile_path)

    if gdf.crs is None:
        gdf.crs = "EPSG:4326"
        print("CRS assigned: EPSG:4326")
        gdf.to_file(shapefile_projected)
    else:
        print("Shapefile already has a CRS:", gdf.crs)


def calculate_exceedance_days_xr(xr_data, pm2p5_threshold, time_dim='time'):
    """
    Calculates the number of days in the xarray dataset where the *daily maximum* PM2.5
    exceeds the given threshold for each grid point, using xarray's temporal aggregation.

    Args:
        xr_data (xr.DataArray or xr.Dataset): The xarray DataArray or Dataset containing PM2.5 data.
        pm2p5_threshold (float): The PM2.5 threshold value (default: 25).
        time_dim (str): Name of the time dimension (default: 'time').

    Returns:
        An xarray DataArray with the number of exceedance days for each grid point
        or None if an error occurs.
    """
    try:
        if isinstance(xr_data, xr.Dataset):
            pm2p5 = xr_data["pm2p5"] if "pm2p5" in xr_data else xr_data["pm2p5_conc"]
        else:
            pm2p5 = xr_data  # Assume it's a DataArray

        # Calculate daily maximum PM2.5 using xarray's resample
        daily_max = pm2p5.resample({time_dim: 'D'}).max()

        # Count the number of days exceeding the threshold
        exceedance_days = (daily_max > pm2p5_threshold).sum(dim=time_dim)

        return exceedance_days

    except Exception as e:
        print(f"Error calculating exceedance days: {e}")
        return None


def create_exceedance_shapefile(exceedance_data, lat, lon, shp_file):
    """Creates a shapefile from the exceedance data."""
    try:
        w = shapefile.Writer(shp_file, shapeType=shapefile.POINT)
        w.field("EXCEED", "N", decimal=0)  # Number of exceedance days (integer)
        w.field("LAT", "F", decimal=10)
        w.field("LON", "F", decimal=10)

        for i in range(len(lat)):
            for j in range(len(lon)):
                value = exceedance_data[i, j].item()
                w.point(lon[j], lat[i])
                w.record(int(value), lat[i], lon[j])  # Convert to integer

        w.close()
        print(f"Successfully created shapefile: {shp_file}")
        return True

    except Exception as e:
        print(f"Error creating shapefile: {e}")
        return False


def summarize_shapefile(input_shapefile, output_csv, group_field, statistics_fields, statistics_types):
    """
    Calculates summary statistics for a shapefile, grouped by a specified field,
    and saves the results to a CSV file.

    Args:
        input_shapefile (str): Path to the input shapefile.
        output_csv (str): Path to the output CSV file.
        group_field (str): Name of the field to group by.
        statistics_fields (list): List of field names to calculate statistics for.
        statistics_types (list): List of statistic types to calculate (e.g., 'mean', 'sum', 'min', 'max', 'std', 'count').
                                  Must correspond to the order of statistics_fields.
    """

    try:
        gdf = gpd.read_file(input_shapefile)
    except Exception as e:
        print(f"Error reading shapefile: {e}")
        return

    if group_field not in gdf.columns:
        print(f"Error: Group field '{group_field}' not found in shapefile.")
        return

    if not all(field in gdf.columns for field in statistics_fields):
        missing_fields = [field for field in statistics_fields if field not in gdf.columns]
        print(f"Error: Statistics fields {missing_fields} not found in shapefile.")
        return

    if len(statistics_fields) != len(statistics_types):
        print("Error: The number of statistics fields and statistics types must match.")
        return

    grouped = gdf.groupby(group_field)
    results = {}

    for i, field in enumerate(statistics_fields):
        stat_type = statistics_types[i]
        try:

            if stat_type == 'count':
                results[f'{field}_count'] = grouped[field].count()
            elif stat_type == 'mean':
                results[f'{field}_mean'] = grouped[field].mean()
            elif stat_type == 'sum':
                results[f'{field}_sum'] = grouped[field].sum()
            elif stat_type == 'min':
                results[f'{field}_min'] = grouped[field].min()
            elif stat_type == 'max':
                results[f'{field}_max'] = grouped[field].max()
            elif stat_type == 'std':
                results[f'{field}_std'] = grouped[field].std()
            elif stat_type == 'median':
                results[f'{field}_median'] = grouped[field].median()
            elif stat_type == 'var':
                results[f'{field}_var'] = grouped[field].var()
            else:
                print(f"Warning: Statistic type '{stat_type}' not supported. Skipping field '{field}'.")
                continue
        except Exception as e:
            print(f"Error calculating {stat_type} for field {field}: {e}")
            continue

    result_df = pd.DataFrame(results)
    result_df.to_csv(output_csv)
    print(f"Summary statistics saved to {output_csv}")


def spatial_join_geopandas(left_gdf, right_gdf, how='inner', predicate='intersects'):
    """
    Performs a spatial join using geopandas.

    Args:
        left_gdf (geopandas.GeoDataFrame): Left GeoDataFrame.
        right_gdf (geopandas.GeoDataFrame): Right GeoDataFrame.
        how (str, optional): Type of join ('left', 'right', 'inner'). Defaults to 'inner'.
        predicate (str, optional): Spatial predicate ('intersects', 'contains', 'within', etc.). Defaults to 'intersects'.

    Returns:
        geopandas.GeoDataFrame: Joined GeoDataFrame.
    """
    try:
        joined_gdf = gpd.sjoin(left_gdf, right_gdf, how=how, predicate=predicate)
        return joined_gdf
    except Exception as e:
        print(f"Error during spatial join: {e}")
        return None


def filter_shapefile_by_field(input_shapefile, output_shapefile, field_name, field_value):
    """
    Filters a shapefile based on a specific field value and exports it as a new shapefile.

    Args:
        input_shapefile (str): Path to the input shapefile.
        output_shapefile (str): Path to save the filtered shapefile.
        field_name (str): Name of the field to filter by.
        field_value (any): Value to filter the field by.
    """
    try:
        gdf = gpd.read_file(input_shapefile)

        filtered_gdf = gdf[gdf[field_name] == field_value]

        filtered_gdf.to_file(output_shapefile)

        print(f"Filtered shapefile saved to: {output_shapefile}")
        print(f"Number of filtered records: {len(filtered_gdf)}")

    except FileNotFoundError:
        print(f"Error: Input shapefile not found at {input_shapefile}")
    except KeyError:
        print(f"Error: Field '{field_name}' not found in the shapefile.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


def extract_zip(zip_file_path, extract_to_path=None):
    """Extracts a zip archive safely."""
    try:
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            if extract_to_path is None:
                base_name = os.path.basename(zip_file_path)
                extract_to_path = os.path.splitext(base_name)[0]
                extract_to_path = os.path.join(os.path.dirname(zip_file_path), extract_to_path)
            os.makedirs(extract_to_path, exist_ok=True)
            zip_ref.extractall(extract_to_path)
        return extract_to_path  # Return the extraction path for later use

    except (FileNotFoundError, zipfile.BadZipFile, Exception) as e:
        print(f"Error extracting {zip_file_path}: {e}")
        return None


def get_cams_data(years, months, dataset, pm2p5_threshold=25):
    if 'forecasts' in dataset:
        forecasts = True
    elif 'reanalyses' in dataset:
        forecasts = False
    else:
        raise ValueError("Invalid dataset type. Must be either 'forecasts' or 'reanalyses'.")

    client = cdsapi.Client()

    for year in years:

        for month in months:
            request = {
                "variable": ["particulate_matter_2.5um"],
                "model": ["ensemble"],
                "level": ["0"]
            }

            if forecasts:
                start_date = f"{year}-{month:02}-01"
                end_year = int(year) + 1 if month == 12 else year
                end_month = 1 if month == 12 else int(month) + 1
                end_date = f"{end_year}-{end_month:02}-01"

                request.update({
                    "date": [f"{start_date}/{end_date}"],
                    "type": ["analysis"],
                    "time": [f"{hour:02}:00" for hour in range(24)],
                    "leadtime_hour": ["0"],
                    "data_format": "netcdf_zip"
                })

            else:
                request.update({
                    "year": year,
                    "month": month,
                    "type": ["validated_reanalysis"]
                })

            try:
                result = client.retrieve(dataset, request)
                zip_file = f"cams_data_{year}_{month}.zip"
                result.download(zip_file)

                extraction_path = extract_zip(zip_file)
                if extraction_path:
                    netcdf_file = None
                    for filename in os.listdir(extraction_path):
                        if filename.endswith(".nc"):
                            netcdf_file = os.path.join(extraction_path, filename)
                            break

                    if netcdf_file:
                        try:
                            xr_dataset = xr.open_dataset(netcdf_file)

                            monthly_exceedance = calculate_exceedance_days_xr(xr_dataset, pm2p5_threshold)

                            if monthly_exceedance is not None:
                                shp_file = f"{get_shapefile_name(year, month)}.shp"
                                try:
                                    lat = xr_dataset['lat'].values if 'lat' in xr_dataset else xr_dataset[
                                        'latitude'].values
                                    lon = xr_dataset['lon'].values if 'lon' in xr_dataset else xr_dataset[
                                        'longitude'].values
                                    if create_exceedance_shapefile(monthly_exceedance, lat, lon, shp_file):
                                        print(f"Monthly exceedance shapefile successfully created at {shp_file}")
                                    else:
                                        print("Failed to create monthly exceedance shapefile.")
                                except Exception as e:
                                    print(f"Error creating monthly exceedance shapefile: {e}")

                        except Exception as e:
                            print(f"Error processing NetCDF file for {year}-{month} with xarray: {e}")
                        finally:
                            if 'xr_dataset' in locals():
                                xr_dataset.close()
                                del xr_dataset  # Explicitly delete

                    else:
                        print(f"No NetCDF file found in the extracted zip archive for {year}-{month}.")

                # Cleanup extracted files and zip archive
                if extraction_path and os.path.exists(extraction_path):
                    import shutil
                    shutil.rmtree(extraction_path)
                if os.path.exists(zip_file):
                    os.remove(zip_file)
            except Exception as e:
                print(f"Error retrieving data for {year}-{month}: {e}")


def main():
    pm2p5_threshold = 5
    years = ["2013", "2014", "2015", "2016", "2017", "2018", "2019", "2020", "2021", "2022"]
    months = ["01", "02", "03", "04", "05", "06", "07", "08", "09", "10", "11", "12"]
    dataset = "cams-europe-air-quality-reanalyses"
    # dataset = "cams-europe-air-quality-forecasts"

    get_cams_data(years, months, dataset, pm2p5_threshold)

    nuts = filter_nuts_3(years)

    perform_spatial_analysis(years, months, nuts)


if __name__ == "__main__":
    main()
