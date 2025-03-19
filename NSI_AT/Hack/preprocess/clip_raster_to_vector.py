import geopandas as gpd
import numpy as np
import rasterio as rio
from rasterio.mask import mask
from pathlib import Path
from typing import List
import fiona


def clip_raster_to_vector(raster_filepath: Path,
                          gdf: gpd.GeoDataFrame,
                          nuts_id: str,
                          out_filepath: Path):
    
    """Clip raster to vector boundaries.
    """

    gdf = gdf[gdf['NUTS_ID']==nuts_id]

    with rio.open(raster_filepath) as src:
        gdf_reprojected = gdf.to_crs(src.crs)
        
        out_image, out_transform = mask(
            src, [gdf_reprojected.geometry], crop=True)
        out_meta = src.meta.copy()

    out_meta.update({
        "driver": "Gtiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform})

    with rio.open(out_filepath, 'w', **out_meta) as dst:
        dst.write(out_image)


def clip_clc_to_raster(vector_filepath, 
                       raster_filepath,
                       out_filepath: Path,
                       raster_crs: str = 'EPSG:4326'):
    
    """Clip raster to CLC forest mask extent
    """
    
    # with fiona.open(vector_filepath, "r") as vectorfile:
    #     geometries = [feature["geometry"] for feature in vectorfile]

    gdf = gpd.read_file(vector_filepath)
    gdf.to_crs(raster_crs, inplace=True)
    
    geometries = [feature for feature in gdf['geometry']]

    for idx, shape in enumerate(geometries):
        with rio.open(raster_filepath) as src:
            out_image, out_transform = rio.mask.mask(src, [shape], crop=True)
            out_meta = src.meta

        out_meta.update({"driver": "GTiff",
                         "height": out_image.shape[1],
                         "width": out_image.shape[2],
                         "transform": out_transform})
        
        with rio.open(out_filepath, "w", **out_meta) as out:
            out.write(out_image)


def apply_threshold_and_normalize(raster_filepath,
                                  out_filepath):

    src = rio.open(raster_filepath)
    dat = src.read()
    profile = src.profile.copy()
    perc_max = np.nanpercentile(dat, 98)
    perc_min = np.nanpercentile(dat, 2)

    dat[dat > perc_max] = np.nan
    dat[dat < perc_min] = np.nan

    scaled = (dat - np.nanmin(dat)) / (np.nanmax(dat) -  np.nanmin(dat))

    with rio.open(out_filepath, 'w', **profile) as out:
        out.write(scaled)


# def extract_field_polygon_pixel_values(gdf_filepath: str,
#                                        raster_filepath: str,
#                                        out_filepath: str,
#                                        months: List[str] = ['04', '05', '06', '07', '08', '09']):
#     
#     """
#     """
# 
#     # TODO: iterate over months before appending to the gdf
#     
#     gdf = gpd.read_file(gdf_filepath)
#     
#     raster = rio.open(raster_filepath)
#     array = raster.read(1)
#     
#     gdf = gdf.to_crs(raster.crs)
# 
#     out_arrays = []
#     
#     for month in months:
# 
#         out_medians, out_means = [], []
#         out_p25, out_p75, out_p10, out_p90 = [], [], [], []
#          
#         for idx, row in gdf.iterrows():
# 
#         
# 
#             out_array, _ = mask(raster, [row.geometry], crop=True) # clip array to polygon
#             out_array = out_array[~np.isnan(out_array)] # store non-nan values
#             out_arrays.append(out_array)
#             out_medians.append(np.median(out_array))
#             out_means.append(np.mean(out_array))
#             out_p10.append(np.percentile(out_array, 10))
#             out_p25.append(np.percentile(out_array, 25))
#             out_p75.append(np.percentile(out_array, 75))
#             out_p90.append(np.percentile(out_array, 90)) 
# 
#         gdf.insert(loc=gdf.shape[1]-1,
#                    column=f'{month}_field_median',
#                    value=out_medians)
#         gdf.insert(loc=gdf.shape[1]-1,
#                    column=f'{month}_field_mean',
#                    value=out_means)
#         gdf.insert(loc=gdf.shape[1]-1,
#                    column=f'{month}_field_p10',
#                    value=out_p10)
#         gdf.insert(loc=gdf.shape[1]-1,
#                    column=f'{month}_field_p25',
#                    value=out_p25)
#         gdf.insert(loc=gdf.shape[1]-1,
#                    column=f'{month}_field_p75',
#                    value=out_p75)
#         gdf.insert(loc=gdf.shape[1]-1,
#                    column=f'{month}_field_p90',
#                    value=out_p90)
#     
#     return gdf