fluidPage(
  fluidRow(
    class="init1",
    tags$div(class="satelita", icon("satellite"))
  ),
  fluidRow(
    class="overRow infor",
    box(
      class="karuzelka",
      collapsible = F,
      width = 12,
      column(width = 7, HTML("FloodWatch is a  tool for flood monitoring using SAR data from Sentinel-1. Due to the specifics of the satellite, not every image was suitable for analysis, requiring careful selection of usable data.<br>
The dashboard is based on September 2024 flood and allows users to customize their outputs (choosing between two NUTS3 Regions - Nyski Region and South Moravian Region)")),
      column(
        width = 5,
        valueBox(value = "",
                 subtitle = "",
                 width = 12,
                 color = "success",
                 footer = a(href="https://sentiwiki.copernicus.eu/web/", "Read more about Sentinel"),
                 icon  = icon("satellite"))
      )
    )
  ),
  fluidRow(
    box(
      collapsible = F,
      status="info",
      width = 12,
      uiOutput("selectNUTS3"),
      uiOutput("opisKaruzeli"),
      uiOutput("opisKaruzeli1"),
      uiOutput("summaryTab3"),
      br(),
      br(),
      fluidRow(
        class="valueB",
        slickROutput("vbox1", width = "40%", height = "480px"),
        div(class="strzalka", icon("arrow-right")),
        slickROutput("vbox2", width = "40%", height = "480px"),
      ),
      br(),
      br()
    )
  ),
  fluidRow(
    box(
      title = "Edge Density",
      collapsible = F,
      width = 12,
      fluidRow(
        column(
          width = 9,
          plotlyOutput("clustersPlot")
        ),
        column(
          width = 3,
          valueBoxOutput("floodArea", width = 12),
          HTML("<b>Edge Density:</b> Measures the intensity of edges in an image using the Sobel filter. It quantifies the amount of structural variation, helping to identify texture complexity and boundary sharpness in the image. Higher values indicate more distinct edges and detailed structures.")
        )
      ),
      DTOutput("weatherOutputTab")
    )
  )
)