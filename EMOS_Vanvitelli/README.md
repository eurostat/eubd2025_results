# European Big Data Hackathon 2025
# EMOS Team Università della Campania “Luigi Vanvitelli” 

---

## Health-Adjusted Air Quality Index (HAQI)

---

## Background

- **DIRECTIVE (EU) 2024/2881 OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL**  
  - This Directive lays down target values for air pollutants and exposure reduction obligations.  
  - EU policies aim to achieve a toxic-free environment, protecting the health and well-being of people, animals, and ecosystems from environmental risks.  
  - The Commission should periodically review scientific evidence on pollutants and their impacts, to assess whether current air quality standards remain appropriate.

---

## Our Proposal

An index that incorporates:

- Pollutant levels over a time interval  
- Frequency of exceeding safety limits defined by the EU  
- An adjustment factor (e.g., vegetation factor) reflecting environmental conditions  

---

## Key Components

1. **Daily Exceedances**  
   Counts how many days each pollutant surpasses its safety limit.  

2. **Vegetation Factor**  
   Uses NDVI (Normalized Difference Vegetation Index) to account for local environmental mitigation.  

3. **Time Series**  
   Considers changes over time to capture pollutant concentrations with respect to their safety limits.  

---

## Pollutant Safety Daily Limit

- **CO**: 4 mg/m³  
- **NO₂**: 50 μg/m³  
- **PM₂.₅**: 25 μg/m³  
- **PM₁₀**: 45 μg/m³  
- **SO₂**: 50 μg/m³  

---

## Health-Adjusted Air Quality Index (HAQI)

The adjusted pollutant component for each pollutant (CO, NO₂, PM₂.₅, PM₁₀, SO₂) for a territorial unit (NUTS-3) is given by:  

![HAQI Formula](https://latex.codecogs.com/png.latex?p_{\mathrm{Adj},i}=E_{p,i}\times\sum_{t=1}^{T}\dfrac{p_{i,t}}{U_{p}}\frac{1}{e^{(NDVI_{i,t}-1)}})

Where:
- **\( U_p \)** is the safety limit defined by the European Union for the pollutant \( p \).  
- **NDVI** is the Normalized Difference Vegetation Index.  
- **\( E_p \)** is the ratio of exceeding days over the time interval.  

The **Health-Adjusted Air Quality Index (HAQI)** is then the sum of all the adjusted pollutant components.  

---

## Reliability Assessment (Internal Consistency)

To assess the reliability of our composite indicator, we have computed **Cronbach’s Alpha**, yielding a value of **0.97**.

---

## Utility for Policymakers

- Ability to effectively detect territorial units that are particularly exposed to health hazards.  
- Control over the temporal evolution of European territorial units toward objective levels of air pollutants.  
- Access to composite data (HAQI) alongside specific pollutant concentration values for targeted interventions.  

---

## Main References

- Ai, Hongshan, Xi Zhang, and Zhengqing Zhou. "The impact of greenspace on air pollution: Empirical evidence from China." *Ecological Indicators* 146 (2023): 109881.  
- **Copernicus Atmosphere Monitoring Service data [2025]**  
- **Copernicus Sentinel data [2025]**  
- Cronbach, Lee J. "Coefficient alpha and the internal structure of tests." *Psychometrika* 16.3 (1951): 297-334.  
- **Directive (EU) 2024/2881** of 23 October 2024 on ambient air quality and cleaner air for Europe (recast)  
- OECD/European Union/EC-JRC (2008), *Handbook on Constructing Composite Indicators: Methodology and User Guide*, OECD Publishing, Paris  

---

## Contacts

- **Gianmarco Borrata**: [Gianmarco.borrata@studenti.unicampania.it](mailto:Gianmarco.borrata@studenti.unicampania.it)  
- **Gennaro Nunziata**: [Gennaro.nunziata@studenti.unicampania.it](mailto:Gennaro.nunziata@studenti.unicampania.it)  
- **Pasquale Pipiciello**: [Pasquale.pipiciello@studenti.unicampania.it](mailto:Pasquale.pipiciello@studenti.unicampania.it)  

---

