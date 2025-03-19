

library(dplyr)
library(data.table)
library(sf)
# library(eurostat)

general_path <- "~/R/00_General/"
reanal_yearly_path <- "~/R/Hacks/Correlation_tests/summary_stats/"  #  CAMS Reanalysis Data downloaded and brought to YEARLY, NUTS3 level in Python (showing number of dangerous days due to PM2.5)
reanal_mnthly_path <- "~/R/Hacks/Live_data_older/summary_stats/"    #  CAMS Reanalysis Data downloaded and brought to MONHTLY, NUTS3 level in Python (showing number of dangerous days due to PM2.5)
forcst_mnthly_path <- "~/R/Hacks/Live_data/summary_stats/"          #  CAMS Forecast Data downloaded and brought to MONTHLY, NUTS3 level in Python (showing number of dangerous days due to PM2.5)
dir.create(rdata_map <- paste0(general_path,"rdata/mappings/"), showWarnings = FALSE, recursive = TRUE)
dir.create(CopRean_Y <- paste0(general_path,"rdata/cams_Y13to22/"), showWarnings = FALSE)
dir.create(CopLive_M <- paste0(general_path,"rdata/cams_M13to24/"), showWarnings = FALSE)

  
# #################################################################################
# [A] Download Eurostat data
toc <- eurostat::get_eurostat_toc()  # table of contents


#   (i) Population in NUTS 3 by age groups - 1 JAN 2025 --> https://ec.europa.eu/eurostat/databrowser/view/demo_r_pjanaggr3/default/table?lang=en
popn_dname <- "demo_r_pjanaggr3"
popn_info  <- toc[toc$code == popn_dname, ]
popn_dt    <- eurostat::get_eurostat(popn_dname)
popn_label <- eurostat::label_eurostat(popn_dt, code = "geo", fix_duplicated = TRUE) %>%
  rename( c("geo_name"="geo", "geo"="geo_code") ) %>%
  select( c("geo","geo_name") ) %>%
  unique()
popn_dt <- left_join(popn_dt, popn_label, by="geo") %>%
  rename( c("population"="values") ) %>%
  filter(age=="TOTAL", sex=="T")
popn_dt <- as.data.table(popn_dt)
popn_dt[is.na(geo_name), geo_name := geo]
saveRDS(popn_dt, paste0(rdata_map,"Popn_NUTS3_ByAge.rds"))
rm(popn_dname, popn_info, popn_label, popn_dt)
gc()


#   (ii) Premature deaths due to exposure to fine particulate matter (PM2.5) --> https://ec.europa.eu/eurostat/databrowser/view/sdg_11_52/default/table?lang=en&category=sdg.sdg_03
pdeaths_dname <- "sdg_11_52"
pdeaths_info  <- toc[toc$code == pdeaths_dname, ] 
pdeaths_dt    <- eurostat::get_eurostat(pdeaths_dname) 
pdeaths_dt_nr <- filter(pdeaths_dt, unit=="NR") %>%
  select( c("geo","TIME_PERIOD","values") ) %>%
  rename("Popln_PM25_Numbr"="values") %>%
  unique()
pdeaths_dt_rt <- filter(pdeaths_dt, unit=="RT") %>%
  select( c("geo","TIME_PERIOD","values") ) %>%
  rename("Popln_PM25_Rate100k"="values") %>%
  unique()
pdeaths_dt_all <- left_join(pdeaths_dt_nr, pdeaths_dt_rt, by = c("geo","TIME_PERIOD"))
pdeaths_dt_all <- as.data.table(pdeaths_dt_all)
saveRDS(pdeaths_dt_all, paste0(rdata_map,"PremDeaths_PM25.rds"))
rm(pdeaths_dname, pdeaths_info, pdeaths_dt, pdeaths_dt_nr, pdeaths_dt_rt, pdeaths_dt_all)
gc()


#   (iii) NUTS3 shapefiles
# nuts3_publication_years <- c("2003", "2006", "2010", "2013", "2016", "2021")
nuts3_publication_years <- c("2021")  # Found out the hard way that "demo_r_pjanaggr3" 
                                      # and "sdg_11_52" only use 2021 NUTS3 regions, even 
                                      # though for the years before 2021
nuts3_list <- list()
for(y in 1:length(nuts3_publication_years)){
  year_inner <- nuts3_publication_years[y]
  nuts3_inner  <- eurostat::get_eurostat_geospatial(resolution = "01", year=year_inner) # Resolution 1:1million (Lowest possible)
  nuts3_inner <- dplyr::mutate(nuts3_inner, year_doc=year_inner)
  
  nuts3_list <- c(nuts3_list, list(nuts3_inner))
  rm(year_inner, nuts3_inner, y)
}
nuts3_shapes <- do.call(bind_rows, nuts3_list)
nuts3_shapes <- dplyr::mutate(nuts3_shapes, area_m2  = as.numeric(sf::st_area(geometry)))
nuts3_shapes <- dplyr::mutate(nuts3_shapes, area_km2 = as.numeric(area_m2 / 1000000))
# The following is performed only in case we want to map NUTS3 regions of "demo_r_pjanaggr3" 
#   and "sdg_11_52" by using the version of the NUTS3 mapping file available at the time. As
#   mentioned above, these datasets are mapped using the latest (2021) NUTS3 region mapping,
#   even though they display results for year before 2021.
#   (e.g.) Population results of year 2016 are published using the 2021 NUTS3 regions in "demo_r_pjanaggr3" 
#           (even if that version of the NUTS3 file was not available at the time!)
if(length(nuts3_publication_years) > 1){
  current_year <- lubridate::year(Sys.Date())
  years_nuts3 <- as.numeric(nuts3_publication_years)
  years_from  <- c(2004, 2008, 2012, 2015, 2018, 2021)
  years_until <- c(2007, 2011, 2014, 2017, 2020, current_year)
  years_diff <- years_until - years_from + 1
  years_diff[length(years_diff)] <- years_diff[length(years_diff)] + 1
  nuts3_years_list <- list()
  for(d in 1:length(years_diff)){
    pub_year <- years_nuts3[d]
    frm_years <- years_from[d]
    nbr_years <- years_diff[d]
    pub_years <- rep(years_nuts3[d], nbr_years)
    ppn_years <- frm_years + seq(nbr_years) - 1
    pub_ppn_df <- data.frame(
      year_doc = as.character(pub_years),
      TIME_PERIOD = as.Date(paste0(ppn_years,"-01-01"))
    )
    nuts3_years_list <- c(list(pub_ppn_df), nuts3_years_list)
    rm(d, pub_year, frm_years, nbr_years, pub_years, ppn_years, pub_ppn_df)
  }
  nuts3_years <- arrange(do.call(bind_rows, nuts3_years_list), TIME_PERIOD) 
  nuts3_shapes <- left_join(nuts3_shapes, nuts3_years, by = c("year_doc"),relationship = "many-to-many")
  rm(current_year, years_nuts3, years_from, years_until, years_diff, nuts3_years_list, nuts3_years)
}
# class(nuts3_shapes)
# sf::st_write(nuts3_shapes, paste0(rdata_path,"NUTS3_Shapefile.gpkg"), delete_dsn = TRUE) # delete_dsn = TRUE overwrites the file.
# sf::st_write(nuts3_shapes, paste0(rdata_path,"NUTS3_Shapefile.shp"), delete_dsn = TRUE) # delete_dsn = TRUE overwrites the file.
saveRDS(nuts3_shapes, paste0(rdata_map,"NUTS3_Shapefile.rds"))
rm(nuts3_list, nuts3_publication_years, nuts3_shapes)
gc()


#   (iv) Copernicus YEARLY ReAnalysis CAMS Data (for Years 2013-2022)
#         Downloaded using Python and show Dangerous Days (PM2.5 > 5) per NUTS3 region
s_years <- 2012 + seq(10)
s_list <- list()
for(s in 1:length(s_years)){
  syear <- s_years[s]
  copern_inner <- read.csv(paste0(reanal_yearly_path,"summary_stats_",syear,".csv"))
  copern_inner <- dplyr::mutate(copern_inner,TIME_PERIOD=as.Date(paste0(syear,"-01-01")))
  s_list <- c(s_list, list(copern_inner))
  cat("Year: ",syear,"\n")
  rm(s,syear,copern_inner)
}
copern_nuts3 <- arrange(do.call(bind_rows, s_list), TIME_PERIOD)
copern_nuts3 <- as.data.table(copern_nuts3)
saveRDS(copern_nuts3, paste0(CopRean_Y,"Copernicus_NUTS3_DDays_PMg5.rds"))
rm(s_years, s_list, copern_nuts3)
gc()


#   (v) Copernicus MONTHLY ReAnalysis CAMS Data (for Years 2013-2022)
#         Downloaded using Python and show Dangerous Days (PM2.5 > 5) per NUTS3 region
s_years <- 2012 + seq(10)
s_months <- seq(12)
s_months_lbl <- sprintf(paste0("%0", 2, "d"), s_months)
s_myears <- c()
s_myears_lbl <- c()
for(y in 1:length(s_years)){
  s_myears <- c(s_myears, paste0(s_years[y],"_",s_months) )
  s_myears_lbl <- c(s_myears_lbl, paste0(s_years[y],"_",s_months_lbl) )
  rm(y)
}
for(s in 1:length(s_myears_lbl)){
  # smyear <- s_myears[s]
  smyear_lbl <- s_myears_lbl[s]
  copern_inner <- read.csv(paste0(reanal_mnthly_path,"summary_stats_",smyear_lbl,".csv"))
  copern_inner <- dplyr::mutate(copern_inner,TIME_PERIOD=as.Date(paste0(substr(smyear_lbl,1,4),"-",substr(smyear_lbl,6,7),"-01")))
  
  # Correct Dangerous Days from Copernicus (EXCEED_mean) due to one extra day being included in the FORECAST data (first day of the next month)
  tper <- unique(copern_inner$TIME_PERIOD)
  if(lubridate::year(tper) > 2022){
    factor <- lubridate::days_in_month(tper)[[1]]
    copern_inner <- mutate(copern_inner, EXCEED_mean=(factor/(factor+1))*EXCEED_mean)
    if(max(copern_inner$EXCEED_mean)>factor){
      print(paste0("ERROR - Dataset: ",full_paths[f]))
    }
    rm(factor)
  }
  copern_inner <- as.data.table(copern_inner)
  saveRDS(copern_inner, paste0(CopLive_M,"NDDI_DDays_PMg5_",smyear_lbl,".rds"))
  cat("MonthYear: ",smyear_lbl,"\n")
  rm(s,smyear_lbl,copern_inner, tper)
}
rm(s_years, s_months, s_months_lbl, s_myears, s_myears_lbl)
gc()


#   (vi) Copernicus MONHTLY Forecast CAMS Data (for Years 2023-2024) 
#         Downloaded using Python and show Dangerous Days (PM2.5 > 5) per NUTS3 region
s_years <- c(2023, 2024)
s_months <- seq(12)
s_months_lbl <- sprintf(paste0("%0", 2, "d"), s_months)
s_myears <- c()
s_myears_lbl <- c()
for(y in 1:length(s_years)){
  s_myears <- c(s_myears, paste0(s_years[y],"_",s_months) )
  s_myears_lbl <- c(s_myears_lbl, paste0(s_years[y],"_",s_months_lbl) )
  rm(y)
}
for(s in 1:length(s_myears_lbl)){
  smyear <- s_myears[s]
  smyear_lbl <- s_myears_lbl[s]
  copern_inner <- read.csv(paste0(forcst_mnthly_path,"summary_stats_",smyear,".csv"))
  copern_inner <- dplyr::mutate(copern_inner,TIME_PERIOD=as.Date(paste0(substr(smyear_lbl,1,4),"-",substr(smyear_lbl,6,7),"-01")))
  
  # Correct Dangerous Days from Copernicus (EXCEED_mean) due to one extra day being included in the FORECAST data (first day of the next month)
  tper <- unique(copern_inner$TIME_PERIOD)
  if(lubridate::year(tper) > 2022){
    factor <- lubridate::days_in_month(tper)[[1]]
    copern_inner <- mutate(copern_inner, EXCEED_mean=(factor/(factor+1))*EXCEED_mean)
    if(max(copern_inner$EXCEED_mean)>factor){
      print(paste0("ERROR - Dataset: ",full_paths[f]))
    }
    rm(factor)
  }
  copern_inner <- as.data.table(copern_inner)
  saveRDS(copern_inner, paste0(CopLive_M,"NDDI_DDays_PMg5_",smyear_lbl,".rds"))
  cat("MonthYear: ",smyear_lbl,"\n")
  rm(s,smyear_lbl,copern_inner, tper)
}
rm(s_years, s_months, s_months_lbl, s_myears, s_myears_lbl)
gc()



