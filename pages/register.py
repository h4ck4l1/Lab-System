import os
from datetime import datetime,date
from glob import glob
import numpy as np
import pandas as pd
from dash import dcc,html,register_page,dash_table,callback,Input,Output,ctx,State



df = pd.DataFrame(
    columns=[
        "Index",
        "S.No.",
        "Patient Name",
        "Reference By",
        "Patient Age",
        "Gender",
        "Amount Paid",
        "Phone No"
    ]
)


index_number = 0

register_layout = html.Div(
    [
        html.Div(html.H1("patient registraton",className="page-heading",style=dict(color="cyan")),className="heading-divs"),
        *[html.Br()]*5,
        html.Div(
            [
                html.Div("Select Date: ",style=dict(color="cyan",fontSize=30)),
                dcc.DatePickerSingle(
                    id="date-pick-single",
                    min_date_allowed=date(1995,8,5),
                    max_date_allowed=date.today(),
                    date=date.today(),
                    style=dict(color="cyan",position="absolute",left="350px")
                )
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *[html.Br()]*5,
        html.Div(
            [
                html.Div("S. No. : ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="serial_number",type="number",placeholder="Enter Serial Number... ",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *[html.Br()]*5,
        html.Div(
            [
                html.Div("Patient Name: ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="patient_name",type="text",placeholder="Enter Patient's Name...",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *[html.Br()]*5,
        html.Div(
            [
                html.Div("Reference Doctor: ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="reference_by",type="text",placeholder="Enter Doctors Name...",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *[html.Br()]*5,
        html.Div(
            [
                html.Div("Patient Age: ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="patient_age",type="number",placeholder="Enter Patient's Age...",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *[html.Br()]*5,
        html.Div(
            [
                html.Div("Gender : ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="gender",type="text",placeholder="Enter Patient's Gender...",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *[html.Br()]*5,
        html.Div(
            [
                html.Div("Amount Paid: ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="amount_paid",type="number",placeholder="Enter Amount Paid...",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *[html.Br()]*5,
        html.Div(
            [
                html.Div("Phone No: ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="phone_number",type="number",placeholder="Enter Phone Paid ...",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *[html.Br()]*5,
        html.Button("Submit",id="button",style=dict(fontSize=30,borderRadius="5px",height="100px",width="250px")),
        *[html.Br()]*5,
        dash_table.DataTable(
            id="data_table",
            data=df.to_dict('records'),
            columns=[{"name":i,"id":i} for i in df.columns],
            style_table=dict(fontSize=25)
        ),
        *[html.Br()]*5,
        html.Div(
            [
                html.Button("Save to Files",id="save-button",style=dict(fontSize=30,borderRadius="5px",height="100px",width="250px")),
                html.Div(id="out-message",style=dict(fontSize=30,color="cyan",position="absolute",left="350px"))
            ]
        )
    ],
    className="subpage-content"
)


@callback(
    [
        Output("data_table","data",allow_duplicate=True)
    ],
    Input("date-pick-single","date"),
    prevent_initial_call=True
)
def initialize_df(date_value):
    global df
    global index_number
    date_obj = date.fromisoformat(date_value)
    date_string = date_obj.strftime("%Y_%m_%d")
    file = glob("all_files/"+date_string+".xlsx")
    if file:
        df = pd.read_excel(file[0])
        index_number = df.iloc[-1,0]
        return index_number,df.to_dict('records')
    else:
        df = pd.DataFrame(
            columns=[
                "Index"
                "S.No.",
                "Patient Name",
                "Reference By",
                "Patient Age",
                "Gender",
                "Amount Paid",
                "Phone No"
            ]
        )
        index_number = 0
        return df.to_dict('records')





@callback(
    Output("data_table","data"),
    [
        Input("button","n_clicks")
    ],
    [
        State("serial_number","value"),
        State("patient_name","value"),
        State("reference_by","value"),
        State("patient_age","value"),
        State("gender","value"),
        State("amount_paid","value"),
        State("phone_number","value")
    ]
)
def append_name_to_dataframe(*vals):
    global index_number
    global df
    if "button" == ctx.triggered_id:
        index_number += 1
        df.loc[index_number-1,"Index"] = index_number
        df.loc[index_number-1,"S.No."] = vals[1]
        df.loc[index_number-1,"Patient Name"] = vals[2]
        df.loc[index_number-1,"Reference By"] = vals[3]
        df.loc[index_number-1,"Patient Age",] = vals[4]
        df.loc[index_number-1,"Gender"] = vals[5]
        df.loc[index_number-1,"Amount Paid"] = vals[6]
        df.loc[index_number-1,"Phone No"] = vals[7]
    return df.to_dict('records')


@callback(
    Output("out-message","children"),
    [
        Input("save-button","n_clicks"),
        Input("date-pick-single","date")
    ]
)
def save_to_files(n_clicks,date_value):
    if "save-button" == ctx.triggered_id:
        date_obj = date.fromisoformat(date_value)
        date_string = date_obj.strftime("%Y_%m_%d")
        df.to_excel("all_files/"+date_string+".xlsx",index=False)
        return "Your File has been saved."


register_page(
    "Register",
    layout=register_layout,
    path="/register"
)

