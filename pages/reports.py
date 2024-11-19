import json
import pandas as pd
from io import StringIO
from reportlab.pdfgen import canvas            # type: ignore
from reportlab.lib.pagesizes import A5,A4      # type: ignore
from reportlab.lib.units import inch           # type: ignore
from reportlab.lib import colors               # type: ignore
from dash import html,dcc,Input,Output,callback,register_page,State,ALL
from dash.exceptions import PreventUpdate


all_reports_dict = {}
all_reports_done_dict = {}
copy_df = None
all_patients_values = {}

patients_dropdown = dcc.Dropdown(
    placeholder="Select Serial Number..,",
    id="patients-dropdown"
)

all_options = [
    "Hb",
    "Total Count (TC)",
    "Platelet Count",
    "Differential Count (DC)",
    "Widal",
    "CRP",
    "Full CBP",
    "Blood Group",
    "Total Bilirubin",
    "Direct & Indirect Bilirubin",
    "Heamogram",
    "HBA1C",      # -------------------------- pack 1
    "Fasting Sugar",                      
    "Random Sugar",
    "Blood Urea", # ----------------------- pack 2
    "Serum Creatinine",
    "Uric Acid",
    "Urine Analysis",
    "Lipid Profile",
    "Mantaoux",
    "Heamogram",
    "Blood for AEC Count",
    "RA Factor",
    "ASO Titre"
]

reports_dropdown = dcc.Dropdown(
    all_options,
    id="reports-dropdown",
    multi=True
)

page_size_dropdown = dcc.Dropdown(
    [
        "SMALL/A5",
        "BIG/A4"
    ],
    "SMALL/A5",
    id="page-size-dropdown"
)

templates_dropdown = dcc.Dropdown(
    options = [
        {"label":"HB, TC, PLATELET, DC","value":json.dumps(["Hb","Total Count (TC)","Platelet Count","Differential Count (DC)"])},
        {"label":"HB, TC, DC","value":json.dumps(["Hb","Total Count (TC)","Differential Count (DC)"])},
        {"label":"HB, TC, PLATELET, DC, URINE","value":json.dumps(["Hb","Total Count (TC)","Platelet Count","Differential Count (DC)","Urine Analysis"])},
        {"label":"HB, TC, PLATELET, DC, RBS","value":json.dumps(["Hb","Total Count (TC)","Platelet Count","Differential Count (DC)","Random Sugar"])},
        {"label":"HB, TC, PLATELET, DC, WIDAL","value":json.dumps(["Hb","Total Count (TC)","Platelet Count","Differential Count (DC)","Widal"])},
        {"label":"PACK 1","value":json.dumps(["HBA1C","Random Sugar","Fasting Sugar"])},
        {"label":"PACK 2","value":json.dumps(["Blood Urea","Serum Creatinine","Lipid Profile"])},
        {"label":"RFT","value":json.dumps(["Blood Urea","Serum Creatinine","Uric Acid"])}
    ],
    id="template-dropdown"
)



layout = html.Div(
    [
        html.Div(html.H1("Patients report",className="page-heading"),className="heading-divs"),
        *[html.Br()]*5,
        html.Div(patients_dropdown,style=dict(width="400px",alignItems="center")),
        *[html.Br()]*5,
        html.Div(reports_dropdown,style=dict(width="400px",alignItems="center")),
        html.Div(page_size_dropdown,style=dict(width="400px",alignItems="center",position="relative",left="420px",bottom="36px")),
        html.Div(templates_dropdown,style=dict(width="400px",alignItems="center",position="relative",left="840px",bottom="73px")),
        *[html.Br()]*10,
        html.Div(id="output-report",style=dict(border="2px solid rgba(0,255,255,0.7)",borderBottom=None,padding="20px",position="relative",left="100px",width="900px",fontSize=18)),
        html.Hr(style=dict(position="relative",left="100px",width="900px",border="1px solid cyan")),
        html.Div("Test Value Reference",style=dict(wordSpacing="300px",paddingTop="20px",paddingLeft="50px",border="2px solid rgba(0,255,255,0.7)",borderTop=None,borderBottom=None,width="900px",height="50px",position="relative",left="100px")),
        html.Hr(style=dict(position="relative",left="100px",width="900px",border="1px solid cyan")),
        html.Div(id="output-report-boxes",style=dict(border="2px solid rgba(0,255,255,0.7)",borderTop=None,padding="2px",position="relative",paddingTop="50px",alignItems="center",left="100px",width="900px",fontSize=18)),
        html.Div(id="last-output"),
        html.Button("Submit".upper(),id="submit-report-button",style=dict(width="200px",height="100px",position="relative",backgroundColor="cyan",left="800px",fontSize=25,borderRadius="20px")),
        html.Div(html.H1("report preview".upper(),className="page-heading"),className="heading-divs",style=dict(position="relative",top="50px")),
        html.Div("type report to preview".upper(),id="report-preview",style=dict(color="cyan",border="10px solid #4b70f5",padding="50px",position="relative",top="100px"))
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
    dcc.Input(id={'type':'dynamic-input','name':'hb'},type="number",placeholder="Type Hb Value..",style=input_style),
    html.Div("( 11.0 - 16.8 Grams%)",style=limits_style)
]

tc_list = [
    html.Div("Total WBC Count :",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'tc_count'},type="number",placeholder="Type Tc value..",style=input_style),
    html.Div("( 5,000 - 10,000 Cells/cumm )",style=limits_style)
]

plt_list = [
    html.Div("Platelet Count :",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'plt_count'},type="number",placeholder="Type Plt Value..",style=input_style),
    html.Div("( 1.5 - 4.0 Lakhs/cumm )",style=limits_style)
]

dc_list = [
    html.Div("Differential Count :",style=text_style),
    html.Br(),
    html.Br(),
    html.Div("Polymorphs :",style=dict(position="relative",left="200px",fontSize=18)),
    dcc.Input(id={'type':'dynamic-input','name':'polymo'},type="number",placeholder="Type polymorphs..",style=dict(position="relative",width="170px",left="400px",bottom="20px",fontSize=20)),
    html.Div("( 40 - 70 %) ",style=dict(position="relative",left="670px",bottom="40px",fontSize=18)),
    html.Div("Lymphocytes :",style=dict(position="relative",left="200px",fontSize=18)),
    dcc.Input(id={'type':'dynamic-input','name':'lympho'},type="number",placeholder="Type Lymphocytes..",style=dict(position="relative",width="170px",left="400px",bottom="20px",fontSize=20)),
    html.Div("( 20 - 40 %)",style=dict(position="relative",left="670px",bottom="40px",fontSize=18)),
    html.Div("Esinophils :",style=dict(position="relative",left="200px",fontSize=18)),
    dcc.Input(id={'type':'dynamic-input','name':'esino'},type="number",placeholder="Type Esinophils..",style=dict(position="relative",width="170px",left="400px",bottom="20px",fontSize=20)),
    html.Div("( 02 - 06 %)",style=dict(position="relative",left="670px",bottom="40px",fontSize=18)),
    html.Div("Monocytes :",style=dict(position="relative",left="200px",fontSize=18)),
    dcc.Input(id={'type':'dynamic-input','name':'mono'},type="number",placeholder="Type Monocytes..",style=dict(position="relative",width="170px",left="400px",bottom="20px",fontSize=20)),
    html.Div("( 01 - 04 %)",style=dict(position="relative",left="670px",bottom="40px",fontSize=18))
]

crp_list = [
    html.Div("CRP :   ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'crp'},type="number",placeholder="Type CRP value..",style=input_style),
    html.Div(" ( < 6 ) ",style=limits_style)
]

widal_list = [
    html.Div("Blood for Widal : ",style=text_style),
    html.Div(dcc.Dropdown(["NON-REACTIVE","REACTIVE"],"REACTIVE"),id={'type':'dynamic-input','name':'widal'},style={**input_style,"width":"200px"}),
    html.Br(),
    html.Div(["OT-1 :",html.Div(dcc.Dropdown([160,80,40],80,id={'type':'dynamic-input','name':'widal-ot-react'}),style=dict(width="100px")),"dilutions"],style=dict(display="flex",gap="40px",position="relative",left="450px")),
    html.Br(),
    html.Div(["HT-1 :",html.Div(dcc.Dropdown([160,80,40],80,id={'type':'dynamic-input','name':'widal-ht-react'}),style=dict(width="100px")),"dilutions"],style=dict(display="flex",gap="40px",position="relative",left="450px")),
    html.Br(),
    html.Div("AH-1 : 40 dilutions",style=dict(position="relative",left="450px")),
    html.Br(),
    html.Div("BH-1 : 40 dilutions",style=dict(position="relative",left="450px"))
]

blood_group_list = [
    html.Div("Blood Group: ",style=text_style),
    html.Div(
        dcc.Dropdown(
            options = [
                "O POSITIVE",
                "A POSITIVE",
                "B POSITIVE",
                "AB POSITIVE",
                "O NEGATIVE",
                "A NEGATIVE",
                "B NEGATIVE",
                "AB NEGATIVE"
            ],
            id={'type':'dynamic-input','name':'blood-group'}    
        ),
        style={**input_style,"width":"200px"}    
    ),
    *[html.Br()]*10
]

total_bilirubin_list = [
    html.Div("Total Bilirubin : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'total-bili'},type="number",placeholder="Enter Total Bilirubin",style=input_style),
    html.Div(" ( 0.2 - 1.0 mg/dl)",style=limits_style)
]

direct_indirect_bilirubin_list = [
    html.Div("Direct Bilirubin: ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'direct-bili'},type="number",placeholder="Enter Direct Bilirubin",style=input_style),
    html.Div(" ( 0.2 - 0.4 mg/dl ) ",style=limits_style),
    html.Div("Indirect Bilirubin: ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'indirect-bili'},type="number",placeholder="Enter Direct Bilirubin",style=input_style),
    html.Div(" ( 0.2 - 0.6 mg/dl )",style=limits_style)
]

full_cbp_list = [
    *hb_list,
    html.Div("Total RBC Count : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'rbc-count'},type="number",placeholder="Rbc Count..",style=input_style),
    html.Div(" ( 4.0 - 5.0 milli/cumm ) ",style=limits_style),
    html.Div("PCV (Haematocrit) : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'hct'},type="number",placeholder="HCT..",style=input_style),
    html.Div(" (40% - 45%) ",style=limits_style),
    *tc_list,
    *plt_list,
    html.Div("E.S.R : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'esr'},type="number",placeholder="E.S.R..,",style=input_style),
    html.Div(" (02 - 10 mm/1 hour) ",style=limits_style),
    *dc_list
]

heamogram_list = [
    *hb_list,
    html.Div("Total RBC Count : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'rbc-count'},type="number",placeholder="Rbc Count..",style=input_style),
    html.Div(" ( 4.0 - 5.0 milli/cumm ) ",style=limits_style),
    html.Div("PCV (Haematocrit) : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'hct'},type="number",placeholder="HCT..",style=input_style),
    html.Div(" (40% - 45%) ",style=limits_style),
    *tc_list,
    *plt_list,
    html.Div("MCV : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'mcv'},type="number",placeholder="MCV..",style=input_style),
    html.Div(" ( 78 - 94 fl) ",style=limits_style),
    html.Div("MCH : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'mch'},type="number",placeholder="MCH..",style=input_style),
    html.Div(" ( 27 - 32 pg ) ",style=limits_style),
    html.Div("MCHC : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'mchc'},type="number",placeholder="MCHC..",style=input_style),
    html.Div(" ( 32 - 32 g/dl ) ",style=limits_style),
    html.Div("E.S.R : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'esr'},type="number",placeholder="E.S.R..,",style=input_style),
    html.Div(" (02 - 10 mm/1 hour) ",style=limits_style),
    *dc_list,
    html.Div("peripheral smear examination :".upper(),style={**text_style,"text-decoraton":"underline"}),
    html.Br(),
    html.Div("RBC: Normocytic Normochromic",style=text_style),
    html.Div("WBC: will be same as Total opinion",style=text_style),
    html.Div("No Blast cells are seen",style=text_style),
    html.Div("Platelets : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'platelet-opinion'},type="text",placeholder="Adequate",style=input_style),
    html.Div("Hemoparasites : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'hemoparasites-opinion'},type="text",placeholder="Not Seen",style=input_style),
    html.Div("Impression : ",style={**text_style,"text-decoration":"underline"}),
    dcc.Input(id={'type':'dynamic-input','name':'total-opinion'},type="text",placeholder="Microcytic Hypochromic Anemia",style={**input_style,"width":"500px"})
]

hba1c_list = [
    
]

blood_urea_list = [
    html.Div("Blood Urea : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'blood-urea'},type="number",placeholder="Enter Urea",style=input_style),
    html.Div(" ( 10 - 40 mg/dl )",style=limits_style)
]

serum_creatinine_list = [
    html.Div("Serum creatinine : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'serum-creat'},type="number",placeholder="Enter creatinine",style=input_style),
    html.Div()
]

uric_acid_list = [
    html.Div("Uric Acid : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'uric-acid'},type="number",placeholder="Enter Uric Acid",style=input_style),
    html.Div(" ( 2.5 - 7.5 IU/L ) ",style=limits_style)
]

urine_analysis_list = []

mantaoux_list = []

sugar_random_list = []

sugar_fasting_list = []

blood_for_aec_list = [
    html.Div("Blood for AEC Count : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'aec-count'},type="number",placeholder="460",style=input_style),
    html.Div(" (50 - 450 cells/cumm ) ",style=limits_style)
]

ra_factor_list = [
    html.Div("ra factor :".upper(),style=text_style),
    html.Div(dcc.Dropdown(["positive".upper(),"negative".upper()],"negative".upper(),id={'type':'dynamic-input','name':'ra-factor'}))
]

aso_titre_list = []


reports_original_dict = {
    "Hb":hb_list,
    "Total Count (TC)":tc_list,
    "Platelet Count":plt_list,
    "Differential Count (DC)":dc_list,
    "CRP":crp_list,
    "Widal":widal_list,
    "Full CBP":full_cbp_list,
    "Blood Group":blood_group_list,
    "Total Bilirubin":total_bilirubin_list,
    "Direct & Indirect Bilirubin":direct_indirect_bilirubin_list,
    "Heamogram":heamogram_list,
    "HBA1C":hba1c_list,
    "Blood Urea":blood_urea_list,
    "Serum Creatinine":serum_creatinine_list,
    "Uric Acid":uric_acid_list,
    "Urine Analysis":urine_analysis_list,
    "Mantaoux":mantaoux_list,
    "Random Sugar":sugar_random_list,
    "Fasting Sugar":sugar_fasting_list,
    "Blood for AEC count":blood_for_aec_list,
    "RA Factor":ra_factor_list,
    "ASO Titre":aso_titre_list
}


def get_df_item(p_sn:int,item_name:str):
    return copy_df.loc[copy_df.loc[:,"S.No."] == p_sn,item_name].item()


@callback(
    [
        Output("output-report","children"),              # patient detials
        Output("output-report-boxes","children")         # report details
    ],
    [
        Input("patients-dropdown","value"),
        Input("reports-dropdown","value"),
        Input("template-dropdown","value")
    ]
)
def submit_report(patients_sno, reports_value,template_value):
    global all_reports_dict,all_patients_values
    if patients_sno:
        all_patients_values[patients_sno] = {}
        all_reports_dict[patients_sno] = {"patient_details":[],"report_details":[]}
        all_reports_done_dict[patients_sno] = {}
        patients_details = [
                html.Div(f"Patient Name: {get_df_item(patients_sno,item_name='Patient Name')}"),
                html.Div(f"Age: {get_df_item(patients_sno,item_name='Patient Age')}"),
                html.Div(f"Reference By: {get_df_item(patients_sno,item_name='Reference By')}"),
                html.Div(f"Date: {get_df_item(patients_sno,item_name="Date")}")
            ]
        all_reports_dict[patients_sno]["patient_details"] = patients_details
        if reports_value:
            for x in reports_value:
                all_reports_dict[patients_sno]['report_details'] += reports_original_dict[x]
        if template_value:
            template_value = json.loads(template_value)
            for x in template_value:
                all_reports_dict[patients_sno]['report_details'] += reports_original_dict[x]
        return all_reports_dict[patients_sno]["patient_details"],all_reports_dict[patients_sno]["report_details"]
    return ["Select a Serial Number to Display....","Select a Test to Display...."]




def create_pdf(filename,page_size,details_dict):

    c = canvas.Canvas(filename=filename,pagesize=page_size)
    page_width, page_height = A5
    margin = inch
    content_width = page_width - 2 * margin
    y_position = page_height - margin
    c.setFont("Times-Italic",12)




@callback(
    Output("patient-data-store","data"),
    Input("submit-report-button","n_clicks"),
    [
        State("patients-dropdown","value"),
        State("page-size-dropdown","value"), 
        State({'type':'dynamic-input','name':ALL},'value'),
        State({'type':'dynamic-input','name':ALL},'id')
    ],
    prevent_initial_call=True
)
def lodge_inputs_to_dict(n_clicks,patients_sno,page_size_value,input_values,input_ids):
    global all_patients_values
    if not input_values:
        raise PreventUpdate
    if n_clicks:
        all_patients_values[patients_sno] = {id['name']: value for id,value in zip(input_ids,input_values)}
        all_patients_values[patients_sno] = {**all_patients_values[patients_sno],'page_size':page_size_value}
        return all_patients_values



register_page(
    "Reports",
    layout=layout,
    path="/reports"
)