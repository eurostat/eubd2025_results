fluidPage(
  fluidRow(
    class="init1"
  ),
  fluidRow(
    class="overRow",
    box(
      width = 12,
      title = HTML('Select NUTS3 Region on the map below (Nyski or Jihomoravský kraj) and check the flood-related data'),
      collapsible = F,
      fluidRow(
        width = 12,
        column(
          width = 5,
          valueBoxOutput("peopleWhoSuff", width = 12),
          br(),
          div(style ="padding:0px 15px", HTML("<b>Sentinel-1 decibel Gamma0 orthorectified radar data for a NUTS 3 area</b> was analyzed before and after a flood event. Thresholding was applied, and VV-band backscatter values were compared, with pixels classified as flooded if the reduction exceeded 0.05. A population density raster was then overlaid to estimate the affected population in the flooded regions."))
        ),
        column(
          class="mapki",width = 7, plotlyOutput("mapTab3"))
      ),
      fluidRow(
        width = 12,
        class = "weatherD",
        column(width = 6, 
               radioButtons("weatherAggr", label = "Select grouping type to check the sum of precipitation:",choices = c("daily", "weekly", "monthly", "quarterly"), selected = "monthly", inline = T)),
        column(width = 6, 
               airDatepickerInput(
                 inputId = "weatherDateSel",
                 label = "Specify the date range of the total precipitation plot:", 
                 minDate = as.Date('2024-01-01'),
                 maxDate = as.Date("2024-12-31"),
                 value = c(as.Date('2024-07-01'), as.Date("2024-12-31")),
                 range = TRUE,
                 width = "100%"
               ))
      ),
      column(width = 12, plotlyOutput("weatherOutput")),
      uiOutput("datePickerTab2"),
      HTML("Two layers - population grid and flood mask shows how many people lived on the flooded area"),
      br(),
      fluidRow(width = 12,
               column(width = 6,
                      leafletOutput("mapTab2")),
               column(width = 6,
                      leafletOutput("mapTabComp2")))
    )
  )
)