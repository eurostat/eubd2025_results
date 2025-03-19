library(ncdf4)
library(stars)
library(sf)
library(dplyr)
library(mapview)
library(terra)


# Load necessary packages
library(terra)
library(future.apply)
library(mapview)

# Set up parallel processing
plan(multisession, workers = parallel::detectCores() - 1)

# FRANCE
# Load raster data
nc_file_FR_2021 <- "SENTINEL2_L2A_FR_2021_mi_Aug.nc"
nc_file_DE_2021 <- "SENTINEL2_L2A_DE_2021_mi_Aug.nc"
raster_data <- rast(nc_file_FR_2021)
#raster_data <- rast(nc_file_DE_2021)

# Réduire la résolution (facteur 5)
raster_data <- aggregate(raster_data, fact = 100, fun = mean)

# Select bands
B08 <- raster_data[["B08_t=11548"]]
B04 <- raster_data[["B04_t=11548"]]

# Compute NDVI directly using terra's built-in functions
ndvi_raster <- (B08 - B04) / (B08 + B04)

# Visualize with transparent NA values
mapview(ndvi_raster, na.color = "transparent")

library(webshot2)  # Ensures proper saving of maps

# Create mapview object
ndvi_map <- mapview(ndvi_raster, na.color = "transparent")

# Save as HTML
mapshot(ndvi_map, url = "ndvi_map.html")


# Select bands
B8A <- raster_data[["B8A_t=11548"]]
B11 <- raster_data[["B11_t=11548"]]

# Compute NDVI directly using terra's built-in functions
moisture_raster <- (B8A - B11) / (B8A+ B11)

# Visualize with transparent NA values
mapview(moisture_raster, na.color = "transparent")

library(webshot2)  # Ensures proper saving of maps

# Create mapview object
ndvi_map <- mapview(moisture_raster, na.color = "transparent")

# Save as HTML
mapshot(ndvi_map, url = "moisture_map.html")


# ALLEMAGNE
# Load raster data
nc_file_FR_2021 <- "SENTINEL2_L2A_FR_2021_mi_Aug.nc"
nc_file_DE_2021 <- "SENTINEL2_L2A_DE_2021_mi_Aug.nc"
#raster_data <- rast(nc_file_FR_2021)
raster_data <- rast(nc_file_DE_2021)

# Réduire la résolution (facteur 5)
raster_data <- aggregate(raster_data, fact = 100, fun = mean)

# Select bands
B08 <- raster_data[["B08_t=11546"]]
B04 <- raster_data[["B04_t=11546"]]

# Compute NDVI directly using terra's built-in functions
ndvi_raster <- (B08 - B04) / (B08 + B04)

# Visualize with transparent NA values
mapview(ndvi_raster, na.color = "transparent")

library(webshot2)  # Ensures proper saving of maps

# Create mapview object
ndvi_map <- mapview(ndvi_raster, na.color = "transparent")

# Save as HTML
mapshot(ndvi_map, url = "ndvi_map.html")


# Select bands
B8A <- raster_data[["B8A_t=11546"]]
B11 <- raster_data[["B11_t=11546"]]

# Compute NDVI directly using terra's built-in functions
moisture_raster <- (B8A - B11) / (B8A+ B11)

# Visualize with transparent NA values
mapview(moisture_raster, na.color = "transparent")

library(webshot2)  # Ensures proper saving of maps

# Create mapview object
ndvi_map <- mapview(moisture_raster, na.color = "transparent")

# Save as HTML
mapshot(ndvi_map, url = "moisture_map.html")





#### Temperature

# ALLEMAGNE
# Load raster data
nc_file_FR_2021 <- "SENTINEL3_SLSTR_FR_2021_mi_Aug.nc"
nc_file_DE_2021 <- "SENTINEL3_SLSTR_DE_2021_mi_Aug.nc"
#raster_data <- rast(nc_file_FR_2021)
raster_data <- rast(nc_file_DE_2021)

# Réduire la résolution (facteur 5)
#raster_data <- aggregate(raster_data, fact = 100, fun = mean)

# Select bands
S7 <- raster_data[["S7_t=11554"]] - 272

# Visualize with transparent NA values
mapview(S7, na.color = "transparent")

library(webshot2)  # Ensures proper saving of maps

# Create mapview object
ndvi_map <- mapview(S7, na.color = "transparent")

# Save as HTML
mapshot(ndvi_map, url = "S7_map_DE_2021.html")


# FRANCE
# Load raster data
nc_file_FR_2021 <- "SENTINEL3_SLSTR_FR_2021_mi_Aug.nc"
nc_file_DE_2021 <- "SENTINEL3_SLSTR_DE_2021_mi_Aug.nc"
raster_data <- rast(nc_file_FR_2021)
#raster_data <- rast(nc_file_DE_2021)

# Réduire la résolution (facteur 5)
#raster_data <- aggregate(raster_data, fact = 100, fun = mean)

# Select bands
S7 <- raster_data[["S7_t=11554"]] - 272

# Visualize with transparent NA values
mapview(S7, na.color = "transparent")

library(webshot2)  # Ensures proper saving of maps

# Create mapview object
ndvi_map <- mapview(S7, na.color = "transparent")

# Save as HTML
mapshot(ndvi_map, url = "S7_map_FR_2021.html")




# 2023

# FRANCE
# Load raster data
nc_file_FR_2021 <- "SENTINEL2_L2A_FR_2023_mi_Aug.nc"
nc_file_DE_2021 <- "SENTINEL2_L2A_DE_2023_mi_Aug.nc"
raster_data <- rast(nc_file_FR_2021)
#raster_data <- rast(nc_file_DE_2021)

# Réduire la résolution (facteur 5)
raster_data <- aggregate(raster_data, fact = 100, fun = mean)

# Select bands
B08 <- raster_data[["B08_t=11548"]]
B04 <- raster_data[["B04_t=11548"]]

# Compute NDVI directly using terra's built-in functions
ndvi_raster <- (B08 - B04) / (B08 + B04)

# Visualize with transparent NA values
mapview(ndvi_raster, na.color = "transparent")

library(webshot2)  # Ensures proper saving of maps

# Create mapview object
ndvi_map <- mapview(ndvi_raster, na.color = "transparent")

# Save as HTML
mapshot(ndvi_map, url = "ndvi_map.html")


# Select bands
B8A <- raster_data[["B8A_t=11548"]]
B11 <- raster_data[["B11_t=11548"]]

# Compute NDVI directly using terra's built-in functions
moisture_raster <- (B8A - B11) / (B8A+ B11)

# Visualize with transparent NA values
mapview(moisture_raster, na.color = "transparent")

library(webshot2)  # Ensures proper saving of maps

# Create mapview object
ndvi_map <- mapview(moisture_raster, na.color = "transparent")

# Save as HTML
mapshot(ndvi_map, url = "moisture_map.html")


# ALLEMAGNE
# Load raster data
nc_file_FR_2021 <- "SENTINEL2_L2A_FR_2021_mi_Aug.nc"
nc_file_DE_2021 <- "SENTINEL2_L2A_DE_2021_mi_Aug.nc"
#raster_data <- rast(nc_file_FR_2021)
raster_data <- rast(nc_file_DE_2021)

# Réduire la résolution (facteur 5)
raster_data <- aggregate(raster_data, fact = 100, fun = mean)

# Select bands
B08 <- raster_data[["B08_t=11546"]]
B04 <- raster_data[["B04_t=11546"]]

# Compute NDVI directly using terra's built-in functions
ndvi_raster <- (B08 - B04) / (B08 + B04)

# Visualize with transparent NA values
mapview(ndvi_raster, na.color = "transparent")

library(webshot2)  # Ensures proper saving of maps

# Create mapview object
ndvi_map <- mapview(ndvi_raster, na.color = "transparent")

# Save as HTML
mapshot(ndvi_map, url = "ndvi_map.html")


# Select bands
B8A <- raster_data[["B8A_t=11546"]]
B11 <- raster_data[["B11_t=11546"]]

# Compute NDVI directly using terra's built-in functions
moisture_raster <- (B8A - B11) / (B8A+ B11)

# Visualize with transparent NA values
mapview(moisture_raster, na.color = "transparent")

library(webshot2)  # Ensures proper saving of maps

# Create mapview object
ndvi_map <- mapview(moisture_raster, na.color = "transparent")

# Save as HTML
mapshot(ndvi_map, url = "moisture_map.html")


#### Temperature

# ALLEMAGNE
# Load raster data
nc_file_FR_2023 <- "SENTINEL3_SLSTR_FR_2023_mi_Aug.nc"
nc_file_DE_2023 <- "SENTINEL3_SLSTR_DE_2023_mi_Aug.nc"
#raster_data <- rast(nc_file_FR_2021)
raster_data <- rast(nc_file_DE_2023)

# Réduire la résolution (facteur 5)
#raster_data <- aggregate(raster_data, fact = 100, fun = mean)

# Select bands
S7 <- raster_data[["S7_t=12284"]] - 272

# Visualize with transparent NA values
mapview(S7, na.color = "transparent")

library(webshot2)  # Ensures proper saving of maps

# Create mapview object
ndvi_map <- mapview(S7, na.color = "transparent")

# Save as HTML
mapshot(ndvi_map, url = "S7_map_DE_2023.html")


# FRANCE
# Load raster data
nc_file_FR_2023 <- "SENTINEL3_SLSTR_FR_2023_mi_Aug.nc"
nc_file_DE_2023 <- "SENTINEL3_SLSTR_DE_2023_mi_Aug.nc"
raster_data <- rast(nc_file_FR_2023)
#raster_data <- rast(nc_file_DE_2021)

# Réduire la résolution (facteur 5)
#raster_data <- aggregate(raster_data, fact = 100, fun = mean)

# Select bands
S7 <- raster_data[["S7_t=12284"]] - 272

# Visualize with transparent NA values
mapview(S7, na.color = "transparent")

library(webshot2)  # Ensures proper saving of maps

# Create mapview object
ndvi_map <- mapview(S7, na.color = "transparent")

# Save as HTML
mapshot(ndvi_map, url = "S7_map_FR_2023.html")


