import os,sys,time,datetime
import numpy as np
import pandas as pd
from io import StringIO
from dash import Dash,html,dcc,Input,Output,callback,ctx,register_page


all_reports_dict = {}
all_reports_done_dict = {}
copy_df = None

patients_dropdown = dcc.Dropdown(
    placeholder="Select Serial Number..,",
    id="patients-dropdown"
)

all_options = [
    "Hb",
    "Total Count (TC)",
    "Platelet Count",
    "Differential Count (DC)",
    "CRP",
    "Total Bilirubin",
    "Direct & Indirect Bilirubin",
    "HBA1C",
    "Blood Urea",
    "Serum Creatinine",
    "Urine Analysis",
    "Mantaoux",
    "Random Sugar",
    "Fasting Sugar",
]

reports_dropdown = dcc.Dropdown(
    all_options,
    id="reports-dropdown",
    multi=True
)

layout = html.Div(
    [
        html.Div(html.H1("Patients report",className="page-heading"),className="heading-divs"),
        *[html.Br()]*5,
        html.Div(patients_dropdown,style=dict(width="400px",alignItems="center")),
        *[html.Br()]*5,
        html.Div(reports_dropdown,style=dict(width="400px",alignItems="center")),
        *[html.Br()]*10,
        dcc.Markdown(id="output-report",style=dict(border="2px solid rgba(0,255,255,0.7)",borderBottom=None,padding="20px",position="relative",left="100px",width="900px",fontSize=18)),
        html.Div(style=dict(border="2px solid rgba(0,255,255,0.7)",borderTop=None,borderBottom=None,width="900px",height="50px",position="relative",left="100px")),
        html.Div(id="output-report-boxes",style=dict(border="2px solid rgba(0,255,255,0.7)",borderTop=None,padding="2px",position="relative",alignItems="center",left="100px",width="900px",fontSize=18))
    ],
    className="subpage-content"
)


@callback(
    Output("patients-dropdown","options"),
    Input("data-store","data")
)
def patients_drpodown_update(data):
    global copy_df
    if data:
        df = pd.read_json(StringIO(data),orient="split")
        copy_df = df.copy().iloc[::-1].reset_index(drop=True)
        return copy_df["S.No."].tolist()
    return []



@callback(
    [
        Output("output-report","children"),
        Output("output-report-boxes","children")
    ],
    [
        Input("patients-dropdown","value"),
        Input("reports-dropdown","value")
    ]
)
def save_and_print_report(patients_sno, reports_value):
    global all_reports_dict
    if patients_sno:
        patients_details = f'''
                            Pt. Name : {copy_df.loc[copy_df.loc[:,"S.No."] == patients_sno,"Patient Name"].item()}
                            
                            &nbsp;&nbsp;&nbsp;&nbsp

                            Pt. Age  : {copy_df.loc[copy_df.loc[:,"S.No."] == patients_sno,"Patient Age"].item()} {copy_df.loc[copy_df.loc[:,"S.No."] == patients_sno,"Age Group"].item()}
                            
                            &nbsp;&nbsp;&nbsp;&nbsp
                            
                            Ref Dr. By : {copy_df.loc[copy_df.loc[:,"S.No."] == patients_sno,"Reference By"].item()}   
                            
                            &nbsp;&nbsp;&nbsp;&nbsp

                            Gender: {copy_df.loc[copy_df.loc[:,"S.No."] == patients_sno,"Gender"].item()}

                            &nbsp;&nbsp;&nbsp;&nbsp

                            Specimen: Blood

                            &nbsp;&nbsp;&nbsp;&nbsp

                            Date: {datetime.date.today().strftime("%d-%m-%y")}

                            &nbsp;&nbsp;&nbsp;&nbsp
                            
                            ***

                            &emsp;
                            &emsp;
                            
                            &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp; Test  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;  Value  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;  Reference Range           
                            
                            &emsp;
                            &emsp;
                               
                            ***
                            
                            '''
        all_reports_dict[patients_sno] = [patients_details]
        if reports_value:
            if "Hb" in reports_value:
                all_reports_dict[patients_sno] += [[html.Div("Heamoglobin :",style=dict(position="relative",left="80px",fontSize=20)),dcc.Input(id="hb",type="number",placeholder="Type Hb Value..",style=dict(width="150px",height="25px",position="relative",left="360px",bottom="20px",fontSize=20)),html.Div("( 11.0 - 16.8 Grams%)",style=dict(position="relative",left="580px",bottom="45px",fontSize=18))]]
                return all_reports_dict[patients_sno]
        return[all_reports_dict[patients_sno],"Select a Test to Display...."]
    return ["Select a Serial Number to Display....","Select a Test to Display...."]




register_page(
    "Reports",
    layout=layout,
    path="/reports"
)