import os
from datetime import datetime,date
from glob import glob
import numpy as np
import pandas as pd
import json
from dash import dcc,html,register_page,dash_table,callback,Input,Output,ctx,State



df = pd.DataFrame(
    {
        "S.No.":pd.Series(dtype="int32"),
        "Date":pd.Series(dtype="str"),
        "Patient Name":pd.Series(dtype="str"),
        "Reference By":pd.Series(dtype="str"),
        "Patient Age":pd.Series(dtype="str"),
        "Age Group":pd.Series(dtype="str"),
        "Gender":pd.Series(dtype="str"),
        "Amount":pd.Series(dtype="int64"),
        "Phone No":pd.Series(dtype="int64"),
        "Paid":pd.Series(dtype="bool"),
        "Print":pd.Series(dtype="bool")
    }
)


doctor_options = [
    "self".capitalize(),
    "NEELIMA AGARWAL GARU, MD(Homeo).,",
    "m rama krishna garu, mbbs, dch.,".upper(),
    "Smt. M.N. SRI DEVI GARU, MBBS, DGO.,",
    "S. Prasad",
    "Babu garu"
]


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
                ),
                html.Button("REFRESH",id="refresh-button",style=dict(position="absolute",height="100px",width="100px",left="600px",color="cyan"))
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
                html.Div("Reference Doctor: ",style=dict(color="cyan",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        html.Div(
            [
                html.Div(
                    [
                        dcc.Dropdown(doctor_options,"SELF",id="doctor-dropdown")
                    ],
                    style=dict(width="400px",position="relative",left="50px",bottom="25px")
                ),
                dcc.Input(id="reference-doctor",type="text",placeholder="Enter Doctors Name...",style=dict(position="relative",left="100px",width="500px",bottom="25px",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center",position="relative",left="300px")
        ),
        *[html.Br()]*5,
        html.Div(
            [
                html.Div("Patient Age: ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="patient_age",type="number",placeholder="Age...",style=dict(display="inline-block",width="150px",position="absolute",left="350px",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        html.Div(
            dcc.Dropdown(["Y","M","D"],"Y",id="age-group-dropdown"),
            style=dict(display="inline-block",alignItems="center",position="relative",left="530px",bottom="35px")
        ),
        *[html.Br()]*5,
        html.Div(
            [
                html.Div("Gender : ",style=dict(color="cyan",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        html.Div(
            dcc.Dropdown(["Male","Female"],"Male",id="gender-dropdown"),
            style=dict(display="inline-block",alignItems="center",position="relative",width="150px",left="350px",bottom="30px")
        ),
        *[html.Br()]*5,
        html.Div(
            [
                html.Div("Amount : ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="amount",type="number",placeholder="Enter Amount To be Paid...",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30))
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
        html.Button("Submit",id="submit-button",style=dict(fontSize=30,borderRadius="5px",height="100px",width="250px")),
        *[html.Br()]*5,
        dash_table.DataTable(
            id="data-table",
            data=df.to_dict('records'),
            columns=[{"name":i,"id":i} for i in df.columns],
            style_table=dict(fontSize=25,backgroundColor="#633fff"),
            style_cell=dict(backgroundColor="#633fff")
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
        Output("data-table","data",allow_duplicate=True),
        Output("data-store","data",allow_duplicate=True)
    ],
    [
        Input("date-pick-single","date"),
        Input("refresh-button","n_clicks")
    ],
    prevent_initial_call=True
)
def initialize_df(date_value,n_clicks):
    global df
    date_obj = date.fromisoformat(date_value)
    date_string = date_obj.strftime("%Y_%m_%d")
    file = glob("all_files/"+date_string+".xlsx")
    if file:
        df = pd.read_excel(file[0])
    else:
        df = pd.DataFrame(
            {
                "S.No.":pd.Series(dtype="int32"),
                "Date":pd.Series(dtype="str"),
                "Patient Name":pd.Series(dtype="str"),
                "Reference By":pd.Series(dtype="str"),
                "Patient Age":pd.Series(dtype="str"),
                "Age Group":pd.Series(dtype="str"),
                "Gender":pd.Series(dtype="str"),
                "Amount":pd.Series(dtype="int64"),
                "Phone No":pd.Series(dtype="int64"),
                "Paid":pd.Series(dtype="bool"),
                "Print":pd.Series(dtype="bool")
            }
        )
        df.loc[1,:] = [1,datetime.today().strftime("%d-%m-%y"),"first_name","some_doc","1","Y","Male",10,20,False,False]
        df.loc[2,:] = [2,datetime.today().strftime("%d-%m-%y"),"second_name","some_doc","2","M","Female",20,30,False,False]
    return df.to_dict('records'),df.to_json(date_format="iso",orient="split")


@callback(
    [
        Output("data-table","data"),
        Output("data-store","data")
    ],
    [
        Input("submit-button","n_clicks")         
    ],
    [
        State("age-group-dropdown","value"),        # 0
        State("gender-dropdown","value"),           # 1
        State("doctor-dropdown","value"),           # 2
        State("date-pick-single","date"),           # 3
        State("serial_number","value"),             # 4
        State("patient_name","value"),              # 5
        State("reference-doctor","value"),          # 6
        State("patient_age","value"),               # 7
        State("amount","value"),                    # 8
        State("phone_number","value")               # 9
    ]
)
def append_name_to_dataframe(n_clicks,*vals):
    global df
    if n_clicks:
        index_number = df.shape[0]
        index_number += 1
        df.loc[index_number,"S.No."] = vals[4]
        date_obj = date.fromisoformat(vals[3])
        df.loc[index_number,"Date"] = date_obj.strftime("%d-%m-%y")
        df.loc[index_number,"Patient Name"] = vals[5]
        if vals[6] == None:
            df.loc[index_number,"Reference By"] = vals[2]
        else:
            df.loc[index_number,"Reference By"] = vals[6]
        df.loc[index_number,"Age Group"] = vals[0]
        df.loc[index_number,"Patient Age",] = vals[7]
        df.loc[index_number,"Gender"] = vals[1]
        df.loc[index_number,"Amount"] = vals[8]
        df.loc[index_number,"Phone No"] = vals[9]
        df.loc[index_number,"Paid"] = False
        df.loc[index_number,"Print"] = False
    return df.to_dict('records'),df.to_json(date_format="iso",orient="split")


@callback(
    Output("out-message","children"),
    [
        Input("save-button","n_clicks"),
        Input("date-pick-single","date")
    ]
)
def save_to_files(n_clicks,date_value):
    if n_clicks:
        date_obj = date.fromisoformat(date_value)
        date_string = date_obj.strftime("%Y_%m_%d")
        df.to_excel("all_files/"+date_string+".xlsx",index=False)
        return "Your File has been saved."


register_page(
    "Register",
    layout=register_layout,
    path="/register"
)

