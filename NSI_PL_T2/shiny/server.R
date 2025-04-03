function(input, output, session) {
  waiter::waiter_hide()
  for(file in list.files("server")) {
    source(file.path("server", file), local = T)
  }
  
  
  output$countryButtons <- renderUI({
    choices <- paste0("flags/", list.files("www/flags/")[grepl(paste(tolower(selected), collapse = "|"), list.files("www/flags/"))])
    
    radioButtons(inputId = "countryInput", label = "Choose the country", inline = TRUE,
                 selected = "Poland",
                 choiceNames = lapply(choices, function(x) img(src = x)),
                 choiceValues = as.list(sort(selected))
    )
    })
  
  nutsRegion <- reactive({
    
    req(input$countryInput)
    
    choice <- case_when(
      grepl("Czech",  input$countryInput) ~ "Czechia",
      TRUE ~  input$countryInput
    )
    
    choices <- giscoR::gisco_get_nuts(nuts_level = 3, resolution = "01", epsg = "4326", year = "2021") %>% 
      dplyr::filter(CNTR_CODE == as.character(giscoR::gisco_countries %>% dplyr::filter(NAME_ENGL %in% choice) %>% dplyr::select(CNTR_ID))[1])
    
  })
  
  
  mapSel <- reactive({
    choices <- giscoR::gisco_get_nuts(nuts_level = 3, resolution = "01", epsg = "4326", year = "2021") %>% 
      dplyr::filter(grepl("PL|CZ", CNTR_CODE))
    choices$values <- 1
    choices$values[choices$NUTS_NAME %in% c("Jihomoravský kraj", "Nyski")] <- 10
    choices
  })
  
  totalCountryPop <- reactive({
    r2 <- project(rast("./mapki/ESTAT_OBS-VALUE-POPULATED_2021_V2.tiff"), "EPSG:4326")
    extent_new <- ext(12.0921, 24.14544, 48.55183, 54.83568)
    r_cropped <- crop(r2, extent_new)
    r_cropped
  })
}

