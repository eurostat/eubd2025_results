#!/usr/bin/env python
# coding: utf-8

# In[20]:


import folium
import streamlit as st
from streamlit_folium import st_folium
import geopandas as gpd
import branca.colormap as cm  
import pandas as pd
import plotly.express as px
import networkx as nx
import plotly.graph_objects as go 
from shapely.geometry import Point

#remove this SUBID
remove_SUBID = [9538563.0, 9539091.0]

#Metadata variables
variables_meta = pd.read_csv("Variables.tsv", sep='\t')

#load geo data
geo_dashboard = gpd.read_file("land_coverage_by_subid_normalized.geojson")
geo_dashboard = geo_dashboard[~geo_dashboard["SUBID"].isin(remove_SUBID)]
geo_dashboard["SUBID"] = geo_dashboard["SUBID"].astype(int).astype(str)
geo_dashboard = geo_dashboard.dropna(subset=["geometry"])

#load land_coverage_2018
land_coverage_2018 = pd.read_csv("land_coverage_2018.csv", index_col = 0)
land_coverage_2018["SUBID"] = land_coverage_2018["SUBID"].astype(int).astype(str)
land_coverage_2018 = land_coverage_2018[~land_coverage_2018["SUBID"].isin(remove_SUBID)]


#load paths
df_long_clean = pd.read_csv("all_pairs.csv")
df_long_clean = df_long_clean[~df_long_clean["SUBID_A"].isin(remove_SUBID)]
df_long_clean = df_long_clean[~df_long_clean["SUBID_B"].isin(remove_SUBID)]
df_long_clean["SUBID_A"] = df_long_clean["SUBID_A"].astype("str")
df_long_clean["SUBID_A"] = df_long_clean["SUBID_B"].astype("str")


#load indicators
indicators = gpd.read_file("indicators.geojson")
indicators = indicators[~indicators["SUBID"].isin(remove_SUBID)]
indicators["SUBID"] = indicators["SUBID"].astype(int).astype(str)
indicators = indicators.dropna()


#load indicators
indicators_2020 = gpd.read_file("indicators_2020.geojson")
indicators_2020 = indicators_2020[~indicators_2020["SUBID"].isin(remove_SUBID)]
indicators_2020["SUBID"] = indicators_2020["SUBID"].astype(int).astype(str)
indicators_2020 = indicators_2020.dropna()


#load all_paths
all_paths = pd.read_csv("all_paths.csv", dtype={"SUBID": str})
all_paths = all_paths[~all_paths["SUBID"].isin(remove_SUBID)]
all_paths = all_paths.applymap(lambda x: str(int(float(x))) if pd.notna(x) else x)

#Rivers
water_bodies = gpd.read_file("tagusriver_waterbodies_simplified.shp")
water_bodies = water_bodies.to_crs(epsg=4326)





#Variable rename
rename_dict = {
    "SUBID": "Sub-basin ID",
    "rdis_tmean": "River discharge (m³/s)",
    "totn_tmean": "Total nitrogen concentration in catchments (mg/L)",
    "totp_tmean": "Total phosphorus concentration in catchments (mg/L)",
    "totlocp_tmean": "Total phosphorus concentration in local streams (mg/L)",
    "totpload_tmean": "Total phosphorus load in catchments (kg/year)",
    "totnload_tmean": "Total nitrogen load in catchments (kg/year)",
    "totlocn_tmean": "Total nitrogen concentration in local streams (mg/L)"
}


if not isinstance(geo_dashboard, gpd.GeoDataFrame):
    geo_dashboard = gpd.GeoDataFrame(geo_dashboard, geometry="geometry")

st.set_page_config(
    page_title="Water Pollution Dashboard",  
    page_icon="🌍",  
    layout="wide"
)

image_url = "image.png"


st.markdown("""
    <style>
        body {{
            background-image: url("{image_url}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            opacity: 0.2;  /* Sets transparency */
            position: fixed;
            width: 100%;
            height: 100%;
            z-index: -1;
        }}
        .main {
            background-color: #ffffff; /* Adjust Streamlit's default page */
        }
        /* Header Styling */
        .big-title {
            font-size: 36px;
            font-weight: bold;
            text-align: center;
            color: #1f77b4;
        }
        /* Subtitle */
        .subtitle {
            font-size: 18px;
            text-align: center;
            color: #555;
            margin-bottom: 20px;
        }
        /* Metadata Section */
        .metadata {
            background-color: #f9f9f9;
            padding: 10px;
            border-radius: 10px;
            border-left: 5px solid #1f77b4;
        }
        /* Enable text wrapping inside tables */
        .scrollable-table {
            overflow-x: auto;
            width: 100%;
            display: block;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            border: 1px solid #ddd;
        }
        th, td {
            text-align: left;
            padding: 10px;
            border: 1px solid #ddd;
            max-width: 400px; /* Adjust column width */
            word-wrap: break-word;
            white-space: normal;
        }
        th {
            background-color: #f4f4f4;
        }
    </style>
""", unsafe_allow_html=True)

land_cover_colors = {
    "Continuous urban fabric": (230, 0, 77),
    "Discontinuous urban fabric": (255, 0, 0),
    "Industrial or commercial units": (204, 77, 242),
    "Road and rail networks and associated land": (204, 0, 0),
    "Port areas": (230, 204, 204),
    "Airports": (230, 204, 230),
    "Mineral extraction sites": (166, 0, 204),
    "Dump sites": (166, 77, 0),
    "Construction sites": (255, 77, 255),
    "Green urban areas": (255, 166, 255),
    "Sport and leisure facilities": (255, 230, 255),
    "Non-irrigated arable land": (255, 255, 168),
    "Permanently irrigated land": (255, 255, 0),
    "Rice fields": (230, 230, 0),
    "Vineyards": (230, 128, 0),
    "Fruit trees and berry plantations": (242, 166, 77),
    "Olive groves": (230, 166, 0),
    "Pastures": (230, 230, 77),
    "Annual crops associated with permanent crops": (255, 230, 166),
    "Complex cultivation patterns": (255, 230, 77),
    "Land principally occupied by agriculture": (230, 204, 77),
    "Agro-forestry areas": (242, 204, 166),
    "Broad-leaved forest": (128, 255, 0),
    "Coniferous forest": (0, 166, 0),
    "Mixed forest": (77, 255, 0),
    "Natural grasslands": (204, 242, 77),
    "Moors and heathland": (166, 255, 128),
    "Sclerophyllous vegetation": (166, 230, 77),
    "Transitional woodland-shrub": (166, 242, 0),
    "Beaches, dunes, sands": (230, 230, 230),
    "Bare rocks": (204, 204, 204),
    "Sparsely vegetated areas": (204, 255, 204),
    "Burnt areas": (0, 0, 0),
    "Glaciers and perpetual snow": (166, 230, 204),
    "Inland marshes": (166, 166, 255),
    "Peat bogs": (77, 77, 255),
    "Salt marshes": (204, 204, 255),
    "Salines": (230, 230, 255),
    "Intertidal flats": (166, 166, 230),
    "Water courses": (0, 204, 242),
    "Water bodies": (128, 242, 230),
    "Coastal lagoons": (0, 255, 166),
    "Estuaries": (166, 255, 230),
    "Sea and ocean": (230, 242, 255)
}

def rgb_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)

color_mapping = {k: rgb_to_hex(v) for k, v in land_cover_colors.items()}



st.markdown('<p class="big-title">🌍 Water Pollution in Tagus River Basin</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Using geospatial data to monitor and analyze pollution levels.</p>', unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])  # Adjust column width (2:1 ratio)

min_pollution_p = indicators["totp_tmean"].min()
max_pollution_p = indicators["totp_tmean"].max()
min_pollution_n = indicators["totn_tmean"].min()
max_pollution_n = indicators["totn_tmean"].max()
colormap_n = cm.linear.YlOrRd_09.scale(min_pollution_n, max_pollution_n)  
colormap_p = cm.linear.YlGnBu_09.scale(min_pollution_p, max_pollution_p) 


# Map
with col1:
    m = folium.Map(location=[39.5, -6], zoom_start=7, control_scale=True, tiles=None)  

    # WMS 1990
    folium.raster_layers.WmsTileLayer(
        url="https://image.discomap.eea.europa.eu/arcgis/services/Corine/CLC1990_WM/MapServer/WMSServer?",
        layers="Corine_Land_Cover_1990_raster17001",
        name="Land Cover 1990",
        fmt="image/png",
        transparent=True,
        overlay=False,
        control=True  
    ).add_to(m)
    
    # WMS 2018
    folium.raster_layers.WmsTileLayer(
        url="https://image.discomap.eea.europa.eu/arcgis/services/Corine/CLC2018_WM/MapServer/WMSServer?",
        layers="12",
        name="Land Cover 2018",
        fmt="image/png",
        transparent=True,
        overlay=False,
        control=True  
    ).add_to(m)


    folium.TileLayer(
        tiles="https://image.discomap.eea.europa.eu/arcgis/services/Corine/CLC1990_WM/MapServer/WMSServer?",
        attr="Land Cover 1990",
        name="Land Cover 1990",
        overlay=False,  
        control=True
    ).add_to(m)

    
    # Clickable GeoJSON Layer
    geojson_layer = folium.GeoJson(
        indicators,
        name="Total nitrogen concentration in catchments (mg/L) 1971-2000",
        tooltip=folium.GeoJsonTooltip(
            fields=["SUBID", "totn_tmean"],
            aliases=["Sub-basin ID:", "Total nitrogen concentration in catchments (mg/L) 1971-2000"],
            localize=True
        ),
        style_function=lambda feature: {
            "fillColor": colormap_n(feature["properties"]["totn_tmean"]),
            "color": "white",
            "weight": 0.5,
            "fillOpacity": 0.7
        },
        overlay=True,
        control=True,
        highlight_function=lambda x: {"weight": 3, "fillOpacity": 0.9},  
    ).add_to(m)

    
    geojson_layer = folium.GeoJson(
        indicators,
        name="Total phosphorus concentration in catchments (mg/L) 1971-2000",
        tooltip=folium.GeoJsonTooltip(
            fields=["SUBID", "totp_tmean"],
            aliases=["Sub-basin ID:", "Total phosphorus concentration in catchments (mg/L) 1971-2000"],
            localize=True
        ),
        style_function=lambda feature: {
            "fillColor": colormap_p(feature["properties"]["totp_tmean"]),
            "color": "white",
            "weight": 0.5,
            "fillOpacity": 0.7
        },
        overlay=True,
        control=True,
        highlight_function=lambda x: {"weight": 3, "fillOpacity": 0.9},  
    ).add_to(m)


    # Clickable GeoJSON Layer
    geojson_layer = folium.GeoJson(
        indicators,
        name="Total nitrogen concentration in catchments (mg/L) 2010-2040",
        tooltip=folium.GeoJsonTooltip(
            fields=["SUBID", "totn_tmean"],
            aliases=["Sub-basin ID:", "Total nitrogen concentration in catchments (mg/L) 2010-2040"],
            localize=True
        ),
        style_function=lambda feature: {
            "fillColor": colormap_n(feature["properties"]["totn_tmean"]),
            "color": "white",
            "weight": 0.5,
            "fillOpacity": 0.7
        },
        overlay=True,
        control=True,
        highlight_function=lambda x: {"weight": 3, "fillOpacity": 0.9},  
    ).add_to(m)

    
    geojson_layer = folium.GeoJson(
        indicators_2020,
        name="Total phosphorus concentration in catchments (mg/L) 2010-2040",
        tooltip=folium.GeoJsonTooltip(
            fields=["SUBID", "totp_tmean"],
            aliases=["Sub-basin ID:", "Total phosphorus concentration in catchments (mg/L) 2010-2040"],
            localize=True
        ),
        style_function=lambda feature: {
            "fillColor": colormap_p(feature["properties"]["totp_tmean"]),
            "color": "white",
            "weight": 0.5,
            "fillOpacity": 0.7
        },
        overlay=True,
        control=True,
        highlight_function=lambda x: {"weight": 3, "fillOpacity": 0.9},  
    ).add_to(m)


    folium.GeoJson(
        water_bodies,
        name="Tagus River Water Bodies",
        tooltip=folium.GeoJsonTooltip(fields=water_bodies.columns[:2].tolist()),  # Adjust tooltip fields
        style_function=lambda x: {
            "fillColor": "#1f76b4",
            "color": "#1f76b4",
            "weight": 1,
            "fillOpacity": 0.4
        }
    ).add_to(m)

    geojson_layer = folium.GeoJson(
        indicators_2020,
        name="Sub-basins",
        tooltip=folium.GeoJsonTooltip(
            fields=["SUBID"],
            aliases=["Sub-basin ID:"],
            localize=True
        ),
        style_function=lambda feature: {
            "fillColor": "#ffffff",
            "color": "black",
            "weight": 1,
            "fillOpacity": 0
        },
        overlay=True,
        control=True,
        highlight_function=lambda x: {"weight": 3, "fillOpacity": 0.9},  
    ).add_to(m)

    

    geojson_layer.add_child(
        folium.features.GeoJsonPopup(fields=["SUBID"], aliases=["Sub-basin ID:"])
    )

    colormap_n.caption = "Total Nitrogen Load (mg/L)"
    colormap_n.location = "topright" 
    m.add_child(colormap_n)
    
    colormap_p.caption = "Total Phosphorus Load (mg/L)"
    colormap_p.location = "topright"
    m.add_child(colormap_p)


    folium.LayerControl(
        position="bottomright", 
        collapsed=False
    ).add_to(m)


    
    map_data = st_folium(m, width=800, height=600, returned_objects=["last_object_clicked"])

    if "selected_subid" in st.session_state:
        if not map_data or not map_data.get("last_object_clicked"):  # No click detected
            del st.session_state["selected_subid"]  # Reset selection
            st.rerun()  # Refresh Streamlit app

    
    if map_data and "last_object_clicked" in map_data and map_data["last_object_clicked"]:
        lat_lng = map_data["last_object_clicked"]

        if lat_lng:
            clicked_point = Point(lat_lng["lng"], lat_lng["lat"])  

            matched_row = geo_dashboard[geo_dashboard.contains(clicked_point)]

            if not matched_row.empty:
                new_subid = str(matched_row.iloc[0]["SUBID"])

                if new_subid != st.session_state.get("selected_subid"):
                    st.session_state["selected_subid"] = new_subid
                    st.experimental_set_query_params(selected_subid=new_subid)  
                    st.rerun()  

    clicked_subid = st.session_state.get("selected_subid", geo_dashboard["SUBID"].iloc[0])
    df_long_clean["SUBID_A"] = df_long_clean["SUBID_A"].astype(str)
    df_long_clean["SUBID_B"] = df_long_clean["SUBID_B"].astype(str)
    
    downstream_subids = df_long_clean[df_long_clean["SUBID_A"] == clicked_subid]["SUBID_B"].astype(str)

    
    
    def style_function(feature):
        subid = feature["properties"]["SUBID"]
        if subid == clicked_subid:
            return {"fillColor": "#ff0000", "color": "white", "weight": 3, "fillOpacity": 0.9} 
        elif subid in downstream_subids:
            return {"fillColor": highlight_color, "color": "white", "weight": 5, "fillOpacity": 0.7} 
        else:
            return {"fillColor": "gray", "color": "white", "weight": 0.5, "fillOpacity": 0.5}
    
    # GeoJSON Layer with Updated Style Function
    folium.GeoJson(
        geo_dashboard,
        name="Clickable Sub-Basins",
        tooltip=folium.GeoJsonTooltip(
            fields=["SUBID", "totnload_tmean"],
            aliases=["Sub-basin ID:", "Total Nitrogen Load (mg/L):"],
            localize=True
        ),
        style_function=style_function,
        overlay=True,
        control=True
    ).add_to(m)


    st.markdown(
        """
        <style>
            /* Adjust the colormap positions */
            .leaflet-container .legend {
                position: absolute !important;
                left: 100px !important;
                top: 50px !important;
                z-index: 1000 !important;
                background: rgba(255, 255, 255, 0.8) !important; /* Optional: Slight transparency */
                padding: 5px !important;
                border-radius: 5px !important;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        """
        <style>
            .leaflet-control-zoom {
                position: absolute !important;
                right: 10px !important;  /* ✅ Moves zoom buttons to the right */
                left: auto !important;   /* ✅ Ensures it's no longer on the left */
                top: 10px !important;    /* ✅ Adjust vertical positioning */
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    
    


with col2:
    if map_data and "last_object_clicked" in map_data and map_data["last_object_clicked"]:
        if clicked_subid in geo_dashboard["SUBID"].values and clicked_subid in land_coverage_2018["SUBID"].values:
            land_cover_1990 = geo_dashboard[geo_dashboard["SUBID"] == clicked_subid].drop(columns=["SUBID", "totnload_tmean", "geometry"]).sum().reset_index()
            land_cover_2018 = land_coverage_2018[land_coverage_2018["SUBID"] == clicked_subid].drop(columns=["SUBID"]).sum().reset_index()
        else:
            st.write("Else")
            land_cover_1990 = geo_dashboard.drop(columns=["SUBID", "totnload_tmean", "geometry"]).sum().reset_index()
            land_cover_2018 = land_coverage_2018.drop(columns=["SUBID"]).sum().reset_index()

    else:
        land_cover_1990 = geo_dashboard.drop(columns=["SUBID", "totnload_tmean", "geometry"]).sum().reset_index()
        land_cover_2018 = land_coverage_2018.drop(columns=["SUBID"]).sum().reset_index()

    land_cover_1990.columns = ["Land Cover Type", "Area"]
    land_cover_2018.columns = ["Land Cover Type", "Area"]

    land_cover_1990["Percentage"] = (land_cover_1990["Area"] / land_cover_1990["Area"].sum()) * 100
    land_cover_2018["Percentage"] = (land_cover_2018["Area"] / land_cover_2018["Area"].sum()) * 100

    land_cover_1990["Year"] = "1990"
    land_cover_2018["Year"] = "2018"

    top_10_types = pd.concat([land_cover_1990, land_cover_2018]).groupby("Land Cover Type")["Area"].sum().nlargest(10).index

    land_cover_1990 = land_cover_1990[land_cover_1990["Land Cover Type"].isin(top_10_types)]
    land_cover_2018 = land_cover_2018[land_cover_2018["Land Cover Type"].isin(top_10_types)]

    stacked_data = pd.concat([land_cover_1990, land_cover_2018])

    fig_bar = px.bar(
        stacked_data,
        x="Year",
        y="Percentage",
        color="Land Cover Type",
        title="Land Cover Change Between 1990 and 2018",
        text_auto=".2f",
        color_discrete_map=color_mapping
    )

    fig_bar.update_layout(
        barmode="stack",  # Full stacked bar
        xaxis_title="Year",
        yaxis_title="Percentage (%)",
        legend_title="Land Cover Type",
        height=500,
        margin=dict(t=20, b=20, l=10, r=10),
        uniformtext_minsize=10,
        uniformtext_mode="hide",
        showlegend=True,
        legend=dict(
            orientation="h", 
            yanchor="bottom",
            y=-0.7, 
            xanchor="center",
            x=0.5,
            font=dict(size=10), 
            tracegroupgap=2
        )
    )

    st.subheader("📊 Land Cover (Top 10)")
    st.plotly_chart(fig_bar, use_container_width=True)
    



    



# Line plot

if clicked_subid:
    selected_row = all_paths[all_paths["SUBID"] == clicked_subid]

    if not selected_row.empty:
        downstream_path = selected_row.iloc[0, 1:].dropna().astype(str).tolist()
        downstream_path.insert(0, clicked_subid)

        filtered_indicators = indicators[indicators["SUBID"].isin(downstream_path)].copy()
        filtered_indicators_2020 = indicators_2020[indicators_2020["SUBID"].isin(downstream_path)].copy()
        
        filtered_indicators = filtered_indicators.drop(columns = ["geometry"])
        filtered_indicators_2020 = filtered_indicators_2020.drop(columns = ["geometry"])        


        
        filtered_indicators["order"] = filtered_indicators["SUBID"].apply(lambda x: downstream_path.index(x))
        filtered_indicators_2020["order"] = filtered_indicators_2020["SUBID"].apply(lambda x: downstream_path.index(x))

        filtered_indicators = filtered_indicators.sort_values("order")
        filtered_indicators_2020 = filtered_indicators_2020.sort_values("order")


        
        filtered_indicators["totn_tmean"] = filtered_indicators["totn_tmean"]
        filtered_indicators["totp_tmean"] = filtered_indicators["totp_tmean"]
        filtered_indicators_2020["totn_tmean"] = filtered_indicators_2020["totn_tmean"]
        filtered_indicators_2020["totp_tmean"] = filtered_indicators_2020["totp_tmean"]


        
        filtered_indicators.rename(columns={
            "totn_tmean": "Total nitrogen concentration in catchments (mg/L) 1971-2000",
            "totp_tmean": "Total phosphorus concentration in catchments (mg/L) 1971-2000"
        }, inplace=True)

        filtered_indicators_2020.rename(columns={
            "totn_tmean": "Total nitrogen concentration in catchments (mg/L) 2011-2040",
            "totp_tmean": "Total phosphorus concentration in catchments (mg/L) 2011-2040"
        }, inplace=True)


        filtered_complete = pd.merge(
            filtered_indicators[["SUBID", "order", "Total nitrogen concentration in catchments (mg/L) 1971-2000",
                                  "Total phosphorus concentration in catchments (mg/L) 1971-2000"]],
            filtered_indicators_2020[["SUBID", "order", "Total nitrogen concentration in catchments (mg/L) 2011-2040",
                                       "Total phosphorus concentration in catchments (mg/L) 2011-2040"]],
            on=["SUBID", "order"],
            how="outer"
        )        
        filtered_complete = filtered_complete.fillna(method="ffill")

        filtered_complete = filtered_complete.sort_values("order")

        
        fig = px.line(
            filtered_complete,
            x="order",
            y=[
                "Total nitrogen concentration in catchments (mg/L) 1971-2000",
                "Total phosphorus concentration in catchments (mg/L) 1971-2000",
                "Total nitrogen concentration in catchments (mg/L) 2011-2040",
                "Total phosphorus concentration in catchments (mg/L) 2011-2040"
            ],
            title="",
            markers=True,
            hover_data={"SUBID": True, "order": False}
        )

        color_mapping = {
            "Total nitrogen concentration in catchments (mg/L) 1971-2000": "#c51126",
            "Total phosphorus concentration in catchments (mg/L) 1971-2000": "#18316c",
            "Total nitrogen concentration in catchments (mg/L) 2011-2040": "#ff5733", 
            "Total phosphorus concentration in catchments (mg/L) 2011-2040": "#1f4f8f"
        }

        for trace in fig.data:
            if trace.name in color_mapping:
                trace.line.color = color_mapping[trace.name]
                trace.marker.color = color_mapping[trace.name]

        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8)
        )

        fig.update_layout(
            xaxis_title="Step",
            yaxis_title="Concentration (mg/L)",
            legend_title="Indicator",
            hovermode="x unified",
            font=dict(size=16), 
            xaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)), 
            yaxis=dict(title_font=dict(size=18), tickfont=dict(size=14)),  
            legend=dict(font=dict(size=14)),  
        )

        st.subheader(f"📈 Water Quality Along Path from {clicked_subid}")
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("⚠️ No downstream path found for the selected SUBID.")
else:
    st.info("ℹ️ Click on a sub-basin to view its downstream path.")



st.subheader("📊 Pollution Data Table")

st.markdown(
    """
    <style>
        /* Apply word wrap for column headers and table cells */
        div[data-testid="stTable"] {
            overflow-x: auto;
            white-space: normal;
        }
        
        th, td {
            max-width: 50px; /* Adjust column width */
            word-wrap: break-word;
            white-space: normal;
            text-align: left;
        }
    </style>
    """,
    unsafe_allow_html=True
)

if map_data and "last_object_clicked" in map_data and map_data["last_object_clicked"]:
    selected_data_1971 = indicators[indicators["SUBID"] == clicked_subid].iloc[:,:-1]
    selected_data_1971["Period"] = "1971-2000"
    selected_data_1971 = selected_data_1971.merge(geo_dashboard.drop(columns=["totnload_tmean", "geometry"]), on = "SUBID")
    selected_data_2020 = indicators_2020[indicators_2020["SUBID"] == clicked_subid].iloc[:,:-1]
    selected_data_2020["Period"] = "2011-2040"
    selected_data_2020 = selected_data_2020.merge(land_coverage_2018, on = "SUBID")
    selected_data = pd.concat([selected_data_1971, selected_data_2020])
    selected_data = selected_data[["Period"] + [col for col in selected_data.columns if col != "Period"]]
    selected_data = selected_data.dropna(axis = 1)
    selected_data = selected_data.drop(columns=["geometry"], errors="ignore")
    
    st.dataframe(
        selected_data.rename(columns=rename_dict).style.hide(axis="index"),
        height=120  
    )
else:
    indicators["Period"] = "1971-2000"
    indicators = indicators.merge(geo_dashboard.drop(columns=["totnload_tmean", "geometry"]), on="SUBID")

    indicators_2020["Period"] = "2011-2040"
    indicators_2020 = indicators_2020.merge(land_coverage_2018, on="SUBID")

    selected_data = pd.concat([indicators, indicators_2020])
    selected_data = selected_data[["Period"] + [col for col in selected_data.columns if col != "Period"]]
    selected_data = selected_data[["SUBID"] + [col for col in selected_data.columns if col != "SUBID"]]
    selected_data = selected_data.dropna(axis = 1, how = "all")
    selected_data = selected_data.drop(columns=["geometry"], errors="ignore")
    selected_data = selected_data.sort_values(by=["SUBID", "Period"])

    st.dataframe(
        selected_data.rename(columns=rename_dict).style.hide(axis="index"),
        height=400
    )




    

# Metadata Section (Collapsible)
with st.expander("📄 **View Metadata**"):
    st.markdown("## 🌍 Water pollution from a river basin perspective")

    st.markdown("### 📜 Description")
    st.write(
        "In the European Union, one of the policy areas addresses specifically Inland Water and pollution. "
        "Currently, there is a **Water Framework Directive**, which states that Member States have to use their "
        "**River Basin Management Plans** to govern over rivers. It also highlights the importance of a common approach, "
        "as many river basins are international."
    )

    st.write(
        "This proposal studies water pollution through the **concentration of phosphorus and nitrogen** in the "
        "**Tagus River’s sub-basin areas**. Using historical data, with **land use information** and **river stream flow**, "
        "predictions of the status of water pollution are made from current land coverage data."
    )

    st.markdown("### 🗺 Geographical area of study")
    st.write("Spain and Portugal, **Tagus River basin**.")

    st.markdown("### 📍 Geographical disaggregation level")
    st.write("**Subbasin units**, which are smaller than **NUTS3**.")

    st.markdown("### 📅 Time periods of study")
    st.write("- **Water pollution reference period:** 1971 to 2000 *(mean value of the period)*")
    st.write("- **Water pollution prediction period:** 2011 to 2040")
    st.write("- **Land coverage reference period:** 1990")
    st.write("- **Land coverage comparison period:** 2018")

    st.markdown("### 📊 Dataset Variables")
    table_html = variables_meta.to_html(index=False, escape=False)
    st.markdown(f'<div class="scrollable-table">{table_html}</div>', unsafe_allow_html=True)

    st.markdown("### References")
    st.write("Copernicus Climate Change Service, Climate Data Store, (2021).")
    st.write("Isberg, K. (2017). Level A Pan Europe Subbasins, E-HYPE 3.0.")
    st.write("Copernicus Land Monitoring Service. (2020). CORINE Land Cover (CLC).")


# In[ ]:




