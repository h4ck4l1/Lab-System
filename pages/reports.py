import json,os,flask,datetime
import pandas as pd
from io import StringIO
from reportlab.pdfgen import canvas            
from reportlab.lib.pagesizes import A5,A4,portrait      
from reportlab.lib.units import inch           
from reportlab.lib import colors               
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from dash import html,dcc,Input,Output,callback,register_page,State,ALL
from dash.exceptions import PreventUpdate
registerFont(TTFont("CenturySchoolBook-BoldItalic","assets/schlbkbi.ttf"))

all_reports_dict = {}
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
    "ESR",
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
    "ASO Titre",
    "Serum Amylase",
    "Serum Lipase",
    "Serum Protein",
    "Serum Albumin",
    "Serum Globulin",
    "Serum A/G Ratio",
    "Serum Sodium",
    "Serum Pottasium",
    "Serum Chloride",
    "Serum Calcium"
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
        {"label":"RFT","value":json.dumps(["Blood Urea","Serum Creatinine","Uric Acid"])},
        {"label":"Lipid Profile","value":json.dumps(["Lipid Profile"])}
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
        html.Button("preview".upper(),id="preview-button",style=dict(width="200px",height="100px",position="relative",left="1500px",fontSize=25,borderRadius="20px",backgroundColor="cyan")),
        html.Div("type report to preview".upper(),id="report-preview",style=dict(color="cyan",border="10px solid #4b70f5",padding="50px",position="relative",top="100px",height="1750px")),
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
    html.Div("----------------",style=dict(position="relative",left="400px",bottom="20px")),
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
    html.Div("-----------",style=limits_style),
    html.Div(" ( 0.2 - 0.6 mg/dl )",style=limits_style)
]

esr_list = [
    html.Div("E.S.R : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'esr'},type="number",placeholder="E.S.R..,",style=input_style),
    html.Div(" (02 - 10 mm/1 hour) ",style=limits_style)
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
    *esr_list,
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
    html.Div("Glycosylated Hb (HbA1c) Test: ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'hba1c_first'},type="number",placeholder="Type Hba1c %..",style=input_style),
    html.Div("%",style=limits_style),
    html.Div("Esitmiated Average Glucose (eAG): ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'hba1c_second'},type="number",placeholder="Type Hba1c mg/dl..",style=input_style),
    html.Div("mg/dl",style=limits_style)
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

urine_analysis_list = [
    html.Div("Urine analysis :",style=text_style),
    html.Br(),
    html.Br(),
    html.Div("Sugar : ",style=text_style),
    html.Div([dcc.Dropdown(["NIL","+","++","+++"],"NIL",id={'type':'dynamic-input','name':'urine_sugar'})],style=input_style),
    html.Div("Albumin : ",style=text_style),
    html.Div([dcc.Dropdown(["NIL","TRACES","+","++","+++"],"TRACES",id={'type':'dynamic-input','name':'urine_albumin'})],style=input_style),
    html.Div("Bile Salts: ",style=text_style),
    html.Div([dcc.Dropdown(["negative".upper(),"positive".upper()],"negative".upper(),id={'type':'dynamic-input','name':'urine_bs'})],style=input_style),
    html.Div("Bile Pigments: ",style=text_style),
    html.Div([dcc.Dropdown(["negative".upper(),"positive".upper()],"negative".upper(),id={'type':'dynamic-input','name':'urine_bp'})],style=input_style),
    html.Div("Micro : ",style=text_style),
    html.Div([
        dcc.Input(id={'type':'dynamic-input','name':'urine_first_pus'},type="number",style=dict(width="100px")),
        "-",
        dcc.Input(id={'type':'dynamic-input','name':'urine_second_pus'},type="number",style=dict(width="100px",marginRight="20px")),
        "Pus Cells"
    ],style=dict(position="relative",left="300px",margin="10px",wordSpacing="10px")),
    html.Div([
        dcc.Input(id={'type':'dyanmic-input','name':'urine_first_rbc'},type="number",placeholder="No..",style=dict(width="100px")),
        "-",
        dcc.Input(id={'type':'dynamic-input','name':'urine_second_rbc'},type="number",placeholder="No..",style=dict(width="100px",marginRight="20px")),
        "RBC  *(leaving blank means No RBC)"
    ],style=dict(position="relative",left="300px",margin="10px",wordSpacing="10px")),
    html.Div([
        dcc.Input(id={'type':'dyanmic-input','name':'urine_first_casts'},type="number",placeholder="No..",style=dict(width="100px")),
        "-",
        dcc.Input(id={'type':'dynamic-input','name':'urine_second_casts'},type="number",placeholder="No..",style=dict(width="100px",marginRight="20px")),
        "Casts  *(leaving blank means No Casts)"
    ],style=dict(position="relative",left="300px",margin="10px",wordSpacing="10px")),
    html.Div([
        dcc.Input(id={'type':'dyanmic-input','name':'urine_first_crystals'},type="number",placeholder="No..",style=dict(width="100px")),
        "-",
        dcc.Input(id={'type':'dynamic-input','name':'urine_second_crystals'},type="number",placeholder="No..",style=dict(width="100px",marginRight="20px")),
        "Crystals  *(leaving blank means No Crystals)"
    ],style=dict(position="relative",left="300px",margin="10px",wordSpacing="10px")),
    html.Div([
        dcc.Input(id={'type':'dynamic-input','name':'urine_first_ep'},type="number",style=dict(width="100px")),
        "-",
        dcc.Input(id={'type':'dynamic-input','name':'urine_second_ep'},type="number",style=dict(width="100px",marginRight="20px")),
        "Epithelial Cells Present"
    ],style=dict(position="relative",left="300px",margin="10px",wordSpacing="10px"))
]

urine_pregnency_list = [
    html.Div("Urine Test Report : ",style=text_style),
    html.Div("Urine Pregnancy Test : ",style=text_style),
    html.Div([dcc.Dropdown(["negative".upper(),"positive".upper()],"negative".upper(),id={'type':'dynamic-input','name':'preg_test'})],style=input_style)
]

pt_aptt_list = [
    html.Div("Prothrombin Time Test",style={**text_style,"left":"500px"}),
    html.Div("P.T Test: 14.9 seconds",text_style),
    html.Div("P.T. Control : 13.4 seconds",text_style),
    html.Div("INR : 1.2",style=text_style)
]

mantaoux_list = [
    html.Div("mantoux test :".upper(),style=text_style),
    html.Div([dcc.Dropdown(["positive".upper(),"negative".upper()],"negative".upper(),id={'type':'dynamic-input','name':'mantoux_test'})],style=input_style)
]

sugar_random_list = [
    html.Div("Blood Sugar ( Random ) : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'random_sugar'},type="number",placeholder="Type RBS..",style=input_style),
    html.Div(" ( 70 - 140 mg/dl ) ",style=limits_style)
]

sugar_fasting_list = [
    html.Div("Blood Sugar ( Fasting ) : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'fasting_sugar'},type="number",placeholder="Type FBS..",style=input_style),
    html.Div(" ( 70 - 110 mg/dl ) ",style=limits_style)
]

lipid_profile_list = [
    html.Div("Total Cholesterol : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_tc'},type="number",placeholder="Type Tc..",style=input_style),
    html.Div("High Density Lipoprotein ( HDL ) : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_hdl'},type="number",placeholder="Type HDL...",style=input_style),
    html.Div("Low Density Lipoprotein : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_ldl'},type="number",placeholder="Type LDL...",style=input_style),
    html.Div("Very Low Density Lipoprotein : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_vldl'},type="number",placeholder="Type VLDL",style=input_style),
    html.Div("Triglyceride (F): ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_tri'},type="number",placeholder="Type Triglyceride...",style=input_style)
]

blood_for_aec_list = [
    html.Div("Blood for AEC Count : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'aec-count'},type="number",placeholder="460",style=input_style),
    html.Div(" (50 - 450 cells/cumm ) ",style=limits_style)
]

ra_factor_list = [
    html.Div("ra factor :".upper(),style=text_style),
    html.Div(dcc.Dropdown(["positive".upper(),"negative".upper()],"negative".upper(),id={'type':'dynamic-input','name':'ra-factor'}),style=dict(position="relative",width="200px",left="300px",bottom="25px")),
    html.Div(" ( 1 : ",style={**limits_style,"bottom":"50px"}),
    dcc.Input(id={'type':'dynamic-input','name':'ra-dilutions'},type="number",placeholder="None",style={**limits_style,"bottom":"75px","left":"620px","width":"100px"}),
    html.Div(" dilutions ) ",style={**limits_style,"left":"730px","bottom":"95px"})
]

aso_titre_list = []

serum_amylase_list = []

serum_lipase_list = []

serum_protein_list = []

serum_albumin_list = []

serum_globulin_list = []

serum_ag_ratio_list = []

serum_sodium_list = []

serum_pottasium_list = []

serum_chloride_list = []

serum_calcium_list = []


reports_original_dict = {
    "Hb":hb_list,
    "Total Count (TC)":tc_list,
    "Platelet Count":plt_list,
    "Differential Count (DC)":dc_list,
    "ESR":esr_list,
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
        patients_details = [
                html.Div(f"Patient Name: {get_df_item(patients_sno,item_name='Patient Name')}"),
                html.Div(f"Age: {get_df_item(patients_sno,item_name='Patient Age')}"),
                html.Div(f"Reference By: {get_df_item(patients_sno,item_name='Reference By')}"),
                html.Div(f"Date: {get_df_item(patients_sno,item_name="Date")}")
            ]
        all_reports_dict[patients_sno]["patient_details"] = patients_details
        if reports_value:
            all_patients_values[patients_sno]["tests"] = []
            for x in reports_value:
                all_reports_dict[patients_sno]['report_details'] += reports_original_dict[x]
                all_patients_values[patients_sno]["tests"].append(x)
        if template_value:
            template_value = json.loads(template_value)
            for x in template_value:
                all_reports_dict[patients_sno]['report_details'] += reports_original_dict[x]
        return all_reports_dict[patients_sno]["patient_details"],all_reports_dict[patients_sno]["report_details"]
    return ["Select a Serial Number to Display....","Select a Test to Display...."]


def cal_string_width(c:canvas.Canvas,total_string,font_name,font_size):
    return c.stringWidth(total_string,font_name,font_size)

def patient_details_canvas(
        c:canvas.Canvas,
        font_name:str,
        font_size:int,
        page_height:float,
        patient_name:str,
        patient_details_space:int,
        patient_age:float,
        patient_age_group:str,
        patient_gender:str,
        doctor_name:str,
        patient_serial_no:int,
        collection_time:str,
        patient_specimen:str,
        frmt_time:str
    ):
    c.setFont(font_name,font_size)
    c.drawString(42,page_height-75,f"Pt. Name : {patient_name.upper()}")
    c.drawString(42,page_height-(75 + patient_details_space),f"Gender : {patient_gender}")                  
    age_string = f"Age: {patient_age} {patient_age_group}"
    c.drawString(375-cal_string_width(c,age_string,font_name,font_size),page_height-(75 + patient_details_space),age_string)     # s
    c.drawString(42,page_height-(75 + 2*patient_details_space),f"Ref.Dr.By. : {doctor_name}")                                                # 99 + 24
    c.drawString(42,page_height-(75 + 3*patient_details_space),f"Serial No: 000{patient_serial_no}")
    time_string = f"Collection Time: {collection_time}"
    c.drawString(375-cal_string_width(c,time_string,font_name,font_size),page_height-(75 + 3*patient_details_space),time_string)        # s
    c.drawString(42,page_height-(75 + 4*patient_details_space),f"Specimen: {patient_specimen}")
    date_string = f"Date: {frmt_time}"
    c.drawString(375-cal_string_width(c,date_string,font_name,font_size),page_height-(75 + 4*patient_details_space),date_string)                         # s
    c.setDash()
    c.line(40,page_height-(75 + 4 * patient_details_space) - 5,379,page_height-(75 + 4 * patient_details_space) - 5)
    c.line(40,page_height-(75 + 4 * patient_details_space) - 18,379,page_height-(75 + 4 * patient_details_space) - 20)
    c.setFont(font_name,8)
    c.drawString(42,page_height-(75 + 4 * patient_details_space) - 15,"test".upper())
    c.drawString(190,page_height-(75 + 4 * patient_details_space) - 15,"value".upper())
    reference_string = "reference range".upper()
    c.drawString(375-cal_string_width(c,reference_string,font_name,8),page_height-(75 + 4 * patient_details_space) - 15,reference_string)
    return c

def if_draw_bold(c:canvas.Canvas,value,value_string,limit_a,limit_b,x,y):
    if (value < limit_a) | (value > limit_b):
        for offset in [0,0.25,-0.25,0.35,-0.35]:
            c.drawString(x+offset,y,f":  {value_string}")
    else:
        c.drawString(x,y,f":  {value_string}")
    return c


def hb_canvas(c:canvas.Canvas,hb_value:float,page_size:str,h:int):
    if page_size == "SMALL/A5":
        entity_height = 25
        c.setFont("Times-BoldItalic",12)
        c.drawString(62,h,"Heamoglobin")
        c = if_draw_bold(c,hb_value,hb_value,11.0,16.8,182,h)
        hb_string = "( 11.0 - 16.8 Grams% )"
        c.drawString(375-cal_string_width(c,hb_string,"Times-BoldItalic",12),h,hb_string)
    else:
        pass
    return c,h - entity_height


def tc_canvas(c:canvas.Canvas,tc_value:int,page_size:str,h:int):
    if page_size == "SMALL/A5":
        entity_height = 25
        c.setFont("Times-BoldItalic",12)
        c.drawString(62,h,"Total WBC Count")
        c = if_draw_bold(c,tc_value,f"{tc_value//1000},000",5000,10000,182,h)
        tc_string = "( 5,000 - 10,000 Cells/cumm )"
        c.drawString(375-cal_string_width(c,tc_string,"Times-BoldItalic",12),h,tc_string)
    else:
        pass
    return c,h-entity_height


def plt_canvas(c:canvas.Canvas,plt_value:float,page_size:str,h:int):
    if page_size == "SMALL/A5":
        entity_height = 25
        c.setFont("Times-BoldItalic",12)
        c.drawString(62,h,"Platelet Count : ")
        if plt_value < 1:
            plt_string = f"{int(plt_value * 100)},000"
        else:
            plt_string = str(plt_value)
        c = if_draw_bold(c,plt_value,plt_string,1.5,4.0,182,h)
        plt_string = "( 1.5 - 4.0 Lakhs/cumm )"
        c.drawString(375-cal_string_width(c,plt_string,"Times-BoldItalic",12),h,plt_string)
    else:
        pass
    return c,h-entity_height

def dc_canvas(
        c:canvas.Canvas,
        dc_count:list,
        page_size:str,
        h:int
    ):
    
    def p(v):
        if v < 10:
            s = f"0{v}"
        else:
            s = f"{v}"
        return s

    polymo_value,lympho_value,esnio_value = dc_count
    if polymo_value + lympho_value + esnio_value == 100:
        esnio_value -= 1
    mono_value = 100 - (polymo_value + lympho_value + esnio_value)
    if page_size == "SMALL/A5":
        entity_height = 130            # 25 * 5 + 5
        c.setFont("Times-BoldItalic",12)
        c.drawString(62,h,"Differential Count:")
        c.line(62,h-5,62+cal_string_width(c,"Differential Count","Times-BoldItalic",12),h-5)
        c.drawString(142,h-30,"Polymorphs")
        c.drawString(142,h-55,"Lymphocytes")
        c.drawString(142,h-80,"Eosinophils")
        c.drawString(142,h-105,"Monocytes")
        c = if_draw_bold(c,polymo_value,p(polymo_value),40,70,260,h-30)
        c = if_draw_bold(c,lympho_value,p(lympho_value),20,40,260,h-55)
        c = if_draw_bold(c,esnio_value,p(esnio_value),2,6,260,h-80)
        c = if_draw_bold(c,mono_value,p(mono_value),1,4,260,h-105)
        c.drawString(375-cal_string_width(c,"( 40 - 70 %)","Times-BoldItalic",12),h-30,"( 40 - 70 %)")
        c.drawString(375-cal_string_width(c,"( 40 - 70 %)","Times-BoldItalic",12),h-55,"( 20 - 40 %)")
        c.drawString(375-cal_string_width(c,"( 40 - 70 %)","Times-BoldItalic",12),h-80,"( 02 - 06 %)")
        c.drawString(375-cal_string_width(c,"( 40 - 70 %)","Times-BoldItalic",12),h-105,"( 01 - 04 %)")
    else:
        pass
    return c,h - entity_height


def crp_canvas():
    pass

def widal_canvas():
    pass

def full_cbp_canvas():
    pass

def blood_group_canvas():
    pass

def total_bilirubin_canvas():
    pass

def direct_and_indirect_bilirubin_canvas():
    pass

def heamogram_canvas():
    pass

def hb1ac_canvas():
    pass

def blood_urea_canvas():
    pass

def serum_creat_canvas():
    pass

def uric_acid_cavnas():
    pass

def urine_analysis_canvas():
    pass

def mantaux_canvas():
    pass

def random_sugar_canvas():
    pass

def fasting_sugar_canvas():
    pass

def blood_for_aec_canvas():
    pass

def ra_factor_canvas():
    pass

def aso_titre_canvas():
    pass




reports_canvas_dict = {
    "Hb":hb_canvas,
    "Total Count (TC)":tc_canvas,
    "Platelet Count":plt_canvas,
    "Differential Count (DC)":dc_canvas,
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

report_canvas_values_dict = {
    "Hb":"hb",
    "Total Count (TC)":"tc_count",
    "Platelet Count":"plt_count",
    "Differential Count (DC)":"dc_count",
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

def create_pdf(serial_no,page_size,details_dict):

    global copy_df,all_patients_values
    patient_serial_no = serial_no
    collection_date = str(get_df_item(serial_no,"Date"))
    collection_time = get_df_item(serial_no,"Time")
    patient_name = get_df_item(serial_no,"Patient Name")
    patient_age = get_df_item(serial_no,"Patient Age")
    patient_age_group = get_df_item(serial_no,"Age Group")
    patient_gender = get_df_item(serial_no,"Gender")
    patient_specimen = "Blood"
    doctor_name = get_df_item(serial_no,"Reference By")
    patient_details_space = 18
    report_details_space = 18
    time_obj = datetime.datetime.strptime(collection_date,"%Y-%m-%d %H:%M:%S")
    frmt_time = time_obj.strftime("%d-%m-%y")
    patient_name_save = patient_name.replace(".","_")
    year_extract,month_extract,day_extract = time_obj.strftime("%Y"),time_obj.strftime("%m"),time_obj.strftime("%d")
    base_dir = "assets"
    year_dir = os.path.join(base_dir,year_extract)
    month_dir = os.path.join(year_dir,month_extract)
    day_dir = os.path.join(month_dir,day_extract)
    os.makedirs(day_dir,exist_ok=True)
    filename = os.path.join(day_dir,f"{patient_name_save}.pdf")
    if page_size == "SMALL/A5":
        font_name = "Times-BoldItalic"
        font_size = 12
        c = canvas.Canvas(filename,pagesize=portrait(A5))
        page_width, page_height = A5
        c.rect(40,40,page_width - 2 * 40, page_height - 2 * 50)

        # c.setDash(6,3)
        # c.setFont(font_name,5)
        # for x in range(0,int(page_width),10):
        #     if x % 20 == 0:
        #         c.line(x,page_height,x,0)
        #         c.drawString(x+2,page_height-30,str(x))
        # for x in range(0,int(page_height),10):
        #     if x % 20 == 0:
        #         c.line(0,x,page_width,x)
        #         c.drawString(30,x+2,str(x))


        c = patient_details_canvas(
            c,
            font_name,
            font_size,
            page_height,
            patient_name,
            patient_details_space,
            patient_age,
            patient_age_group,
            patient_gender,
            doctor_name,
            patient_serial_no,
            collection_time,
            patient_specimen,
            frmt_time
        )

        h = 410
        serial_no = str(serial_no)
        tests_list = details_dict[serial_no]["tests"]
        for t in tests_list:
            c,h = reports_canvas_dict[t](c,details_dict[serial_no][report_canvas_values_dict[t]],page_size,h)
        c.save()
    else:
        pass
    return filename

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
        temp_dict = {"dc_count":[]}
        for id,value in zip(input_ids,input_values):
            print(id['name'])
            if id['name'] in ['polymo','lympho','esino']:
                temp_dict["dc_count"].append(value)
            else:
                temp_dict[id['name']] = value
        all_patients_values[patients_sno] = {**all_patients_values[patients_sno],**temp_dict}
        all_patients_values[patients_sno] = {**all_patients_values[patients_sno],'page_size':page_size_value}
        return all_patients_values
    


@callback(
    Output("report-preview","children"),
    Input("preview-button","n_clicks"),
    [
        State("patient-data-store","data"),
        State("patients-dropdown","value"),
        State("page-size-dropdown","value")
    ]
)
def preview_report(n_clicks,data,patient_sno,page_size):
    if not n_clicks:
        raise PreventUpdate
    if n_clicks:
        print(data)
        filename = create_pdf(patient_sno,page_size,data)
        return html.Iframe(
            src=filename,
            style=dict(width="100%",height="1650px")
        )


register_page(
    "Reports",
    layout=layout,
    path="/reports"
)