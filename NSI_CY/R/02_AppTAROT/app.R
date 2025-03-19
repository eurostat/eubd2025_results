
library(dplyr)
library(data.table)
library(sf)
library(leaflet)
library(shiny)
library(shinydashboard)

setwd("~/R/02_AppTAROT/")
ccodes <- readRDS("data_supp/NUTS0_geonames_map.rds")
myears <- readRDS("data_supp/PeriodsInFilter.rds")
corr_eqn <- readRDS("data_supp/CorrExpEqnCoeffs_PMg5.rds")

ui <- dashboardPage(
  dashboardHeader(title = "TAROT"),
  dashboardSidebar(
    sidebarMenu(
      titlePanel("The AiR Out There"),
      menuItem("Leaflet Map", tabName = "leaflet_tab", icon = icon("map")),
      selectInput("upto_myear","Month:", myears[12:length(myears)]),
      selectInput("zoom_ccode","Country:", choices = setNames(c(NA,ccodes$CNTR_CODE), c("Choose",ccodes$CNTR_NAME))),
      selectInput("nuts_lvl","NUTS Level:", choices = setNames(c(0,1,2,3), c("NUTS0","NUTS1","NUTS2","NUTS3") )),
      tags$div(
        style = "text-align: center; padding: 10px; position: absolute; bottom: 30; width: 100%;",
        tags$img(src = "logo_minimal.png", width = "150px")
      )
    )
  ),
  dashboardBody(
    tabItems(
      tabItem(tabName = "leaflet_tab",
              fluidRow(
                box(width = 12, height="90vh", leafletOutput("map", height = "87vh"))
              )
      )
      
    )
  )
)


server <- function(input, output) {
  
  # Filtered data based on NUTS level and TIME_PERIOD
  filtered_data <- reactive({
    indx <- which(myears==input$upto_myear)
    periods <- myears[(indx-11) : indx]
    
    data_list <- list()
    for(p in 1:length(periods)){
      myear <- periods[p]
      dt <- readRDS(paste0("data/Estimate_PremDths_",myear,".rds"))
      if(p==length(periods)){
        polygon_map <- unique(select(dt, c("CNTR_CODE","geo","LEVL_CODE","geometry","population_CNTR","area_km2_CNTR")))
      }
      dt$geometry <- NULL
      dt <- as.data.table(dt)
      data_list <- c(data_list, list(dt))
      rm(myear, dt)
    }
    shinydt_inn <- rbindlist(data_list, use.names = T)
    rm(data_list)
    
    shinydt_inn <- shinydt_inn[, .(ND2I_AvgNrDDays = sum(ND2I_AvgNrDDays,na.rm=T)), 
                                  by=c("LEVL_CODE","CNTR_CODE","geo", "geo_name")]
    shinydt_inn <- left_join(polygon_map , shinydt_inn, by=c("CNTR_CODE","geo","LEVL_CODE"))
    shinydt_inn <- mutate(shinydt_inn, EstPremDeatsRate = round(exp((corr_eqn$s * ND2I_AvgNrDDays) + corr_eqn$i) - corr_eqn$b))
    shinydt_inn <- mutate(shinydt_inn, EstPremDeatsNmbr = round(EstPremDeatsRate*population_CNTR/100000))
    shinydt_inn
  })
  
  # Create the Leaflet map
  output$map <- renderLeaflet({
    
    selected_geo <- filtered_data() %>%
      filter(LEVL_CODE==input$nuts_lvl)
    
    leaflet(selected_geo, options = leafletOptions(minZoom = 2.2)) %>%
      setView(lng = 10, lat = 52, zoom = 4) %>%
      addTiles() %>% 
      {
        quantiles <- quantile(selected_geo$EstPremDeatsRate, probs = c(0, 0.25, 0.5, 0.75, 1), na.rm = TRUE)
        pal <- colorBin("YlOrRd", domain = selected_geo$EstPremDeatsRate, bins = quantiles)
        addPolygons(.,
                    fillColor = ~pal(EstPremDeatsRate),
                    fillOpacity = 0.7,
                    color = "black",
                    weight = 1,
                    highlightOptions = highlightOptions(
                      color = "red",
                      weight = 2,
                      bringToFront = TRUE
                    ),
                    label = ~geo_name,
                    popup = ~paste0(geo_name, " (Population: ", format(population_CNTR, big.mark = ","), ")",
                                    "<b><u><br>Premature Deaths Rate:</u> ", format(EstPremDeatsRate, big.mark = ","), " / 100k popln</b>",
                                    "<b><u><br>Premature Deaths Number:</u> ", format(EstPremDeatsNmbr, big.mark = ","), "</b>"
                    )
        ) %>%
          addLegend(
            pal = pal,
            values = ~EstPremDeatsRate,
            title = "Premature Deaths Rate<br>(Per 100,000 inhabitants)",
            opacity = 1
          )
      }
  })
  
  
  # Choose and zoom into a specific Country
  observeEvent(input$zoom_ccode, {
    
    selected_country <- filtered_data() %>%
      filter(LEVL_CODE==0, geo == input$zoom_ccode)
    if (nrow(selected_country) > 0) {
      # Option 1: Using bounding box (fitBounds)
      bounds <- sf::st_bbox(selected_country)
      leafletProxy("map") %>%
        flyToBounds(
          lng1 = bounds[["xmin"]],
          lat1 = bounds[["ymin"]],
          lng2 = bounds[["xmax"]],
          lat2 = bounds[["ymax"]],
          options = list(duration = 1)
        )
    }
    
    
  })
  
  
}

shinyApp(ui = ui, server = server)




