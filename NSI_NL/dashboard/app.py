#!/usr/bin/env python3
import pandas as pd
import geopandas as gpd
from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
import postgresdb as pgdb
import dash_bootstrap_components as dbc

from dash.exceptions import PreventUpdate

table_name: str = "final"

# CSS imports
dbc_css = [
  "https://www.cbs.nl/content/css/cbs.min.css",
  "https://www.cbs.nl/content/css/cbs-print.min.css",
	"https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css"
]

#
# setup
#
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME, dbc_css])

gdf = pgdb.select_rows(table_name)
gdf = gdf.sort_values(["year", "month"])


# precalculate aggs for fast 
gdf_aggs = gdf.groupby(["nuts_id", "year"])
gdf_aggs = gdf_aggs[["gdp_per_ca", "index", "air_inequi"]].mean().round(2)

#
# Html layout
#

app.layout = html.Div([
  html.Div(
    html.Img(src="/assets/cbs-logo.png", style={"width": "100px", "height": "auto"})
  , className="header"),
  html.Div([html.H1("Air Inequity Dashboard"),], className="page_title"),
  html.Div([
    dcc.Graph(id="choropleth"),
    html.Div([
      html.Div([
        html.H4("Display Country"),
        dcc.RadioItems(
          id="cntr_code",
          options=["NL", "SI"],
          value="NL",
          inline=True
      )], className="filter"),
      html.Div([
        html.H4("Display Year"),
        dcc.Dropdown(
          id="year",
          options=gdf["year"].unique(),
          value=max(gdf["year"]),
          clearable=False,
        )], className="filter"),
    ], className="filters"),

  ], className="map"),
  html.Div([
    html.Div([html.H2("Air Inequity Index (Annual Mean)"), html.H3(id="index_aii")], className="index"),
    html.Div([html.H2("Pollution Index"), html.H3(id="index_pi")], className="index"),
    html.Div([html.H2("GDP per Capita"), html.H3(id="index_gdp")], className="index"),
  ], className="indexes"),

  html.Div([html.H2("Air Inequity Index per Month"), dcc.Graph(id="graph_trend")], className="trend"),
  html.Div([html.H2("Air quality scores"), dcc.Graph(id="graph_box")], className="box"),
  html.Div([html.Button("Download Dataset", id="btn_download"), dcc.Download(id="csv_download")], className="csv"),
  dcc.Store(id="selected_nuts_id")
], className="container")

#
# Callback functions
#
@app.callback(
  Output("selected_nuts_id", "data"),
  Input("year", "value"),
  Input("choropleth", "hoverData")
)
def get_selected_nuts_id(year: int, hoverData: dict) -> list:
  if (not hoverData) or (len(gdf) == 0):
    return None
  return hoverData["points"][0]["location"]

@app.callback(
  Output("index_gdp", "children"),
  Input("selected_nuts_id", "data"),
  Input("year", "value"),
)
def gdp_index(selected_nuts_id: str, year: int):
  if not selected_nuts_id: return "NA"
  return gdf_aggs.at[(selected_nuts_id, year), "gdp_per_ca"]

@app.callback(
  Output("index_pi", "children"),
  Input("selected_nuts_id", "data"),
  Input("year", "value"),
)
def pollution_index(selected_nuts_id: str, year: int):
  if not selected_nuts_id: return "NA"
  return gdf_aggs.at[(selected_nuts_id, year), "index"]

@app.callback(
  Output("index_aii", "children"),
  Input("selected_nuts_id", "data"),
  Input("year", "value"),
)
def air_inequity_index(selected_nuts_id: str, year: int):
  if not selected_nuts_id: return "NA"
  return gdf_aggs.at[(selected_nuts_id, year), "air_inequi"]
  
@app.callback(
  Output("graph_box", "figure"),
  Input("selected_nuts_id", "data"),
  Input("year", "value"),
)
def update_bar(selected_nuts_id: str, year: int):
  pollutant_col_mapping = {
    "o3_quality": "O3",
    "co_quality": "CO",
    "no2_qualit": "NO2",
    "so2_qualit": "SO2",
    "pm25_quali": "PM2.5",
    "hcho_quali": "HCHO",
  }

  gdf_ = gdf.loc[(gdf["nuts_id"] == selected_nuts_id) & (gdf["year"] == year)]

  pollutant_scores = gdf_[pollutant_col_mapping.keys()]
  pollutant_scores = pollutant_scores.rename(pollutant_col_mapping, axis=1)
  pollutant_scores = pollutant_scores.melt(var_name="pollutants", value_name="scores")

  fig = px.box(
    pollutant_scores,
    x="scores",
    y="pollutants",
    labels={"scores": "Scores"},
    range_x=(0, 7),
  )
  fig.update_xaxes(
    tickvals=[1, 2, 3, 4, 5, 6],
    ticktext=["Very Good", "Good", "Medium", "Poor", "Very Poor", "Extremely Poor"]
  )
  return fig

@app.callback(
  Output("graph_trend", "figure"),
  Input("selected_nuts_id", "data"),
  Input("year", "value"),
)
def update_trend_aii(selected_nuts_id: str, year: int):
  gdf_ = gdf.loc[(gdf["nuts_id"] == selected_nuts_id) & (gdf["year"] == year)]

  fig = px.line(
    gdf_,
    x="month",
    y="air_inequi",
    orientation='h',
    markers=True,
    labels={"month": f"Month in {year}", "air_inequi": "Air Inequity Index"},
    range_y=(0, max(gdf["air_inequi"])),
  )
  fig.update_traces(marker=dict(symbol='circle', size=10, color='blue')) 
  return fig

@app.callback(
  Output("choropleth", "figure"),
  Input("cntr_code", "value"),
  Input("year", "value"))
def update_choropleth(cntry_code: str, year: int):
  if cntry_code == "NL":
    start_pos = {"lat": 52.1326, "lon": 5.2913}
  elif cntry_code == "SI":
    start_pos = {"lat": 46.1512, "lon": 14.9955}
  else:
    print(f"Country not found: {cntry_code}")
    exit(1)

  gdf_ = gdf.loc[(gdf["country"] == cntry_code) & (gdf["year"] == year)]
  gdf_ = gdf_.set_index("nuts_id")

  gdf_["air_inequi"] = gdf_.groupby("nuts_id")["air_inequi"].mean().round(2)

  geojson = gdf_.to_geo_dict()
  
  fig = px.choropleth_mapbox(
    gdf_,
    geojson=geojson,
    locations=gdf_.index,
    color="air_inequi",
    mapbox_style="carto-positron",
    color_continuous_scale="RdYlGn_r",
    center=start_pos,
    range_color=(0, max(gdf["air_inequi"])),
    zoom=6,
    labels={"nuts_id": "NUTS-3", "air_inequi": f"Air Inequity {year}"}
  )

  fig.update_geos(fitbounds="locations")
  fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
  return fig

@app.callback(
  Output("csv_download", "data"),
  Input("btn_download", "n_clicks"))
def download_csv(n_clicks):
  download_fn = "download.csv"
  if n_clicks is None:
    raise PreventUpdate
  else:
    global gdf
    csv_content = gdf.to_csv(path_or_buf=None)
    return dict(content=csv_content, filename=download_fn)


if __name__ == '__main__':
  app.run(host='0.0.0.0', port=8050)

