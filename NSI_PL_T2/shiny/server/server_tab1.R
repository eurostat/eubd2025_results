#fluidRow2 #########

obrazki <- reactive({
  
  
  obrazki <- paste0("flood/", tolower(input$krajUITab2), "/", list.files(paste0("www/flood/", tolower(input$krajUITab2))))
  dataInfo <- as.Date(gsub("\\.png", "", list.files(paste0("www/flood/", tolower(input$krajUITab2)))), format="%Y%m%d")
  
  list(obrazki, dataInfo)
})

output$summaryTab3 <- renderUI({
  req(input$krajUITab2)
  req(input$countryInput)
  tags$div(style = "text-transform:uppercase;width:100%;text-align:center;color:white;font-size:30px", 
           tags$div(HTML(input$countryInput,  "</b> NUTS3 ", input$krajUITab2, "REGION")),
           tags$div(style = "font-size:15px; text-transform:initial;", HTML("The entire NUTS3 region is shown on the left, while a selected section of the region is displayed on the right for a more detailed look at the flooded area."))
           )
  
})


output$vbox1 <- renderSlickR({
  
  req(input$krajUITab2)
  
  if(input$krajUITab2 %in% c("Jihomoravský kraj", "Nyski")) {
    
    slickR(slideId = "sld1", obj = obrazki()[[1]], slideType = c("img")) + 
      settings(dots = F, adaptiveHeight = F, fade = T, autoplay = T, autoplaySpeed = 1500, speed = 500)
    
  } else {
    
    show_alert(
      title = "No data!",
      text = "Please select a different NUTS3 REGION",
      type = "info"
    )
    
  }
  
})

active_slick <- shiny::reactiveValues()

shiny::observeEvent(input$vbox1_current,{
  
  center_slide     <- input$vbox1_current$.center
  active_slick$center     <- input$vbox1_current$.center
  
})

output$opisKaruzeli <- renderUI({
  
  tags$div(obrazki()[[2]][active_slick$center], class="headerKaruzela")
  
})


output$selectNUTS3 <- renderUI({
  
  req(nutsRegion())
  
  pickerInput(
    inputId = "krajUITab2", label = "Select a NUTS3 Region", 
    choices = sort(nutsRegion()$NUTS_NAME),
    selected = sort(nutsRegion()$NUTS_NAME)[sort(nutsRegion()$NUTS_NAME) %in% c("Jihomoravský kraj", "Nyski")],
    options = pickerOptions(container = "body", 
                            title = "Select a NUTS3 Region"),
    width = "70%"
  )
  
})

output$obrazekTab2 <- renderPlotly({
  
  req(input$countryInput)
  
  data <- data.frame(
    geo = "geo", 
    type = "choropleth", 
    z = rep(1, length(ue)), 
    showscale = F, 
    locationmode = "country names", 
    locations = ue) %>% 
    dplyr::filter(locations == input$countryInput)
  
  plot_ly(
    data,
    source= "obrazekTab2",
    geo = "geo",
    type = "choropleth",
    locations = data$locations,
    locationmode = "country names",
    z = data$z,
    hoverinfo="none",
    showscale = F,
    colorscale = list(c(0, 1), c("white", "white")),  # Grey color for all countries
    marker = list(line = list(color = "rgba(0,0,0,0)", width = 0.5))  # White borders
  ) %>% 
    layout(
      geo = list(
        framecolor = "rgba(0,0,0,0)", 
        scope = 'europe',
        domain = list(
          x = c(0, 1), 
          y = c(0, 1)
        ),
        showland = TRUE, 
        landcolor = "rgba(0,0,0,0)", 
        showframe = TRUE, 
        projection = list(type = "conic conformal"), 
        resolution = 50, 
        countrycolor = "rgba(0,0,0,0)", 
        coastlinecolor = "rgba(0,0,0,0)", 
        showcoastlines = TRUE,
        fitbounds='locations'
      )) %>%
    config(displayModeBar = F) %>%
    layout(dragmode=F) %>%
    layout(
      paper_bgcolor = 'rgba(0,0,0,0)',  # Fully transparent background
      plot_bgcolor = 'rgba(0,0,0,0)'
    )
  
  
})


obrazki1 <- reactive({
  obrazki <- paste0("flood_zoom/", tolower(input$krajUITab2), "/", list.files(paste0("www/flood_zoom/", tolower(input$krajUITab2))))
  dataInfo <- as.Date(gsub(".*\\_", "", gsub("\\.png", "", list.files(paste0("www/flood_zoom/", tolower(input$krajUITab2))))), format="%Y%m%d") %>% sort()
  
  list(obrazki, dataInfo)
})


output$vbox2 <- renderSlickR({
  
  req(input$krajUITab2)
  
  if(input$krajUITab2 %in% c("Jihomoravský kraj", "Nyski")) {
    slickR(slideId = "sld2", obj = obrazki1()[[1]], slideType = c("img")) + 
      settings(dots = F, adaptiveHeight = F, fade = T, autoplay = T, autoplaySpeed = 1500, speed = 500)
    
  }
  
})


active_slick1 <- shiny::reactiveValues()

shiny::observeEvent(input$vbox2_current,{
  active_slick1$center     <- input$vbox2_current$.center
})

output$opisKaruzeli1 <- renderUI({
  tags$div(obrazki1()[[2]][active_slick1$center], class="headerKaruzela1")
  
})
# fluidRow3 ###########

output$clustersPlot <- renderPlotly({
  
  req(input$countryInput)
  
  choice <- case_when(
    grepl("Czech",  input$countryInput) ~ "cz",
    grepl("Poland",  input$countryInput) ~ "pl",
  )
  
  cluster = read.csv("./www/data/combined_pixel_stats.csv") %>%
    dplyr::filter(
      country == !!choice
    ) %>% 
    dplyr::arrange(Date) %>% 
    dplyr::mutate(
      Date = as.Date(Date)
    )
  
  plot_ly(cluster, x = ~Date, y = ~`Edge.Density`, type = 'scatter', mode = 'lines') %>% 
    layout(dragmode=F) %>%
    layout(
      paper_bgcolor = 'rgba(0,0,0,0)',  # Fully transparent background
      plot_bgcolor = 'rgba(0,0,0,0)'    # Fully transparent plot area
    ) %>%
    layout(yaxis = list(title = "Edge Density"))
  
})


output$floodArea <- renderValueBox({
  
  choice <- case_when(
    grepl("Czech",  input$countryInput) ~ 16.23,
    TRUE ~  13.43
  )
  
  valueBox(
    color = "info",
    width = 12,
    value = paste0(choice, "%"),
    subtitle = paste0("of a NUTS3 Region ", input$krajUITab2, " was affected by flood!"),
    icon = icon("panorama")
  )
  
})


output$weatherOutputTab <- renderDataTable({
  
  req(input$countryInput)
  
  choice <- case_when(
    grepl("Czech",  input$countryInput) ~ "cz",
    grepl("Poland",  input$countryInput) ~ "pl",
  )
  
  cluster = read.csv("./www/data/combined_pixel_stats.csv") %>%
    dplyr::filter(
      country == !!choice
    ) %>% 
    dplyr::arrange(Date) %>% 
    dplyr::mutate(
      Date = as.Date(Date)
    ) %>% 
    dplyr::select(-country) %>% 
    dplyr::select(Date, everything()) %>% 
    dplyr::mutate_at(vars("Mean.Intensity", "Median.Intensity", "Std.Dev.Intensity", "Skewness", "Kurtosis", "Entropy", "Edge.Density"), funs(round(., 2)))
  
  colnames(cluster) <- gsub("\\.", " ", colnames(cluster))
  
  datatable(cluster,rownames = FALSE, extensions = 'Buttons',
            options = list(dom='Bfrtip',
                           buttons=c('copy', 'csv', 'excel'),
                           scrollX = TRUE))
  
})