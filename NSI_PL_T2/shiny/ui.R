bs4Dash::dashboardPage(
  dark = F,
  fullscreen = TRUE,
  scrollToTop = TRUE,
  footer = dashboardFooter(
    left = "created by Franek Koprowski, Ania Rękowska, Ola Skowrońska",
    right = tags$img(src="https://cros.ec.europa.eu/system/files/inline-images/EU-Big-Data-Hackathon-2025_horiz_0.jpg", class='imgstop')
  ),
  header = dashboardHeader(
    fixed  = T,
    title = tags$div(
      class="headerek",
      tags$div(class="tytul", "floodwatch"))
  ),
  sidebar = dashboardSidebar(
    skin = "light",
    tags$div(
      class="logoH",
      tags$img(src="https://dataspace.copernicus.eu/themes/custom/copernicus/logo.svg", class='imgcop'),
      tags$img(src="https://cis.stat.gov.pl/szablony/portalinformacyjny/images/cis_logo_pl.svg", class='imgcis')
    ),
    tags$div(
      class = "countrySel",
      uiOutput("countryButtons"),
    ),
    collapsed = F,
    sidebarMenu(
      id = "tabs",
      menuItem("home", tabName = "infoTab", icon = icon("satellite")),
      menuItem("NUTS3 regions in details", tabName = "secondTab", icon = icon("cloud-showers-water")),
      menuItem("next steps", tabName = "thirdTab", icon = icon("circle-info")),
      tags$div(class="panelIn")
    )
  ),
  body = shinydashboard::dashboardBody(
    id = "appId",
    useWaiter(),
    waiter_show_on_load(spin_4()),
    autoWaiter(c("vbox1", "vbox2", "clustersPlot", "weatherOutputTab", "weatherOutput", "mapTab2", "mapTabComp2"), html = spin_loaders(id = 16, color = "#0c4594"), color = "rgba(0,0,0,0)"),
    includeCSS("www/style.css"),
    skin = "blue",
    tabItems(
      tabItem(
        "infoTab",
        source("ui/ui_tab1.R")$value
      ),
      tabItem(
        "secondTab",
        source("ui/ui_tab2.R")$value
      ),
      tabItem(
        "thirdTab",
        source("ui/ui_tab3.R")$value
      )
    )
  )
)
