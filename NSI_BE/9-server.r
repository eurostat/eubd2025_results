library(shiny)
library(readr)
library(dplyr)
library(leaflet)
library(sf)
library(plotly)
library(ggplot2)

directory <- dirname(rstudioapi::getActiveDocumentContext()$path)
sentinel <- readRDS(paste0(directory,"/preprocessed_data/sentinel.rds"))
# sentinel <- readRDS(paste0(directory,"/preprocessed_data/sentinel_test.rds"))
nuts_aggregated <- readRDS(paste0(directory,"/preprocessed_data/nuts_aggregated.rds"))
nuts_aggregated_nuts3 <- readRDS(paste0(directory,"/preprocessed_data/nuts_aggregated_nuts3.rds"))
nuts_aggregated_nuts2 <- readRDS(paste0(directory,"/preprocessed_data/nuts_aggregated_nuts2.rds"))


# sentinel_backup <- sentinel

# ajouter à sentinel les dummy des bonnes couleurs
# sentinel <- sentinel %>%
#   mutate(color_var = case_when(
#     final_clc_fe == 1 & change == "change" ~ "Urbanisation",
#     final_clc_fe == 1 & change != "change" ~ TX_CLC_LVL0,
#     final_clc_fe == 2 & change == "change" ~ "Vegetalisation",
#     final_clc_fe == 2 & change != "change" ~ TX_CLC_LVL0,
#     final_clc_fe == 3 ~ TX_CLC_LVL0
#   ))
# write_rds(sentinel,paste0(directory,"/preprocessed_data/sentinel.rds"))

# sentinel_test <- sentinel %>% filter(NUTS_ID %in% c("BE211","BE213"),
#                          year %in% c(2018,2021,2024))
# write_rds(sentinel_test,paste0(directory,"/preprocessed_data/sentinel_test.rds"))
# 
# 
# nuts_aggregated <- nuts_aggregated %>%
#   select(NUTS_3, year, TX_LAND_COVER = LAND_COVER, NM_LAND_COVER = CODE_LC, PCT_AREA) %>%
#   mutate(PCT_AREA = round(PCT_AREA * 100, 4)) %>%
#   pivot_wider(
#     names_from = year,  # Create a column for each unique year
#     values_from = PCT_AREA  # Values for each year will be from PCT_AREA
#   )

# write_rds(nuts_aggregated,paste0(directory,"/preprocessed_data/nuts_aggregated_download.rds"))

# sentinel change en 2018 ?
# sentinel <- sentinel %>%
#   mutate(color_var = recode(color_var,"Urbanisation" = "Urbanization")) %>%
#   mutate(color_var = recode(color_var,"Vegetalisation" = "De-urbanization"))
# write_rds(sentinel,paste0(directory,"/preprocessed_data/sentinel.rds"))

# legend <- readRDS(paste0(directory,"/preprocessed_data/clc_legend_cleaned.rds"))


server <- function(input, output, session) {
  
  # ---- Flash Estimate Data ----
  
  observe({
    updateSelectInput(session,"nuts_level", choices = c("NUTS_3","NUTS_2"))
  })
  
  nuts_aggregated_download <- reactive({
    if(input$nuts_level == "NUTS_3") {
      return(nuts_aggregated_nuts3)  # Assuming nuts_aggregated_nuts3 is defined
    } else if(input$nuts_level == "NUTS_2") {
      return(nuts_aggregated_nuts2)  # Assuming nuts_aggregated_nuts2 is defined
    }
  })
  
  # Render the table
  output$data_fe <- renderDataTable({
    nuts_aggregated_download()  # Call the reactive expression to get the correct data
  })
  
  
  #  download data
  output$downloadData <- downloadHandler(
    filename = function() {
      paste("clc-fe-", Sys.Date(), ".", input$download_type, sep = "")
    },
    content = function(file) {
      if (input$download_type == "csv") {
        write.csv(nuts_aggregated_download, file, row.names = FALSE)
      } else if (input$download_type == "xlsx") {
        write.xlsx(nuts_aggregated_download, file, rowNames = FALSE)
      }
    }
  )
  
  
  # ---- Flash Estimate Visualisation ----
  observe({
    updateSelectInput(session,"selected_nuts3", choices = unique(sentinel$NUTS_tot))
    updateSelectInput(session,"year", choices = unique(sentinel$year))
  })

  filtered_data <- reactive({
    sentinel %>%
      filter(NUTS_tot == input$selected_nuts3,
             year == input$year)
  })
  
  chart_data <- reactive({
    nuts_aggregated %>%
      filter(NUTS_3 == substr(input$selected_nuts3,1,5),
             year == input$year)
  })
  
  output$map <- renderPlot({
    # Ensure the data is available
    req(filtered_data())
    
    # Use the data from the reactive expression
    data <- filtered_data()
    
    # Get unique NUTS_tot and year values
    unique_nuts <- unique(data$NUTS_tot)  # Get unique NUTS_tot
    unique_year <- unique(data$year)  # Get unique year
    
    ggplot() +
      geom_point(data = data, aes(x = X, y = Y, color = color_var), size = 1.5) +  # Scatter points
      geom_sf(data = st_as_sf(data %>% distinct(NUTS_ID, .keep_all = TRUE) %>% select(geometry)),
              fill = NA, color = "black", linewidth = 0.4) +
      scale_color_manual(values = c(
        "Artificial surfaces" = "#bb3966",
        "Wetlands and water bodies" = "#0A9396",
        "Green and agricultural areas" = "#AEC123",
        "Urbanization" = "#691f39",
        "De-urbanization" = "#586019"
      )) +
      coord_sf() +
      labs(
        title = paste(unique_nuts," for year ",unique_year),  # Title with unique NUTS and Year
        x = NULL,  # Removes x axis label name
        y = NULL,  # Removes y axis label name
        color = "Land Cover Type"  # Changes legend title to "Land Cover Type"
      ) +
      theme_minimal() +
      theme(
        axis.title = element_blank(),  # Removes axis titles (names)
        axis.text = element_text(size = 10),  # Keeps axis values with text size 10 (adjust if needed)
        axis.ticks = element_line(size = 0.5),  # Keeps axis ticks with adjusted size
        legend.title = element_text(size = 18, face = "bold"),  # Significantly larger legend title
        legend.text = element_text(size = 14),  # Significantly larger legend text
        plot.title = element_text(size = 16, face = "bold", hjust = 0.5)  # Title size 16 and centered
      )
  })
  
  output$pie_chart <- renderPlot({
    req(chart_data())
    req(nrow(chart_data()) > 0)  # Ensure there's data to plot
    
    ggplot(chart_data(), aes(x = "", y = PCT_AREA, fill = LAND_COVER)) +
      geom_bar(stat = "identity", width = 1) +
      coord_polar("y", start = 0) +  # Converts to a pie chart
      scale_y_continuous(labels = scales::percent_format(accuracy = 1)) +  # Converts decimals to %
      scale_fill_manual(values = c(
        "Artificial surfaces" = "#bb3966",
        "Wetlands and water bodies" = "#0A9396",
        "Green and agricultural areas" = "#AEC123",
        "Urbanisation" = "#691f39",
        "Vegetalisation" = "#586019"
      ), drop = FALSE) +  # Prevents ggplot from dropping missing categories
      labs(
        fill = "Land Cover", 
        title = paste("Land Cover Distribution -", unique(chart_data()$year))
      ) +
      theme_void() +  # Removes background grid
      theme(
        legend.position = "bottom",  # Keep the legend at the bottom
        legend.title = element_text(size = 12),
        legend.text = element_text(size = 10),
        plot.title = element_text(hjust = 0.5, size = 14, face = "bold"),
        legend.box = "horizontal",  # Makes the legend layout horizontal
        legend.spacing.x = unit(0.5, "cm"),  # Adjusts space between legend items
        legend.box.spacing = unit(1, "cm")  # Adjusts space between legend and plot
      ) +
      geom_text(
        aes(label = scales::percent(PCT_AREA, accuracy = 0.01)),  # Display percentage
        position = position_stack(vjust = 0.5),  # Place text in the center of each slice
        size = 4,  # Adjust text size
        color = "white"  # Text color
      )
  })
  
  # ---- Change Detection ----
  observe({
    updateSelectInput(session,"nuts3_selected", choices = unique(sentinel$NUTS_tot))
  })
  
  slider_data <- reactive({
    sentinel %>%
      filter(NUTS_tot == input$nuts3_selected,
             year == input$slider)
  })
  
  output$map_slider <- renderPlot({
  # Ensure the data is available
  req(slider_data())
  
  # Use the data from the reactive expression
  data <- slider_data()
  
  # Get unique NUTS_tot and year values
  unique_nuts <- unique(data$NUTS_tot)  # Get unique NUTS_tot
  unique_year <- unique(data$year)  # Get unique year
  
  ggplot() +
    geom_point(data = data, aes(x = X, y = Y, color = color_var), size = 1.5) +  # Scatter points
    geom_sf(data = st_as_sf(data %>% distinct(NUTS_ID, .keep_all = TRUE) %>% select(geometry)),
            fill = NA, color = "black", linewidth = 0.4) +
    scale_color_manual(values = c(
      "Artificial surfaces" = "#bb3966",
      "Wetlands and water bodies" = "#0A9396",
      "Green and agricultural areas" = "#AEC123",
      "Urbanization" = "#691f39",
      "De-urbanization" = "#586019"
    )) +
    coord_sf() +
    labs(
      title = paste(unique_nuts," for year ",unique_year),  # Title with unique NUTS and Year
      x = NULL,  # Removes x axis label name
      y = NULL,  # Removes y axis label name
      color = "Land Cover Type"  # Changes legend title to "Land Cover Type"
    ) +
    theme_minimal() +
    theme(
      axis.title = element_blank(),  # Removes axis titles (names)
      axis.text = element_text(size = 10),  # Keeps axis values with text size 10 (adjust if needed)
      axis.ticks = element_line(size = 0.5),  # Keeps axis ticks with adjusted size
      legend.title = element_text(size = 18, face = "bold"),  # Significantly larger legend title
      legend.text = element_text(size = 14),  # Significantly larger legend text
      plot.title = element_text(size = 16, face = "bold", hjust = 0.5)  # Title size 16 and centered
    )
})

  
}
