# -*- coding: utf-8 -*-
"""
Created on Fri Mar 28 08:25:09 2025

@author: Stolle
"""

import geopandas as gpd
import os
import pandas as pd

# import NUTS regions

NUTS_BB = gpd.read_file("/pth/to/file")
# only include NUTS3 level
NUTS3_BB = NUTS_BB.loc[0:17]


NUTS_SM = gpd.read_file("/pth/to/file")
# only include NUTS3 level
NUTS3_SM = NUTS_SM.loc[0:5]

## calculate small woody features total area per NUTS3 region

def SWF_area_sum(swf, NUTS):
    
    # import Small Woody Features 
    if isinstance(swf, list):
        
        itms = []
        for i in swf: 
            itm = gpd.read_file(i)
            itms.append(itm)
            
        complete = pd.concat(itms)
    
    else: 
        complete = gpd.read_file(swf)
    
    # join small woody features with NUTS levels
    joined = gpd.sjoin(complete, NUTS, how="left", predicate="intersects")
    
    return joined
        

# Brandenburg    
BB_15 = SWF_area_sum("pth", NUTS3_BB)  
BB_15_sum = BB_15.groupby("NUTS_ID")["area"].sum().reset_index() 
BB_18 = SWF_area_sum("pth", NUTS3_BB) 
BB_18_sum = BB_18.groupby("NUTS_ID")["area"].sum().reset_index() 

# create dataframe and add columns for NUTS ID and area(ha)/year
df_BB =  pd.DataFrame()
df_BB["NUTS3_ID"] = BB_15_sum.NUTS_ID
df_BB["2015_SWF_area_ha"] = BB_15_sum["area"] / 10000
df_BB["NUTS2_ID"] = "DE40"
df_BB["NUTS1_ID"] = "DE"
df_BB = df_BB.sort_index(axis = 1)

df_BB["2018_SWF_area_ha"] = BB_18_sum["area"] / 10000

# Steiermark

SM_15 = SWF_area_sum("pth", NUTS3_SM)
SM_15_sum = SM_15.groupby("NUTS_ID")["area"].sum().reset_index() 
SM_18 = SWF_area_sum("pth", NUTS3_SM)
SM_18_sum = SM_18.groupby("NUTS_ID")["area"].sum().reset_index() 

# create dataframe and add columns for NUTS ID and area(ha)/year
df_SM =  pd.DataFrame()
df_SM["NUTS3_ID"] = SM_15_sum.NUTS_ID
df_SM["2015_SWF_area_ha"] = SM_15_sum["area"] / 10000
df_SM["NUTS2_ID"] = "AT22"
df_SM["NUTS1_ID"] = "AT"
df_SM = df_SM.sort_index(axis = 1)

df_SM["2018_SWF_area_ha"] = SM_18_sum["area"] / 10000


df_final = pd.concat([df_BB, df_SM], ignore_index=True)
df_final = df_final[["NUTS1_ID", "NUTS2_ID", "NUTS3_ID", "2015_SWF_area_ha", "2018_SWF_area_ha"]]


df_final.to_csv("output/pth/fl.csv")



## SWF area by type of SWF 

# group by type and calculaet area
BB_15_type = BB_15.groupby(["NUTS_ID", "code"])["area"].sum().reset_index()
BB_15_type["area"] = BB_15_type["area"] / 10000

# pivot dataframe to wide format
df_BB_15_wide = BB_15_type.pivot_table(index="NUTS_ID", columns="code", values="area", fill_value=0).reset_index()
df_BB_15_wide.rename(columns = {"NUTS_ID": "NUTS3_ID", "1" : "2015_linear_features", "2": "2015_patchy_features", "3": "2015_other_features"}, inplace = True)

# add column with total area
col_names = ["2015_linear_features", "2015_patchy_features", "2015_other_features" ]
df_BB_15_wide["2015_total_area_ha"] = df_BB_15_wide[col_names].sum(axis=1)

# repeat for 2018
BB_18_type = BB_18.groupby(["NUTS_ID", "code"])["area"].sum().reset_index()
BB_18_type["area"] = BB_18_type["area"] / 10000

df_BB_18_wide = BB_18_type.pivot_table(index="NUTS_ID", columns="code", values="area", fill_value=0).reset_index()

df_BB_18_wide.rename(columns = {"NUTS_ID": "NUTS3_ID", 1 : "2018_small_structures"}, inplace = True)
col_names = ["2018_small_structures"]
df_BB_18_wide["2018_total_area_ha"] = df_BB_18_wide[col_names].sum(axis=1)

# add together
df_type_BB = df_BB_15_wide
df_type_BB["2018_small_structures"] = df_BB_18_wide["2018_small_structures"]
df_type_BB["2018_total_area_ha"] = df_BB_18_wide["2018_total_area_ha"]
df_type_BB.insert(0, "NUTS2_ID", "DE40")
df_type_BB.insert(0, "NUTS1_ID", "DE")


# repeat for SM

# group by type and calculaet area
SM_15_type = SM_15.groupby(["NUTS_ID", "code"])["area"].sum().reset_index()
SM_15_type["area"] = SM_15_type["area"] / 10000

# pivot dataframe to wide format
df_SM_15_wide = SM_15_type.pivot_table(index="NUTS_ID", columns="code", values="area", fill_value=0).reset_index()
df_SM_15_wide.rename(columns = {"NUTS_ID": "NUTS3_ID", "1" : "2015_linear_features", "2": "2015_patchy_features", "3": "2015_other_features"}, inplace = True)

# add column with total area
col_names = ["2015_linear_features", "2015_patchy_features", "2015_other_features" ]
df_SM_15_wide["2015_total_area_ha"] = df_SM_15_wide[col_names].sum(axis=1)

# repeat for 2018
SM_18_type = SM_18.groupby(["NUTS_ID", "code"])["area"].sum().reset_index()
SM_18_type["area"] = SM_18_type["area"] / 10000

df_SM_18_wide = SM_18_type.pivot_table(index="NUTS_ID", columns="code", values="area", fill_value=0).reset_index()

df_SM_18_wide.rename(columns = {"NUTS_ID": "NUTS3_ID", 1 : "2018_small_structures"}, inplace = True)
col_names = ["2018_small_structures"]
df_SM_18_wide["2018_total_area_ha"] = df_SM_18_wide[col_names].sum(axis=1)

# add together
df_type_SM = df_SM_15_wide
df_type_SM["2018_small_structures"] = df_SM_18_wide["2018_small_structures"]
df_type_SM["2018_total_area_ha"] = df_SM_18_wide["2018_total_area_ha"]
df_type_SM.insert(0, "NUTS2_ID", "DE40")
df_type_SM.insert(0, "NUTS1_ID", "DE")


## add all together

df_type_final = pd.concat([df_type_BB ,df_type_SM ], ignore_index= True)
df_type_final.to_csv("output/pth/fl.csv")


## SWF area by corine agricultural class

# import corine

corine_BB = gpd.read_file("pth/to/corine")
# convert corine code to string
corine_BB["Code_18"] = corine_BB["Code_18"].astype("str")
# filter corine to only include agricultural land
corine_BB_agr = corine_BB[corine_BB["Code_18"].str.startswith("2", na = False)]

# Create a new column with the first two digits
corine_BB_agr['agri_class'] = corine_BB_agr['Code_18'].astype(str).str[:2].astype(int)


corine_SM = gpd.read_file("pth/to/corine")
# convert corine code to string
corine_SM["Code_18"] = corine_SM["Code_18"].astype("str")
# filter corine to only include agricultural land
corine_SM_agr = corine_SM[corine_SM["Code_18"].str.startswith("2", na = False)]

# Create a new column with the first two digits
corine_SM_agr['agri_class'] = corine_SM_agr['Code_18'].astype(str).str[:2].astype(int)




def calc_area_corine_class(SWF, corine, predicate):
    
    SWF = SWF.drop(columns = ["index_right"])
    
    jn = gpd.sjoin(SWF, corine, how = "inner", predicate = predicate)
    
    jn_area = jn.groupby(["NUTS_ID", "agri_class"])["area"].sum().reset_index()
    jn_area["area"] = jn["area"] / 10000
    
    jn_wide = jn_area.pivot_table(index="NUTS_ID", columns="agri_class", values="area", fill_value=0).reset_index()
    
    return jn_wide

BB_15_corine = calc_area_corine_class(BB_15, corine_BB, "within")
BB_15_corine.columns =  [f"Agricode{col}" for col in BB_15_corine.columns]
BB_15_corine.rename(columns = {"AgricodeNUTS_ID": "NUTS3_ID", "Agricode21" : "Arable_Land_2015", "Agricode22": "Permanent_Crops_2015", "Agricode23": "Pastures_2015", "Agricode24": "Heterogeneous_Agricultural_Areas_2015"}, inplace = True)
col_names = ["Arable_Land_2015", "Permanent_Crops_2015", "Pastures_2015", "Heterogeneous_Agricultural_Areas_2015"]
BB_15_corine["2015_total_area_ha"] = BB_15_corine[col_names].sum(axis=1)

# repeat for 2018

BB_18_corine = calc_area_corine_class(BB_18, corine_BB, "within")
BB_18_corine.columns =  [f"Agricode{col}" for col in BB_18_corine.columns]
BB_18_corine.rename(columns = {"AgricodeNUTS_ID": "NUTS3_ID", "Agricode21" : "Arable_Land_2018", "Agricode22": "Permanent_Crops_2018", "Agricode23": "Pastures_2018", "Agricode24": "Heterogeneous_Agricultural_Areas_2018"}, inplace = True)
col_names = ["Arable_Land_2018", "Permanent_Crops_2018", "Pastures_2018", "Heterogeneous_Agricultural_Areas_2018"]
BB_18_corine["2018_total_area_ha"] = BB_18_corine[col_names].sum(axis=1)



corine_final_BB = pd.merge(BB_15_corine, BB_18_corine, on = "NUTS3_ID")
corine_final_BB.insert(0, "NUTS2_ID", "DE40")
corine_final_BB.insert(0, "NUTS1_ID", "DE")

# repeat  for SM

SM_15_corine = calc_area_corine_class(SM_15, corine_SM, "within")
SM_15_corine.columns =  [f"Agricode{col}" for col in SM_15_corine.columns]
SM_15_corine.rename(columns = {"AgricodeNUTS_ID": "NUTS3_ID", "Agricode21" : "Arable_Land_2015", "Agricode22": "Permanent_Crops_2015", "Agricode23": "Pastures_2015", "Agricode24": "Heterogeneous_Agricultural_Areas_2015"}, inplace = True)
col_names = ["Arable_Land_2015", "Permanent_Crops_2015", "Pastures_2015", "Heterogeneous_Agricultural_Areas_2015"]
SM_15_corine["2015_total_area_ha"] = SM_15_corine[col_names].sum(axis=1)

# repeat for 2018

SM_18_corine = calc_area_corine_class(SM_18, corine_SM, "within")
SM_18_corine.columns =  [f"Agricode{col}" for col in SM_18_corine.columns]
SM_18_corine.rename(columns = {"AgricodeNUTS_ID": "NUTS3_ID", "Agricode21" : "Arable_Land_2018", "Agricode22": "Permanent_Crops_2018", "Agricode23": "Pastures_2018", "Agricode24": "Heterogeneous_Agricultural_Areas_2018"}, inplace = True)
col_names = ["Arable_Land_2018", "Permanent_Crops_2018", "Pastures_2018", "Heterogeneous_Agricultural_Areas_2018"]
SM_18_corine["2018_total_area_ha"] = SM_18_corine[col_names].sum(axis=1)


corine_final_SM = pd.merge(SM_15_corine, SM_18_corine, on = "NUTS3_ID")
corine_final_SM.insert(0, "NUTS2_ID", "AT22")
corine_final_SM.insert(0, "NUTS1_ID", "AT")


corine_final = pd.concat([corine_final_BB,corine_final_SM ], ignore_index= True)
corine_final.to_csv("output/pth/corine.csv")


