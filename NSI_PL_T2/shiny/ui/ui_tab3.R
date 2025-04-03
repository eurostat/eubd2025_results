fluidPage(
  fluidRow(
    class="init1"
  ),
  fluidRow(
    class="overRow rowTab3",
    box(
      width = 12,
      height = "430px",
      title = div(style = "font-size:40px;color: var(--main)", HTML('<b>NEXT STEPS</b>')),
      HTML("<b>1. Using AI to create a model, which predicts the flooded area <br>
           2. Preparing outputs for more NUTS3 Regions<br>
           3. Considering Sentinel2 and Sentinel5P clouds data</b>")
      
    )
  )
)