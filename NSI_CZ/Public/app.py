from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import rasterio
from rasterio.transform import rowcol
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import os
import json


years = list(range(2017, 2025))  

DATA_FOLDER = "/home/eouser/export"
CITIES_FILE = os.path.join(DATA_FOLDER, "cities.json")

DEFAULT_CITY = "Praha"
DEFAULT_YEAR = 2017
height = 0
width = 0

def load_cities_from_json():
    if not os.path.exists(CITIES_FILE):
        print(f"? Soubor {CITIES_FILE} neexistuje!")
        return []
    
    try:
        with open(CITIES_FILE, "r", encoding="utf-8") as file:
            cities_data = json.load(file)

        if not isinstance(cities_data, list):
            print("? Chybný formát JSON souboru (očekáván seznam)!")
            return []
        
        return [{"label": city.get("name", "Unknown"), "value": city.get("name", "Unknown")} for city in cities_data]
    
    except json.JSONDecodeError:
        print("? Chyba při načítání JSON souboru (chybný formát)!")
        return []

def load_bbox_from_json(city):
    """Načte BBOX z odpovídajícího meta souboru pro vybrané město."""
    bbox_file = os.path.join(DATA_FOLDER, city, f"meta_{city}.json")

    global width, height
    
    if not os.path.exists(bbox_file):
        print(f"? Soubor {bbox_file} neexistuje pro {city}!")
        return None
    
    with open(bbox_file, "r", encoding="utf-8") as file:
        try:
            meta_data = json.load(file)
        except json.JSONDecodeError:
            print(f"? Chyba při načítání JSON souboru: {bbox_file}")
            return None

    bbox = meta_data.get("bbox")

    if not bbox or len(bbox) != 4:
        print(f"? Chybný BBOX ve {bbox_file}: {bbox}")
        return None
    height = bbox[3] - bbox[1]
    width = bbox[2] - bbox[0]
    print(f"? BBOX načten pro {city}: {bbox}")
    return bbox


def determine_sampling(zoom_level):
    """Dynamicky nastaví sampling podle zoom levelu."""
    if zoom_level < 7:
        return 20  
    elif zoom_level < 10:
        return 10  
    elif zoom_level < 13:
        return 5  
    else:
        return 2 




def load_ndvi_data(city, year, bbox, sampling=3):
    file_path = os.path.join(DATA_FOLDER, city, f"ndvi_{city}_{year}.tiff")

    if not os.path.exists(file_path):
        print(f"? NDVI soubor {file_path} neexistuje!")
        return pd.DataFrame()

    print(f"? Načítám NDVI data z {file_path}")

    with rasterio.open(file_path) as dataset:
        if dataset.crs is None:
            print(f"? Soubor {file_path} nemá definovaný CRS!")
            return pd.DataFrame()

        band = dataset.read(1, masked=True).filled(np.nan)  
        transform = dataset.transform

        rows, cols = band.shape
        latitudes, longitudes, intensities = [], [], []
        
        for row in range(0, rows, sampling):  
            for col in range(0, cols, sampling):  
                val = band[row, col]
                if np.isnan(val) or val < -1 or val > 1: 
                    continue
                
                lon, lat = transform * (col, row)

                # ?? **Filtrovat pouze body v rámci BBOX**
                if bbox and (bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]):
                    latitudes.append(lat)
                    longitudes.append(lon)
                    intensities.append(val)

        df = pd.DataFrame({"lat": latitudes, "lon": longitudes, "intensity": intensities})

    print(f"? Načteno {len(df)} bodů NDVI pro {city} {year} (vzorkování: {sampling})")

    return df

        
def load_temp_data(city, year, bbox, sampling=1):
    sampling=1
    file_path = os.path.join(DATA_FOLDER, city, f"temp_{city}_{year}.tiff")

    if not os.path.exists(file_path):
        print(f"? TMP soubor {file_path} neexistuje!")
        return pd.DataFrame()

    print(f"? Načítám TMP data z {file_path}")

    with rasterio.open(file_path) as dataset:
        if dataset.crs is None:
            print(f"? Soubor {file_path} nemá definovaný CRS!")
            return pd.DataFrame()

        band = dataset.read(1, masked=True).filled(np.nan)  # Použití masked_array a nahrazení NoData hodnot NaN
        transform = dataset.transform

        rows, cols = band.shape
        latitudes, longitudes, intensities = [], [], []
        
        for row in range(0, rows, sampling):  # Čtení pouze každého sampling-tého řádku
            for col in range(0, cols, sampling):  # Čtení pouze každého sampling-tého sloupce
                val = band[row, col]
                if np.isnan(val) or val < -1 or val > 1:  # Ignorovat NoData a nevalidní hodnoty
                    continue
                
                lon, lat = transform * (col, row)

                # ?? **Filtrovat pouze body v rámci BBOX**
                if bbox and (bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]):
                    latitudes.append(lat)
                    longitudes.append(lon)
                    intensities.append(val)

        df = pd.DataFrame({"lat": latitudes, "lon": longitudes, "intensity": intensities})

    print(f"? Načteno {len(df)} bodů TEMP pro {city} {year} (vzorkování: {sampling})")

    return df


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], title="Heat in the City")

        
# Navbar
navbar = dbc.Navbar(
    dbc.Container([
        html.A(
            dbc.Row([
        dbc.Col(dbc.NavbarBrand("Heat in the City", className="fw-bold fs-1 text-light py-16"))
    ], align="center", className="g-0")
        ),
    ], fluid=True),
    color=None, 
    dark=True,
    style={
        "background": "linear-gradient(135deg, #0071bc, #005f73)", 
        "padding": "20px 20px",
        "boxShadow": "0px 4px 10px rgba(0, 0, 0, 0.2)", 
        "marginBottom": "20px",
        "width": "100%"
    }
    )

sidebar = dbc.Card(
    [
        html.H4("Settings", className="card-title text-left"),
        html.Hr(),
        html.Label("Find Any City on the Map", className="fw-bold"),
        dcc.Dropdown(id="city-dropdown", options=load_cities_from_json(), value=DEFAULT_CITY, placeholder="Select City"),
            
        html.Div(id="selected-city"),
        html.Label("Layers", className="fw-bold mt-4"),
        html.Hr(),
        dcc.Checklist(
            id="layer-selection",
            options=[
                {"label": " Vegetation (Green)", "value": "green"},
                {"label": " Heat Index (Red)", "value": "red"}
            ],
            value=["green", "red"],
            inline=False,
            className="mb-3"
        ),
        html.Label("Select Year", className="fw-bold"),
        html.Hr(),
        dcc.Slider(
            id="year-slider",
            min=min(years), max=max(years), step=1,
            marks={year: str(year) for year in years if year % 1 == 0},
            value=2017,
            className="mb-4"
        ),
        html.Label("Animation", className="fw-bold"),
        html.Hr(),
        dbc.Button("▶ Play", id="play-button", color="primary", className="mt-2"),
        dcc.Interval(id="year-interval", interval=2017, n_intervals=0, disabled=True),
        html.Div(id="image-source-container", children=[
            html.Img(id="city-image", src=None, style={"width": "100%", "marginTop": "50px", "borderRadius": "10px"}),
            html.Div([
                html.A("#ShowYourStripes", href="https://showyourstripes.info/", target="_blank", style={"textDecoration": "none", "color": "#007bff"}),
                html.Span(" by "),
                html.A("Ed Hawkins", href="https://research.reading.ac.uk/meteorology/people/ed-hawkins/", target="_blank", style={"textDecoration": "none", "color": "#007bff"}),
                html.Span(" is licensed under  "),
                html.A("CC BY 4.0", href="https://creativecommons.org/licenses/by/4.0/", target="_blank", style={"textDecoration": "none", "color": "#007bff"}),
            ], style={"fontSize": "12px", "color": "#555", "marginTop": "5px"})
        ], style={"display": "none"}),
    ],
    body=True,
    className="shadow p-3 mb-5 bg-white rounded",  
    style={"backgroundColor": "#f8f9fa"} 
    )

app.layout = dbc.Container([
    navbar,
    dcc.Store(id="map-state", data={"zoom": 10, "center": {"lat": 50.0755, "lon": 14.4378}}), 
    dbc.Row([
        dbc.Col(sidebar, xs=12, md=4),
        dbc.Col([
            html.H5(id="year-display", className="text-left"), 
            dcc.Graph(id="map-content", style={
                "width": "100%",
                "height": "75vh",  # Výchozí hodnota pro PC
                "minHeight": "300px", 
                "maxHeight": "800px" 
                }, className="responsive-map"),
            html.Pre(id="data-output", style={"whiteSpace": "pre-wrap"}) 
        ],  xs=12, md=8)
    ]),
     html.Footer(
        "📢 Map created with Plotly | Data source: Copernicus",
        style={
        "textAlign": "center",
        "padding": "15px",
        "backgroundColor": "#e4f5ff",
        "position": "fixed",
        "width": "100%",
        "bottom": "0",
        "left": "0",
        "zIndex": "1000"
        }
    )

 ], fluid=True, style={"paddingBottom": "60px"})


    

def determine_sampling(zoom_level):
    """Dynamicky nastaví sampling podle zoom levelu."""
    if zoom_level < 7:
        return 20  # Hrubší vzorkování pro velké oblasti
    elif zoom_level < 10:
        return 10  
    elif zoom_level < 13:
        return 5  
    else:
        return 2  # Nejjemnější vzorkování při velkém přiblížení


    
@callback(
    Output("year-slider", "value"),
    Input("year-interval", "n_intervals"),
    State("year-slider", "value"),
    prevent_initial_call=True
    )

def update_year(n_intervals, current_year):
    next_year = current_year + 1 if current_year < max(years) else min(years)
    return next_year

@callback(
    Output("year-display", "children"),
    Input("year-slider", "value")
    )
def update_year_display(selected_year):
    return f"Year: {selected_year}"

@callback(
    [Output("year-interval", "disabled"),
     Output("play-button", "children")],
    Input("play-button", "n_clicks"),
    State("year-interval", "disabled"),
    prevent_initial_call=True
    )


def toggle_animation(n_clicks, is_disabled):
    if n_clicks is None:
        return True, "▶ Play"
    return (not is_disabled, "⏸ Pause" if is_disabled else "▶ Play")

@callback(
    Output("city-dropdown", "options"),
    Input("city-dropdown", "search_value"),
    prevent_initial_call=True
    )
def update_city_options(search_value):
    cities = load_cities_from_json()
    if not cities:
        return no_update
    if not search_value:
        return cities  
    filtered_cities = [city for city in cities if search_value.lower() in city["label"].lower()]
    return filtered_cities if filtered_cities else cities


@callback(
    [Output("map-content", "figure"),  
     Output("map-state", "data")],  # Už nevracíme texty
    [Input("city-dropdown", "value"), 
     Input("year-slider", "value"),
     Input("layer-selection", "value"),
     Input("map-content", "relayoutData")],
    [State("map-state", "data")]
)

def update_map(selected_city, selected_year, selected_layers, relayout_data, map_state):
    if not selected_city:
        return go.Figure(), map_state

    bbox = load_bbox_from_json(selected_city)
    if not bbox or len(bbox) != 4:
        return go.Figure(), map_state

    zoom_level = map_state["zoom"]
    map_center = map_state["center"]

    if bbox:
        new_center = {"lat": (bbox[1] + bbox[3]) / 2, "lon": (bbox[0] + bbox[2]) / 2}
        if map_state["center"] != new_center:  # Pouze pokud se liší
            map_center = new_center  

    if relayout_data:
        if "mapbox.zoom" in relayout_data:
            zoom_level = relayout_data["mapbox.zoom"]
        if "mapbox.center" in relayout_data:
            map_center = relayout_data["mapbox.center"]

    if bbox[2] - bbox[0] < 0.2:
        zoom_level = 20
        
        
    updated_map_state = {"zoom": zoom_level, "center": map_center}

        

    sampling = determine_sampling(zoom_level)
    
    fig_map = go.Figure()


    
       # ?? **Teplotní index (Heatmap)**
    df_red = pd.DataFrame()
    if "red" in selected_layers:
        df_red = load_temp_data(selected_city, selected_year, bbox, sampling)
        if not df_red.empty:
            fig_map.add_trace(go.Heatmap(
                x=df_red["lon"],  
                y=df_red["lat"],  
                hovertemplate='Lon: %{x}<br>Lat: %{y}<br>Temp: %{z} °C<extra></extra>',
                z=round((df_red["intensity"] * 100) - 50, 1),  
                colorscale="Reds",  
                opacity=0.7,
                zmin=((df_red["intensity"].min() * 100) - 50),
                zmax=((df_red["intensity"].max() * 100) - 50),
                name="Heat Index",
                showscale=True,
                coloraxis="coloraxis2"
            ))
    ndvi_colorscale = [
        [0, "rgba(255, 255, 255, 0)"],  # Průhledná bílá pro hodnoty blízké 0
        [0.2, "rgba(173, 221, 142, 0.0)"],  # Světle zelená
        [0.5, "rgba(116, 196, 118, 0.2)"],  # Střední zelená
        [0.8, "rgba(35, 139, 69, 0.5)"],  # Tmavě zelená
        [1, "rgba(0, 100, 0, 1)"]        
        ]  

    # ?? **NDVI Grid (Heatmap)**
    df_green = pd.DataFrame()
    if "green" in selected_layers:
        df_green = load_ndvi_data(selected_city, selected_year, bbox, sampling)
        if not df_green.empty:
            fig_map.add_trace(go.Heatmap(
                x=df_green["lon"],  
                y=df_green["lat"],  
                z=df_green["intensity"],  
                hovertemplate='Lon: %{x}<br>Lat: %{y}<br>NDVI: %{z}<extra></extra>',
                colorscale=ndvi_colorscale,  
                opacity=0.9,
                zmin=-1,
                zmax=1,
                name="NDVI Vegetation",
                showscale=True,
                coloraxis="coloraxis1"
            ))
 

    
    fig_map.update_layout(
        mapbox_zoom=zoom_level,  
        mapbox_center=map_center,
        coloraxis1=dict(
            colorscale=ndvi_colorscale,
            colorbar=dict(title="NDVI", x=1.1)
        ),
        coloraxis2=dict(
            colorscale="Reds",
            colorbar=dict(title="°C", x=1.0)
        )
    )
    fig_map.update_layout(map_style="open-street-map")
    fig_map.update_layout(margin={"r":0,"t":40,"l":0,"b":0})

    # ? **Uložit poslední hodnoty zoomu a středu do `dcc.Store`**
    updated_map_state = {"zoom": zoom_level, "center": map_center}

    return (fig_map, updated_map_state)





@callback(
    [Output("city-image", "src"),
     Output("image-source-container", "style")], 
    Input("city-dropdown", "value")
)
def update_city_image(selected_city):
    image_filename = f"{selected_city}.png"
    image_path = os.path.join("assets", image_filename)

    if os.path.exists(image_path):
        return f"/assets/{image_filename}", {"display": "block"}
    else:
        return None, {"display": "none"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)