import os
import folium
import geopandas as gpd
from flask import Blueprint, request
from folium.elements import Element
from .navigation import get_nav_bar_html  # Import the navigation component

index_bp = Blueprint("index_bp", __name__)

@index_bp.route("/", methods=["GET"])
def index():
    country_code = request.args.get("country_code", "LT").upper()
    year = request.args.get("year", "2023")
    month = request.args.get("month", "01")
    # Get the dataset choice: 'lst' (default) or 'air'
    dataset_choice = request.args.get("dataset", "lst").lower()
    
    try:
        month_int = int(month)
    except ValueError:
        month_int = 1
    month_str = f"{month_int:02d}"

    # Determine the base directory and header based on dataset choice.
    if dataset_choice == "air":
        base_dir = "temperature"
        dataset_label = "Air Temperature"
        header_title = f"Air Temperature (°C) For {country_code} - {year}-{month_str}"
    else:
        base_dir = "lts"
        dataset_label = "LST"
        header_title = f"Land Surface Temperature (°C) For {country_code} - {year}-{month_str}"

    # Construct the filename using the chosen directory.
    filename = f"{base_dir}/grid_aggregated_{country_code}_{year}_{month_str}.geojson"
    if not os.path.exists(filename):
        return (f"No precomputed {dataset_label} file for {country_code} for {year}-{month_str}! "
                f"Please run precompute.py for that period.")

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
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.0,
        legend_name=f"Mean {dataset_label} (°C)"
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

    # Build a dropdown form for dataset choice.
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
      <label for="dataset">Dataset:</label>
      <select id="dataset" name="dataset">
        <option value="lst" {"selected" if dataset_choice == "lst" else ""}>LST</option>
        <option value="air" {"selected" if dataset_choice == "air" else ""}>Air Temperature</option>
      </select>
      &nbsp;
      <input type="submit" id="submit-button" class="button" value="Show {dataset_label}" />
    </form>
    """

    html = f"""
    <html>
      <head>
        <title>Temperature Dashboard - {country_code} {year}-{month_str}</title>
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
        <h2 style="text-align:center;">{header_title}</h2>
        {form_html}
        <div style="margin: 0 40px;">{map_html}</div>
        <script>
          // Update button text when the dataset type is changed
          document.getElementById("dataset").addEventListener("change", function() {{
            var selectedText = this.options[this.selectedIndex].text;
            document.getElementById("submit-button").value = "Show " + selectedText;
          }});
        </script>
      </body>
    </html>
    """
    return html
