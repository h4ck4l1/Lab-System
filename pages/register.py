import os,time
from datetime import datetime,date
from glob import glob
from io import StringIO
import numpy as np
import pandas as pd
import json
from dash import dcc,html,register_page,dash_table,callback,Input,Output,ctx,State
from dash.exceptions import PreventUpdate



columns = [
    "S.No.",
    "Date",
    "Patiens Name",
    "Reference By",
    "Patient Age",
    "Age Group",
    "Gender",
    "Amount",
    "Phone No",
    "Paid",
    "Due",
    "Sample",
]


doctor_options = [
    "self".capitalize(),
    "NEELIMA AGARWAL GARU, MD(Homeo).,",
    "m rama krishna garu, mbbs, dch.,".upper(),
    "Smt. M.N. SRI DEVI GARU, MBBS, DGO.,",
    "akula satyanarayana garu, mbbs, dch.,".upper(),
    "a. ganga bhavani garu, mbbs, dgo.,".upper(),
    "k. rajendra prasad garu, b.m.p.,".upper(),
    "ch. kiran kumar garu, b.m.p.,".upper(),
    "S. Prasad".upper(),
    "Babu garu".upper(),
]

big_break = [html.Br()] * 5

register_layout = html.Div(
    [
        html.Div(html.H1("patient registraton",className="page-heading",style=dict(color="cyan")),className="heading-divs"),
        *big_break,
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
        *big_break,
        html.Div(
            [
                html.Div("S. No. : ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="serial_number",type="number",placeholder="Enter Serial Number... ",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *big_break,
        html.Div(
            [
                html.Div("Patient Name: ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="patient_name",type="text",placeholder="Enter Patient's Name...",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *big_break,
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
        *big_break,
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
        *big_break,
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
        *big_break,
        html.Div(
            [
                html.Div("Amount : ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="amount",type="number",placeholder="Enter Amount To be Paid...",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *big_break,
        html.Div(
            [
                html.Div("Phone No: ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="phone_number",type="number",placeholder="Enter Phone Number...",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *big_break,
        html.Div(
            [
                html.Div("Paid or Not: ",style=dict(color="cyan",fontSize=30)),
                html.Div(dcc.Dropdown(["paid".upper(),"not paid".upper(),"due".upper()],"not paid".upper(),id="paid-dropdown"),style=dict(display="inline-block",fontSize=20,width="200px",height="75px",position="relative",left="150px",top="25px")),
                html.Div("Due Amount : ",style=dict(color="cyan",fontSize=30,position="relative",left="200px")),
                dcc.Input(id="paid-input",type="number",placeholder="Enter Due Amount",value=0,style=dict(display="inline-block",width="200px",fontSize=30,height="50px",position="relative",left="300px"))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *big_break,
        html.Div(
            [
                html.Div("Sample Bougth by: ",style=dict(color="cyan",fontSize=30)),
                html.Div(dcc.Dropdown(["self".upper(),"outside".upper()],"self".upper(),id="sample-source-dropdown"),style=dict(display="inline-block",fontSize=20,width="200px",height="75px",position="relative",left="350px",bottom="25px")),
                dcc.Input(id="sample-source-input",type="text",placeholder="Enter Name",value="Outside",style=dict(display="inline-block",width="200px",fontSize=30,height="50px",position="relative",left="400px",bottom="75px"))
            ]
        ),
        *big_break,
        html.Button("Submit",id="submit-button",style=dict(fontSize=30,borderRadius="5px",height="100px",width="250px")),
        *big_break,
        dash_table.DataTable(
            id="data-table",
            columns=[{"name":i,"id":i} for i in columns],
            style_table=dict(fontSize=25,backgroundColor="#633fff"),
            style_cell=dict(backgroundColor="#633fff")
        ),
        *big_break,
        html.Div(
            [
                html.Button("Save to Files",id="save-button",style=dict(fontSize=30,borderRadius="5px",height="100px",width="250px")),
                html.Div(id="out-message",style=dict(fontSize=30,color="cyan",position="absolute",left="350px"))
            ]
        ),
        html.Div(
            [
                html.Button("clear everything".upper(),id="clear-button",style=dict(color="cyan",backgroundColor="red",fontWeight=700,fontSize=30,borderRadius="5px",position="relative",left="80vw",height="100px",width="250px")),
                html.Div(children="Storage",id="out-message",style=dict(fontSize=30,color="cyan",position="absolute"))
            ]
        )
    ],
    className="subpage-content"
)


@callback(
    [
        Output("data-table","data"),
        Output("data-store","data")
    ],
    [
        Input("date-pick-single","date"),
        Input("refresh-button","n_clicks")
    ],
)
def initialize_df(date_value,n_clicks):
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
                "Time":pd.Series(dtype="str"),
                "Patient Name":pd.Series(dtype="str"),
                "Reference By":pd.Series(dtype="str"),
                "Patient Age":pd.Series(dtype="int64"),
                "Age Group":pd.Series(dtype="str"),
                "Gender":pd.Series(dtype="str"),
                "Amount":pd.Series(dtype="int64"),
                "Phone No":pd.Series(dtype="int64"),
                "Paid":pd.Series(dtype="str"),
                "Due":pd.Series(dtype="int64"),
                "Sample":pd.Series(dtype="str")
            }
        )
        df.loc[1,:] = [1,datetime.today().strftime("%d-%m-%y"),"01:11:23 PM","first_name","some_doc",1,"Y","Male",10,20,"PAID",0,"SELF"]
        df.loc[2,:] = [2,datetime.today().strftime("%d-%m-%y"),"12:10:56 AM","second_name","some_doc",2,"M","Female",20,30,"NOT PAID",1000,"OUTSIDE"]
    return df.to_dict('records'),df.to_json(date_format="iso",orient="split")


@callback(
    [
        Output("data-table","data",allow_duplicate=True),
        Output("data-store","data",allow_duplicate=True)
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
        State("phone_number","value"),              # 9
        State("paid-dropdown","value"),             # 10
        State("paid-input","value"),                # 11
        State("sample-source-dropdown","value"),    # 12
        State("sample-source-input","value"),       # 13
        State("data-store","data")                  # 14
    ],
    prevent_initial_call=True
)
def append_name_to_dataframe(n_clicks,*vals):
    if not n_clicks:
        raise PreventUpdate
    if n_clicks:
        df = pd.read_json(StringIO(vals[14]),orient="split")
        index_number = df.shape[0]
        index_number += 1
        df.loc[index_number,"S.No."] = vals[4]
        date_obj = date.fromisoformat(vals[3])
        df.loc[index_number,"Date"] = date_obj.strftime("%d-%m-%y")
        t = time.localtime()
        t_hour,t_min,t_sec = t.tm_hour,t.tm_min,t.tm_sec
        if t_sec <= 9:
            t_sec = f"0{t_sec}"
        if t_min <= 9:
            t_min = f"0{t_min}"
        if t_hour > 11:
            if t_hour != 12:
                t_hour -= 12
            if t_hour <= 9:
                t_hour = f"0{t_hour}"
            t_time = f"{t_hour}:{t_min}:{t_sec} PM"
        else:
            if t_hour <= 9:
                t_hour = f"0{t_hour}"
            t_time = f"{t_hour}:{t_min}:{t_sec} AM"
        df.loc[index_number,"Time"] = t_time
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
        df.loc[index_number,"Paid"] = vals[10]
        if vals[10] == "due".upper():
            df.loc[index_number,"Due"] = vals[11]
        else:
            df.loc[index_number,"Due"] = 0
        df.loc[index_number,"Sample"] = vals[12]
        if (vals[12] == "outside".upper()) & (vals[13] is not None):
            df.loc[index_number,"Sample"] = vals[13]
        df.loc[index_number,"Print"] = False
        return df.to_dict('records'),df.to_json(date_format="iso",orient="split")


@callback(
    Output("out-message","children"),
    Input("save-button","n_clicks"),
    [
        State("data-store","data"),
        State("date-pick-single","date"),
    ]
)
def save_to_files(n_clicks,date_value,data):
    if n_clicks:
        df = pd.read_json(StringIO(data),orient="split")
        date_obj = date.fromisoformat(date_value)
        date_string = date_obj.strftime("%Y_%m_%d")
        df.to_excel("all_files/"+date_string+".xlsx",index=False)
        return "Your File has been saved."


register_page(
    "Register",
    layout=register_layout,
    path="/register"
)

