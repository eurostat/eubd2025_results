import os
from flask import Blueprint, send_from_directory, render_template_string
from .navigation import get_nav_bar_html  # Import the navigation component

spacial_analysis_bp = Blueprint("spacial_analysis_bp", __name__, url_prefix="/spacial_analysis")

@spacial_analysis_bp.route("/", methods=["GET"])
def spacial_analysis():
    folder = "spacial_analysis"
    if not os.path.exists(folder):
        return "Spacial Analysis folder not found."

    # List all PNG files (case-insensitive)
    image_files = [f for f in os.listdir(folder) if f.lower().endswith(".png")]
    if not image_files:
        return "No PNG images found in the spacial_analysis folder."

    # Build HTML to display each image in a responsive container
    images_html = ""
    for image in image_files:
        image_url = f"/spacial_analysis/image/{image}"
        images_html += f'<img src="{image_url}" alt="{image}" />'

    # Add a link to the documentation
    documentation_url = "/spacial_analysis/documentation"
    documentation_link = f'<p class="centered"><a href="{documentation_url}">View Documentation</a></p>'

    # Read the table HTML from the file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    table_file_path = os.path.join(base_dir, "../spacial_analysis/table.html")
    if not os.path.exists(table_file_path):
        return "Table file not found."

    with open(table_file_path, "r") as file:
        table_html = file.read()

    # Build the full HTML page with a collapsible section for the table and documentation under it
    html = f"""
    <html>
      <head>
        <title>Spacial Analysis</title>
        <link rel="stylesheet" type="text/css" href="/static/styles.css">
        <style>
          /* Global Styles */
          body {{
            background-color: #F7F9FB;
            font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
            color: #2C3E50;
            margin: 0;
            padding: 0;
          }}
          /* Container for page content */
          .container {{
            max-width: 1200px;
            margin: 40px auto;
            padding-left: 210px;
          }}
          /* Headings and centered text */
          h2, .centered {{
            padding-top: 20px;
            text-align: center;
          }}
          .centered {{
            margin: 20px auto;
            max-width: 800px;
            line-height: 1.8;
          }}
          .centered a {{
            color: #2980B9;
            text-decoration: none;
            font-weight: bold;
          }}
          .centered a:hover {{
            text-decoration: underline;
          }}
          /* Table Styling */
          .table-container {{
            width: 100%;
            margin: 20px auto;
            overflow-x: auto; /* Enable horizontal scrolling */
          }}
          table {{
            width: 100%;
            min-width: 800px; /* Adjust if needed so table doesn't shrink too much */
            border-collapse: collapse;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          }}
          th, td {{
            padding: 12px 15px;
            border: 1px solid #ddd;
            text-align: left;
            font-size: 0.9em;
          }}
          th {{
            background-color: #58608b;
            color: #fff;
          }}
          tbody tr:nth-child(even) {{
            background-color: #f9f9f9;
          }}
          tbody tr:hover {{
            background-color: #f1f1f1;
          }}
          /* Image Styling */
          .image-container {{
            text-align: center;
            margin-top: 40px;
          }}
          .image-container img {{
            max-width: 100%;
            height: auto;
            margin: 20px auto;
            display: block;
          }}
          /* Collapsible Section */
          .collapsible {{
            background-color: #57608B;
            color: #fff;
            cursor: pointer;
            padding: 10px;
            width: 100%;
            border: none;
            text-align: left;
            outline: none;
            font-size: 1.1em;
            margin-top: 20px;
          }}
          .active, .collapsible:hover {{
            background-color: #2C3E50;
          }}
          .content {{
            padding: 0 18px;
            display: none;
            overflow-x: auto; /* Allow horizontal scrolling within the content */
            overflow-y: auto; /* Allow vertical scrolling if needed */
            background-color: #f1f1f1;
            margin-bottom: 20px;
          }}

          /* Responsive Design for Mobile */
          @media (max-width: 768px) {{
            /* Ensure the navigation bar does not overlay content */
            nav.navbar {{
              position: fixed;
              top: 0;
              left: 0;
              width: 100%;
              z-index: 1000;
            }}
            /* Offset container to account for fixed nav bar */
            .container {{
              margin-top: 80px;
            }}
          }}
        </style>
      </head>
      <body>
        {get_nav_bar_html()}
        <h2 style="text-align:center;">Spacial Analysis</h2>
        <div class="container">
          <button type="button" class="collapsible">Show/Hide Data Table</button>
          <div class="content table-container">
            {table_html}
          </div>
          {documentation_link}
          <div class="image-container">
            {images_html}
          </div>
        </div>
        <script>
          var coll = document.getElementsByClassName("collapsible");
          for (var i = 0; i < coll.length; i++) {{
            coll[i].addEventListener("click", function() {{
              this.classList.toggle("active");
              var content = this.nextElementSibling;
              if (content.style.display === "block") {{
                content.style.display = "none";
              }} else {{
                content.style.display = "block";
              }}
            }});
          }}
        </script>
      </body>
    </html>
    """
    return html

# Helper route to serve image files from the spacial_analysis folder.
@spacial_analysis_bp.route("/image/<filename>")
def spacial_analysis_image(filename):
    folder = "spacial_analysis"
    return send_from_directory(folder, filename)

# Route to serve the documentation from Methods.html
@spacial_analysis_bp.route("/documentation", methods=["GET"])
def spacial_analysis_documentation():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    methods_file_path = os.path.join(base_dir, "../spacial_analysis/Methods.html")

    if not os.path.exists(methods_file_path):
        return "Documentation not found."

    with open(methods_file_path, "r") as file:
        methods_html = file.read()
        safe_html = "{% raw %}" + methods_html + "{% endraw %}"

    return render_template_string(safe_html)
