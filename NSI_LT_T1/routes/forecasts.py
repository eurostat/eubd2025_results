import os
from flask import Blueprint, send_from_directory, request
from flask import current_app  # if needed for config
from .navigation import get_nav_bar_html  # Import the navigation component

forecasts_bp = Blueprint("forecasts_bp", __name__, url_prefix="/forecasts")


@forecasts_bp.route("/", methods=["GET"])
def forecasts():
    # Define the folder containing the forecast PNG images
    folder = "forecasts"
    if not os.path.exists(folder):
        return "Forecasts folder not found."

    # List all PNG files (case-insensitive)
    image_files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
    if not image_files:
        return "No PNG images found in the forecasts folder."

    # Build HTML to display each image
    images_html = ""
    for image in image_files:
        # Use a helper route to serve the image
        image_url = f"/forecasts/image/{image}"
        images_html += f'<img src="{image_url}" alt="{image}" style="max-width:90%; margin:10px auto; display:block;" />'

    # Build the full HTML page
    html = f"""
    <html>
      <head>
        <title>Forecasts</title>
        <link rel="stylesheet" type="text/css" href="/static/styles.css">
      </head>
      <body>
        {get_nav_bar_html()}

        <h2 style="text-align:center;">Forecasts</h2>
        <div style="text-align:center;">{images_html}</div>
      </body>
    </html>
    """
    return html

# Helper route to serve image files from the forecasts folder.
@forecasts_bp.route("/image/<filename>")
def forecast_image(filename):
    folder = "forecasts"
    return send_from_directory(folder, filename)
