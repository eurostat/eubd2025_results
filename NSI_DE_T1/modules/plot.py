from shiny import ui, module, reactive, render
from shinywidgets import (
    output_widget,
    render_widget,
)
from utils.helper_text import (
    about_text,
    slider_text_plot,
    dataset_information,
    missing_note,
)
from utils import * 
from sqlalchemy import create_engine
import psycopg2
import pandas as pd
import pathlib


data_read2 = pd.read_parquet(pathlib.Path(__file__).parent.parent / "www/data/final/tbl_hedge_nuts3.parquet")
data_read2 = data_read2[data_read2["NUTS_ID"].isin([ "DE40A" ,"AT222" ] )] 
list_Nuts3_latin = data_read2["NAME_LATN"].unique().tolist()

@module.ui
def plot_ui():
    return ui.tags.div(
        ui.tags.div(
            about_text,
            ui.tags.hr(),
            slider_text_plot,
            ui.tags.br(),

            ui.input_select(
                id="NUTS3_select_2",
                label="Select NUTS:",
                choices=list_Nuts3_latin
            ),
            ui.tags.hr(),
            dataset_information,
            ui.tags.hr(),
            missing_note,
            class_="main-sidebar card-style",
        ),
        ui.tags.div(
            ui.img(src="data/picture/ueberlagerung_corine_swf_bb40A.PNG"),
            class_="main-main card-style",
        ),
        ui.tags.div(
            ui.img(src="data/picture/ueberlagerung_corine_swf_liezen.PNG"),
            ui.output_ui("image_display"),
            class_="main-main card-style",
        ),
        class_="main-layout",
    )


@module.server
def plot_server(input, output, session):#, is_wb_data):

    @render.ui             
    def image_display():
        image_path  = "data/picture/ueberlagerung_corine_swf_bb40A.PNG" if input.NUTS3_select2() != "Liezen" else "data/picture/ueberlagerung_corine_swf_liezen.PNG"
        return ui.img(src=image_path, height = "300px" )
