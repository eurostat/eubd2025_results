library(leaflet.extras2)
library(waiter)
library(shinydashboard)
library(shinyWidgets)
library(shiny)
library(plotly)
library(bslib)
library(DT)
library(dbplyr)
library(dplyr)
library(leaflet)
library(sf)
library(bs4Dash)
library(shinySearchbar)
library(slickR)
library(DBI)
library(odbc)
library(terra)
library(lubridate)

ue <- c("Belgium", "France", "Netherlands", "Luxemburg", "Germany", "Italy", "Denmark", "Ireland", "Greece", "Spain", "Portugal", "Austria", "Finland", "Sweden", "Cyprus", "Czech Republic", "Estonia", "Lithuania","Latvia", "Malta", "Poland", "Slovakia", "Slovenia", "Hungary", "Bulgaria", "Romania", "Croatia")

selected <- c("Poland", "Czech Republic")

set.seed(4242)

random_sparkline_plot <- function() {
  timeseries <- cumsum(runif(100, -2, 2))
  x_axis <- seq_along(timeseries)
  x_lim <- c(1, length(timeseries))
  y_lim <- range(timeseries) + c(-2, 0)
  
  par(mar = c(0, 0, 0, 0))
  
  # Set up the plot area
  plot(
    timeseries, type = "n",
    axes = FALSE, frame.plot = FALSE,
    ylim = y_lim, xlim = x_lim,
    ylab = "",    xlab = "",
    yaxs = "i",   xaxs = "i",
  )
  
  # Add the sparkline line
  lines(timeseries, type = "l", pch = NA, col = "#0B538E", lwd = 3)
  
  # Create polygon coordinates for shading
  polygon_x <- c(1, x_axis, length(timeseries))
  polygon_y <- c(min(y_lim), timeseries, min(y_lim))
  
  # Add shading under the line
  polygon(polygon_x, polygon_y, col = "#e6f2fd", border = NA)
}
