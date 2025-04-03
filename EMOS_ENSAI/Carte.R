library(mapview)
library(viridis)
library(RColorBrewer)
library(classInt)

rm(list=ls())

nuts3 <- "FR"
date <- "2021"

if (nuts3 == "DE"){
  fond <- "DATA/Nuts3/germany.geojson"
  pays <- "Germany"
}
if (nuts3 == "FR"){
  fond <- "DATA/Nuts3/ile.geojson"
  pays <- "France"
}

data <- get(load(paste0("Rdata/data_", nuts3 ,"_", date ,".Rdata")))

pal_agriculture <- colorRampPalette(c("#e5f5e0", "#006837"))(100) 
pal_temp <- colorRampPalette(rev(brewer.pal(11, "RdYlBu")))(100)
pal_moisture <- colorRampPalette(brewer.pal(9, "BrBG"))(100)  
pal_ndvi <- colorRampPalette(c("#8c510a", "#d9f0a3", "#006837"))(100)

carte <- mapview(data, zcol = "agriculture_share", col.regions = pal_agriculture, 
        layer.name = "Agriculture share", homebutton = F)
mapshot(carte, url = paste0("Map/",pays,"_Grid_Crop_",date,".html"))

carte <- mapview(data, zcol = "temperature", col.regions = pal_temp, 
        layer.name = "Temperature", homebutton = F)
mapshot(carte, url =paste0("Map/",pays,"_Grid_Temperature_",date,".html"))

carte <- mapview(data, zcol = "moisture_index", col.regions = pal_moisture, 
        layer.name = "Moisture Index", homebutton = F)
mapshot(carte, url = paste0("Map/",pays, "_Grid_Moisture_",date,".html"))

carte <- mapview(data, zcol = "ndvi", col.regions = pal_ndvi, 
        layer.name = "NDVI", homebutton = F)
mapshot(carte, url = paste0("Map/",pays, "_Grid_NDVI_",date,".html"))

nuts3_data <- st_read(fond)
mini <- st_intersection(data, nuts3_data)
# mapview(nuts3_data) + mapview(mini, col.regions = "red") + mapview(data, col.regions="green")

table(mini$NUTS2021_3)

mini <- mini %>%
  summarize(temperature = mean(temperature, na.rm = TRUE),
            agriculture_share = mean(agriculture_share, na.rm = TRUE),
            moisture_index = mean(moisture_index, na.rm = TRUE),
            ndvi = mean(ndvi, na.rm = TRUE),
            TOT_P_2021 = sum(TOT_P_2021))

nuts3_data <- nuts3_data %>%
  mutate(TOT_P_2021 = mini$TOT_P_2021,
         temperature = mini$temperature,
         agriculture_share = mini$agriculture_share,
         moisture_index = mini$moisture_index,
         ndvi = mini$ndvi,
         ) %>% 
  bind_rows(data %>% 
              st_drop_geometry(data))

carte <- mapview(nuts3_data, zcol = "agriculture_share", col.regions = pal_agriculture, 
        layer.name = "Agriculture share", homebutton = F)
mapshot(carte, url = paste0("Map/",pays,"_NUTS3_Crop_",date,".html"))

carte <- mapview(nuts3_data, zcol = "temperature", col.regions = pal_temp, 
        layer.name = "Temperature", homebutton = F)
mapshot(carte, url = paste0("Map/",pays,"_NUTS3_Temperature_",date,".html"))

carte <- mapview(nuts3_data, zcol = "moisture_index", col.regions = pal_moisture, 
        layer.name = "Moisture Index", homebutton = F)
mapshot(carte, url = paste0("Map/",pays,"_NUTS3_Moisture_",date,".html"))

carte <- mapview(nuts3_data, zcol = "ndvi", col.regions = pal_ndvi, 
        layer.name = "NDVI", homebutton = F)
mapshot(carte, url = paste0("Map/",pays,"_NUTS3_NDVI_",date,".html"))


if (date == "2021"){
  jenks_breaks <- classIntervals(data$TOT_P_2021, n = 5, style = "jenks")
  pal_pop <- brewer.pal(5, "YlGnBu")  # 5 couleurs pour 5 classes
  data$population_class_col <- findColours(jenks_breaks, pal_pop)
  data$population_class_intervals <- cut(data$TOT_P_2021, breaks = jenks_breaks$brks, include.lowest = TRUE,
                                         labels = paste0("(", head(jenks_breaks$brks, -1), ", ", 
                                                         tail(jenks_breaks$brks, -1), "]"))
  
  # Cartes à l'échelle carreaux 
  carte <- mapview(data, zcol = "population_class_intervals", col.regions = pal_pop, 
                   layer.name = "Total Population", homebutton = FALSE)
  mapshot(carte, url = paste0("Map/",pays,"_Grid_Population_",date,".html"))
  
  carte <- mapview(nuts3_data, zcol = "TOT_P_2021", 
                   layer.name = "Total Population", homebutton = FALSE)
  mapshot(carte, url = paste0("Map/",pays,"_NUTS3_Population_",date,".html"))
}