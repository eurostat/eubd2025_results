from typing import cast
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from shiny import ui, module, reactive, render
from shinywidgets import output_widget, render_widget , render_plotly

from ipywidgets import Layout
from ipyleaflet import Map, LayerGroup, basemaps, GeoJSON, Marker , Rectangle, projections

from shapely.wkb import loads
import geopandas as gpd
from shapely.geometry import shape
from sqlalchemy import create_engine
import json
import folium
from pyproj import Proj, transform
import pathlib

from utils import * 
import random

from utils.helper_text import (
    about_text,
    missing_note,
    dataset_information,
    slider_text_map,
)

basemap = cast(dict, basemaps)
def random_color(feature):
    return {
        "color": "black",
        "fillColor": random.choice(["red", "yellow", "green", "orange"]),
    }

data_read2 = pd.read_parquet(pathlib.Path(__file__).parent.parent / "www/data/final/tbl_hedge_nuts3.parquet")
data_read = pd.read_parquet(pathlib.Path(__file__).parent.parent / "www/data/merged_data.parquet")
list_Nuts3 = data_read["NUTS3_ID"].unique().tolist()
list_Nuts2 = data_read["NUTS2_ID"].unique().tolist()
list_Nuts3_latin = data_read2["NAME_LATN"].unique().tolist()

@module.ui
def map_ui():
    return ui.tags.div(
        ui.tags.div(
            about_text,
            ui.tags.hr(),
            slider_text_map,
            ui.tags.br(),
            ui.input_select(
                id="nuts2_value",
                label="Select Nuts2",
                choices=list_Nuts2,
            ),
            ui.input_select(
                id="nuts3_name",
                label="Select Nuts3",
                choices=list_Nuts3_latin,
            ),
            ui.tags.hr(),
            dataset_information,
            ui.tags.hr(),
            missing_note,
            class_="main-sidebar card-style",
        ),
        ui.tags.div(
            #output_widget("map", width="auto", height="auto"),
            output_widget("geopack_map"),
            #class_="main-main card-style no-padding",
        #),
        #ui.tags.div(
            ui.card(
                ui.output_data_frame("table"),
                class_="column",
            ),
            ui.card(
                #ui.output_plot("barchart"),
                ui.output_plot("piechart"),
                #output_widget("piechart"),
                class_="column",
            ),
            #class_="main-main card-style no-padding two-columns",
        ),
        class_="main-layout",
    )


@module.server
def map_server(input, output, session):#, is_wb_data):

    def _():
        # Example to read the Parquet file
        data_read = pd.read_parquet(pathlib.Path(__file__).parent.parent / "www/data/merged_data.parquet")
        gdf_SWF_DEA40_2018 = gpd.read_file(pathlib.Path(__file__).parent.parent / "www/data/clip_DEA40_2018.gpkg")
        print("SWF", gdf_SWF_DEA40_2018.shape, gdf_SWF_DEA40_2018.columns)
        print("SWF", gdf_SWF_DEA40_2018.head())

    @render_widget 
    def geopack_map():
        gdf_NUTS_BB = gpd.read_file(pathlib.Path(__file__).parent.parent / "www/data/NUTS_BB.gpkg")
        gdf_NUTS_SM = gpd.read_file(pathlib.Path(__file__).parent.parent / "www/data/NUTS_SM.gpkg")
        gdf_CORINE_AT222 = gpd.read_file(pathlib.Path(__file__).parent.parent / "www/data/clip_AT222_corine.gpkg")
        gdf_CORINE_DEA40 = gpd.read_file(pathlib.Path(__file__).parent.parent / "www/data/clip_DEA40_corine.gpkg")
        gdf_SWF_AT222_2018 = gpd.read_file(pathlib.Path(__file__).parent.parent / "www/data/clip_AT222_2018.gpkg")
        gdf_SWF_DEA40_2018 = gpd.read_file(pathlib.Path(__file__).parent.parent / "www/data/clip_DEA40_2018.gpkg")
        print(gdf_SWF_AT222_2018.shape, gdf_CORINE_DEA40.shape)
        print("SWF", gdf_SWF_DEA40_2018.shape, gdf_SWF_DEA40_2018.columns)
        print("SWF", gdf_SWF_DEA40_2018.head())

        m = Map(location=[52.5, 13.3], zoom=5)
        print("to CRS")
        gdf_NUTS_BB = gdf_NUTS_BB.to_crs(epsg=4326)
        #gdf_NUTS_SM = gdf_NUTS_SM.to_crs(epsg=4326)
        gdf_CORINE_AT222 = gdf_CORINE_AT222.to_crs(epsg=4326)
        gdf_CORINE_DEA40 = gdf_CORINE_DEA40.to_crs(epsg=4326)
        gdf_SWF_DEA40_2018 = gdf_SWF_DEA40_2018.to_crs(epsg=4326)
        #gdf_SWF_AT222_2018 = gdf_SWF_AT222_2018.to_crs(epsg=4326)

        print("to JSON") 
        gdf_NUTS_BB = gdf_NUTS_BB.geometry.to_json()
        #gdf_NUTS_SM = gdf_NUTS_SM.geometry.to_json()
        gdf_CORINE_AT222 = gdf_CORINE_AT222.geometry.to_json()
        gdf_CORINE_DEA40 = gdf_CORINE_DEA40.geometry.to_json()
        #gdf_SWF_AT222 = gdf_SWF_AT222.geometry.to_json()
        gdf_SWF_DEA40 = gdf_SWF_DEA40_2018.geometry.to_json()

        print("to Layer")
        #gdf_NUTS_BB_layer = GeoJSON(data=json.loads(gdf_NUTS_BB) , name="geojson")
        #gdf_NUTS_SM_layer = GeoJSON(data=json.loads(gdf_NUTS_SM) , name="geojson")
        gdf_CORINE_AT222_layer = GeoJSON(data=json.loads(gdf_CORINE_AT222) , name="geojson")
        gdf_CORINE_DEA40_layer = GeoJSON(data=json.loads(gdf_CORINE_DEA40) , name="geojson")
        #gdf_SWF_DEA40_layer = GeoJSON(data=json.loads(gdf_SWF_DEA40) , name="geojson")
        #print("HEad", gdf_SWF_DEA40_layer.head())

        print("to Map")
        #m.add_layer(gdf_NUTS_BB_layer)
        #m.add_layer(gdf_NUTS_SM_layer)
        m.add_layer(gdf_CORINE_DEA40_layer)
        m.add_layer(gdf_CORINE_AT222_layer)
        #m.add_layer(gdf_SWF_DEA40_layer)
        return m
    
    @render.plot
    def barchart():
        data_read = pd.read_parquet(pathlib.Path(__file__).parent.parent / "www/data/final/tbl_hedge_nuts3.parquet")
        
        # Create a bar chart using Matplotlib
        fig, ax = plt.subplots()
        ax.bar(data_read.loc[data_read["NUTS2_ID"] == input.nuts2_value(),"NUTS3_ID"], 
               data_read.loc[data_read["NUTS2_ID"] == input.nuts2_value(),'2015_SWF_area_ha'])
        ax.set_title('Bar Chart Example')
        ax.set_xlabel('NUTS3_ID')
        ax.set_ylabel('2015_SWF_area_ha')
        
        return fig
    
    @render.plot
    def piechart():
        corine_final = pd.read_parquet(pathlib.Path(__file__).parent.parent / "www/data/merged_data.parquet")

        plot_df = corine_final[["NUTS3_ID", "Arable_Land_2018", "Permanent_Crops_2018", "Pastures_2018", "Heterogeneous_Agricultural_Areas_2018"]] 
        plot_df = pd.merge(plot_df, data_read2[["NUTS3_ID", "NAME_LATN"]], on="NUTS3_ID")
        plot_df_filter = plot_df[plot_df["NAME_LATN"]== input.nuts3_name()] 
        plot_df_filter = plot_df_filter.drop(["NUTS3_ID"], axis = 1) 
        df_reshaped = plot_df_filter.melt(var_name='LCL', value_name='Area') 
        df_reshaped= df_reshaped.loc[df_reshaped["LCL"] !="NAME_LATN",:]
        # Create a Pie Chart using Plotly 
        print(df_reshaped)
        #fig = px.bar(df_reshaped, x ='LCL', y='Area', title="Share of Small Woody Features (ha) per CLC class Oberhavel (GER) 2018") 
        # # Show the plot 
            # Create a bar chart using Matplotlib
        fig, ax = plt.subplots()
        ax.bar(df_reshaped['LCL'], df_reshaped['Area'])
        ax.set_title("Share of Small Woody Features (ha) per CLC class Oberhavel (GER) 2018")
        ax.set_xlabel('LCL')
        ax.set_ylabel('Area')
        
        return fig
       

    
    @render.data_frame
    def table():
        data_read = pd.read_parquet(pathlib.Path(__file__).parent.parent / "www/data/final/tbl_hedge_nuts3.parquet")
        df = data_read.loc[data_read["NAME_LATN"] == input.nuts3_name(), :] 
        df.drop(["NUTS3_ID", "Unnamed: 0"] , axis = 1, inplace = True)

        # Round numeric columns to 2 digits
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        df[numeric_cols] = df[numeric_cols].round(2)

        print(df)
        return render.DataGrid(df )     
    


    engine = create_engine(DATABASE_URL)
    query = f"""SELECT "NUTS_ID", "LEVL_CODE", "NUTS_NAME", 
        ST_AsGeoJSON("geometry", 3035) AS geojson from public."Nuts3_data" Where "LEVL_CODE" = 0;"""
    
    @render.data_frame 
    def geojs():
        df = gpd.read_postgis(query, engine, geom_col="geojson")
        gdf = df.to_crs(epsg=4326)
        return gdf

    @render_widget 
    def map():
        map = Map(center=(4355000, 2700000), zoom=6, crs = projections.EPSG3035,)  
        # Query the WKB data
        query = f"""SELECT "NUTS_ID", "LEVL_CODE", "NUTS_NAME", 
            ST_AsGeoJSON("geometry", 3035) AS geojson from public."Nuts3_data" Where "LEVL_CODE" = 0;"""
        #df = gpd.read_postgis(query, engine, geom_col="geojson")
        df = pd.read_sql(query, engine)
        geojson = json.loads(df.to_json())
        #geojson_data = df["geojson"].apply(lambda x: json.loads(x))
        #geojson_layer = GeoJSON(data=geojson_data.to_dict(),
               #                 style={  
              #  "opacity": 1,  
             #   "dashArray": "9",  
            #    "fillOpacity": 0.1,  
           #     "weight": 1,  
          #  },
         #   hover_style={"color": "white", "dashArray": "0", "fillOpacity": 0.5},  
        #    style_callback=random_color,  )
        #folium.GeoJson(geojson, name="geojson").add_to(map)

        ###
        #proj_3035 = Proj(init="epsg:3035")
        #proj_4326 = Proj(init="epsg:4326")
        # Convert the coordinates to EPSG 4326
        min_x = 500000
        max_x = 1000000
        min_y = 6000000
        max_y = 7000000
        #min_lon, min_lat = transform(proj_3035, proj_4326, min_x, min_y)
        #max_lon, max_lat = transform(proj_3035, proj_4326, max_x, max_y)

        rect = Rectangle(
            bounds=[[4255000, 2500000], [4955000.5, 2900000]],
            color="blue",
            fill=True,
            fill_color="blue",
            
        )
        map.add_layer(rect)
        # Add a marker
        #map.add_layer(geojson_layer )
        return map

    

        # 🔹 Extract just the geometry part for mapping


    # Initialize and display when the session starts (1)
    # map = Map(
    #     basemap=basemap["CartoDB"]["Positron"],
    #     center=(50, 10),
    #     zoom=5,
    #     scroll_wheel_zoom=True,
    #     min_zoom=3,
    #     max_zoom=18,
    #     no_wrap=True,
    #     layout=Layout(width="100%", height="100%"),
    # )
    # map.panes = {"circles": {"zIndex": 650}, "choropleth": {"zIndex": 750}}
    # register_widget("map", map)

    # # Circles Layer will later be filled with circleMarkers
    # circle_markers_layer = LayerGroup()
    # circle_markers_layer.pane = "circles"
    # map.add_layer(circle_markers_layer)

    # # Polygon layer will later be filled reactively
    # choropleth_layer = LayerGroup()
    # choropleth_layer.pane = "choropleth"
    # map.add_layer(choropleth_layer)

    # @reactive.Calc
    # def point_data() -> DataFrame:
    #     if is_wb_data():
    #         return filter_data(map_data_world_bank, input.years_value())
    #     return filter_data(map_data_oecd, input.years_value())

    # @reactive.Effect
    # def _() -> None:
    #     add_circles(point_data(), circle_markers_layer)

    # @reactive.Effect()
    # def _() -> None:
    #     add_polygons(polygon_data, point_data(), choropleth_layer)