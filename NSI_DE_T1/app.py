# Here starts the front-end of the application of our Hackathon2025 Project
# LEAFY LINES - Monitoring small woody features on agriculutral land

from pathlib import Path
from shiny import App, ui, reactive, Session

from modules import map, plot
from utils.helper_text import info_modal
import geopandas as gpd


page_dependencies = ui.tags.head(
    ui.tags.link(rel="stylesheet", type="text/css", href="layout.css"),
    ui.tags.link(rel="stylesheet", type="text/css", href="style.css"),
    ui.tags.script(src="index.js"),

   
    ui.tags.meta(name="description", content="LEAFY LINES - Monitoring small woody features on agriculutral land"),
    ui.tags.meta(name="theme-color", content="#000000"),
    ui.tags.meta(name="viewport", content="width=device-width, initial-scale=1"),
)

# top navbar
page_header = ui.tags.div(
    ui.tags.div(
        ui.tags.a(
            ui.tags.img(
                src="static/img/favicon.bmp", height="50px"
            ),
            href="https://cros.ec.europa.eu/2025EuropeanBigDataHackathon",
        ),
        id="logo-top",
        class_="navigation-logo",
    ),

    ui.tags.div(
        ui.tags.div(
            ui.input_action_button(
                id="tab_map",
                label="Map",
                class_="navbar-button",
            ),
            id="div-navbar-map",
        ),
        ui.tags.div(
            ui.input_action_button(
                id="tab_plot",
                label="Graphs",
                class_="navbar-button",
            ),
            id="div-navbar-plot",
        ),
        id="div-navbar-tabs",
        class_="navigation-menu",
    ),

    # ui.tags.div(
    #     ui.input_switch(
    #         id="dataset", label="World Bank", value=True
    #     ),
    #     id="div-navbar-selector",
    #     class_="navigation-dataset",
    # ),

    ui.tags.div(
        ui.input_action_button(
            id="info_icon",
            label=None,
            icon=ui.tags.i(class_="glyphicon glyphicon-info-sign"),
            class_="navbar-info",
        ),
        class_="navigation-info",
    ),

    id="div-navbar",
    class_="navbar-top page-header card-style",
)

map_ui = ui.tags.div(
    map.map_ui("map"),
    id="map-container",
    class_="page-main main-visible",
)

plot_ui = ui.tags.div(
    plot.plot_ui("plot"),
    id="plot-container",
    class_="page-main",
)

page_layout = ui.tags.div(
    page_header,
    map_ui,
    plot_ui,
    class_ = "page-layout"
)

app_ui = ui.page_fluid(
    page_dependencies,
    page_layout,
    title="Leafy Lines - Monitoring small woody features on agriculutral land",
)


def server(input, output, session: Session):

    info_modal()

    @reactive.Effect
    @reactive.event(input.info_icon)
    def _():
        #pass
        info_modal()

    # @reactive.Calc
    # def is_wb_data():
    #     return input.dataset()

    map.map_server("map")#, is_wb_data)
    plot.plot_server("plot")#, is_wb_data)

    @reactive.Effect
    @reactive.event(input.tab_map)
    async def _():
        await session.send_custom_message(
            "toggleActiveTab", {"activeTab": "map"}
        )

    @reactive.Effect
    @reactive.event(input.tab_plot)
    async def _():
        await session.send_custom_message(
            "toggleActiveTab", {"activeTab": "plot"}
        )


www_dir = Path(__file__).parent / "www"
app = App(app_ui, server, static_assets=www_dir)