from pathlib import Path
from typing import List

import numpy as np


def create_lol_nuts3_index_filepaths(in_path: Path,
                                     nuts3_id: str,
                                     indices: List[str] = ['NDVI', 'EVI', 'LWC', 'LCI', 'NDMI']):
    
    """Returns a list of list, each containing the sorted filepaths of a certain 
    index, e.g.  
    [
    [Path(/foo/bar/NDVI/NUTS3ID/YEAR/NDVI_NUTS3ID_YEAR_MONTH.tif),
     Path(/foo/bar/NDVI/NUTS3ID/YEAR/NDVI_NUTS3ID_YEAR_MONTH.tif),
     ...],
    [Path(/foo/bar/EVI/NUTS3ID/YEAR/EVI_NUTS3ID_YEAR_MONTH.tif),
     Path(/foo/bar/EVI/NUTS3ID/YEAR/EVI_NUTS3ID_YEAR_MONTH.tif),
     ...]
    ]
    """

    lol_filepaths = []

    for index in indices:

        lol_filepaths.append(in_path.joinpath(f'{index}/{nuts3_id}'))

        index_filepaths = []

        for index_filepath in lol_filepaths:
            index_filepaths.append(sorted([i for i in index_filepath.rglob('*.tif')]))

        return lol_filepaths
    

def create_baseline_filepaths(in_path: Path,
                              n_years: int = 8,
                              indices: List[str] = ['NDVI', 'EVI', 'LWC', 'LCI', 'NDMI']):
    
    for index in indices:

        filepaths = [i for i in in_path.rglob(f'*{index}*.tif')]

        fps_year_sorted = sorted(filepaths)
        fps_month_sorted = np.array(sorted(fps_year_sorted, key=lambda x: str(x).split('_')[-2]))
        fps_reshaped = fps_month_sorted.reshape(int(len(fps_month_sorted)/n_years), n_years)

    return fps_reshaped