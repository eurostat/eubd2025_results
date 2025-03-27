# FUNCTION TO CALCULATE THE ND2I index, that calculates a weighted average number of 
#   dangerous days at the NUTS0 level (using NUTS3 level Copernicus Dangerous Days).
# 
# copern_nuts3 must contain columns c("TIME_PERIOD","geo","EXCEED_mean","LEVEL_AGGR")
# dt_geo_nuts3 must contain columns c("TIME_PERIOD","geo","geo_name","area_km2","population")
nd2i_fn <- function(copern_nuts3, dt_geo_nuts3){
  
  copern_nuts3 <- left_join(dt_geo_nuts3, copern_nuts3, by = c("geo","TIME_PERIOD"))
  copern_nuts3 <- filter(copern_nuts3, !is.na(EXCEED_mean) )
  copern_nuts3 <- filter(copern_nuts3, !is.na(population) )
  copern_nuts3 <- dplyr::mutate(copern_nuts3, 
                                popn_density = population/area_km2,
                                popn_density_mexc = popn_density * EXCEED_mean)
  
  # Elevate to NUTS0 using ND2I
  copern_nuts3_AGGR <- copern_nuts3 %>%
    group_by(LEVEL_AGGR, TIME_PERIOD) %>%
    mutate(area_km2_CNTR = sum(area_km2), 
           population_CNTR = sum(population),
           popn_density_CNTR = sum(popn_density),
           popn_density_mexc_CNTR = sum(popn_density_mexc)
    ) %>%
    ungroup()
  copern_nuts3_AGGR <- mutate(copern_nuts3_AGGR, ND2I_AvgNrDDays = popn_density_mexc_CNTR/popn_density_CNTR)
  copern_nuts3_AGGR <- unique(copern_nuts3_AGGR[, c("TIME_PERIOD", "LEVEL_AGGR",
                                                    "population_CNTR", "area_km2_CNTR", # "popn_density_mexc_CNTR", "popn_density_CNTR"
                                                    "ND2I_AvgNrDDays"), with=F])
  return(copern_nuts3_AGGR)
}
