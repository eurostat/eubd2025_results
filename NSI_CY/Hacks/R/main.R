

# ----------------------------------------------------
# NSI-CY -- MAIN CODE TO RECREATE THE RESULTS PRODUCED 
#           IN THE 2025 EUROPEAN BIG DATA HACKATHON
# ----------------------------------------------------


# ##############################################################################
# [A] PACKAGES
pckgs <- c("data.table", "dplyr", "lubridate", "sf",  "giscoR", "eurostat", "leaflet", "shiny", "shinydashboard", "openxlsx", "tidyr")
if( length(setdiff(pckgs, rownames(installed.packages()))) > 0 ){
  toinstall <- setdiff( pckgs, rownames(installed.packages()))
  cat(paste0("   --> Will be installing the following packages: '",paste(toinstall,collapse="' + '"),"'\n"))
  install.packages(toinstall)
  rm(toinstall)
  cat("\n")
  gc()
}

library(dplyr)
library(data.table)
library(sf)


# ##############################################################################
# [B] PATHS TO BE USED BY R SCRIPTS
curr_path <- paste0(getwd(),"/")    # ----- Make sure the 'curr_path' is pointing to the "eubd2025_results/NSI_CY/Hacks/R/" folder
curr_path_split <- strsplit(curr_path, "/")[[1]]
if(length(curr_path_split)>3){
  curr_path_last4 <- curr_path_split[(length(curr_path_split)-3) : length(curr_path_split)]
  curr_path_last4 <- paste0(curr_path_last4, collapse="/")
}else{
  curr_path_last4 <- curr_path
}
rm(curr_path_split)


if(curr_path_last4 == "eubd2025_results/NSI_CY/Hacks/R"){
  cat(paste0("  GREAT, codes were found at the following folder path - can now run the process:\n  ",curr_path,"\n"))
  
  hack_path <- paste0(dirname(curr_path),"/")
  home_path <- paste0(dirname(hack_path),"/")
  data_path <- paste0(hack_path,"Data/")            # Folder path to save created datasets
  nutm_path <- paste0(data_path,"NUTS_Mapping2124/")# Folder path to manually save NUTS2021 to NUTS2024 mapping file
  mapr_path <- paste0(data_path,"MappingFiles_R/")  # Eurostat Files necessary for analysis 
  cdse_path <- paste0(data_path,"CDSE_Monthly/")    # CAMS Reanalysis (2013-2022) and Forecast (2023-2024) Data, downloaded and brought to MONTHLY, NUTS3 level in Python (showing number of dangerous days due to PM2.5) and saved as .CSV files
  live_path <- paste0(data_path,"CDSE_Monthly_R/")  # CAMS MONTHLY NUTS3 Dangerous Days data converted from .CSV to .RDS 
  corln_path <- paste0(data_path,"CDSE_YearCor_R/") # CAMS MONTHLY NUTS3 Dangerous Days data converted to a single YEARLY NUTS3 dataset, to be correlated against the published Eurostat Premature Deaths dataset
  corrln_reslts <- paste0(data_path,"Results_Corrln/")  # Path to the correlation results
  TAROT_app <- paste0(home_path,"Dashboard_TAROT/")   # Path to the TAROT Rshiny dashboard
  TAROT_dats <- paste0(TAROT_app,"data/")             # Path to the TAROT live data (MONTHLY CAMS Dangerous Days data at NUTS3)
  TAROT_supp <- paste0(TAROT_app,"data_supp/")        # Path to the TAROT supporting data (Correlation Eqn Coeffs, Geometry polygons for the NUTS regions, etc...)
  
  # 00 - Load NDDI index calculation function - used to aggregate NUTS3 Dangerous Days to NUTS0, based on population densities
  source(paste0(curr_path,"00_FunctionsUsed.R"))
  
  
  # 01 - Create all necessary files
  dir.create(mapr_path, showWarnings = FALSE)
  dir.create(live_path, showWarnings = FALSE)
  dir.create(corln_path, showWarnings = FALSE)
  varsToKeep <- unique(c(ls(), "varsToKeep"))
  source(paste0(curr_path,"01_ImportDatasets.R"))
  varstoDelt <- ls()[! ls() %in% varsToKeep]
  rm(list=varstoDelt)
  gc()

  
  # 02 - Run correlation at YEARLY and NUTS) level, between the CAMS Dangerous Days data (PM2.5 > 5 micrograms) and the published Eurostat Premature Deaths dataset
  dir.create(corrln_reslts, showWarnings = FALSE)
  varsToKeep <- unique(c(ls(), "varsToKeep"))
  source(paste0(curr_path,"02_Correlation_Code.R"))
  varstoDelt <- ls()[! ls() %in% varsToKeep]
  rm(list=varstoDelt)
  gc()
  
  
  # 03 - Clean up and create the data necessary for the TAROT dashboard app to run
  dir.create(TAROT_dats, showWarnings = FALSE)
  dir.create(TAROT_supp, showWarnings = FALSE)
  varsToKeep <- unique(c(ls(), "varsToKeep"))
  source(paste0(curr_path,"03_DataForTAROT.R"))
  varstoDelt <- ls()[! ls() %in% varsToKeep]
  rm(list=varstoDelt)
  gc()
  
  
  # Run the TAROT Dashboard app
  shiny::runApp(TAROT_app)
  
  
}else{
  cat("  Please set variable 'curr_path' to the path where code 'main.R' is found, ending in: 'eubd2025_results/NSI_CY/Hacks/R'\n")
  stop(" -- ERROR -- CANNOT RUN ANY OF THE CODES AS 'curr_path' DOES NOT POINT TO THE FOLDER PATH WHERE THIS 'main.R' SCRIPT IS FOUND.")
}

rm(list=ls())
gc()




