from shiny.ui import modal_show, modal, modal_button
from htmltools import TagList, tags

about_text = TagList(
    tags.h3("About"),
    tags.br(),
    tags.p(
        """
        The app gives a visual overview of small woody features on
        agricultural land. We propose a method to display small woody features overlapping with agricultural land. 
        There is ongoing demand for data required based on the SAIO. """,
        style="""
        text-align: justify;
        word-break:break-word;
        hyphens: auto;
        """,
    ),
)

slider_text_map = tags.p(
    """
    Please use the slider below to choose the year. The map will
    reflect data for the input
    """,
    style="""
    text-align: justify;
    word-break:break-word;
    hyphens: auto;
    """,
)

slider_text_plot = tags.p(
    """
    Please use the slider below to change the years as well as the
    dropdown to select the NUTS3 to compare. 
    """,
    style="""
    text-align: justify;
    word-break:break-word;
    hyphens: auto;
    """,
)

dataset_information = TagList(
    tags.strong(tags.h3("Dataset Information")),
    tags.p(
        """
        For the app, we have chosen data from CORINE Land Cover, Small Woody Features, for Quality assurance InVeKoS.
        The analysis overs data from 2015 and 2018 for the countries Germany and Austria. 

        """,
        style="""
        text-align: justify;
        word-break:break-word;
        hyphens: auto;
        """,
    ),
    tags.ul(
        tags.li(
            tags.a(
                "Corine Land Cover",
                href="https://land.copernicus.eu/pan-european/corine-land-cover",
            )
        ),
        tags.li(
            tags.a(
                "Small Woody Features",
                href="https://land.copernicus.eu/en/products/high-resolution-layer-small-woody-features/small-woody-features-2015",
            )
        ),
        tags.li(
            tags.a(
                "InVeKoS SOURCETOBEFILLED",
                href="https://www.govdata.de/suche?q=invekos",
            )
        ),
    ),
)

missing_note = TagList(
    tags.p(
        tags.strong("Note: "),
        """
        Since 2015 the SMF data was collected
        at every 3-year mark. That is, the SMF data is only
        available for
        2015, 2018, and 2021 onwards is still being produced.
        """,
        style="""
        font-size: 14px;
        text-align: justify;
        word-break:break-word;
        hyphens: auto;
        """,
    ),
)


def info_modal():
    modal_show(
        modal(
            tags.strong(tags.h3("LEAFY LINES")),
            tags.p(
                "Monitoring small woody features on agriculutral land"
            ),
            tags.hr(),
            tags.strong(tags.h4("Problem Statement")),
            tags.p(
                """
            The protoype will be an adjustable dashboard, in which the user choose a NUTS3
            reion of interest and see map feature showing the amount of hedges in the region, 
            agriculutrual land (greenland, or arable land) , as well as percentages.
            It contributes to the GAP guidlines and aims at monitoring SDGs on biodiversity.
            Currently many member states are not able to deliver on the requiremqents of the SAIO.
            It is required to report landscape features on agriculutral land. We offer a step forward
            to comply with indicator provision on this topic. 
            """,
                style="""
            text-align: justify;
            word-break:break-word;
            hyphens: auto;
            """,
            ),
            tags.hr(),
            dataset_information,
            tags.hr(),
            missing_note,
            size="l",
            easy_close=True,
            footer=modal_button("Close"),
        )
    )