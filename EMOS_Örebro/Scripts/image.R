## Row

### Column 



```{python}
#| warning: false
#| messages: false

import geopandas as gpd
import folium

# Read and prepare shapefile data
local_shapefile_path = r"../data/nuts/NUTS_RG_20M_2024_3035.shp"
gdf = gpd.read_file(local_shapefile_path).to_crs(epsg=4326)  # Convert to WGS84

# Create base map centered on your custom polygon area
m = folium.Map(location=[40.7, -8.4], zoom_start=11)  # Coordinates approximate to your polygon

# Add original shapefile data (NUTS regions)
folium.GeoJson(
  gdf,
  name="NUTS Regions",
  style_function=lambda x: {'fillColor': 'none', 'color': 'grey', 'weight': 0.5}
).add_to(m)

# Add your custom polygon overlay
custom_polygon = {
  "type": "Polygon",
  "coordinates": [[
    [-8.422394,40.623855],[-8.419304,40.610825],[-8.440247,40.602484],
    [-8.444023,40.592839],[-8.409691,40.587885],[-8.390808,40.599356],
    [-8.366432,40.610825],[-8.351326,40.618643],[-8.32386,40.627243],
    [-8.327637,40.636102],[-8.347206,40.643136],[-8.32077,40.647825],
    [-8.31665,40.654076],[-8.329353,40.657722],[-8.34034,40.681679],
    [-8.365059,40.695217],[-8.345146,40.714476],[-8.347549,40.736592],
    [-8.382225,40.740494],[-8.391151,40.760001],[-8.389091,40.791719],
    [-8.398361,40.801076],[-8.393555,40.815888],[-8.404541,40.820565],
    [-8.412781,40.839788],[-8.420334,40.81329],[-8.434753,40.818486],
    [-8.441277,40.827579],[-8.438873,40.840827],[-8.470802,40.81303],
    [-8.464279,40.804714],[-8.44574,40.806273],[-8.44162,40.796398],
    [-8.448143,40.786261],[-8.463593,40.782361],[-8.472862,40.774302],
    [-8.471146,40.768582],[-8.474579,40.75688],[-8.484535,40.744396],
    [-8.485222,40.728527],[-8.484535,40.710052],[-8.512344,40.695217],
    [-8.532257,40.680638],[-8.555603,40.686105],[-8.556976,40.666577],
    [-8.54496,40.662931],[-8.542557,40.65095],[-8.519554,40.647564],
    [-8.528137,40.634538],[-8.502731,40.629588],[-8.500328,40.639488],
    [-8.485909,40.640009],[-8.482132,40.631151],[-8.469429,40.642875],
    [-8.469772,40.650169],[-8.479729,40.656941],[-8.466682,40.658764],
    [-8.449173,40.654597],[-8.454323,40.642875],[-8.440933,40.640791],
    [-8.422394,40.623855]
  ]]
}

folium.GeoJson(
  custom_polygon,
  name="Portugal Focus Area",
  style_function=lambda x: {
    'fillColor': '#ff0000',  # Red fill
    'color': '#ff0000',      # Red border
    'weight': 2,
    'fillOpacity': 0.3
  },
  tooltip="Portugal Focus Areas"
).add_to(m)

# Add layer control and save
folium.LayerControl().add_to(m)
m.save("overlay_map.html")
m # Display in Jupyter Notebook
```

## Row {.tabset}

```{r}
library(imager)

# Load the image
image_path <- "../photo/Portugal/NDVI_before_Portugal.jpg"
img <- load.image(image_path)

# Display the image
plot(img, axes = F)
```

