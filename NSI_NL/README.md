# Air Inequity Dashboard: Insights on Pollution & Socioeconomic Disparities

## Overview
The Air Inequity Dashboard provides insights into pollution levels and socioeconomic disparities across different regions. This project combines satellite data on air pollutants with socioeconomic metrics to calculate an **Air Inequity Index (AII)**, highlighting inequity in air quality exposure relative to economic vulnerability.

---

## Data Sources

### 1. Satellite Data
- **Pollutants**: PM2.5, O3, NO2, SO2, CO, HCHO
- **Source**:
  - Sentinel-5P TROPOMI satellite data (via [Sentinel Hub through CDSE](https://www.sentinel-hub.com/))
  - PM2.5 data downloaded from [Google Earth Engine](https://earthengine.google.com/)
  - Monthly mean concentrations for each pollutant.

### 2. Socioeconomic Data
- **GDP per capita per NUTS3 region**:
  - Retrieved from [Eurostat](https://ec.europa.eu/eurostat).
  - Used to calculate normalized GDP per capita as a proxy for economic vulnerability.

### 3. Pollutant Scores and Weights
- Derived from:
  - The European Air Quality Index ([CAMS Training](https://www.copernicus.eu/en)).
  - National Ambient Air Quality Standards (NAAQS) by the U.S. Environmental Protection Agency (EPA).
  - World Health Organization (WHO) guidelines.
  - Expert judgment for missing pollutants (CO and HCHO).

---

## Methodology

### 1. Calculating the Air Quality Index (AQI)
The AQI is derived from the following steps:

1. **Pollutant Scoring**:
   - Pollutant concentrations are categorized into qualitative groups (`Very Good`, `Good`, `Medium`, `Poor`, `Very Poor`, `Extremely Poor`) based on predefined thresholds (Table 1 below).
   - Each category is assigned a score (1–6).

   **Table 1: Pollutant Scores**
   
| POLLUTANT | UNIT | VERY GOOD | GOOD | MEDIUM | POOR | VERY POOR | EXTREMELY POOR |
|-----------|------|-----------|------|--------|------|----------|----------------|
| O₃        | mol/m³ | 0–0.05    | 0.05–0.10 | 0.10–0.15 | 0.15–0.20 | 0.20–0.30 | 0.30–0.80 |
| CO        | mol/m³ | 0–0.01    | 0.01–0.02 | 0.02–0.03 | 0.03–0.05 | 0.05–0.10 | 0.10–0.50 |
| NO₂       | µg/m³ | 0–50      | 50–100 | 100–200 | 200–500 | 500–1,000 | 1,000–100,000 |
| SO₂       | µg/m³ | 0–50      | 50–100 | 100–150 | 150–200 | 200–300 | 300–500 |
| PM2.5     | µg/m³ | 0–10      | 10–15 | 15–20 | 20–30 | 30–50 | 50–200 |
| HCHO      | µg/m³ | 0–5       | 5–10 | 10–15 | 15–20 | 20–30 | 30–50 |

2. **Weighted Mean Calculation**:
   - Pollutants are weighted based on their harmfulness to human health (Table 2 below).
   - Seasonal adjustments are applied to account for variations in pollutant prevalence (Table 3 below).

   **Table 2: Pollutant Weights Based on Harmfulness**

   | Pollutant | Weight | Justification |
   |-----------|--------|---------------|
   | PM2.5     | 0.35   | Most harmful due to deep lung penetration. |
   | NO₂       | 0.25   | Strongly associated with respiratory diseases. |
   | O₃        | 0.17   | Causes lung inflammation and exacerbates asthma. |
   | SO₂       | 0.11   | Causes short-term respiratory irritation. |
   | CO        | 0.06   | Typically not a major outdoor air pollutant. |
   | HCHO      | 0.06   | Carcinogenic but mostly an indoor issue. |

   **Table 3: Seasonal Weights**

   | Pollutant | Winter (Dec-Feb) | Spring (Mar-May) | Summer (Jun-Aug) | Autumn (Sep-Nov) |
   |-----------|------------------|------------------|------------------|------------------|
   | PM2.5     | 0.40             | 0.36             | 0.25             | 0.35             |
   | NO₂       | 0.25             | 0.22             | 0.15             | 0.23             |
   | O₃        | 0.10             | 0.15             | 0.30             | 0.15             |
   | SO₂       | 0.12             | 0.12             | 0.05             | 0.12             |
   | CO        | 0.06             | 0.07             | 0.10             | 0.07             |
   | HCHO      | 0.07             | 0.08             | 0.15             | 0.08             |

3. **Final AQI Formula**:
   \[
   \text{AQI} = \sum (\text{Score of Pollutant}_i \times \text{Weight of Pollutant}_i)
   \]

### 2. Normalizing GDP per capita
To incorporate socioeconomic disparities:
1. Retrieve GDP per capita per NUTS3 region from Eurostat.
2. Normalize GDP per capita using the formula:
   \[
   \text{Normalized GDP per captia} = 1 - \frac{\text{GDP per capita}_{\text{region}} - \text{GDP per capita}_{\text{min}}}{\text{GDP per capita}_{\text{max}} - \text{GDP per capita}_{\text{min}}}
   \]
   - High values indicate economic vulnerability; low values indicate wealthier regions.

### 3. Calculating the Air Inequity Index (AII)
The AII combines the AQI and normalized GDP per capita:
\[
\text{AII} = \text{AQI} \times \text{Normalized GDP per capita}
\]
- Higher AII values indicate greater air inequity.

---

## Pilot Study
The methodology was first tested on two countries:
- **The Netherlands**: High GDP per capita, temperate climate.
- **Slovenia**: Lower GDP per capita, diverse climate.

These countries were chosen to evaluate the model's performance across economic and environmental conditions.

---
Dashboard - http://64.225.142.197:8050/
---

## Future Work
- Expand the dashboard to include additional countries and regions.
- Incorporate real-time data updates for dynamic monitoring.
- Explore additional socioeconomic and demographic factors influencing air inequity.

---

## References
1. European Air Quality Index: [CAMS Training](https://www.copernicus.eu/en)
2. U.S. EPA National Ambient Air Quality Standards (NAAQS): [EPA Guidelines](https://www.epa.gov)
3. WHO Indoor Air Quality Guidelines: [WHO Standards](https://www.who.int)
4. Eurostat GDP Data: [Eurostat](https://ec.europa.eu/eurostat)

---

If you have any questions or need further clarification, please contact:
as.loganathan@cbs.nl
s.vanhoudt@cbs.nl
c.lam@cbs.nl
