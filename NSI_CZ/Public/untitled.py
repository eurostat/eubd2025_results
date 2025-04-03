import dash
import dash_leaflet as dl
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, State
import rasterio
import numpy as np
import json
import os
import matplotlib.pyplot as plt
from rasterio.mask import mask
from shapely.geometry import shape

# **Cesty k souborům**
DATA_FOLDER = "/home/eouser/export"
CITIES_FILE = os.path.join(DATA_FOLDER, "cities.json")

DEFAULT_CITY = "Praha"
DEFAULT_YEAR = 2017

# **Načítání seznamu měst**
def load_cities():
    if not os.path.exists(CITIES_FILE):
        return []
    
    with open(CITIES_FILE, "r", encoding="utf-8") as file:
        cities_data = json.load(file)
    
    return [{"label": city["name"], "value": city["name"]} for city in cities_data]

# **Načtení BBOX z meta souboru**
def load_bbox(city):
    bbox_file = os.path.join(DATA_FOLDER, city, f"meta_{city}.json")

    if not os.path.exists(bbox_file):
        return None
    
    with open(bbox_file, "r", encoding="utf-8") as file:
        meta_data = json.load(file)

    bbox = meta_data.get("bbox")
    return bbox if bbox and len(bbox) == 4 else None

# **Načtení a ořezání TIFF souboru**
def load_tiff_data(city, year, layer, bbox):
    file_path = os.path.join(DATA_FOLDER, city, f"{layer}_{city}_{year}.tiff")
    
    if not os.path.exists(file_path):
        return None
    
    with rasterio.open(file_path) as src:
        clipped, transform = mask(src, [shape({"type": "Polygon", "coordinates": [[
            [bbox[0], bbox[1]], [bbox[2], bbox[1]],
            [bbox[2], bbox[3]], [bbox[0], bbox[3]],
            [bbox[0], bbox[1]]
        ]]})], crop=True, nodata=-9999)

    return clipped[0] if clipped is not None else None

# **Konverze NDVI do obrázku**
def process_ndvi(ndvi_data):
    if ndvi_data is None:
        return None

    ndvi_valid = np.where(ndvi_data == -9999, np.nan, ndvi_data)
    ndvi_min, ndvi_max = np.nanmin(ndvi_valid), np.nanmax(ndvi_valid)
    ndvi_normalized = (ndvi_valid - ndvi_min) / (ndvi_max - ndvi_min)

    cmap = plt.get_cmap("Greens")
    rgba_image = cmap(ndvi_normalized)
    rgba_image[:, :, 3] = np.where(ndvi_data <= 0, 0, 1)

    plt.imsave("ndvi_overlay.png", rgba_image)
    return "ndvi_overlay.png"

# **Konverze teploty do obrázku**
def process_temp(temp_data):
    if temp_data is None:
        return None

    temp_valid = np.where(temp_data == -9999, np.nan, temp_data)
    temp_min, temp_max = np.nanmin(temp_valid), np.nanmax(temp_valid)
    temp_normalized = (temp_valid - temp_min) / (temp_max - temp_min)

    cmap = plt.get_cmap("Reds")
    rgba_image = cmap(temp_normalized)
    rgba_image[:, :, 3] = np.where(np.isnan(temp_data), 0, 1)

    plt.imsave("temp_overlay.png", rgba_image)
    return "temp_overlay.png"

# **Inicializace aplikace**
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H2("Heat in the City", className="text-center"),
    dcc.Store(id="map-state", data={"zoom": 10, "center": {"lat": 50.0755, "lon": 14.4378}}),

    # **Výběr města a roku**
    dbc.Row([
        dbc.Col(dcc.Dropdown(id="city-dropdown", options=load_cities(), value=DEFAULT_CITY, placeholder="Vyber město")),
        dbc.Col(dcc.Slider(id="year-slider", min=2017, max=2025, step=1, value=2017, marks={year: str(year) for year in range(2017, 2025)}))
    ], className="mb-3"),

    # **Výběr vrstev**
    dcc.Checklist(
        id="layer-selection",
        options=[
            {"label": " Vegetace (zelená)", "value": "ndvi"},
            {"label": " Teplota (červená)", "value": "temp"}
        ],
        value=["ndvi", "temp"],
        inline=True,
        className="mb-3"
    ),

    # **Mapa**
    dbc.Row([
        dbc.Col(dl.Map([
            dl.TileLayer(),
            dl.ImageOverlay(id="ndvi-layer", opacity=0.7),
            dl.ImageOverlay(id="temp-layer", opacity=0.5),
            dl.GeoJSON(id="city-boundary", style={"color": "blue", "weight": 2})
        ], center=[50.0755, 14.4378], zoom=10, id="map-content", style={"height": "75vh"}))
    ])
])

# **Callback pro aktualizaci mapy**
@app.callback(
    [Output("map-content", "center"),
     Output("map-content", "zoom"),
     Output("city-boundary", "data"),
     Output("ndvi-layer", "url"),
     Output("temp-layer", "url")],
    [Input("city-dropdown", "value"),
     Input("year-slider", "value"),
     Input("layer-selection", "value")]
)
def update_map(selected_city, selected_year, selected_layers):
    if not selected_city:
        return dash.no_update

    bbox = load_bbox(selected_city)
    if not bbox:
        return dash.no_update

    # **Vypočet středu města**
    center_lat = (bbox[1] + bbox[3]) / 2
    center_lon = (bbox[0] + bbox[2]) / 2

    # **Načtení NDVI a teploty**
    ndvi_url = None
    temp_url = None

    if "ndvi" in selected_layers:
        ndvi_data = load_tiff_data(selected_city, selected_year, "ndvi", bbox)
        ndvi_url = process_ndvi(ndvi_data)

    if "temp" in selected_layers:
        temp_data = load_tiff_data(selected_city, selected_year, "temp", bbox)
        temp_url = process_temp(temp_data)

    # **Vykreslení polygonu města**
    city_boundary = {
        "type": "Feature",
        "geometry": {"type": "Polygon", "coordinates": [[
            [bbox[0], bbox[1]], [bbox[2], bbox[1]],
            [bbox[2], bbox[3]], [bbox[0], bbox[3]],
            [bbox[0], bbox[1]]
        ]]},
        "properties": {"name": selected_city}
    }

    return [center_lat, center_lon], 12, city_boundary, ndvi_url, temp_url

# **Spuštění aplikace**
if __name__ == "__main__":
    app.run_server(debug=True)
