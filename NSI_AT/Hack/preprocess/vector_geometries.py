from pathlib import Path
import geopandas as gpd


def return_bounds_from_gdf(gdf: gpd.GeoDataFrame,
                           idx: int):
    
    """
    gdf filepath: '/home/mkaes/hackathon/data/NUTS/2021/NUTS_RG_01M_2021_4326_subset.gpkg'
    """

    minx, miny, maxx, maxy = gdf.loc[idx, 'geometry'].bounds
    aoi = {'west': minx, 'south': miny, 'east': maxx, 'north': maxy}
    id = gdf.loc[idx, 'NUTS_ID']

    return aoi, id


def clip_vectors(vector_boundary_filepath: Path,
                 vector_to_clip_filepath: Path,
                 out_filepath: Path,
                 vector_boundary_subset_index: int = None):
    

    vector_boundary = gpd.read_file(vector_boundary_filepath)
    if not vector_boundary_subset_index:
        vector_boundary = vector_boundary[vector_boundary.index==vector_boundary_subset_index]

    vector_to_clip = gpd.read_file(vector_to_clip_filepath)

    vector_to_clip.to_crs(vector_boundary.crs, inplace=True)

    clipped = gpd.clip(vector_to_clip, mask=vector_boundary)    

    if not out_filepath.suffix == '.gpkg':
        out_filepath = f'{out_filepath.stem}.gpkg'

    clipped.to_file(out_filepath, driver='GPKG')