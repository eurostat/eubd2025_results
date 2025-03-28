
# TAROT - The AiR Out There

* **STEP 1:** For an easy installation process, run the setup.exe. This will install the required python packages and create the virtual environment for the project using the uv package manager.

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
