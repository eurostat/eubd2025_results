
library(dplyr)
library(data.table)
library(sf)


general_path <- "~/R/00_General/"
rdata_map <- paste0(general_path,"rdata/mappings/")
CopRean_Y <- paste0(general_path,"rdata/cams_Y13to22/")
dir.create(corr_path <- "~/R/01_Correlation/CorrReslts/", showWarnings = FALSE, recursive = TRUE)
source(paste0(general_path,"FunctionsUsed.R"))



# #################################################################################
# [A] Import Created .RDS Datasets
nuts3_shapes <- readRDS(paste0(rdata_map,"NUTS3_Shapefile.rds"))              # Eurostat - NUTS3 mapping from Eurostat
popn_dt <- readRDS(paste0(rdata_map,"Popn_NUTS3_ByAge.rds"))                  # Eurostat - Population at NUTS regions from Eurostat
pdeaths_dt_all <- readRDS(paste0(rdata_map,"PremDeaths_PM25.rds"))            # Eurostat - Premature Deaths from Eurostat (at YEARLY and NUTS0 Level)
copern_nuts3 <- readRDS(paste0(CopRean_Y,"Copernicus_NUTS3_DDays_PMg5.rds"))  # Copernicus - CAMS ReAnlysis YEARLY data for 2013-2022


# #################################################################################
# [B] PREPARE FILES FOR CORRELATION
time_periods <- unique(pdeaths_dt_all[,TIME_PERIOD]) # keep only periods we can compare for correlation
eu_country_codes <- c("AT", "BE", "BG", "CY", "CZ",
                      "DE", "DK", "EE", "ES", "FI",
                      "FR", "EL", "HR", "HU", "IE",
                      "IT", "LT", "LU", "LV", "MT",
                      "NL", "PL", "PT", "RO", "SE",
                      "SI", "SK")

nuts3_shapes$geometry <- NULL # remove geometry from NUTS3 mapping file (unnecessary for Correlation)
nuts3_shapes <- as.data.table(nuts3_shapes)

copern_nuts3 <- unique(copern_nuts3[, c("TIME_PERIOD","NUTS_ID","EXCEED_mean"), with=F])
setnames(copern_nuts3, c("NUTS_ID"), c("geo"))
copern_nuts3[, LEVEL_AGGR := substr(geo,1,2)]
copern_nuts3 <- copern_nuts3[LEVEL_AGGR %in% eu_country_codes]


# #################################################################################
# [C] JOIN FILES FOR CORRELATION
dt_j <- left_join(popn_dt, pdeaths_dt_all, by = c("geo","TIME_PERIOD"))
dt_geo <- left_join(dt_j, nuts3_shapes, by = c("geo"))
dt_geo <- dt_geo[TIME_PERIOD %in% time_periods]
dt_geo <- dt_geo[CNTR_CODE %in% eu_country_codes]
dt_geo <- dt_geo[, LEVEL_AGGR := CNTR_CODE]
# dt_geo <- dt_geo[!is.na(area_m2)]
dt_geo_nuts3 <- unique(dt_geo[LEVL_CODE==3, 
                              c("TIME_PERIOD","geo","geo_name","area_km2","population"), with=F])
dt_geo_nuts0 <- unique(dt_geo[LEVL_CODE==0, 
                              c("TIME_PERIOD","geo","geo_name","area_km2","population","Popln_PM25_Numbr","Popln_PM25_Rate100k"), with=F])


# #################################################################################
# [D] ND2I
copern_nuts3_CNTR <- nd2i_fn(copern_nuts3, dt_geo_nuts3)
setnames(copern_nuts3_CNTR, c("LEVEL_AGGR"), c("CNTR_CODE"))


# #################################################################################
# [E] CORRELATION
addincr <- 0.001
correln_dt <- left_join(copern_nuts3_CNTR, dt_geo_nuts0, 
                        select(dt_geo_nuts0,c("TIME_PERIOD","geo","Popln_PM25_Numbr","Popln_PM25_Rate100k")), 
                        by=c("TIME_PERIOD","CNTR_CODE"="geo") )
correln_dt <- filter(correln_dt, !is.na(ND2I_AvgNrDDays), !is.na(Popln_PM25_Rate100k)) 
correlation_result <- cor.test(correln_dt$ND2I_AvgNrDDays, log(correln_dt$Popln_PM25_Rate100k + addincr), method = "pearson") # Replace "asthma_incidence" with your column
print(correlation_result)

# Plot scatter graph before taking the log:
pdf(paste0(corr_path, "01_Scatter_PMg5.pdf"))
plot(correln_dt$ND2I_AvgNrDDays, correln_dt$Popln_PM25_Rate100k,
     xlab = "Number Of Dangerous Days (PM2.5 > 5 \u00B5g/m\u00B3)", 
     ylab = "Premeture Deaths Due to PM2.5",
     main = "PM2.5 > 5 \u00B5g/m\u00B3\nDangerous Days (Vs) Premature Deaths")
dev.off()

pdf(paste0(corr_path, "02_Correlation_PMg5.pdf"))
plot(correln_dt$ND2I_AvgNrDDays, log(correln_dt$Popln_PM25_Rate100k + addincr),
     xlab = "Number Of Dangerous Days (PM2.5 > 5 \u00B5g/m\u00B3)", 
     ylab = "LOG(Premeture Deaths Due to PM2.5)",
     main = "PM2.5 > 5 \u00B5g/m\u00B3\nDangerous Days (Vs) LOG(Premature Deaths)")
abline(lm(log(Popln_PM25_Rate100k + addincr) ~ ND2I_AvgNrDDays, data = correln_dt), col = "blue", lwd = 3)
legend("right", 
       legend = paste0("Correlation:\n   ",round(correlation_result$estimate[[1]],4)*100,"%"),
       bty = "n", 
       cex = 1.2, 
       text.col = "blue") 
dev.off()


# Correlation Equation
linear_model <- lm(log(Popln_PM25_Rate100k + addincr) ~ ND2I_AvgNrDDays, , data = correln_dt)
intercept <- coef(linear_model)[[1]]
slope <- coef(linear_model)[[2]]
print(paste0("Equation of the line: log(Popln_PM25_Rate100k + addincr) = ", slope, " ND2I_AvgNrDDays + (", intercept,")"))

# EQUATION TO CAULCULATE PrematureDeaths/100000 inhabitants (PDeaths) based on Number of Dangerous Days (NDDays):
#   PremDeaths = exp((slope * NDDays) + intercept) - addincr
CorrEqnCoeffs <- list(s = slope, i=intercept, b=addincr)
saveRDS(CorrEqnCoeffs,paste0(corr_path,"CorrExpEqnCoeffs_PMg5.rds"))
  

