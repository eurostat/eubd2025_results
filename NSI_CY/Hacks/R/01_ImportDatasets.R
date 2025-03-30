
  
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
saveRDS(popn_dt, paste0(mapr_path,"Popn_NUTS3_ByAge.rds"))
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
saveRDS(pdeaths_dt_all, paste0(mapr_path,"PremDeaths_PM25.rds"))
rm(pdeaths_dname, pdeaths_info, pdeaths_dt, pdeaths_dt_nr, pdeaths_dt_rt, pdeaths_dt_all)
gc()


#   (iii) NUTS3 shapefiles
# nuts3_publication_years <- c("2003", "2006", "2010", "2013", "2016", "2021")
nuts3_publication_years <- c("2021")  
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
# class(nuts3_shapes)
# sf::st_write(nuts3_shapes, paste0(rdata_path,"NUTS3_Shapefile.gpkg"), delete_dsn = TRUE) # delete_dsn = TRUE overwrites the file.
# sf::st_write(nuts3_shapes, paste0(rdata_path,"NUTS3_Shapefile.shp"), delete_dsn = TRUE) # delete_dsn = TRUE overwrites the file.
saveRDS(nuts3_shapes, paste0(mapr_path,"NUTS3_Shapefile.rds"))
rm(nuts3_list, nuts3_publication_years, nuts3_shapes)
gc()


#   (iv) Copernicus MONHTLY CAMS Data (ReAnalysis Data for Years 2013-2022 and Forecast Data for Years 2023-2024) 
#         Downloaded using Python and show Dangerous Days (PM2.5 > 5) per NUTS3 region
s_copern_yearly <- list()
s_years <- 2012 + seq(12)
s_months <- seq(12)
s_months_lbl <- sprintf(paste0("%0", 2, "d"), s_months)
for(y in 1:length(s_years)){
  cat("--> Year: ",s_years[y],"\n")
  
  # --- Copernicus MONHTLY CAMS Data (ReAnalysis Data for Years 2013-2022 and Forecast Data for Years 2023-2024) 
  #     Downloaded using Python and they show Dangerous Days (PM2.5 > 5) per NUTS3 region
  smyear <- list()
  s_myears_lbl <- c()
  s_myears_lbl <- c(s_myears_lbl, paste0(s_years[y],"_",s_months_lbl) )
  for(s in 1:length(s_myears_lbl)){
    smyear_lbl <- s_myears_lbl[s]
    cat("MonthYear: ",smyear_lbl,"\n")
    copern_inner <- read.csv(paste0(cdse_path,"summary_stats_",smyear_lbl,".csv"))
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
    saveRDS(copern_inner, paste0(live_path,"NDDI_DDays_PMg5_",smyear_lbl,".rds"))
    smyear <- c(smyear, list(copern_inner))
    rm(s,smyear_lbl,copern_inner, tper)
  }
  
  
  # --- Copernicus YEARLY CAMS Data at NUTS3 level. 
  #     Aggregated from the MONTHLY, NUTS3 Copernicus data above
  copern_yearly <- rbindlist(smyear)
  copern_yearly[, TIME_PERIOD := as.Date(paste0(lubridate::year(TIME_PERIOD),"-01-01"))]
  nc <- copy(names(copern_yearly))
  copern_yearly <- copern_yearly[, .(EXCEED_mean = sum(EXCEED_mean,na.rm=T)), by=.(NUTS_ID, TIME_PERIOD)]
  copern_yearly <- copern_yearly[, c(nc), with=F]
  s_copern_yearly <- c(s_copern_yearly, list(copern_yearly))
  rm(y, s_myears_lbl, copern_yearly, nc, smyear)
}

# Save YEARLY CAMS Data at NUTS3 level as a single dataset 
copern_yearly <- rbindlist(s_copern_yearly)
saveRDS(copern_yearly, paste0(corln_path,"NDDI_DDays_PMg5_YEARLY.rds"))
rm(s_years, s_months, s_months_lbl, copern_yearly)
gc()


