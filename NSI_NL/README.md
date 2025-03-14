Documentation
Air Inequity Dashboard: Insights on Pollution & Socioeconomic Disparities

Data:
-	Sentinel-5P TROPOMI satellite data on pollutants (PM2.5, O3, NO2, SO2, CO, HCHO)
-	GDP per NUTS3 region (Statistics | Eurostat)
-	Scores per pollutant
-	Weights per pollutant

Methodology
Calculating the Air Quality Index
First we need to download the satellite data on pollutant concentrations from Sentinel Hub through CDSE. PM2.5 is not available there though, so we had to download it from Google Earth Engine. We downloaded a the mean concentration per month for each pollutant. 
Subsequently we had to derive an Air Quality Index (AQI) from this. To do so, we had to score the mean concentrations. We derived a table with scores from the European Air Quality Index (European Air Quality Index Calculation — CAMS Training). Very good will get a score of 1 and extremely poor will get a score of 6 (Table 1). CO and HCHO were not available. The National Ambient Air Quality Standards (NAAQS) set by the U.S. Environmental Protection Agency (EPA) specify primary standards for CO as 9 ppm (10 mg/m³) over 8 hours and 35 ppm (40 mg/m³) over 1 hour (epa.gov+2standard.wellcertified.com+2Wikipedia+2). The World Health Organization (WHO) recommends an indoor air quality guideline of 0.1 mg/m³ (100 µg/m³) over a 30-minute exposure to prevent sensory irritation and long-term health effects, including cancer (standard.wellcertified.com). Based on this information and expert judgement we created the groups to score those pollutant concentrations. 
Table 1. Pollutant scores based on concentrations. 
![image](https://github.com/user-attachments/assets/d88b7ec1-b739-49f2-aa3b-12a09e2892e4)
