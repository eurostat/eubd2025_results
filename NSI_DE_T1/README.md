# Leafy lines
## Monitoring Small Woody Features in accordance to the SAIO
The app gives a visual overview of small woody features on agricultural land. We propose a method to display small woody features overlapping with agricultural land. There is ongoing demand for data required based on the SAIO.

## State of the app
The current working app displays on the map corine Land cover for agricultural land. Small Woody Features are not displayed as polygons of that high resolution crashed the map visual. 
Bar plot and Table show the calculated Small Woody Features area on Corine Land Cover Classes.

Open Issues: 
- Optimze map visual to display Small Woody Features
- Add Backend Infrastructure with Database support to query data directly from Database. 

## Files
### statistics_woody_features.py
This script is used to process the data source Small woody features. As the data is quite large we have used only example paths to the data. As an output the script produces aggregated statistics of for the two selected regions in Germany and Austria
### The remaining scripts
The rest of the codebase is used to create the python shiny webapp. We serve the data from the www/data folder, which is not versioned. 

## How to use
Change directory to NSI_DE_T1
- cd NSI_DE_T1
Create a Virtual Python environment with the name venv
- python -m venv venv 
Activate the venv
- For Windows: venv/Scripts/activate
- For Linux: source venv/bin/activate
Install the requirements.txt in 
- pip install -r requiremetns.txt
As Data is large (~1 GB), we dont want to insert it into repo. It should remain a code repo afterall. Data is freely available. For the specifc files write to joshua.jaeger@destatis.de. I will happily make it accessable. 
We used the script prepare_descriptives.py to recode the CRS, which gave us a headache. It needs to run once. 
Shiny app runs on localhost 
- shiny run --reload app.py


