from flask import Blueprint
from .navigation import get_nav_bar_html  # Import the navigation component

docs_bp = Blueprint("docs_bp", __name__, url_prefix="/docs")

@docs_bp.route("/", methods=["GET"])
def docs():
    docs_html = f"""
    <html>
      <head>
        <title>Documentation</title>
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
            max-width: 1000px;
            margin: 40px auto;
            padding-left: 210px;
          }}
          /* Headings and Text */
          h2 {{
            text-align: center;
            margin: 40px 0 20px;
            font-size: 2em;
            color: #34495E;
          }}
          .centered {{
            text-align: center;
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
          table {{
            width: 100%;
            margin: 30px auto;
            border-collapse: collapse;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          }}
          th, td {{
            padding: 12px 15px;
            border: 1px solid #ddd;
          }}
          th {{
            background-color: #58608b;
            color: #fff;
            font-weight: bold;
            text-align: left;
          }}
          tbody tr:nth-child(even) {{
            background-color: #f9f9f9;
          }}
          tbody tr:hover {{
            background-color: #f1f1f1;
          }}
        </style>
      </head>
      <body>
        {get_nav_bar_html()}
        <div class="container">
          <h2>Copernicus Sentinel-3 LST Documentation</h2>
          <p class="centered">
            This application uses data from the Copernicus Sentinel-3 SLSTR instrument, 
            providing Land Surface Temperature (LST) measurements.
            <br/><br/>
            For official Sentinel-3 documentation, see: 
            <a href="https://sentinel.esa.int/web/sentinel/user-guides/sentinel-3-slstr-lst" target="_blank">
              Sentinel-3 SLSTR LST
            </a>.
          </p>
          <h2>Copernicus Sentinel-2 L2A Documentation</h2>
          <p class="centered">
            This application also uses data from the Copernicus Sentinel-2 L2A instrument, 
            providing high-resolution optical imagery.
            <br/><br/>
            For official Sentinel-2 documentation, see: 
            <a href="https://docs.sentinel-hub.com/api/latest/data/sentinel-2-l2a/" target="_blank">
              Sentinel-2 L2A
            </a>.
          </p>
          <h2>Copernicus Sentinel-1 Documentation</h2>
          <p class="centered">
            This application also uses data from the Copernicus Sentinel-1 instrument, 
            providing all-weather, day-and-night radar imagery.
            <br/><br/>
            For official Sentinel-1 documentation, see: 
            <a href="https://sentinels.copernicus.eu/copernicus/sentinel-1" target="_blank">
              Sentinel-1
            </a>.
          </p>
          <h2>Air Temperature Documentation</h2>
          <p class="centered">
            This application also uses air temperature data from the ERA5 reanalysis dataset, 
            providing hourly estimates of a large number of atmospheric, land, and oceanic climate variables.
            <br/><br/>
            For official ERA5 documentation, see: 
            <a href="https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview" target="_blank">
              ERA5 Reanalysis
            </a>.
          </p>
          <h2>Soil Moisture Documentation</h2>
          <p class="centered">
            This application also uses soil moisture data from the Copernicus Climate Data Store, 
            providing satellite-based soil moisture measurements.
            <br/><br/>
            For official soil moisture documentation, see: 
            <a href="https://cds.climate.copernicus.eu/datasets/satellite-soil-moisture?tab=overview" target="_blank">
              Satellite Soil Moisture
            </a>.
          </p>
          <h2>Drought Stress Index (DSI)</h2>
          <p class="centered">
            The Drought Stress Index (DSI) is calculated using the following formula:
            <br/><br/>
            <strong>DSI = (NDVI - NDWI) / Soil Moisture</strong>
            <br/><br/>
            <strong>NDVI (Normalized Difference Vegetation Index)</strong> measures plant greenness.
            <strong>NDWI (Normalized Difference Water Index)</strong> assesses water content in vegetation.
            <strong>Soil Moisture</strong> provides a direct measure of available ground moisture.
          </p>
          <p class="centered">
            <strong>Interpretation:</strong>
            <br/><br/>
            <strong>High DSI values:</strong> Indicate drought stress where vegetation health is declining due to low soil moisture.
            <strong>Low DSI values:</strong> Suggest adequate water availability, ensuring healthy vegetation.
          </p>
          <p class="centered">
            <strong>Significance:</strong>
            <br/><br/>
            Helps in detecting early-stage drought conditions.
            Useful for tracking the impact of climate change on regional water availability.
          </p>
          <p class="centered">
            <strong>Applications in Policy:</strong>
            <br/><br/>
            <strong>Drought Relief & Subsidy Allocation:</strong> Can be used to target government aid to drought-affected farmers.
            <strong>Irrigation Optimization:</strong> Helps prioritize areas where irrigation systems need improvement.
            <strong>Disaster Preparedness:</strong> Supports proactive planning against prolonged drought periods.
          </p>
          <p class="centered">
            <strong>Existing Similar Indices:</strong>
            <br/><br/>
            <strong>Vegetation Health Index (VHI) (Kogan, 1995):</strong> Combines NDVI and temperature to estimate drought stress.
            <strong>Temperature Condition Index (TCI):</strong> Also factors in temperature anomalies.
            <strong>Soil Moisture Stress Index (SMSI):</strong> Uses soil moisture and NDVI.
          </p>
          <p class="centered">
            <strong>Novelty of DSI:</strong>
            <br/><br/>
            This formulation directly incorporates soil moisture as a denominator, unlike VHI and TCI, which focus more on temperature.
            By combining NDVI (vegetation health), NDWI (water availability in vegetation), and actual soil moisture, it uniquely isolates drought impact on crops.
            It aligns with modern drought assessment techniques but is a new combination of indices.
          </p>
          <p class="centered">
            <strong>Scientific Basis & Sources:</strong>
            <br/><br/>
            Kogan, F. N. (1995). Application of Vegetation Index and Brightness Temperature for Drought Detection. Advances in Space Research, 15(11), 91-100. DOI: 10.1016/0273-1177(95)00079-T
            <br/>
            Zhou et al. (2013). Modeling drought-induced maize yield loss based on NDVI and climate data. Agricultural and Forest Meteorology, 174, 10-23. DOI: 10.1016/j.agrformet.2013.01.003
            <br/>
            Houborg et al. (2012). Monitoring drought stress using combined optical and microwave remote sensing. Remote Sensing of Environment, 121, 162-174. DOI: 10.1016/j.rse.2012.01.016
          </p>
          <h2>Thermal-Anomaly Soil Moisture Index (TASMI)</h2>
          <p class="centered">
            The Thermal-Anomaly Soil Moisture Index (TASMI) is calculated using the following formula:
            <br/><br/>
            <strong>TASMI = (LST - T_avg) / Soil Moisture</strong>
            <br/><br/>
            <strong>LST (Land Surface Temperature)</strong> measures surface temperature.
            <strong>T_avg (Average Temperature)</strong> is the monthly average temperature.
            <strong>Soil Moisture</strong> indicates water availability.
          </p>
          <p class="centered">
            <strong>Interpretation:</strong>
            <br/><br/>
            <strong>High TASMI values:</strong> Suggest areas where high temperatures exacerbate soil drying, leading to water stress.
            <strong>Low TASMI values:</strong> Indicate better water retention even under warm conditions.
          </p>
          <p class="centered">
            <strong>Significance:</strong>
            <br/><br/>
            Crucial for identifying heat-induced soil moisture deficits.
            Helps predict crop yield losses due to heat stress.
          </p>
          <p class="centered">
            <strong>Applications in Policy:</strong>
            <br/><br/>
            <strong>Heatwave Preparedness Plans:</strong> Helps policymakers implement early-warning systems for extreme heat.
            <strong>Soil Conservation Programs:</strong> Encourages policies that promote soil retention practices (e.g., mulching, cover cropping).
            <strong>Irrigation Scheduling:</strong> Can inform farmers about the best times for watering crops to counteract heat stress.
          </p>
          <p class="centered">
            <strong>Existing Similar Indices:</strong>
            <br/><br/>
            <strong>Temperature-Vegetation Dryness Index (TVDI) (Sandholt et al., 2002):</strong> Relates LST to NDVI for dryness estimation.
            <strong>Soil Moisture Deficit Index (SMDI) (Narasimhan & Srinivasan, 2005):</strong> Uses soil moisture anomaly.
            <strong>Evaporative Stress Index (ESI):</strong> Integrates LST with moisture availability.
          </p>
          <p class="centered">
            <strong>Novelty of TASMI:</strong>
            <br/><br/>
            This formulation divides temperature anomaly by soil moisture, meaning it captures the impact of heatwaves on soil moisture stress directly.
            Existing indices do not directly normalize LST anomalies using soil moisture, making TASMI a new variant suited for heatwave-drought interactions.
          </p>
          <p class="centered">
            <strong>Scientific Basis & Sources:</strong>
            <br/><br/>
            Sandholt, I., Rasmussen, K., & Andersen, J. (2002). A simple interpretation of LST–NDVI space for assessing surface moisture status. Remote Sensing of Environment, 79(2-3), 213-224. DOI: 10.1016/S0034-4257(01)00274-7
            <br/>
            Narasimhan, B., & Srinivasan, R. (2005). Development and evaluation of Soil Moisture Deficit Index (SMDI) and Evapotranspiration Deficit Index (ETDI) for agriculture drought monitoring. Agricultural and Forest Meteorology, 133(1-4), 69-88. DOI: 10.1016/j.agrformet.2005.07.012
            <br/>
            Anderson, M. C., et al. (2011). Using satellite-derived surface temperature for land–atmosphere coupling diagnostics. Journal of Hydrometeorology, 12(4), 635-653. DOI: 10.1175/JHM-D-10-05015.1
          </p>
          <h2>Space Planter</h2>
            <p class="centered">
            Dataset shows ideal soil moisture and temperature conditions for various crops grown in Poland and Lithuania.
            </p>

          <table>
            <thead>
              <tr>
                <th>Crop</th>
                <th>Planting Month</th>
                <th>Land Surface Temperature (°C)</th>
                <th>Soil Humidity (% VWC)</th>
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
        </div>
      </body>
    </html>
    """
    return docs_html