# Chargement des librairies nécessaires
library(shiny)
library(shinydashboard)
library(tidyverse)
library(leaflet)

ui <- dashboardPage(
  # En-tête du dashboard
  dashboardHeader(title = HTML("CLC Change Tracker")),
  
  # Barre latérale du dashboard
  dashboardSidebar(
    sidebarMenu(
      menuItem("NUTS3 Change Tracker", tabName = "tabfe", icon = icon("table")), 
      menuItem(HTML("Change Tracker<br>Visualisation in NUTS3"), 
               tabName = "fev", 
               icon = icon("fas fa-map")),
      menuItem("Change Detection", tabName = "cd", icon = icon("chart-bar"))
    ),
    
    # Add custom PNG images at the end of the sidebar
    tags$div(
      style = "position: absolute; top: 210px; left :10px;",  # Positioning at the bottom of the sidebar
      tags$img(src = "BDH.jpg",height = "50px")  # First Image
      ),
    
    tags$div(
      style = "position: absolute; top: 275px;left :18px;",  # Positioning at the bottom of the sidebar
      tags$img(src = "statbel.jpg",height = "60px")
    ) 
    ),
  
  # Contenu principal du dashboard
  dashboardBody(
    
    tags$head(
      tags$style(HTML("
    .skin-blue .main-header .navbar {
      background-color: #2644A7;  /* Changed red to #388AE3 */
    }
    .skin-blue .main-header .logo {
      background-color: #2644A7;  /* Changed green to #388AE3 */
    }
    .skin-blue .main-sidebar {
      background-color: #1C4041;  /* Changed pink to #388AE3 */
    }
    
    .box .box-header {
          background-color: #388AE3;  /* Set your desired background color*/
          color: white;  /* Optional: Change the text color to white for contrast */
        }"
                      )
                 )
      ),
      
    tabItems(
      # ---- Onglet 1 : Change Tracker Table ----
      tabItem(tabName = "tabfe",
              
              fluidRow(
                box(width = 12, title = "Select NUTS Level", solidHeader = TRUE,
                    selectInput(inputId = "nuts_level",
                                label = "",
                                choices = NULL,
                                selected = "NUTS_3")
                )
              ),
              
              fluidRow(
                box(
                  width = 12, 
                  title = "Corine Land Cover Change Tracker data", status = "info", solidHeader = TRUE,
                  div(style = "height: 70vh; overflow-y: auto;",  # Adjust height dynamically
                      dataTableOutput("data_fe")
                  )
                )
              ),
              
              fluidRow(
                box(
                  width = 12, 
                  title = "Download Data",
                  solidHeader = TRUE,
                  p("Choose a format and download the file"),
                  selectInput(inputId = "download_type", 
                              label ="Select Download Format:", 
                              choices = c("Spreadsheet (.xlsx)" = "xlsx","SDMX-CSV" = "csv")),
                  downloadButton("downloadData", "Download Data")
                )
              )
      ),
      
      # ---- Onglet 2 : Change Tracker Visualisation ----
      tabItem(tabName = "fev",
              fluidRow(  # Make the entire row fluid
                column(width = 12,
                       box(width = 12, title = "Select NUTS3", solidHeader = TRUE,
                           selectInput(inputId = "selected_nuts3",
                                       label = "NUTS3 subset :",
                                       choices = NULL,
                                       selected = NULL),
                           selectInput(inputId = "year",
                                       label = "Year :",
                                       choices = NULL,
                                       selected = NULL)
                       )
                )
              ),
              
              fluidRow(  # Another fluid row for map and pie chart
                column(width = 8,  # Map box takes 8/12 of the row
                       box(width = 12, title = "Map", solidHeader = TRUE,status = "info",
                           plotOutput("map", height = "480px", width = "100%")
                       )
                ),
                column(width = 4,  # Pie chart box takes 4/12 of the row
                       box(width = 12, title = "Land Cover Type", solidHeader = TRUE,
                           plotOutput("pie_chart", height = "480px")  # Increase the height for more space
                       )
                )
              )
      ),
      
      # ---- Onglet 3 : Change Detection ----
      tabItem(tabName = "cd",
              fluidRow(column(width = 6,
                              box(width = 12, title = "Select NUTS3", solidHeader = TRUE,
                                  selectInput(inputId = "nuts3_selected",
                                       label = "NUTS3 subset :",
                                       choices = NULL,
                                       selected = NULL)
                       )
                ),
                column(width = 6,  # Slider
                       box(width = 12, title = "Slider", solidHeader = TRUE,
                           sliderInput("slider", 
                                       label = "Slide to year :",
                                       min = 2018, 
                                       max = 2024, 
                                       value = 2018,
                                       step = 1,  # Ensures the slider moves year by year
                                       animate = animationOptions(
                                         interval = 5000,  # Duration of each animation step (milliseconds)
                                         loop = FALSE,    # Whether the animation should loop
                                       ),  # Smooth transition for slider movement
                                       ticks = TRUE,
                                       sep = "",
                                       dragRange = TRUE# Removes the default ticks on the slider
                                       )
                           )
                       )
                ),
              
              fluidRow(  # Second row with Map
                column(width = 12,  # Full width for the map
                       box(width = 12, title = "Map", solidHeader = TRUE,status = "info",
                           plotOutput("map_slider", height = "600px")  # Set a specific height for the map
                       )
                )
              )
      )
    )
  )
)
