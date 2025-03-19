output$mapTab3 <- renderPlotly({
  
  choices <- mapSel()
  
  plot_ly(choices, split = ~NUTS_NAME, color = ~values,
          text = ~NUTS_NAME, 
          colors = c("#dddddd", "#0c4594"),
          hoverinfo = "text", # White borders
          showlegend = FALSE) %>%
    config(displayModeBar = F) %>%
    highlight_key() %>%
    layout(dragmode=F) %>%
    layout(
      paper_bgcolor = 'rgba(0,0,0,0)',  # Fully transparent background
      plot_bgcolor = 'rgba(0,0,0,0)'    # Fully transparent plot area
    ) %>%
    layout(
      clickmode = "event+select") %>% 
    event_register(event = 'plotly_click') 
  
})


country <- reactive({
  
  choices <- mapSel()
  country <- choices[as.numeric(event_data("plotly_click")$key), ]
  
  if(nrow(country) == 0) {
    country =  mapSel() %>% dplyr::filter(NUTS_NAME == "Nyski")
  } else {
    country = country
  }
  country
})

output$mapTab2 = renderLeaflet({
  
  req(country())
  req(totalCountryPop())
  req(input$selectDateMap)
  
  data <- country()
  dzien <- paste0(gsub("\\-", "", input$selectDateMap), ".tiff")
  
  if(data$NUTS_NAME %in% c("Jihomoravský kraj", "Nyski")) {
    
    sf_multipoly <- st_sfc(data[1,]$geometry)
    coords <- st_coordinates(sf_multipoly)
    
    flood <- rast(paste0("./www/rast/",tolower(data$NUTS_NAME), "/", dzien)) 
    flood <- project(flood, "EPSG:4326")
    
    flood <- mask(flood, vect(data))
    popul <- mask(totalCountryPop(), vect(data))
    
    leaflet() %>%
      addProviderTiles("OpenStreetMap.Mapnik") %>% 
      addRasterImage(popul, opacity = 0.7, maxBytes = Inf, group = "population grid") %>%
      addRasterImage(flood, opacity = 0.6, group = "flood") %>% 
      addPolygons(data = data, weight = 4,fill=F,
                  color = "black"
      ) %>% 
      fitBounds(
        lat1 = min(coords[,2]),
        lat2 = max(coords[,2]),
        lng1 = min(coords[,1]),
        lng2 = max(coords[,1])
      ) %>% 
      addLayersControl(overlayGroups = c("flood", "population grid"))
    
  }
  
})


output$mapTabComp2 <- renderLeaflet({
  
  req(country())
  req(totalCountryPop())
  req(input$selectDateMap)
  
  dzien <- paste0(gsub("\\-", "", input$selectDateMap), ".tiff")
  data <- country()
  
  if(data$NUTS_NAME %in% c("Jihomoravský kraj", "Nyski")) {
    
    sf_multipoly <- st_sfc(data[1,]$geometry)
    coords <- st_coordinates(sf_multipoly)
    
    flood <- rast(paste0("./www/rast/",tolower(data$NUTS_NAME), "/", dzien)) 
    flood <- project(flood, "EPSG:4326") 
    
    flood <- mask(flood, vect(data))
    popul <- mask(totalCountryPop(), vect(data))
    
    leaflet() %>% 
      addMapPane("right", zIndex = 0) %>% 
      addMapPane("left",  zIndex = 0) %>% 
      addTiles(group = "base", layerId = "baseid1", options = pathOptions(pane = "right")) %>% 
      addTiles(group = "base", layerId = "baseid2", options = pathOptions(pane = "left")) %>% 
      addRasterImage(x = flood, options = leafletOptions(pane = "right"), group = "flood") %>% 
      addRasterImage(x = popul, options = leafletOptions(pane = "left"), group = "population grid", maxBytes = Inf) %>% 
      addLayersControl(overlayGroups = c("flood", "population grid")) %>% 
      addSidebyside(layerId = "sidecontrols",
                    rightId = "baseid1",
                    leftId  = "baseid2") %>%
      addPolygons(data = data, weight = 4,fill=F,
                  color = "black"
      ) %>% 
      fitBounds(
        lat1 = min(coords[,2]),
        lat2 = max(coords[,2]),
        lng1 = min(coords[,1]),
        lng2 = max(coords[,1])
      )
  }
})

##### wykresy pogodowe ####

output$weatherOutput <- renderPlotly({
  
  req(country())
  req(input$weatherDateSel)
  data <- country()
  
  if(data$NUTS_NAME %in% c("Jihomoravský kraj", "Nyski")) {
    
    choice <- case_when(
      grepl("kraj",  data$NAME_LATN) ~ "cz",
      grepl("Nyski",  data$NAME_LATN) ~ "pl",
    )
    
    grouping <- case_when(
      grepl("daily",  input$weatherAggr) ~ "day",
      grepl("weekly",  input$weatherAggr) ~ "week",
      grepl("monthly",  input$weatherAggr) ~ "month",
      grepl("quarterly",  input$weatherAggr) ~ "quarter"
    )
    
    data <- read.csv(paste0("./www/data/tp_", choice, ".csv")) %>%
      dplyr::mutate(
        date = lubridate::floor_date(as.Date(date), !!grouping) + months(1)
      ) %>% 
      dplyr::group_by(date) %>% 
      dplyr::summarise(
        total_tp = sum(total_tp)
      ) %>% 
      dplyr::filter(between(date, as.Date(input$weatherDateSel[1]), as.Date(input$weatherDateSel[2]))) %>% 
      dplyr::select(
        date, total_tp
      )
    
    plot_ly(data, x = ~date, y = ~total_tp, type = 'bar') %>% 
      layout(
        paper_bgcolor = 'rgba(0,0,0,0)',  # Fully transparent background
        plot_bgcolor = 'rgba(0,0,0,0)'    # Fully transparent plot area
      ) %>%
      plotly::layout(
        title = 'Total Precipitation',
        xaxis = list(title = "Date", showgrid = FALSE),
                     yaxis = list(title = "Total Precipitation", showgrid = FALSE))
    
  } else {
    
    show_alert(
      title = "No data!",
      text = "Please select a different NUTS3 Region",
      type = "info"
    )
    
    
  }
  
})


output$datePickerTab2 <- renderUI({
  
  data <- c("2024-09-15", "2024-09-18", "2024-09-23", "2024-09-30")
  
  disabledDates <-  seq.Date(as.Date(data[1]), as.Date(data[length(data)]), by = "day")
  disabledDates <- disabledDates[!(disabledDates %in% data)]
  
  airDatepickerInput(
    inputId = "selectDateMap",
    label = "Select a date to check the flooded area:", 
    minDate = data[1],
    maxDate = data[length(data)],
    value = data[1],
    disabledDates = disabledDates,
    width = "100%"
  )
  
})


output$peopleWhoSuff <- renderValueBox({
  
  req(country())
  
  data <- country()
  
  choice <- case_when(
    grepl("kraj",  data$NUTS_NAME) ~ 187324,
    TRUE ~  47372
  )
  
  valueBox(
    color = "info",
    width = 12,
    value = paste0("est. ", format(choice, big.mark = " ")),
    subtitle = paste0("people in NUTS3 Region ",  data$NUTS_NAME, " was affected by flood!"),
    icon = icon("people-group")
  )
  
})


