import os,sys,time,datetime
from pages.register import df
import numpy as np
import pandas as pd
from dash import Dash,html,dcc,Input,Output,callback,ctx,register_page


patients_dropdown = dcc.Dropdown(
    df["S.No."].to_list(),
    placeholder="Select Serial No",
    id="reports-dropdown"
)

all_options = [
    "Hb",
    "Total Count (TC)",
    "Platelet Count",
    "Differential Count (DC)",
    "CRP",
    "Total Bilirubin",
    "Direct & Indirect Bilirubin",
    "Urine Analysis",
    "Mantaoux",
    "Random Sugar",
    "Fasting Sugar",
]

reports_dropdown = dcc.Dropdown(
    all_options,
    multi=True
)

layout = html.Div(
    [
        html.Div(html.H1("Patients report",className="page-heading"),className="heading-divs"),
        patients_dropdown,
        reports_dropdown
    ],
    className="subpage-content"
)


register_page(
    "Reports",
    layout=layout,
    path="/reports"
)