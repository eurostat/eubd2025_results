import os
import folium
import geopandas as gpd
from flask import Blueprint, request
from folium.elements import Element
import logging
from .navigation import get_nav_bar_html  # Import the navigation component

tasmi_bp = Blueprint("tasmi_bp", __name__, url_prefix="/tasmi")

@tasmi_bp.route("/", methods=["GET"])
def tasmi():
    country_code = request.args.get("country_code", "LT").upper()
    base_dir = "tasmi"  # Folder containing precomputed TASMI GeoJSON files
    filename = f"{base_dir}/grid_aggregated_{country_code}.geojson"
    logging.debug(f"Checking for file: {filename}")

    if not os.path.exists(filename):
        logging.error(f"File not found: {filename}")
        return f"No precomputed TASMI file. Please run precompute_tasmi.py for that period."

    try:
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
            columns=["grid_id", "mean_tasmi"],
            key_on="feature.properties.grid_id",
            fill_color="YlOrBr",  # Using a yellow-orange-brown scale for TASMI
            fill_opacity=0.7,
            line_opacity=0.0,
            legend_name="Mean TASMI"
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
    except Exception as e:
        logging.error(f"Error loading file {filename}: {e}")
        return f"Error loading file {filename}: {e}"

    form_html = f"""
    <form method="GET" style="text-align:center; margin-bottom:20px;">
      <label for="country_code">Country Code:</label>
      <select id="country_code" name="country_code">
        <option value="LT" {"selected" if country_code == "LT" else ""}>LT</option>
        <option value="PL" {"selected" if country_code == "PL" else ""}>PL</option>
      </select>
      &nbsp;
      <input type="submit" class="button" value="Show TASMI" />
    </form>
    """

    html = f"""
    <html>
      <head>
        <title>Thermal Anomaly Soil Moisture Index Dashboard</title>
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
        <h2 style="text-align:center;">Thermal Anomaly Soil Moisture Index Mean2023/24</h2>
        {form_html}
        <div style="margin: 0 40px;">{map_html}</div>
      </body>
    </html>
    """
    return html