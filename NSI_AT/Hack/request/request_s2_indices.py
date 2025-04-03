from calendar import monthrange
from openeo.processes import log
from preprocess.vector_geometries import return_bounds_from_gdf
from typing import List
from pathlib import Path

import argparse
import geopandas as gpd
import openeo


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument('--max_cc', dest='max_cc', type=int, default=50,
                        help='Provide the maximum cloud cover for collecting data')
    
    parser.add_argument('--out_path', dest='out_path', type=str, 
                        default='/home/mkaes/hackathon/data/new_s2_indices',
                        help='Requested files will be written to out_path')
    
    parser.add_argument('--years', dest='years', type=str, nargs='+',
                        default=['2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024'],
                        help='Downloads the listed years')
    
    parser.add_argument('--months', dest='months', type=str, nargs='+',
                        default=[f'{i:02d}' for i in range(1, 13)],
                        help='Downloads the listed monhts - format: MM')
    
    parser.add_argument('--indices', dest='indices', type=str, nargs='+',
                        default=['NDMI', 'NDVI', 'EVI', 'LWC', 'LCI'],
                        help='Downloads the following indices')
    
    parser.add_argument('--aoi_filepath', dest='aoi_filepath', type=str,
                        default='/home/mkaes/hackathon/data/NUTS/2021/NUTS_RG_01M_2021_4326_subset.gpkg',
                        help=str('Path to the vector file containing the NUTS '
                                 'regions and their geometries'))
    
    args = parser.parse_args()
    return args


def calc_ndvi(b4, b8):

    return (b8 - b4) / (b8 + b4)


def calc_leaf_water_content_index(b8, b11):

    nominator = (1 - (b8 - b11))
    nominator = nominator.apply(lambda x: log(x, 10))

    denominator = (1 - (b8 - b11))
    denominator = denominator.apply(lambda x: -log(x, 10))

    return nominator / denominator


def calc_leaf_chlorophyll_index(b4, b5, b8):

    return (b8 - b5 / b8 + b4)


def calc_enhanced_vi(b1, b5, b9):

    return 2.5 * ((b9 - b5) / (b9 + 6 * b5 - 7.5 * b1) + 1)


def calc_ndmi(b8, b11):

    # normalized difference moisture index
    return ((b8 - b11) / (b8 + b11))


def request_and_download_data(aoi: dict,
                              nuts_id: str,
                              out_path: str,
                              months: List[str],
                              years: List[str],
                              indices: List[str],
                              max_cc: int,
                              collection_name: str = 'SENTINEL2_L2A',
                              bands: List[str] = ['B01', 'B04', 'B05', 'B08', 'B09', 'B11'],
                              aggregate_reducer: str = 'mean',
                              aggregate_period: str = 'month'):

    connection = openeo.connect(url='openeo.dataspace.copernicus.eu')
    connection.authenticate_oidc()

    for month in months:

        for year in years:

            print(f'month-year: {month}-{year}')

            last_day = str(monthrange(year=int(year), month=int(month))[1])
            temporal_extent = [f'{year}-{month}-01', f'{year}-{month}-{last_day}']

            s2cube = connection.load_collection(
                collection_name,
                temporal_extent=temporal_extent,
                spatial_extent=aoi,
                bands=bands,
                max_cloud_cover=max_cc)
            
            s2_temp = s2cube.aggregate_temporal_period(
                period=aggregate_period,
                reducer=aggregate_reducer)
            s2_100 = s2_temp.resample_spatial(resolution=100, method='near')
            s2_4326 = s2_100.resample_spatial(projection=4326)

            b1 = s2_4326.band('B01')
            b4 = s2_4326.band('B04')
            b8 = s2_4326.band('B08')
            b5 = s2_4326.band('B05')
            b8 = s2_4326.band('B08')
            b9 = s2_4326.band('B09')
            b11 = s2_4326.band('B11')

            if 'NDMI' in indices:

                op = f'{out_path}/NDMI/{nuts_id}/{year}'
                if not Path(op).exists():
                    Path(op).mkdir(parents=True, exist_ok=True)
                out_filepath = f'{op}/NDMI_{nuts_id}_{year}_{month}.tif'
                
                ndmi = calc_ndmi(b8=b8, b11=b11)
                ndmi.download(out_filepath)
                print('NDMI finished')

            if 'NDVI' in indices:
                
                op = f'{out_path}/NDVI/{nuts_id}/{year}'
                if not Path(op).exists():
                    Path(op).mkdir(parents=True, exist_ok=True)
                out_filepath = f'{op}/NDVI_{nuts_id}_{year}_{month}.tif'
                
                ndvi = calc_ndvi(b4=b4, b8=b8)  # (b4 - b8) / (b4 + b8)
                ndvi.download(out_filepath)
                print('NDVI finished')

            if 'LWC' in indices:
                
                op = f'{out_path}/LWC/{nuts_id}/{year}'
                if not Path(op).exists():
                    Path(op).mkdir(parents=True, exist_ok=True)
                out_filepath = f'{op}/LWC_{nuts_id}_{year}_{month}.tif'

                lwc = calc_leaf_water_content_index(b8=b8, b11=b11)
                lwc.download(out_filepath)
                print('LWC finished')

            if 'LCI' in indices:

                op = f'{out_path}/LCI/{nuts_id}/{year}'
                if not Path(op).exists():
                    Path(op).mkdir(parents=True, exist_ok=True)
                out_filepath = f'{op}/LCI_{nuts_id}_{year}_{month}.tif'

                lci = calc_leaf_chlorophyll_index(b4=b4, b5=b5, b8=b8)
                lci.download(out_filepath)
                print('LCI finished')
            
            if 'EVI' in indices:

                op = f'{out_path}/EVI/{nuts_id}/{year}'
                if not Path(op).exists():
                    Path(op).mkdir(parents=True, exist_ok=True)
                out_filepath = f'{op}/EVI_{nuts_id}_{year}_{month}.tif'

                evi = calc_enhanced_vi(b1=b1, b5=b5, b9=b9)
                evi.download(out_filepath)
                print('EVI finished')


if __name__ == '__main__':

    args = parse_args()
    gdf = gpd.read_file(args.aoi_filepath)
    idxs = gdf.index
    for idx in idxs:
        aoi, nuts_id = \
            return_bounds_from_gdf(gdf=gdf,
                                   idx=idx)
        
        print('NUTS:\t', nuts_id)
        print('AOI:\t', aoi)

        request_and_download_data(aoi=aoi,
                                  nuts_id=nuts_id,
                                  out_path=args.out_path,
                                  months=args.months,
                                  years=args.years,
                                  indices=args.indices,
                                  max_cc=args.max_cc)