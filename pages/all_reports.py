import os,time
from glob import glob
from datetime import date
from dash import html,dcc,callback,Output,Input,register_page


layout = html.Div(
    [
        html.Div(html.H1("all reports".upper(),className="page-heading"),className="heading-divs"),
        html.Div(dcc.DatePickerSingle(
            id="date-pick-all-reports",
            min_date_allowed=date(1995,8,5),
            max_date_allowed=date.today(),
            date=date.today(),
            style=dict(position="relative",left="100px")
        )),
        html.Div(
            dcc.Dropdown(
                id="all-reports-dropdown",
                style=dict(width="1000px",height="100px",maxHeight="200px"),
                className="custom-dropdown"
            ),
            style=dict(position="relative",left="400px",top="100px",fontSize=20)
        ),
        html.Div(id="output-all-reports",style=dict(border="10px solid cyan",position="relative",top="200px",height="1100px",width="85%"))
    ],
    className="subpage-content"
)

@callback(
    Output("all-reports-dropdown","options"),
    Input("date-pick-all-reports","date")
)
def populate_dropdown(date:str):
    year,month,day = date.split("-")

    if os.path.exists(f"assets/{year}/{month}/{day}"):
        return [{"label":os.path.basename(f),"value":f} for f in glob(f"assets/{year}/{month}/{day}/*.pdf")]
    return []


@callback(
    Output("output-all-reports","children"),
    Input("all-reports-dropdown","value")
)
def display_report(value:str):
    if value:
        cache_buster = f"?v={int(time.time())}"
        return html.Iframe(
            src=f"{value}{cache_buster}",
            style={
                "width":"100%",
                "height":"1000px"
            }
        )


register_page(
    "All Reports",
    path="/all_reports",
    layout=layout
)