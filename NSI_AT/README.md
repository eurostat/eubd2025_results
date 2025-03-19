# Austrian contribution to the EU Big Data Hackathon 2025 in Brussels

# Aim
The aim of this project was to develop a light weight web app for forest stress indicators using S2-data over 2 NUTS3 regions, one in Lower Austria and the other in Calabria.

# Description of processing steps required
## Download Data
|step_n|step_description|information|
|------|----------------|-----------|
|1     |Download        |Sentinel-2 indices|
|2     |Download        |ERA5 temperature data|
|3     |Download        |NUTS3 regions|
|4     |Download        |CLC data|
|5     |Preprocess      |Cut raster to the AOI (NUTS3)|
|6     |Preprocess      |Cut raster to CLC forest mask|
|7     |Preprocess      |Apply threshold (S2 indices) and normalize raster values|

|8     |Preprocess      |Calculate the baseline mean for 2017-2023|
|9     |Preprocess      |Calculate the delta between most-recent year and the baseline|


## 1. Download - Sentinel-2 indices
1. In the repositories `request` folder, run the request_s2.py script providing relevant arguments

* Run the script with all default arguments
```bash
python request_s2_indices.py
```

* Get a description of the available arguments
```bash
python request_s2_indices.py -h
```

* Run the script using specific arguments
```bash
python request_s2_indices.py --max_cc 30 --out_path /home/user/foo/bar --years '2020' '2021' --months '08' '09' --indices 'NDVI'
```
* maximum cloud cover of up to 30%
* different out_path = /home/user/foo/bar
* temporal range:
    * years 2020 and 2021
    * months 08 and 09
* indices: only for NDVI

## 2. Download - ERA5 temperature data
1. In repository, run the jupyter lab: `request/request_era.ipynb`

## 3. Download - NUTS3 regions
1. create an s3 config file in your `/home/user/` directory, called `.s3cfg`, according to the CDSE documentation, the file could contain the following contents:
```bash
[default]
host_base = https://s3.waw3-2.cloudferro.com
host_bucket = https://s3.waw3-2.cloudferro.com
human_readable_sizes = false
secret_key = YOUR_SECRET_KEY
access_key = YOUR_ACCESS_KEY
use_https = true
```

2. Run the script using the following command line invocation
```bash
python request_nuts3_regions.py --s3_config_filepath /home/YOUR_USERNAME/.s3cfg --nuts3_ids 'AT123' 'ITF63' --out_filepath /home/foo/bar
```

## 4. Download - CLC data
Download the CLC data from the Web and clip the geometries to the NUTS3 regions.

## 5. Preprocess - Cut raster to vector AOI

```python
from pathlib import Path
from preprocess.paths import create_lol_nuts3_index_filepaths
from preprocess.clip_raster_to_vector import clip_raster_to_vector

nuts3_id = 'ITF63'
# change paths accordingly
gdf_filepath = Path('/path/to/NUTS3/REGION/FROM/STEP/3/nuts3_regions.gpkg')
raster_out_path = Path(f'/path/to/preprocess/cut_to_nuts/{nuts3_id}')

gdf = gpd.read_file(gdf_filepath)

# create list of lists containing raster filepaths
lol_filepaths = create_lol_nuts3_index_filepaths(
    in_path=Path('/path/to/downloaded/indices/'),
    nuts3_id=nuts3_id)  # repeat for AT123

for indices_path in lol_filepaths:
    for raster_filepath in indices_paths:
        raster_out_filepath = raster_out_path.joinpath(
            f'NUTS_clip_{raster_filepath.stem}.tif'
        )

        clip_raster_to_vector(
            raster_filepath=raster_filepath,
            gdf=gdf,
            nuts_id=nuts3_id,
            out_filepath=out_filepath)
```

## 6. Preprocess - Cut Raster to CLC forest mask

```python
from pathlib import Path
from preprocess.paths import create_lol_nuts3_index_filepaths
from preprocess.clip_raster_to_vector import clip_raster_to_vector

nuts3_id = 'ITF63'
# change paths accordingly
gdf_filepath = Path('/path/to/CLC/forest/mask.gpkg')
raster_in_path = Path(f'/path/to/preprocess/cut_to_nuts/{nuts3_id}')
raster_out_path = Path(f'/path/to/preprocess/cut_to_clc/{nuts3_id}')

cut_to_nuts_filepaths = [i for i in rater_in_path.rglob('*.tif')]

for cut_to_nuts_filepath in cut_to_nuts_filepaths:

    raster_out_filepath = raster_out_path.joinpath(
        f"CLC_clip_{'_'.join(cut_to_nuts_filepath.stem.split('_')[2:])}.tif")
    
    clip_clc_to_raster(
        shapefile_path=gdf_filepath,
        raster_path=cut_to_nuts_filepath,
        out_filepath=raster_out_filepath)
```

## 7. Preprocess - Apply threshold & normalize

```python
from preprocess.clip_raster_to_vector import apply_threshold_and_normalize

# change paths accordingly

in_path = Path(f'/path/to/preprocess/cut_to_clc/{nuts3_id}')
out_path = Path(f'/path/to/preprocess/threshold_and_normalize/{nuts_id}')

clc_filepaths = [i for i in in_path.rglob('*.tif')]

for clc_filepath in clc_filepaths:

    out_filepath = out_path.joinpath(
        f"{'_'.join(clc_filepath.stem.split('_')[2:])}_normalized.tif")

    apply_threshold_and_normalize(raster_filepath=clc_filepath,
                                  out_filepath=out_filepath)
```

## 8. Preprocess - Calculate the baseline mean

```python

from preprocess.paths import create_baseline_filepaths

import numpy as np
import rasterio as rio

# change paths accordingly
in_path = Path(f'/path/to/preprocess/threshold_and_normalize/{nuts_id}')
out_path = Path(f'/path/to/repo/app/static/geodata/raster') # must be a relative path to the repository folder /app/static/geodata/raster

baseline_filepaths = create_baseline_filepaths(
    in_path=in_path)

for arr in baseline_filepaths:

    month = arr[0].stem.split('_')[-2]
        out_name = f'{index}_{nuts_id}_{month}_baseline.tif'

        arrays = []
        for fp in arr[:1]:

            in_name = arr[0].stem
            index_used = in_name.split('_')[0]
            month = arr[0]

            r = rio.open(fp)
            profile = r.profile.copy()
            arrays.append(r.read(1))

        height = profile['height']
        width = profile['width']
        
        mean_array = np.nanmean(np.dstack(arrays), axis=2)
        mean_array_reshaped = mean_array.reshape(1, height, width)

        out_filepath = Path(out_path).joinpath(out_name)
        with rio.open(out_filepath, 'w', **profile) as out:
            out.write(mean_array_reshaped)
```

## 9. Calculate the delta

```python
import numpy as np
import rasterio as rio

nuts3_id = 'ITF63'  # repeat for all other nuts3 regions downloaded in step 3

baseline = Path(f'/path/to/repo/app/static/geodata/raster') # must be a relative path to the repository folder /app/static/geodata/raster
current_year_path = Path(f'/path/to/preprocess/threshold_and_normalize/{nuts_id}')
out_path = Path(f'/path/to/repo/app/static/geodata/raster') # must be a relative path to the repository folder /app/static/geodata/raster

indices = ['NDVI', 'EVI', 'LCI', 'LWC']
months = ['04', '05', '06', '07', '08', '09']

for index in indices:

    for month in months:

        out_filepath = out_path.joinpath(f'{index}_{nuts_id}_{month}_delta.tif')

        baseline_filepath = baseline_path.joinpath(
            f'{index}_{nuts_id}_{month}_baseline.tif')
        current_year_filepath = current_year_path.joinpath(
            f'{index}_{nuts_id}_2024_{month}_normalized.tif')

        base_r = rio.open(baseline_filepath)
        base_profile = base_r.profile.copy()
        baseline_array = base_r.read(1)

        current_r = rio.open(current_year_filepath)
        # print(current_r)
        current_prof = current_r.profile.copy()
        current_array = current_r.read(1)
        
        height = base_profile['height']
        width = base_profile['width']

        diff = current_array - baseline_array # np.subtract(current_array, baseline_array)
        # print(diff.shape)
        diff_reshaped = diff.reshape(1, height, width)

        with rio.open(out_filepath, 'w', **base_profile) as out:
            out.write(diff_reshaped)
```