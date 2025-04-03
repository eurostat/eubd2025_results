import os
import folium
import geopandas as gpd
from flask import Blueprint, request
from folium.elements import Element
from .navigation import get_nav_bar_html  # Import the navigation component

soil_moisture_bp = Blueprint("soil_moisture_bp", __name__, url_prefix="/soil_moisture")



@soil_moisture_bp.route("/", methods=["GET"])
def soil_moisture():
    country_code = request.args.get("country_code", "LT").upper()
    year = request.args.get("year", "2023")
    month = request.args.get("month", "01")
    try:
        month_int = int(month)
    except ValueError:
        month_int = 1
    month_str = f"{month_int:02d}"

    # filename = f"vws/grid_aggregated_{country_code}_{year}_{month_str}.geojson"
    filename = f"moisture_new/grid_soil_moisture_{country_code}_{year}_{month_str}.geojson"

    if not os.path.exists(filename):
        return f"No precomputed soil moisture file for {country_code} for {year}-{month_str}! Please run precompute_moisture.py for that period."

    grid = gpd.read_file(filename)
    map_center = [0, 0]
    if not grid.empty:
        centroid = grid.unary_union.centroid
        map_center = [centroid.y, centroid.x]

    m = folium.Map(location=map_center, zoom_start=7)
    grid_json = grid.to_json()
    folium.Choropleth(
        geo_data=grid_json,
        data=grid,
        columns=["grid_id", "mean_val"],
        key_on="feature.properties.grid_id",
        fill_color="Blues",
        fill_opacity=0.7,
        line_opacity=0.0,
        legend_name="Mean Soil Moisture (% VWC)"
    ).add_to(m)

    legend_css = """
    <style>
      .legend {
        font-size: 16px !important;
        padding-top: 20px;
      }
    </style>
    """
    m.get_root().header.add_child(Element(legend_css))
    map_html = m._repr_html_()

    form_html = f"""
    <form method="GET" style="text-align:center; margin-bottom:20px;">
      <label for="country_code">Country Code:</label>
      <select id="country_code" name="country_code">
        <option value="LT" {"selected" if country_code == "LT" else ""}>LT</option>
        <option value="PL" {"selected" if country_code == "PL" else ""}>PL</option>
      </select>
      &nbsp;
      <label for="year">Year:</label>
      <select id="year" name="year">
        <option value="2023" {"selected" if year == "2023" else ""}>2023</option>
        <option value="2024" {"selected" if year == "2024" else ""}>2024</option>
      </select>
      &nbsp;
      <label for="month">Month:</label>
      <select id="month" name="month">
        {"".join([f'<option value="{str(i).zfill(2)}" {"selected" if month_str == str(i).zfill(2) else ""}>{str(i).zfill(2)}</option>' for i in range(1, 13)])}
      </select>
      &nbsp;
      <input type="submit" class="button" value="Show Soil Moisture" />
    </form>
    """

    html = f"""
    <html>
      <head>
        <title>Soil Moisture Dashboard - {country_code} {year}-{month_str}</title>
        <link rel="stylesheet" type="text/css" href="/static/styles.css">
        <style>
          /* Improved styling for selectors */
          select {{
              font-size: 0.9em;
              padding: 8px;
              min-width: 100px;
              border: 1px solid #ccc;
              border-radius: 4px;
          }}
        </style>
      </head>
      <body>
        {get_nav_bar_html()}
        <h2 style="text-align:center;">Soil Moisture (% VWC) For {country_code} - {year}-{month_str}</h2>
        {form_html}
        <div style="margin: 0 40px;">{map_html}</div>
      </body>
    </html>
    """
    return html
