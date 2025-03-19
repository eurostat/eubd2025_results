library(sf)
library(tidyr)
library(dplyr)

corine <- read.csv("/opt/scripts/clc-benelux-2018.csv",sep="|")

#VALUE
# unique(corine$VALUE)

library(eurostat)

# Get the NUTS3 regions for the EU
nuts_data <- eurostat::get_eurostat_geospatial(output_class = "sf", 
                                               resolution = "10",
                                               nuts_level = "all",
                                               year = 2024,
                                               crs = "3035")

# combine corine with nuts_data
corine_sf <- st_as_sf(corine, coords = c("X", "Y"), crs = 3035)

st_crs(corine_sf)
st_crs(nuts_data)

# st_crs(nuts_data) == st_crs(corine_sf) # TRUE

# keep level 3 and benelux
nuts_data_lvl_3 <- nuts_data %>%
  filter(LEVL_CODE==3) %>%
  filter(CNTR_CODE %in% c("BE","NL","LU"))

# st_crs(nuts_data_lvl_3) == st_crs(corine_sf) # TRUE

# long
corine_with_nuts <- st_join(corine_sf, nuts_data_lvl_3, join = st_within)

# matches <- st_intersects(corine_sf, nuts_data)
corine_with_nuts_benelux <- corine_with_nuts %>%
  filter(!is.na(id), 
         ! substr(id,1,2) %in% c("DE","FR"))

corine_with_nuts_benelux <- corine_with_nuts_benelux %>%
  arrange(id)

write.table(corine_with_nuts_benelux,"/opt/scripts/clc_benelux_nuts.csv",sep = "|",row.names = FALSE)

### legend --> simplification
legend <- read.csv("/opt/scripts/TD_LAND_COVER.csv",sep="|")

legend_simple <- legend %>%
  mutate(TX_CLC_LVL0 = case_when(
    grepl("Agricultural areas|Forest and semi natural areas", TX_CLC_LVL1) ~ "Green and agricultural areas",
    grepl("Wetlands|Water bodies", TX_CLC_LVL1) ~ "Wetlands and water bodies",
    grepl("NODATA|UNCLASSIFIED", TX_CLC_LVL1) ~ "Not available",
    TRUE ~ TX_CLC_LVL1)) %>%
  mutate(CD_COVER_SIMP = case_when(
    grepl("Artificial surfaces", TX_CLC_LVL0) ~ 1,
    grepl("Green and agricultural areas", TX_CLC_LVL0) ~ 2,
    grepl("Wetlands and water bodies", TX_CLC_LVL0) ~ 3,
    grepl("Not available", TX_CLC_LVL0) ~ 4,
    TRUE ~ 5
  ))

write.table(legend_simple,"/opt/scripts/legend_clc.csv",sep = "|",row.names = FALSE)


####### test ##########
# nuts_in_corine_with_nuts_benelux <- data.frame(id = unique(corine_with_nuts_benelux$id))
# test <- nuts_data_lvl_3 %>%
#   filter(substr(id,1,2) %in% c("LU","BE","NL")) %>%
#   anti_join(nuts_in_corine_with_nuts_benelux)
# on les a tous
# 
# test <- corine_with_nuts_benelux  %>%
#   st_join(nuts_data_lvl_3 %>% select(NUTS_ID, nuts_geom = geometry), join = st_intersects)
# 
# test <- test %>%
#   st_sf()

#############################"

# Bruxelles box
# 3917634.3490,3091014.6057;3930282.7671,3101024.3400

# bruxelles_corine <- corine %>%
#   dplyr::filter(.data$X > 3917634 & .data$X < 3930282 &
#                   .data$Y > 3091014 & .data$Y < 3101024)
# 
# write.table(bruxelles_corine,"/opt/scripts/corine_bxl.csv",sep = "|",row.names = FALSE)

# test 
# corine_sf_bx <- st_as_sf(bruxelles_corine, coords = c("X", "Y"), crs = 3035)
# nuts_data_lvl_3 <- nuts_data %>% 
#   # mutate(LEVL_CODE = as.numeric(LEVL_CODE)) %>%
#   filter(LEVL_CODE==3)

# start <- proc.time()
# corine_with_nuts <- st_join(corine_sf_bx, nuts_data_lvl_3, join = st_within)
# end <- proc.time()
# duration <- end-start
