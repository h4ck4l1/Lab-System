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
    "Blood Group",
    "Total Bilirubin",
    "Direct & Indirect Bilirubin",
    "Heamogram",
    "HBA1C",
    "Blood Urea",
    "Serum Creatinine",
    "Uric Acid",
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


limits_style = dict(position="relative",left="550px",bottom="45px",fontSize=18)
input_style = dict(width="150px",height="25px",position="relative",left="360px",bottom="20px",fontSize=20)
text_style = dict(position="relative",left="80px",fontSize=20)


hb_list = [
    html.Div("Heamoglobin :",style=text_style),
    dcc.Input(id="hb",type="number",placeholder="Type Hb Value..",style=input_style),
    html.Div("( 11.0 - 16.8 Grams%)",style=limits_style)
]

tc_list = [
    html.Div("Total WBC Count :",style=text_style),
    dcc.Input(id="tc_count",type="number",placeholder="Type Tc value..",style=input_style),
    html.Div("( 5,000 - 10,000 Cells/cumm )",style=limits_style)
]

plt_list = [
    html.Div("Platelet Count :",style=text_style),
    dcc.Input(id="plt_count",type="number",placeholder="Type Plt Value..",style=input_style),
    html.Div("( 1.5 - 4.0 Lakhs/cumm )",style=limits_style)
]

dc_list = [
    html.Div("Differential Count :",style=text_style),
    html.Br(),
    html.Br(),
    html.Div("Polymorphs :",style=dict(position="relative",left="200px",fontSize=18)),
    dcc.Input(id="polymo",type="number",placeholder="Type polymorphs..",style=dict(position="relative",left="400px",bottom="20px",fontSize=20)),
    html.Div("( 40 - 70 %) ",style=dict(position="relative",left="670px",bottom="40px",fontSize=18)),
    html.Div("Lymphocytes :",style=dict(position="relative",left="200px",fontSize=18)),
    dcc.Input(id="lympho",type="number",placeholder="Type Lymphocytes..",style=dict(position="relative",left="400px",bottom="20px",fontSize=20)),
    html.Div("( 20 - 40 %)",style=dict(position="relative",left="670px",bottom="40px",fontSize=18)),
    html.Div("Esinophils :",style=dict(position="relative",left="200px",fontSize=18)),
    dcc.Input(id="esino",type="number",placeholder="Type Lymphocytes..",style=dict(position="relative",left="400px",bottom="20px",fontSize=20)),
    html.Div("( 02 - 06 %)",style=dict(position="relative",left="670px",bottom="40px",fontSize=18)),
    html.Div("Monocytes :",style=dict(position="relative",left="200px",fontSize=18)),
    dcc.Input(id="mono",type="number",placeholder="Type Lymphocytes..",style=dict(position="relative",left="400px",bottom="20px",fontSize=20)),
    html.Div("( 01 - 04 %)",style=dict(position="relative",left="670px",bottom="40px",fontSize=18))
]

crp_list = [
    html.Div("CRP         :   ",style=text_style),
    dcc.Input(id="crp",type="number",placeholder="Type CRP value..",style=input_style),
    html.Div(" ( < 6 ) ",style=limits_style)
]

reports_original_dict = {
    "Hb":hb_list,
    "Total Count (TC)":tc_list,
    "Platelet Count":plt_list,
    "Differential Count (DC)":dc_list,
    "CRP":crp_list,
}


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
        all_reports_dict[patients_sno] = {"patient_details":[],"report_details":[]}
        all_reports_done_dict[patients_sno] = {}
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
        all_reports_dict[patients_sno]["patient_details"] = patients_details      # {"1": [[dcc.Markdown],[]]}
        if reports_value:
            for x in reports_value:
                all_reports_dict[patients_sno]['report_details'] += reports_original_dict[x]
            # if ("Hb" in reports_value):# and ("Hb" not in all_reports_done_dict[patients_sno]):
            #     all_reports_dict[patients_sno]["report_details"] += hb_list
            #     # all_reports_done_dict[patients_sno]["Hb"] = True                
            # if ("Total Count (TC)" in reports_value): #and ("Total Count (TC)" not in all_reports_done_dict[patients_sno]):
            #     all_reports_dict[patients_sno]["report_details"] += tc_list
            #     # all_reports_done_dict[patients_sno]["TC"] = True
            # if ("Differential Count (DC)" in reports_value): #and ("Differential Count (DC)" not in all_reports_done_dict[patients_sno]):
            #     all_reports_dict[patients_sno]["report_details"] += dc_list
            #     # all_reports_done_dict[patients_sno]["DC"] = True
            # if ("Platelet Count" in reports_value):
            #     all_reports_dict[patients_sno]["report_details"] += plt_list
            return all_reports_dict[patients_sno]["patient_details"],all_reports_dict[patients_sno]["report_details"]
        return[all_reports_dict[patients_sno]["patient_details"],"Select a Test to Display...."]
    return ["Select a Serial Number to Display....","Select a Test to Display...."]


register_page(
    "Reports",
    layout=layout,
    path="/reports"
)