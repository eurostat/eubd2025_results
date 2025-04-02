import pandas as pd
import pathlib

# Load data
tbl_hedge_inter = pd.read_csv("www/data/Table_hedge_area_ha_per_nuts3_and_INTERSECTS_corine_agri_cls.csv")
tbl_hedge_within = pd.read_csv("www/data/Table_hedge_area_ha_per_nuts3_and_WITHIN_corine_agri_cls.csv")
tbl_hedge_class = pd.read_csv("www/data/Table_hedge_area_ha_per_nuts3_and_WITHIN_corine_agri_cls.csv")
tbl_hedge_nuts3 = pd.read_csv("www/data/Table_total_hedge_area_ha_nuts3.csv")
tbl_label_nuts3_bb = pd.read_csv("www/data/nuts_names_BB.csv")
tbl_label_nuts3_sm = pd.read_csv("www/data/nuts_names_SM.csv")

tbl_label_nuts3 = pd.concat([tbl_label_nuts3_bb, tbl_label_nuts3_sm])

# Merge data
data_merged = pd.merge(tbl_hedge_inter, tbl_label_nuts3.iloc[:,1:] , left_on="NUTS3_ID", right_on="NUTS_ID", how="left")
data_merged = pd.merge(data_merged, tbl_hedge_within.iloc[:,3:] , on="NUTS3_ID")
data_merged = pd.merge(data_merged, tbl_hedge_class.iloc[:,3:] , on="NUTS3_ID")
tbl_hedge_nuts3 = pd.merge(tbl_label_nuts3, tbl_hedge_nuts3.iloc[:,3:] , left_on="NUTS_ID", right_on="NUTS3_ID") 

# Save merged data as Parquet file
tbl_hedge_nuts3.to_parquet("www/data/final/tbl_hedge_nuts3.parquet")

data_merged.to_parquet("www/data/merged_data.parquet")

# Example to read the Parquet file
data_read = pd.read_parquet("www/data/merged_data.parquet")
print(data_read.head())
print(data_read.columns)


##PART 2 Preprossing for the map
import geopandas as gpd
gdf_NUTS_BB = gpd.read_file( "www/data/NUTS_BB.gpkg")
gdf_NUTS_SM = gpd.read_file( "www/data/NUTS_SM.gpkg")
gdf_CORINE_BB = gpd.read_file("www/data/corine_clip_BB.gpkg")
gdf_CORINE_SM = gpd.read_file("www/data/corine_clip_SM.gpkg")
print(gdf_CORINE_SM.shape, gdf_CORINE_BB.shape)


gdf_NUTS_BB = gdf_NUTS_BB.to_crs(epsg=4326)
gdf_NUTS_SM = gdf_NUTS_SM.to_crs(epsg=4326)
gdf_CORINE_BB = gdf_CORINE_BB.to_crs(epsg=4326)
gdf_CORINE_SM = gdf_CORINE_SM.to_crs(epsg=4326)

# Save merged data as Parquet file
gdf_NUTS_BB.to_file("www/data/gdf_NUTS_BB.gpkg", driver="GPKG")
gdf_NUTS_SM.to_file("www/data/gdf_NUTS_SM.gpkg", driver="GPKG")
gdf_CORINE_BB.to_file("www/data/gdf_CORINE_BB.gpkg", driver="GPKG")
gdf_CORINE_SM.to_file("www/data/gdf_CORINE_SM.gpkg", driver="GPKG")
