library(shiny)
library(leaflet)
library(sf)
library(dplyr)
library(ggplot2)
library(readr)
library(arrow)
library(shinythemes)

# Read in NDVI monthly data
ireland_data1K <- read_csv("1kgrid-stats2.csv")
france_data <- read_csv("FR_p1_month.csv")
ireland_data <- read_csv("IE_p1_month_gridstats.csv")

# Read maps and combine with tables
map_ire <- st_read("Ireland_1km_NUTS3_IE052_sel_2_2018_2023_CROP_Comparision_results_POLYGON_WGS84.shp") %>%
  left_join(ireland_data1K %>% select(-1), by = 'fid') %>%
  mutate(spring_bare_parcels = case_when(spring.bare.parcels<10 ~ '<10',
                                         spring.bare.parcels<20 ~ '<15',
                                         spring.bare.parcels<30 ~ '<20',
                                         spring.bare.parcels<10 ~ '<25',
                                         spring.bare.parcels<20 ~ '<30',
                                         spring.bare.parcels<30 ~ '<35',
                                         spring.bare.parcels>=40 ~ '\u2264 40',
                                         TRUE ~'NA'),
         autumn_bare_parcels = case_when(autumn.bare.parcels<10 ~ '<10',
                                         autumn.bare.parcels<20 ~ '<15',
                                         autumn.bare.parcels<30 ~ '<20',
                                         autumn.bare.parcels<10 ~ '<25',
                                         autumn.bare.parcels<20 ~ '<30',
                                         autumn.bare.parcels<30 ~ '<35',
                                         autumn.bare.parcels>=40 ~ '\u2264 40',
                                         TRUE ~'NA'))
map_fr <- sf::st_as_sf(read_parquet("part1_fr_wgs84.parquet") %>%
  left_join(france_data %>% select(-1), by = 'feature_index'))

# UI
ui <- navbarPage(
  "NDVI Analysis",
  theme = shinytheme("darkly"),
  
  # First Tab - Ireland Map
  tabPanel("Ireland Map",
           tags$style(HTML("
        #map_ire { position: absolute; top: 50px; bottom: 0; width: 100%; }
        .leaflet-container { height: calc(100vh - 56px) !important; }
    ")),  
           div(
             leafletOutput("map_ire"), # Map auto-adjusts to available space
             absolutePanel(
               top = 80, left = 20, width = 250, draggable = TRUE, class = "panel panel-default",
               style = "background-color: rgba(255, 255, 255, 0.8); padding: 10px; border-radius: 10px;",
               selectInput("color_var_ire", "Choose variable to color map:", 
                           choices = c("Spring" = "spring", "Autumn" = "autumn"))
             )
           )
  ),
  
  
  
  # Second Tab - France Map
  tabPanel("France Map",
           leafletOutput("map_fr", height = "600px")
  ),
  
  # Third Tab - NDVI Plots
  tabPanel("NDVI Trends",
           sidebarLayout(
             sidebarPanel(
               selectizeInput("feature_input", label = 'Choose a feature in Ireland:', choices = unique(ireland_data$feature_index), options = list(
                 placeholder = 'Type a feature index', maxOptions = 5)),
               selectizeInput("feature_inputF", label = 'Choose a feature in France:', choices = unique(france_data$feature_index), options = list(
                 placeholder = 'Type a feature index', maxOptions = 5))
             ),
             mainPanel(
               plotOutput("ire_plot"),
               plotOutput("fr_plot")
             )
           )
  )
)

# Server
server <- function(input, output, session) {
  
  # Render Irish Map
  output$map_ire <- renderLeaflet({
    req(input$color_var_ire)
    selected_var <- input$color_var_ire
    if (selected_var=='spring_bare_parcels') {
      map_ire_leaf <- map_ire %>% rename(var = spring_bare_parcels)
    } else {
      map_ire_leaf <- map_ire %>% rename(var = autumn_bare_parcels)
    } 
    
    pal_ire <- colorFactor(palette = "Set1", domain = map_ire_leaf$var)
    
    leaflet(map_ire_leaf) %>%
      addTiles() %>%
      addPolygons(
        fillColor = ~pal_ire(var),
        fillOpacity = 0.7,
        color = "#BDBDC1",
        weight = 1
      ) %>%
      addLegend(
        pal = pal_ire, values = ~var,
        position = "bottomright",
        title = "Spring bare parcels"
      )
  })

  # Render French Map
  output$map_fr <- renderLeaflet({
    pal_fr <- colorFactor(palette = "Set1", domain = map_fr$year_drop)
    
    leaflet(map_fr) %>%
      addTiles() %>%
      addPolygons(
        fillColor = ~pal_fr(year_drop),
        fillOpacity = 0.7,
        color = "#BDBDC1",
        weight = 1
      ) %>%
      addLegend(
        pal = pal_fr, values = ~year_drop,
        position = "bottomright",
        title = "Year Drop"
      )
  })
  
  # Irish NDVI time series
  output$ire_plot <- renderPlot({
    req(input$feature_input)
    filtered_ire <- ireland_data %>% filter(feature_index == input$feature_input)
    
    ggplot(filtered_ire, aes(x = date, y = ndvi_month)) +
      geom_line(color = "blue") +
      geom_point(color = "blue") +
      labs(title = paste("NDVI in Ireland for Feature ", input$feature_input), x = "Date", y = "NDVI") +
      theme_minimal()
  })
  
  # French NDVI time series
  output$fr_plot <- renderPlot({
    req(input$feature_input)
    filtered_fr <- france_data %>% filter(feature_index == input$feature_inputF) %>% mutate(date = as.Date(month))
    
    ggplot(filtered_fr, aes(x = date, y = ndvi_month)) +
      geom_line(color = "red") +
      geom_point(color = "red") +
      labs(title = paste("NDVI in France for Feature", input$feature_inputF), x = "Date", y = "NDVI") +
      theme_minimal()
  })
}

# Run the app
shinyApp(ui, server)
