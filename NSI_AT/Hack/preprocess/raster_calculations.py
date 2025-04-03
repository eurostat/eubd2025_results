from pathlib import Path
from typing import List

import rasterio as rio
import numpy as np


# def calc_raster_means(band_raster_filepaths: List[Path],
#                       out_name: str,
#                       nuts_id: str,
#                       out_path: Path):
#     
#     """
#     Arguments:
#     ----------
#     band_raster_list: 
#         [2017-01_NDVI_raster, 2018-01_NDVI_raster, ..., 2023-01_NDVI_raster]
#     spectral_index_name
#         One of: NDVI, LWC, EVI, Temp, LCI
#     spectral_index_name
#         INDEX_MONTH, e.g. NDVI_06
#     nuts_id
#         Either AT123 or ITF63
#     """
# 
#     band_raster_list = []
#     for band_raster_filepath in band_raster_filepaths:
#         band_raster_list.append(
#             rio.open(band_raster_filepath))
#     
#     init_raster = band_raster_list[0]
#     init_profile = init_raster.profile.copy()
# 
#     arrays = []
#     for band_raster in band_raster_list:
#         arrays.append(band_raster.read(1))
# 
#     mean_array = np.mean(arrays)
# 
#     out_name = f'TS_mean_{out_name}_{nuts_id}.tif'
#     out_filepath = out_path.joinpath(out_name)
# 
#     with rio.open(out_filepath, 'w', **init_profile) as out:
#         out.write(mean_array)


def calc_baseline_means(out_path: str,
                        input_filepaths: List[Path],
                        nuts_id: str,
                        indices: List[str] = ['LWC', 'NDVI', 'EVI', 'LCI'],
                        n_years: int = 8):
    
    """
    Input filenames should follow the format: 
    INDEX_NUTSCODE_YEAR_MONTH_DESCRIPTION.tif 
    where month is a two-digit string.
    """
    
    for index in indices:

        fps_year_sorted = sorted(input_filepaths)
        fps_month_sorted = np.array(sorted(
            fps_year_sorted, key=lambda x: str(x).split('_')[2]))
        fps_reshaped = fps_month_sorted.reshape(
            int(len(fps_month_sorted)/n_years), n_years)

        for arr_filepaths in fps_reshaped:

            month = arr_filepaths[0].stem.split('_')[-2]
            out_name = f'{index}_{nuts_id}_{month}_baseline.tif'

            arrays = []
            for arr_filepath in arr_filepaths:

                r = rio.open(arr_filepath)
                profile = r.profile.copy()
                arrays.append(r.read(1))

            height = profile['height']
            width = profile['width']

            mean_array = np.nanmean(np.dstack(arrays), axis=2)
            mean_array_reshaped = mean_array.reshape(1, height, width)

            out_filepath = Path(out_path.joinpath(out_name))
            with rio.open(out_filepath, 'w', **profile) as out:
                out.write(mean_array_reshaped)


def calculate_deltas(baseline_path: str,
                     current_year_str: str,
                     current_year_path: str,
                     out_path: Path,
                     nuts_id: str,
                     indices: List[str] = ['NDVI', 'EVI', 'LCI', 'LWC'],
                     months: List[str] = ['04', '05', '06', '07', '08', '09']):

    for index in indices:

        for month in months:

            out_filepath = out_path.joinpath(
                f'{index}_{nuts_id}_{month}_baseline.tif')
            baseline_filepath = baseline_path.joinpath(
                f'{index}_{nuts_id}_{month}_baseline.tif')
            current_year_filepath = current_year_path.joinpath(
                f'{index}_{nuts_id}_{current_year_str}_{month}_normalized.tif')
            
            base_r = rio.open(baseline_filepath)
            base_profile = base_r.profile.copy()
            baseline_array = base_r.read(1)

            current_r = rio.open(current_year_filepath)
            current_profile = current_r.profile.copy()
            current_array = current_r.read(1)

            delta = current_array - baseline_array
            delta_reshaped = delta.reshape(1, 
                                           base_profile['height'], 
                                           base_profile['weight'])

            with rio.open(out_filepath, 'w', **base_profile) as out:
                out.write(delta_reshaped)
            


def calc_raster_deltas(raster_ts_array: np.array,
                       raster_t0_filepath: str,
                       out_path: Path):
    
    r_t0 = rio.open(raster_t0_filepath)
    profile = r_t0.profile.copy()
    arr_t0 = r_t0.read(1)

    delta = np.subtract(arr_t0, raster_ts_array)

    out_name = f'delta_{Path(raster_t0_filepath).stem}.tif'
    out_filepath = out_path.joinpath(out_name)

    with rio.open(out_filepath, 'w', **profile) as out:
        out.write(delta)