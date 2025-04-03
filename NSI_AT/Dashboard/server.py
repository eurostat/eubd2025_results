from flask import Flask, render_template, request, jsonify, jsonify, send_file
from waitress import serve
import geopandas as gpd
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import rasterio as rio
from io import BytesIO
import logging
import seaborn as sns
from dotenv import load_dotenv

# load  environment variables
load_dotenv()
# Selects the environment based on the FLASK_ENV environment variable
# Defaults to development if not set
env = os.getenv('FLASK_ENV', 'development')

# select the configuration class based on the environment
config_class = ProductionConfig if env == 'production' else DevelopmentConfig

app = Flask(__name__)
app.config.from_object(config_class)

# Set up logging configuration at the top of your file
logging.basicConfig(
    level=app.config['LOG_LEVEL'],
    format=app.config['LOG_FORMAT'],
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)

@app.route("/")
@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/get_shapes')
def get_shapes():
    shapes_folder = os.path.join(os.path.dirname(__file__), 'static/geodata/NUTS/2021/')
    geopackages = [os.path.join(shapes_folder, f) for f in os.listdir(shapes_folder) if f.endswith('.gpkg')]
    
    features = []
    for geopackage in geopackages:
        gdf = gpd.read_file(geopackage)
        # Ensure proper CRS for web mapping
        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')
        features.extend(gdf.__geo_interface__['features'])
    
    geojson = {"type": "FeatureCollection", "features": features}
    return jsonify(geojson)

@app.route('/add_tiff/<layer_id>')
def add_tiff(layer_id):
    try:
        # Get date and shapefile id from query parameters
        year = request.args.get('year', '')
        month = request.args.get('month', '').zfill(2)  # Ensure month has leading zero
        region = request.args.get('region', '')
        
        if not all([year, month, region]):
            return jsonify({
                "error": "Missing required parameters (year, month, or region)"
            }), 400
        
        # Search for the TIFF file with layer_id and date pattern
        raster_folder = os.path.join(os.path.dirname(__file__), 'static/geodata/raster')
        pattern = f'^{layer_id}_{region}_{year}_{month}.*\.(tif|tiff)$'
        
        # Ensure raster folder exists
        if not os.path.exists(raster_folder):
            return jsonify({
                "error": f"Raster folder not found: {raster_folder}"
            }), 404
        
        tiff_files = [f for f in os.listdir(raster_folder) if re.match(pattern, f, re.IGNORECASE)]
        
        if tiff_files:
            tiff_url = os.path.join('static/geodata/raster', tiff_files[0])
            return jsonify({
                "tiff_url": tiff_url,
                "filename": tiff_files[0]
            })
        else:
            return jsonify({
                "error": f"TIFF file not found for pattern: {pattern}"
            }), 404
            
    except Exception as e:
        return jsonify({
            "error": f"Server error: {str(e)}"
        }), 500
    
@app.route('/get_corine_shape')
def get_corine_shape():
    try:
        region = request.args.get('region', '')

        # Adjust the path to your CORINE shapefile
        corine_folder = os.path.join(os.path.dirname(__file__), 'static/geodata/corine/')
        pattern = f'^NUTS_corine_{region}_clip_forest_multi.gpkg$'
        matching_files = [f for f in os.listdir(corine_folder) if re.match(pattern, f, re.IGNORECASE)]
        
        if not matching_files:
            return jsonify({"error": "CORINE shapefile not found"}), 404
            
        corine_file = os.path.join(corine_folder, matching_files[0])
        gdf = gpd.read_file(corine_file)
        
        # Ensure proper CRS for web mapping
        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')
                
        geojson = gdf.__geo_interface__
        return jsonify(geojson)

    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route('/get_dataframe')
def get_dataframe():
    try:
        region = request.args.get('region', '')
        logging.info(f"Generating Table for region: {region}")
        years = [str(year) for year in range(2017, 2025)]
        month = request.args.get('month', '')
        indicators = ['ndvi', 'lwc', 'lci', 'evi']
        plot_folder = os.path.join(os.path.dirname(__file__), 'static/geodata/raster/')
        
        data = {}
        for indicator in indicators:
            matching_files = []
            for year in years:
                pattern = f'{indicator}_{region}_{year}_{month}_.*\.(tif|tiff)$'
                year_files = [f for f in os.listdir(plot_folder) if re.match(pattern, f, re.IGNORECASE)]
                matching_files.extend(year_files)
            logging.info(f"Found {len(matching_files)} matching files: {matching_files}")
            
            yearly_means = []
            for filepath in matching_files:
                full_path = os.path.join(plot_folder, filepath)
                with rio.open(full_path) as r:
                    array = r.read(1)
                    mean = np.nanmean(array)
                    yearly_means.append(mean)
            
            data[indicator] = yearly_means

        df = pd.DataFrame(data, index=years)
        logging.info(f"DataFrame contents:\n{df}")
        return df.to_html(classes='data', header=True, index=True)

    except Exception as e:
        return jsonify({"error": f"Error generating table: {str(e)}"}), 500


@app.route('/get_timeline_plot')
def get_timeline_plot():
    try:
        region = request.args.get('region', '')
        logging.info(f"Generating timeline plot for region: {region}")

        years = [str(year) for year in range(2017, 2025)]
        logging.debug(f"Years range: {years}")

        month = request.args.get('month', '')
        logging.debug(f"Month range: {month}")

        indicators = ['ndvi', 'lwc', 'lci', 'evi']
        plot_folder = os.path.join(os.path.dirname(__file__), 'static/geodata/raster/')
        logging.debug(f"Looking for files in: {plot_folder}")
        
        data = {}
        for indicator in indicators:

            matching_files = []
            for year in years:
                pattern = f'{indicator}_{region}_{year}_{month}_.*\.(tif|tiff)$'
                logging.debug(f"Searching with pattern: {pattern}")
                year_files = [f for f in os.listdir(plot_folder) if re.match(pattern, f, re.IGNORECASE)]
                matching_files.extend(year_files)
            logging.info(f"Found {len(matching_files)} matching files: {matching_files}")
            
            yearly_means = []
            for filepath in matching_files:  # Fixed: removed os.path.join here
                full_path = os.path.join(plot_folder, filepath)
                logging.debug(f"Processing file: {full_path}")
                try:
                    with rio.open(full_path) as r:
                        array = r.read(1)
                        mean = np.nanmean(array)
                        yearly_means.append(mean)
                        logging.debug(f"Calculated mean for {filepath}: {mean}")
                except Exception as e:
                    logging.error(f"Error processing file {filepath}: {str(e)}")
                    raise
            
            data[indicator] = yearly_means
            logging.debug(f"Yearly means for {indicator}: {yearly_means}")

        df = pd.DataFrame(data, index=years)


        title_dict = {'04': 'April', '05': 'May', '06': 'June', '07': 'July', '08': 'August', '09': 'September'}
        
        logging.debug(f"DataFrame contents:\n{df}")
    
        sns.set_style("white")
        sns.set_context("notebook", font_scale=1.2)
        plt.figure(figsize=(12, 7), dpi=100)
        ax = plt.gca()
        ax.spines['left'].set_visible(True)
        ax.spines['bottom'].set_visible(True)
        
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f1c40f']
        markers = ['o', 's', '^', 'D']
        
        for idx, column in enumerate(df.columns):
            df[column].plot(ax=ax, marker=markers[idx], markersize=8, 
                          color=colors[idx], linewidth=2, label=column.upper())
        
        # Move legend to top-left with better formatting
        ax.legend(loc='upper left', bbox_to_anchor=(0.0, 1.0), frameon=True, 
                 fancybox=True, shadow=True)
        ax.set_title(f'Indicator timeseries - {title_dict.get(month, "Unknown")}', 
                    size=22, pad=20)
        ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1])
        ax.set_ylabel('Normalized values', fontsize=18, weight='bold')
        ax.set_xticks(range(len(years)))
        ax.set_xticklabels(years)
        ax.set_xlabel('Years', fontsize=18, weight='bold')
        ax.tick_params(axis='both', labelsize=14)
        ax.grid(True, alpha=0.3, linestyle='--')
    
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()
    
        return send_file(buf, mimetype='image/png')

    except Exception as e:
        print(f"Error in get_timeline_plot: {str(e)}")  # Add logging
        return jsonify({"error": f"Error generating plot: {str(e)}"}), 500

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)