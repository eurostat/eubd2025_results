
library(dplyr)
library(data.table)
library(sf)


general_path <- "~/R/00_General/"
corr_path <- "~/R/01_Correlation/CorrReslts/"
rdata_map <- paste0(general_path,"rdata/mappings/")
CopLive_M <- paste0(general_path,"rdata/cams_M13to24/")
dir.create(appd_path <- "~/R/02_AppTAROT/data/", showWarnings = FALSE, recursive = TRUE)
dir.create(appdsupp_path <- "~/R/02_AppTAROT/data_supp/", showWarnings = FALSE, recursive = TRUE)
source(paste0(general_path,"FunctionsUsed.R"))


# #################################################################################
# [A] Import Created .RDS Datasets
nuts3_shapes <- readRDS(paste0(rdata_map,"NUTS3_Shapefile.rds"))  # Eurostat - NUTS3 mapping from Eurostat
popn_dt <- readRDS(paste0(rdata_map,"Popn_NUTS3_ByAge.rds"))      # Eurostat - Population at NUTS regions from Eurostat
corr_eqn <- readRDS(paste0(corr_path,"CorrExpEqnCoeffs_PMg5.rds"))# Derived - Correlation Equation Coefficients
saveRDS(corr_eqn, paste0(appdsupp_path,"CorrExpEqnCoeffs_PMg5.rds")) 


# #################################################################################
# [B] PREPARE FILES FOR CORRELATION
eu_country_codes <- c("AT", "BE", "BG", "CY", "CZ",
                      "DE", "DK", "EE", "ES", "FI",
                      "FR", "EL", "HR", "HU", "IE",
                      "IT", "LT", "LU", "LV", "MT",
                      "NL", "PL", "PT", "RO", "SE",
                      "SI", "SK")

nuts3_shapes_geom <- unique(select(nuts3_shapes, c("CNTR_CODE","geo","geometry")))
nuts3_shapes$geometry <- NULL # remove geometry from NUTS3 mapping file (unnecessary for Correlation)
nuts3_shapes <- as.data.table(nuts3_shapes)


# #################################################################################
# [C] JOIN FILES FOR CORRELATION
dt_geo <- left_join(popn_dt, nuts3_shapes, by = c("geo"))
dt_geo <- dt_geo[CNTR_CODE %in% eu_country_codes]
# dt_geo <- dt_geo[!is.na(area_km2)]
dt_geo_nuts3 <- unique(dt_geo[LEVL_CODE==3, 
                              c("TIME_PERIOD","geo","geo_name","area_km2","population"), with=F])
dt_geo_names <- unique(dt_geo[, c("geo","geo_name"), with=F])
dt_CNTR_names <- unique(dt_geo[LEVL_CODE==0, c("geo","geo_name"), with=F])
setnames(dt_CNTR_names, c("geo","geo_name"), c("CNTR_CODE","CNTR_NAME"))
saveRDS(dt_CNTR_names, paste0(appdsupp_path,"NUTS0_geonames_map.rds")) 


# #################################################################################
# [C] IMPORT COPERNICUS DATA
full_paths <- list.files(CopLive_M, full.names = TRUE)
myears <- c()
for(f in 1:length(full_paths)){
  myear <- substr(full_paths[f], nchar(full_paths[f])-10, nchar(full_paths[f])-4)
  dtfile <- readRDS(full_paths[f])
  dtfile <- rename(dtfile,"geo"="NUTS_ID")

  dtlist <- list()
  for(r in 0:3){
    copern_inn <- mutate(dtfile, LEVEL_AGGR=substr(geo, 1, 2+r))
    tper <- unique(copern_inn$TIME_PERIOD)
    # Use population of year this current month belongs to, to calculate population density and then NDDI
    copern_inn <- mutate(copern_inn, TIME_PERIOD = as.Date(paste0(lubridate::year(TIME_PERIOD),"-01-01")))
    copern_inn <- nd2i_fn(copern_nuts3=copern_inn, dt_geo_nuts3)
    copern_inn <- unique(mutate(copern_inn, TIME_PERIOD = as.Date(tper), LEVL_CODE=r))
    dtlist <- c(dtlist, list(copern_inn))
    rm(copern_inn, tper, r)
  }
  copern <- unique(arrange(do.call(bind_rows, dtlist), TIME_PERIOD, LEVL_CODE))
  copern <- mutate(copern, EstPremDeatsRate = round(exp((corr_eqn$s * ND2I_AvgNrDDays) + corr_eqn$i) - corr_eqn$b))
  copern <- mutate(copern, EstPremDeatsNmbr = round(EstPremDeatsRate*population_CNTR/100000))
  copern <- mutate(copern, my = myear)
  copern <- rename(copern,"geo"="LEVEL_AGGR")
  copern <- unique(left_join(copern, dt_geo_names, by=c("geo")))
  copern$geo_name <- ifelse(is.na(copern$geo_name), as.character(copern$geo), copern$geo_name)
  copern <- unique(filter(left_join(nuts3_shapes_geom, copern, by=c("geo")), !is.na(LEVL_CODE)))
  # copern <- unique(filter(copern, !is.na(population_CNTR), !is.na(ND2I_AvgNrDDays), !is.na(geometry)))
  
  saveRDS(copern, paste0(appd_path,"Estimate_PremDths_",myear,".rds"))
  myears <- c(myears, myear)
  rm(dtfile, dtlist, copern, f, myear)
}
saveRDS(myears, paste0(appdsupp_path,"PeriodsInFilter.rds"))
rm(full_paths, dtlist, dt_geo_inn, copern, myears)
gc()

