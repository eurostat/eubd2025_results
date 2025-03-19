# ------------------------------------------------------------------------------
# Preprocessing Script for Shiny App Display
# 
# This script loads and processes various datasets, including:
# - Corine Land Cover 2018 data and its legend
# - NUTS (Nomenclature of Territorial Units for Statistics) data
# - Satellite outputs (in Parquet format)
#
# It then performs machine learning classification, computes flash estimates,
# aggregates data by NUTS regions, and finally exports the preprocessed data.
#
# Required packages: readr, dplyr, stringr, tidyr, rpart, rpart.plot, caret, data.table, arrow
# ------------------------------------------------------------------------------

# ----------------------------- SETUP ------------------------------------------
# Load required packages
library(readr)
library(dplyr)
library(tidyr)
library(stringr)
library(rpart)
library(rpart.plot)
library(caret)
library(data.table)
library(arrow)

# --------------------------- IMPORT DATA --------------------------------------


# Import NUTS data using data.table for efficiency
clc_nuts_cleaned <- read_rds("clc_nuts_light.rds")

# Transform geometry column: extract coordinates and adjust by subtracting 50
clc_nuts_transformed <- clc_nuts_cleaned %>%
  mutate(geometry = str_remove_all(geometry, "c\\(|\\)")) %>%
  separate(geometry, into = c("X", "Y"), sep = ",", convert = TRUE) %>%
  mutate(
    X = as.numeric(str_trim(X)) - 50,
    Y = as.numeric(str_trim(Y)) - 50
  )
# Import Corine Land Cover 2018 for BENELUX
clc_2018 <- read_delim("scripts/clc_benelux_grid_BL.csv", 
                       delim = "|", escape_double = FALSE, trim_ws = TRUE) %>% 
  semi_join(clc_nuts_transformed %>% select(X, Y), by = c("X", "Y"))

# Import Corine Land Cover categories nomenclature and create VALUE column
clc_legend <- read_delim("scripts/legend_clc.csv", 
                         delim = "|", escape_double = FALSE, trim_ws = TRUE) %>% 
  mutate(VALUE = CD_COVER) 
  

# Merge CLC 2018 data with simplified categories from the legend
clc_2018_cleaned <- clc_2018 %>% 
  full_join(clc_legend) %>% 
  select(X, Y, CD_COVER_SIMP, TX_CLC_LVL0)

clc_2018 <- NULL

# Clean up clc_legend further (select only necessary columns)
clc_legend <- clc_legend %>% 
  mutate(VALUE = CD_COVER) %>% 
  select(VALUE, CD_COVER_SIMP, TX_CLC_LVL0)

# --------------------- FUNCTION DEFINITIONS -----------------------------------
# Function to import and process satellite data for a given geo and time.
process_geo_time <- function(geo, time, file_path_template = "scripts/%s_%s.parquet") {
  file_path <- sprintf(file_path_template, geo, time)
  
  df <- read_parquet(file_path)
  
  df <- df %>%  
    mutate(
      X = X_rounded, 
      Y = Y_rounded,
      year = time
    ) %>% 
    select(
      X, Y, 
      Band_10_min,
      Band_10_mean,
      Band_10_max,
      Band_9_min,
      Band_9_mean,
      Band_9_max,
      Band_8_min,
      Band_8_mean,
      Band_8_max,
      Band_7_min,
      Band_7_mean,
      Band_7_max,
      Band_6_min,
      Band_6_mean,
      Band_6_max,
      Band_5_min,
      Band_5_mean,
      Band_5_max,
      Band_4_min,
      Band_4_mean,
      Band_4_max,
      Band_3_min,
      Band_3_mean,
      Band_3_max,
      Band_2_min,
      Band_2_mean,
      Band_2_max,
      Band_1_min,
      Band_1_mean,
      Band_1_max,
      year
    ) %>% 
    # Join with transformed NUTS data based on X and Y
    left_join(clc_nuts_transformed, by = c("X", "Y")) %>% 
    # Filter for specific NUTS regions
    filter(!is.na(NUTS_ID) & NUTS_ID %in% c("BE211", "BE213", "BE225",
                                            "NL411", "NL415", "NL414", "NL422"))
  
  return(df)
}

# Function to compute flash estimates and changes 
# Uses thresholds for classification that are determined in the Decision Tree Modelling
compute_flash_and_change <- function(geo, year) {
  data <- process_geo_time(geo, year) %>% 
    left_join(clc_2018_cleaned, by = c("X", "Y")) %>% 
    mutate(
      clc_2018_categ = CD_COVER_SIMP,
      clc_fe = case_when(
        Band_5_max == 1 ~ clc_2018_categ,  
        clc_2018_categ == 3 ~ 3,
        clc_2018_categ == 4 ~ 4,
        Band_7_max >= -0.22 & 
          Band_7_mean >= -0.51 ~ 1,
        TRUE ~ 2
      )
    ) %>% 
    select(X, Y, clc_2018_categ, clc_fe, year, NUTS_ID, CNTR_CODE, NUTS_NAME)
  
  return(data)
}

# ----------------- MACHINE LEARNING: CLASSIFICATION ---------------------------
# Process 2018 satellite data and merge with CLC 2018 data
sentinel_2018 <- process_geo_time("sentinel", "2018")
sentinel_2018_thresh <- sentinel_2018 %>% 
  left_join(clc_2018_cleaned, by = c("X", "Y"))

# Filter data for target land cover types
data <- sentinel_2018_thresh %>% 
  filter(TX_CLC_LVL0 %in% c("Artificial surfaces", "Green and agricultural areas")) 

# Select predictor variables (Band_7 and Band_8 columns - selected after recursive tests) and target variable
data_model <- data %>% 
  select(starts_with("Band_7"), starts_with("Band_8"), CD_COVER_SIMP)

# Convert target variable to factor
data_model$CD_COVER_SIMP <- as.factor(data_model$CD_COVER_SIMP)

# Split data into training (70%) and testing (30%) sets
set.seed(123)  # For reproducibility
train_index <- createDataPartition(data_model$CD_COVER_SIMP, p = 0.7, list = FALSE)
train_data <- data_model[train_index, ]
test_data  <- data_model[-train_index, ]

# Build a decision tree model using the training data
model_tree <- rpart(CD_COVER_SIMP ~ ., data = train_data, method = "class")

# Visualize the decision tree
rpart.plot(model_tree)

# Make predictions on the test set and evaluate accuracy using a confusion matrix
predictions <- predict(model_tree, newdata = test_data, type = "class")
conf_matrix <- confusionMatrix(predictions, test_data$CD_COVER_SIMP)
print(conf_matrix)  # Expected accuracy: ~85%

# ------------------ COMPUTE FLASH ESTIMATES AND CHANGES -----------------------
# Compute flash estimates for 2018 and add a consistency label
# Calibrate the CLC2018 validated data with the predicted CLC value
# Conservative rationale : in uncertain events, priority to CLC2018 validated data

sentinel_2018 <- compute_flash_and_change("sentinel", "2018") %>% 
  mutate(
    clc_2018_fe = clc_fe,
    consistence = ifelse((clc_2018_fe == clc_2018_categ),
                         "consistent",
                         "non-consistent") 
  ) %>% 
  select(-clc_2018_fe)

# Extract consistency information for 2018 (to be merged later)
sen2018 <- sentinel_2018 %>% select(X, Y, consistence)

# Compute flash estimates for other years
sentinel_2019 <- compute_flash_and_change("sentinel", "2019")
sentinel_2020 <- compute_flash_and_change("sentinel", "2020")
sentinel_2021 <- compute_flash_and_change("sentinel", "2021")
sentinel_2022 <- compute_flash_and_change("sentinel", "2022")
sentinel_2023 <- compute_flash_and_change("sentinel", "2023")
sentinel_2024 <- compute_flash_and_change("sentinel", "2024")

# Merge 2018+ data with 2018 consistency information and full 2018 data.
sentinel <- sentinel_2019 %>% 
  full_join(sentinel_2020) %>% 
  full_join(sentinel_2021) %>% 
  full_join(sentinel_2022) %>% 
  full_join(sentinel_2023) %>% 
  full_join(sentinel_2024) %>% 
  full_join(sen2018) %>% 
  full_join(sentinel_2018)

sentinel_2018 <- NULL
sentinel_2019 <- NULL
sentinel_2020 <- NULL
sentinel_2021 <- NULL
sentinel_2022 <- NULL
sentinel_2023 <- NULL
sentinel_2024 <- NULL

# ------------------- CALCULATE FINAL FLASH ESTIMATES --------------------------
# Convert merged data to data.table (handles better large datasets) and ensure proper ordering
head(sentinel)
DT <- as.data.table(sentinel)
DT[, year := as.numeric(year)]
setorder(DT, X, Y, year)

# Calculate final_clc_fe per group (by X and Y) based on "consistence"
# Conservative rationale : Idea is to detect "consistent" changes that persist over time ; 
# -> for volatile predictions, priority is given to CLC2018 validated data

DT[, final_clc_fe := {
  # Check if the first value of `consistence` is "consistent"
  if (!is.na(consistence[1]) && consistence[1] == "consistent") {
    baseline <- clc_fe[1]
    
    # If all `clc_fe` values are the same as `baseline`
    if (all(clc_fe == baseline)) {
      clc_fe
    } else {
      # Find the first index where `clc_fe` differs from `baseline`
      first_change_index <- which(clc_fe != baseline)[1]
      candidate <- clc_fe[first_change_index]
      
      # If all values from the first change to the end are `candidate`
      if (all(clc_fe[first_change_index:.N] == candidate)) {
        clc_fe
      } else {
        # Otherwise, revert everything to `baseline`
        rep(baseline, .N)
      }
    }
  } else {
    # If it's not "consistent", just use `clc_2018_categ`
    clc_2018_categ
  }
}, by = .(X, Y)]



# Convert back to tibble for easier inspection and add change/direction indicators
sentinel_final <- as_tibble(DT) %>%
  mutate(
    change = ifelse(final_clc_fe == clc_2018_categ, "no change", "change"),
    direction = case_when(
      clc_2018_categ == final_clc_fe ~ "no change",
      clc_2018_categ == 1 & final_clc_fe == 2 ~ "vegetalisation", # from artificial to green
      clc_2018_categ == 2 & final_clc_fe == 1 ~ "urbanisation", # from green to artificial
      TRUE ~ NA_character_
    )
  )


# ------------------ CLEAN AND EXPORT PREPROCESSED DATA --------------------------
# Clean the data to avoid any unnecessary processing in the shiny app (dashboard)
# Clean up the CLC legend data for export
clc_legend_cleaned <- clc_legend %>%
  select(-VALUE) %>%
  unique() %>%
  mutate(final_clc_fe = CD_COVER_SIMP) %>%
  select(-CD_COVER_SIMP)

# Clean sentinel_final data, create NUTS_tot, merge with legend, and drop extra columns
sentinel_cleaned <- sentinel_final %>%
  select(-c(clc_2018_categ, clc_fe, consistence)) %>%
  mutate(NUTS_tot = paste0(NUTS_ID, " - ", NUTS_NAME)) %>%
  full_join(clc_legend_cleaned, by = c("final_clc_fe" = "final_clc_fe"))

nuts_3 <- eurostat::get_eurostat_geospatial(output_class = "sf",
                                            resolution = "10",
                                            nuts_level = "all",
                                            year = 2024,
                                            crs = "3035")

sentinel_cleaned <- sentinel_cleaned %>%
  mutate(NUTS_ID = substr(NUTS_tot,1,5)) %>%
  inner_join(clc_legend_cleaned) %>%
  inner_join(nuts_3 %>% select(NUTS_ID,geometry)) %>%
    mutate(color_var = case_when(
      final_clc_fe == 1 & change == "change" ~ "Urbanisation",  # jaune foncé
      final_clc_fe == 1 & change != "change" ~ TX_CLC_LVL0,
      final_clc_fe == 2 & change == "change" ~ "Vegetalisation",
      final_clc_fe == 2 & change != "change" ~ TX_CLC_LVL0,
      final_clc_fe == 3 ~ TX_CLC_LVL0
    ))


# Preview cleaned data
head(sentinel_cleaned)

# Save preprocessed data as RDS files
saveRDS(sentinel_cleaned, file = "/home/eouser/scripts/dashboard/preprocessed_data/sentinel.rds")

# ------------------- FILTER REAL CHANGES --------------------------------------
# Export a subset that contains only the cells that changed
# This is helpful to ease CLC validation for future human interventions

detected_changes <- sentinel_final %>% 
  filter(change == "change")

# Export detected changes as CSV
write_csv(detected_changes, "/home/eouser/scripts/detected_changes.csv")

# --------------------- NUTS AGGREGATION -----------------------------------------
# Preprocessing the tables that are displayed in the shiny app to avoid any unnecessary computing operations in the dashboard

# Aggregates in NUTS3
final_clc_fe_summary_nuts3 <- sentinel_cleaned %>% 
  group_by(year, NUTS_ID, final_clc_fe) %>% 
  summarise(count = n(), .groups = "drop") %>% 
  group_by(year,NUTS_ID) %>% 
  mutate(proportion = count / sum(count)) %>% 
  ungroup() %>% 
  select(-count) %>% 
  mutate(CD_COVER_SIMP = final_clc_fe) %>%
  left_join(clc_legend_cleaned, by = c("CD_COVER_SIMP" = "final_clc_fe")) %>% 
  rename(CD_COVER = CD_COVER_SIMP) %>%
  mutate(
    NUTS_0 = substr(NUTS_ID, 1, 2), 
    NUTS_1 = substr(NUTS_ID, 1, 3),  
    NUTS_2 = substr(NUTS_ID, 1, 4),  
    NUTS_3 = NUTS_ID               
  ) %>% 
  select(-final_clc_fe)

final_clc_fe_summary_nuts3_wide <- final_clc_fe_summary_nuts3 %>% 
  rename(TX_LAND_COVER = TX_CLC_LVL0,
         NM_LAND_COVER = CD_COVER, 
         PCT_AREA = proportion) %>% 
  select(NUTS_ID, year, TX_LAND_COVER, NM_LAND_COVER, PCT_AREA) %>%
  mutate(PCT_AREA = round(PCT_AREA * 100, 1)) %>%
  pivot_wider(
    names_from = year,  # Create a column for each unique year
    values_from = PCT_AREA  # Values for each year will be from PCT_AREA
  )


# Aggregates in NUTS2
final_clc_fe_summary_nuts2 <- final_clc_fe_summary_nuts3 %>%
  group_by(year, NUTS_0, NUTS_1, NUTS_2, CD_COVER, TX_CLC_LVL0) %>%
  summarise(proportion = sum(proportion), .groups = "drop") %>%
  group_by(year, NUTS_0, NUTS_1, NUTS_2) %>%
  mutate(proportion = proportion / sum(proportion)) %>%
  ungroup() %>%
  mutate(NUTS_ID = NUTS_2) %>%
  select(year, NUTS_ID, proportion, CD_COVER, TX_CLC_LVL0, NUTS_0, NUTS_1, NUTS_2)

final_clc_fe_summary_nuts2_wide <- final_clc_fe_summary_nuts2 %>% 
  rename(TX_LAND_COVER = TX_CLC_LVL0,
         NM_LAND_COVER = CD_COVER, 
         PCT_AREA = proportion) %>% 
  select(NUTS_ID, year, TX_LAND_COVER, NM_LAND_COVER, PCT_AREA) %>%
  mutate(PCT_AREA = round(PCT_AREA * 100, 1)) %>%
  pivot_wider(
    names_from = year,  # Create a column for each unique year
    values_from = PCT_AREA  # Values for each year will be from PCT_AREA
  )

# Save aggregated NUTS data
saveRDS(final_clc_fe_summary_nuts3_wide, file = "/home/eouser/scripts/dashboard/preprocessed_data/nuts_aggregated_nuts3.rds")
saveRDS(final_clc_fe_summary_nuts2_wide, file = "/home/eouser/scripts/dashboard/preprocessed_data/nuts_aggregated_nuts2.rds")

# -------------------------- EXPLORE -------------------------------------------

sentinel_test_2018 <- process_geo_time("sentinel", "2018")
sentinel_test_2024 <- process_geo_time("sentinel", "2024")
sentinel_test <- full_join(sentinel_test_2018, sentinel_test_2024, by = c("X", "Y"))

detected_changes_test <- detected_changes %>% 
  select(X, Y, direction)

sentinel_test_change <- inner_join(sentinel_test, detected_changes_test, by = c("X", "Y"))


sentinel_final  %>% 
  filter(change %in% "change") %>%  head()

sentinel_final  %>% 
  filter(X %in% "3919900" & Y %in% "3179800") 
