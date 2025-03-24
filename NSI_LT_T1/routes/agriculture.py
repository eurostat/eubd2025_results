import os
import folium
import geopandas as gpd
from flask import Blueprint, request
from folium.elements import Element
from .navigation import get_nav_bar_html  # Import the navigation component


agriculture_bp = Blueprint("agriculture_bp", __name__, url_prefix="/agriculture")

nav_bar_html = """
<nav class="navbar">
  <div class="nav-container">
    <a href="/" class="nav-link">Surface & Air Temperature</a>
    <a href="/soil_moisture" class="nav-link">Soil Moisture</a>
    <a href="/drought_index" class="nav-link">Drought Index</a>
    <a href="/agriculture" class="nav-link">Space Planter</a>
    <a href="/spacial_analysis" class="nav-link">Spacial Analysis</a>

    <a href="/forecasts" class="nav-link">Forecasts</a>
    <a href="/docs" class="nav-link">Docs</a>
  </div>
</nav>
"""

@agriculture_bp.route("/", methods=["GET"])
def agriculture():
    crop = request.args.get("crop", "Potato")
    country_code = request.args.get("country_code", "LT").upper()
    year = request.args.get("year", "2023")
    month = request.args.get("month", "05")

    crop_conditions = {
        "Winter Wheat": {"planting_month": "09-11", "temp_range": (5, 10)},
        "Spring Wheat": {"planting_month": "03-05", "temp_range": (7, 12)},
        "Winter Barley": {"planting_month": "09-11", "temp_range": (5, 10)},
        "Spring Barley": {"planting_month": "03-04", "temp_range": (7, 12)},
        "Maize": {"planting_month": "05-06", "temp_range": (13, 18)},
        "Sunflower": {"planting_month": "05-06", "temp_range": (15, 20)},
        "Potato": {"planting_month": "03-05", "temp_range": (7, 12)},
        "Rapeseed": {"planting_month": "08-09", "temp_range": (5, 10)},
        "Sugar Beet": {"planting_month": "03-05", "temp_range": (7, 12)},
        "Peas": {"planting_month": "03-05", "temp_range": (5, 10)}
    }
    ideal_soil_humidity = {
        "Winter Wheat": "20 – 25",
        "Spring Wheat": "20 – 25",
        "Winter Barley": "20 – 25",
        "Spring Barley": "20 – 25",
        "Maize": "25 – 30",
        "Sunflower": "25 – 30",
        "Potato": "25 – 30",
        "Rapeseed": "20 – 25",
        "Sugar Beet": "20 – 25",
        "Peas": "20 – 25"
    }

    available_crops = {}
    for cp, cond in crop_conditions.items():
        planting_value = cond['planting_month']
        if "-" in planting_value:
            start, end = planting_value.split("-")
            months_list = [f"{m:02d}" for m in range(int(start), int(end) + 1)]
        else:
            months_list = [planting_value]
        avail_months = []
        for m in months_list:
            filename = f"crop_geojsons/grid_{cp.replace(' ', '_')}_{country_code}_{year}_{m}.geojson"
            if os.path.exists(filename):
                avail_months.append(m)
        if avail_months:
            available_crops[cp] = avail_months

    message = ""
    map_html = ""
    month_options_html = ""

    crop_options = "".join([
        (
            lambda sel: f'<option value="{c}" {sel}>{c}</option>'
        )('selected="selected"' if crop == c else '')
        for c in available_crops.keys()
    ])

    if crop and crop in available_crops:
        avail_months = available_crops[crop]
        if month not in avail_months:
            month = avail_months[0]
        month_options_html = "".join([
            "<option value='{m}' {selected}>{m}</option>".format(
                m=m,
                selected='selected="selected"' if month == m else ''
            )
            for m in avail_months
        ])
        filename = f"crop_geojsons/grid_{crop.replace(' ', '_')}_{country_code}_{year}_{month}.geojson"
        if not os.path.exists(filename):
            message = f"<p style='text-align:center;color:red;'>File {filename} not found.</p>"
        else:
            grid = gpd.read_file(filename)
            if not grid.empty:
                centroid = grid.unary_union.centroid
                map_center = [centroid.y, centroid.x]
            else:
                map_center = [0, 0]
            m = folium.Map(location=map_center, zoom_start=7)
            grid_json = grid.to_json()

            def style_function(feature):
                return {
                    'fillColor': '#228B22',
                    'color': 'white',
                    'weight': 1,
                    'fillOpacity': 0.5
                }
            folium.GeoJson(
                data=grid_json,
                style_function=style_function,
                tooltip=folium.GeoJsonTooltip(
                    fields=['grid_id', 'mean_temp', 'mean_moisture'],
                    aliases=['Grid ID:', 'Mean Temp:', 'Mean Moisture:'],
                    localize=True
                )
            ).add_to(m)

            legend_html = f"""
             <div style="position: fixed;
                         bottom: 50px; left: 50px;
                         border:2px solid grey; z-index:9999; font-size:14px;
                         background-color:white;
                         padding: 10px;
                         max-width: 200px;
                         max-height: 100px;
                         overflow: auto;">
               <strong>Crop:</strong> {crop}<br>
               <strong>Year:</strong> {year}<br>
               <strong>Month:</strong> {month}
             </div>
            """
            m.get_root().html.add_child(Element(legend_html))
            map_html = m._repr_html_()
    elif crop:
        message = "<p style='text-align:center;color:red;'>Selected crop not available for the chosen country and year.</p>"

    form_html = f"""
    <form method="GET" style="text-align:center; margin-bottom:20px;">
      <label for="country_code">Country Code:</label>
      <select id="country_code" name="country_code">
        <option value="LT" {"selected" if country_code == "LT" else ""}>LT</option>
        <option value="PL" {"selected" if country_code == "PL" else ""}>PL</option>
      </select>
      &nbsp;
      <label for="crop">Crop:</label>
      <select id="crop" name="crop">
        <option value="">--Choose a crop--</option>
        {crop_options}
      </select>
      &nbsp;
      <label for="year">Year:</label>
      <select id="year" name="year">
        <option value="2023" {"selected" if year == "2023" else ""}>2023</option>
        <option value="2024" {"selected" if year == "2024" else ""}>2024</option>
      </select>
      &nbsp;
      {f'<label for="month">Month:</label><select id="month" name="month">{month_options_html}</select>' if crop and crop in available_crops else ""}
      &nbsp;
      <input type="submit" class="button" value="Show Map" />
    </form>
    """

    if crop and crop in crop_conditions:
        planting = crop_conditions[crop]["planting_month"]
        temp_range = crop_conditions[crop]["temp_range"]
        ideal = ideal_soil_humidity.get(crop, "")
        table_html = f"""
        <table border="1" style="width:80%; margin:20px auto; border-collapse: collapse; text-align:center;">
          <thead>
            <tr style="background-color:#f2f2f2;">
              <th>Crop</th>
              <th>Planting Months</th>
              <th>LST (°C)</th>
              <th>VWC % </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{crop}</td>
              <td>{planting}</td>
              <td>{temp_range[0]} – {temp_range[1]}</td>
              <td>{ideal}</td>
            </tr>
          </tbody>
        </table>
        """
    else:
        table_html = """
        <table border="1" style="width:80%; margin:20px auto; border-collapse: collapse; text-align:center;">
          <thead>
            <tr style="background-color:#f2f2f2;">
              <th>Crop</th>
              <th>Planting Month</th>
              <th>Decent Land Surface Temperature (°C)</th>
              <th>Ideal Soil Humidity (% VWC)</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Winter Wheat</td>
              <td>09-11</td>
              <td>5 – 10</td>
              <td>20 – 25</td>
            </tr>
            <tr>
              <td>Spring Wheat</td>
              <td>03-05</td>
              <td>7 – 12</td>
              <td>20 – 25</td>
            </tr>
            <tr>
              <td>Winter Barley</td>
              <td>09-11</td>
              <td>5 – 10</td>
              <td>20 – 25</td>
            </tr>
            <tr>
              <td>Spring Barley</td>
              <td>03-04</td>
              <td>7 – 12</td>
              <td>20 – 25</td>
            </tr>
            <tr>
              <td>Maize</td>
              <td>05-06</td>
              <td>13 – 18</td>
              <td>25 – 30</td>
            </tr>
            <tr>
              <td>Sunflower</td>
              <td>05-06</td>
              <td>15 – 20</td>
              <td>25 – 30</td>
            </tr>
            <tr>
              <td>Potato</td>
              <td>03-05</td>
              <td>7 – 12</td>
              <td>25 – 30</td>
            </tr>
            <tr>
              <td>Rapeseed</td>
              <td>08-09</td>
              <td>5 – 10</td>
              <td>20 – 25</td>
            </tr>
            <tr>
              <td>Sugar Beet</td>
              <td>03-05</td>
              <td>7 – 12</td>
              <td>20 – 25</td>
            </tr>
            <tr>
              <td>Peas</td>
              <td>03-05</td>
              <td>5 – 10</td>
              <td>20 – 25</td>
            </tr>
          </tbody>
        </table>
        """

    html = f"""
    <html>
      <head>
        <title>Agriculture Dashboard for Crops</title>
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
        <h2 style="text-align:center;">Space Planter</h2>
        {form_html}
        {message}
        {table_html}
        <div style="margin: 0 40px;">{map_html}</div>
      </body>
    </html>
    """
    return html
