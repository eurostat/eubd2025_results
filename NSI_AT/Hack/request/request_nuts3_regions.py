from typing import List

import argparse
import boto3
import configparser
import geopandas as gpd
import os
import tempfile


def parse_args():

    parser = argparse.ArgumentParser()

    parser.add_argument('--s3_config_filepath', dest='s3_config_filepath', type=str,
                        help='s3 credential filepath - /home/username/.s3cfg')
    parser.add_argument('--nuts3_ids', dest='nuts3_ids', type=str, nargs='+',
                        default=['AT123', 'ITF63'])
    parser.add_argument('--out_filepath', dest='out_filepath', type=str,
                        help='Location where the requested and subsetted NUTS3 file will be stored')
    
    args = parser.parse_args()
    return args


def request_nuts3_region_file(s3_config_filepath: str,
                              nuts3_ids: List[str],
                              out_filepath: str):
    

    config = configparser.ConfigParser()
    config.read(s3_config_filepath)
    credentials = dict(config['default'].items())
    s3 = boto3.client('s3',
                    endpoint_url=credentials['host_base'],
                    aws_access_key_id=credentials['access_key'],
                    aws_secret_access_key=credentials['secret_key'],
                    use_ssl=True,
                    verify=False)
    response = s3.list_objects_v2(Bucket='ESTAT', Prefix='NUTS')

    if 'Contents' in response:
        print("Objects in bucket:")
        # Iterate over each object
        for obj in response['Contents']:
            print(obj['Key'])
    else:
        print("No objects found in the bucket.")

    object_path = 'NUTS/2021/NUTS_RG_01M_2021_4326.shp.zip'

    # Create a temporary directory to store the shapefile
    with tempfile.TemporaryDirectory() as tmpdirname:
        # Define local path to save shapefile
        local_shapefile_path = os.path.join(tmpdirname, object_path.split('/')[-1])

        # Download the shapefile from S3
        s3.download_file('ESTAT', object_path, local_shapefile_path)

        # Read the shapefile into a GeoDataFrame
        gdf = gpd.read_file(local_shapefile_path)
    
    subset = gdf[gdf['NUTS_ID'].isin(nuts3_ids)]
    subset.to_file(out_filepath, driver='GPKG')


if __name__ == '__main__':

    args = parse_args()

    request_nuts3_region_file(s3_config_filepath=args.s3_config_filepath,
                              nuts3_ids=args.nuts3_ids,
                              out_filepath=args.out_filepath)
