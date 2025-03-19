
# TAROT - The AiR Out There

* **STEP 0:** Install the following libraries in your favourite python IDE:
  ```
  pip install geopandas cdsapi xarray pyshp
  ```

* **STEP 1:** Run the Python code "main.py" to download the data from Copernicus CAMS. You can choose which years/months to download, as well as which dataset. For further documentation on the specific datasets, please visit:
  ```
  https://ads.atmosphere.copernicus.eu/datasets/cams-europe-air-quality-reanalyses?tab=overview
  ```
  ```
  https://ads.atmosphere.copernicus.eu/datasets/cams-europe-air-quality-forecasts?tab=overview
  ```

  The output data will be a list of NUTS3 regions with values for the Number of Dangerous Days due to high concentrations of PM2.5
  
* **STEP 2:** Navigate to folder "R/00_General/" and run code ImportDatasets.R. Make sure the paths at the top of the code point to the path of the data downloaded from Python in **STEP 1** above. More specifically, verify or ammend appropriately the following paths:
  * general_path
  * reanal_yearly_path
  * reanal_mnthly_path
  * forcst_mnthly_path

* **STEP 3:** In case you want to see the Correlation calculation, navigate to folder "R/01_Correlation/" and run code Correlation_Code.R. This produces the Correlation plot but most importantly also produces the Correlation Equation coefficients (that are used to estimate the Rate of Premature Deaths from the Number of Dangerous Days as identified from the CAMS data)

* **STEP 4:** In order to recreate the TAROT dashboard, first run the cleanDataForApp.R code. Then you are ready to run the app.R code, which creates the TAROT dashboard.

Until the CREODIAS VM is taken offline, the TAROT Dashboard can be found at: http://64.225.141.186:3838/tarot/
