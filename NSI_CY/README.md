
# TAROT - The AiR Out There

* **STEP 0:** Run the Python code "setup.exe" to install the required packages. This will create a virtual environment and install all the required packages using the uv package manager. You can also run the following command in your terminal:
  ```
  pip install -r requirements.txt
  ```

  Make sure you have the following packages installed:
  * pandas
  * geopandas
  * shapely
  * netCDF4
  * xarray
  * cdsapi
  * zipfile
  * python-dotenv


* **STEP 1:** Copy the `.env.example` file and rename it to `.env`. This file contains the credentials for the Copernicus Atmospheric Data Store (ADS) API. You can obtain your ADS API key by creating an account on the Copernicus Atmospheric Data Store website:'
  ```
  https://ads.atmosphere.copernicus.eu/how-to-api
  ```

  After creating an account, you can find your api key on the url above. Copy and paste this key into the `.env` file. The `.env` file should look like this:
  ```
  CDSAPI_URL=https://ads.atmosphere.copernicus.eu/api
  CDSAPI_KEY=your_api_key
  ```


* **STEP 2:** Run the Python code "main.py" to download the data from Copernicus CAMS. You can choose which years/months to download, as well as which dataset. For further documentation on the specific datasets, please visit:
  ```
  https://ads.atmosphere.copernicus.eu/datasets/cams-europe-air-quality-reanalyses?tab=overview
  ```
  ```
  https://ads.atmosphere.copernicus.eu/datasets/cams-europe-air-quality-forecasts?tab=overview
  ```

  The output data will be a list of NUTS3 regions with values for the Number of Dangerous Days due to high concentrations of PM2.5
  

* **STEP 3:** Navigate to folder "Hacks/R/" and run code main.R:
  * Make sure that your R working directory is the same as the folder where main.R is saved. You can either set this manually by using function `setwd()`, or by double-clicking on the main.R file (where RStudio opens up, ready and initialised with the required working dierectory). 
  * Assuming STEP 1 above was completed successfuly using Python, the downloaded CAMS Dangerous Days .csv can should be found in "Hacks/Data/CDSE_Monthly/" (the repository already contains the .csv files downloaded and used during the Hackathon, to aid users in case issues are encountered at STEP 1 above). 
  * By running main.R the TAROT Dashboard should be produced.
