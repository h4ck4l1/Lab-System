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
big_break = [html.Br()] * 5
large_break = [html.Br()] * 10
small_break = [html.Br()] * 2

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
    "Malaria",
    "PCV(HCT)",
    "DENGUE",
    "Blood Group",
    "Total Bilirubin",
    "Direct & Indirect Bilirubin",
    "SGOT",
    "SGPT",
    "ALKP",
    "Heamogram",
    "HBA1C",
    "Fasting Sugar",       
    "Random Sugar",
    "Blood Urea",
    "Serum Creatinine",
    "Uric Acid",
    "Urine Analysis",
    "Urine Pregnancy",
    "Lipid Profile",
    "Mantaoux",
    "Heamogram",
    "Blood for AEC Count",
    "RA Factor",
    "ASO Titre",
    "PT APTT",
    "Serum Amylase",
    "Serum Lipase",
    "Serum Protein",
    "Serum Albumin",
    "Serum Globulin",
    "Serum A/G Ratio",
    "Serum Sodium",
    "Serum Potassium",
    "Serum Chloride",
    "Serum Calcium",
    "V.D.R.L",
    "HBsAg",
    "HIV I & II Antibodies Test",
    "HCV I & II Antibodies Test",
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
        {"label":"HB, TC, PLATELET, DC, CRP","value":json.dumps(["Hb","Total Count (TC)","Platelet Count","Differential Count (DC)","CRP"])},
        {"label":"HB, TC, DC","value":json.dumps(["Hb","Total Count (TC)","Differential Count (DC)"])},
        {"label":"HB, TC, PLATELET, DC, URINE","value":json.dumps(["Hb","Total Count (TC)","Platelet Count","Differential Count (DC)","Urine Analysis"])},
        {"label":"HB, TC, PLATELET, DC, RBS","value":json.dumps(["Hb","Total Count (TC)","Platelet Count","Differential Count (DC)","Random Sugar"])},
        {"label":"HB, TC, PLATELET, DC, WIDAL","value":json.dumps(["Hb","Total Count (TC)","Platelet Count","Differential Count (DC)","Widal"])},
        {"label":"PACK 1","value":json.dumps(["HBA1C","Random Sugar","Fasting Sugar"])},
        {"label":"PACK 2","value":json.dumps(["Blood Urea","Serum Creatinine","Lipid Profile"])},
        {"label":"RFT","value":json.dumps(["Blood Urea","Serum Creatinine","Uric Acid"])},
        {"label":"Lipid Profile","value":json.dumps(["Lipid Profile"])},
        {"label":"Electrolytes","value":json.dumps(["Serum Amylase","Serum Lipase","Serum Protein","Serum Albumin","Serum Globulin","Serum A/G Ratio","Serum Sodium","Serum Potassium","Serum Chloride","Serum Calcium"])}
    ],
    id="template-dropdown"
)

layout = html.Div(
    [
        html.Div(html.H1("Patients report",className="page-heading"),className="heading-divs"),
        *big_break,
        html.Div(patients_dropdown,style=dict(width="400px",alignItems="center")),
        html.Div(id="data-present",style=dict(position="relative",left="100px",top="50px",color="red")),
        html.Button("Storage Clear",id="clear-storage",style=dict(position="relative",backgroundColor="red",left="500px",bottom="50px",width="100px",height="50px")),
        *big_break,
        html.Div(reports_dropdown,style=dict(width="400px",alignItems="center")),
        html.Div(page_size_dropdown,style=dict(width="400px",alignItems="center",position="relative",left="420px",bottom="36px")),
        html.Div(templates_dropdown,style=dict(width="400px",alignItems="center",position="relative",left="840px",bottom="73px")),
        *large_break,
        html.Div(id="output-report",style=dict(border="2px solid rgba(0,255,255,0.7)",borderBottom=None,padding="20px",position="relative",left="100px",width="900px",fontSize=18)),
        html.Hr(style=dict(position="relative",left="100px",width="900px",border="1px solid cyan")),
        html.Div("Test Value Reference",style=dict(wordSpacing="300px",paddingTop="20px",paddingLeft="50px",border="2px solid rgba(0,255,255,0.7)",borderTop=None,borderBottom=None,width="900px",height="50px",position="relative",left="100px")),
        html.Hr(style=dict(position="relative",left="100px",width="900px",border="1px solid cyan")),
        html.Div(id="output-report-boxes",style=dict(border="2px solid rgba(0,255,255,0.7)",borderTop=None,padding="2px",position="relative",paddingTop="50px",alignItems="center",left="100px",width="900px",fontSize=18)),
        html.Div(id="last-output"),
        html.Button("Submit".upper(),id="submit-report-button",style=dict(width="200px",height="100px",position="relative",backgroundColor="cyan",left="800px",fontSize=25,borderRadius="20px")),
        html.Div(html.H1("report preview".upper(),className="page-heading"),className="heading-divs",style=dict(position="relative",top="50px")),
        html.Button("preview".upper(),id="preview-button",style=dict(width="200px",height="100px",position="relative",left="600px",top="75px",fontSize=25,borderRadius="20px",backgroundColor="cyan")),
        html.Div(["top space slider  ".upper(),dcc.Slider(min=0,max=200,step=20,value=0,id="top-slider")],style=dict(left="50px",position="relative",width="550px",fontSize=15)),
        html.Div(["between space slider  ".upper(),dcc.Slider(min=10,max=40,step=2,value=24,id="slider")],style=dict(left="50px",position="relative",width="550px",top="20px",fontSize=15)),
        html.Div("type report to preview".upper(),id="report-preview",style=dict(color="cyan",border="10px solid #4b70f5",padding="50px",position="relative",height="1750px",top="100px")),
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

malaria_list = [
    html.Div("Test For Malaria Parasite (M.P): NON-REACTIVE",style=text_style),
    html.Div([dcc.Dropdown(["Long","Short"],"Short",id={'type':'dynamic-input','name':'malaria-test'})],style={**input_style,"left":"700px"})
]

widal_list = [
    html.Div("Blood for Widal : ",style=text_style),
    html.Div([dcc.Dropdown(["NON-REACTIVE","REACTIVE"],"REACTIVE",id={'type':'dynamic-input','name':'widal'})],style={**input_style,"width":"200px"}),
    html.Div([dcc.Dropdown(["SHORT","LONG"],"LONG",id={'type':'dynamic-input','name':'widal-form'})],style=dict(position="relative",left="600px",bottom="50px",width="100px",height="50px")),
    html.Br(),
    html.Div(["OT-1 :",html.Div(dcc.Dropdown([160,80,40],80,id={'type':'dynamic-input','name':'widal-ot-react'}),style=dict(width="100px")),"dilutions"],style=dict(display="flex",gap="40px",position="relative",left="450px")),
    html.Br(),
    html.Div(["HT-1 :",html.Div(dcc.Dropdown([160,80,40],80,id={'type':'dynamic-input','name':'widal-ht-react'}),style=dict(width="100px")),"dilutions"],style=dict(display="flex",gap="40px",position="relative",left="450px")),
    html.Br(),
    html.Div("AH-1 : 40 dilutions",style=dict(position="relative",left="450px")),
    html.Br(),
    html.Div("BH-1 : 40 dilutions",style=dict(position="relative",left="450px")),
    *small_break
]

blood_group_list = [
    html.Div("Blood Group: ",style=text_style),
    html.Div(
        dcc.Dropdown(
            options = ["O POSITIVE","A POSITIVE","B POSITIVE","AB POSITIVE","O NEGATIVE","A NEGATIVE","B NEGATIVE","AB NEGATIVE"],
            id={'type':'dynamic-input','name':'blood-group'}    
        ),
        style={**input_style,"width":"200px"}    
    )
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

sgot_list = [
    html.Div("Aspirate Amino Transferase (SGOT): ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'sgot'},type="number",placeholder="29 (normal)",style={**input_style,"left":"500px"}),
    html.Div("( < 40 )",style={**limits_style,"left":"700px"})
]

sgpt_list = [
    html.Div("Alinine  Amino Transferase (SGPT): ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'sgpt'},type="number",placeholder="29 (normal)",style={**input_style,"left":"500px"}),
    html.Div("( < 40 )",style={**limits_style,"left":"700px"})
]

alkp_list = [
    html.Div("Alkaline Phosphatase (ALKP): ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'alkp'},type="number",placeholder="29 (normal)",style={**input_style,"left":"500px"}),
    html.Div("( 37 - 147 )",style={**limits_style,"left":"700px"})
]

esr_list = [
    html.Div("E.S.R : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'esr'},type="number",placeholder="E.S.R..,",style=input_style),
    html.Div(" (02 - 10 mm/1 hour) ",style=limits_style)
]

hct_list = [
    html.Div("PCV (Haematocrit) : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'hct'},type="number",placeholder="HCT..",style=input_style),
    html.Div(" (40% - 45%) ",style=limits_style),
]

dengue_list = [
    html.Div("dengue test".upper(),style={**input_style,"text-decoration":"underline"}),
    html.Div("IgM  antibodies to Dengue Virus   : ",style=text_style),
    html.Div([dcc.Dropdown(["negative".upper(),"positive".upper()],"negative".upper(),id={'type':'dynamic-input','name':'dengue_igm'},style=input_style)]),
    html.Div("IgG  antibodies to Dengue Virus   : ",style=text_style),
    html.Div([dcc.Dropdown(["negative".upper(),"positive".upper()],"negative".upper(),id={'type':'dynamic-input','name':'dengue_igg'},style=input_style)]),
    html.Div("NS1  antibodies to Dengue Virus  : ",style=text_style),
    html.Div([dcc.Dropdown(["negative".upper(),"positive".upper()],"positive".upper(),id={'type':'dynamic-input','name':'dengue_ns'},style=input_style)]),
]

full_cbp_list = [
    *hb_list,
    html.Div("Total RBC Count : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'rbc-count'},type="number",placeholder="Rbc Count..",style=input_style),
    html.Div(" ( 4.0 - 5.0 milli/cumm ) ",style=limits_style),
    *hct_list,
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
    *hct_list,
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
    html.Div(" ( 32 - 36 g/dl ) ",style=limits_style),
    *esr_list,
    *dc_list,
    html.Div("peripheral smear examination :".upper(),style={**text_style,"text-decoraton":"underline"}),
    *small_break,
    html.Div("RBC: ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'heamo-rbc'},type="text",placeholder="Normocytic Normochromic",value="Normocytic Normochromic",style=input_style),
    html.Div("WBC: will be same as Total opinion",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'blast-cells'},type="text",placeholder="No Blast cells are seen",value="No Blast cells are seen",style=text_style),
    html.Div("Platelets : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'platelet-opinion'},type="text",placeholder="Adequate",value="Adequate",style=input_style),
    html.Div("Hemoparasites : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'hemoparasites-opinion'},type="text",placeholder="Not Seen",value="Not Seen",style=input_style),
    html.Div("Impression : ",style={**text_style,"text-decoration":"underline"}),
    dcc.Input(id={'type':'dynamic-input','name':'total-opinion'},type="text",placeholder="Microcytic Hypochromic Anemia",value="Microcytic Hypochromic Anemia",style={**input_style,"width":"500px"})
]

hba1c_list = [
    html.Div("Glycosylated Hb (HbA1c) Test: ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'hba1c_first'},type="number",placeholder="Type Hba1c %..",style={**input_style,"left":"500px"}),
    html.Div("%",style={**limits_style,"left":"700px"}),
    html.Div("Esitmiated Average Glucose (eAG): ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'hba1c_second'},type="number",placeholder="Type Hba1c mg/dl..",style={**input_style,"left":"500px"}),
    html.Div("mg/dl",style={**limits_style,"left":"700px"}),
    html.Div([dcc.Dropdown(["SMALL","LONG"],"LONG",id={'type':'dynamic-input','name':'hba1c_dropdown'})],style={**limits_style,"width":"150px","left":"800px","bottom":"25px"})
]

blood_urea_list = [
    html.Div("Blood Urea : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'blood-urea'},type="number",placeholder="Enter Urea",style=input_style),
    html.Div(" ( 10 - 40 mg/dl )",style=limits_style)
]

serum_creatinine_list = [
    html.Div("Serum creatinine : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'serum-creat'},type="number",placeholder="Enter creatinine",style=input_style),
    html.Div("( 2.5 - 7.5 IU/L )",style=limits_style)
]

uric_acid_list = [
    html.Div("Uric Acid : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'uric-acid'},type="number",placeholder="Enter Uric Acid",style=input_style),
    html.Div(" ( 2.5 - 7.5 IU/L ) ",style=limits_style)
]

urine_analysis_list = [
    html.Div("Urine analysis :",style=text_style),
    *small_break,
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
    html.Div("Prothrombin Time Test",style={**text_style,"left":"400px","text-decoration":"underline"}),
    *big_break,
    html.Div("P.T Test:",style=text_style),
    html.Div(" 14.9 seconds",style=input_style),
    html.Div("P.T. Control : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'pt_control'},type="number",placeholder="13.4 seconds",style=input_style),
    html.Div("INR : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'pt_inr'},type="number",placeholder="1.2",style=input_style),
    *small_break,
    html.Div("Activate Partial Thromboplastin Time",style={**text_style,"left":"400px","text-decoration":"underline"}),
    *big_break,
    html.Div("APTT Test :",style=text_style),
    html.Div(" 36",style=input_style),
    html.Div(" ( Nor: 26 - 38 sec )",style=limits_style),
    html.Div("APTT Control : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'aptt_control'},type="number",placeholder="33.6 seconds...",style=input_style),
    html.Div("( Nor 26 - 38 sec )",style=limits_style)
]

mantaoux_list = [
    html.Div("mantoux test :".upper(),style=text_style),
    html.Div([dcc.Dropdown(["positive".upper(),"negative".upper()],"negative".upper(),id={'type':'dynamic-input','name':'mantoux_test'})],style=input_style)
]

sugar_random_list = [
    html.Div("Blood Sugar (Random):",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'random_sugar'},type="number",placeholder="Type RBS..",style=input_style),
    html.Div(" ( 70 - 140 mg/dl ) ",style=limits_style)
]

sugar_fasting_list = [
    html.Div("Blood Sugar (Fasting):",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'fasting_sugar'},type="number",placeholder="Type FBS..",style=input_style),
    html.Div(" ( 70 - 110 mg/dl ) ",style=limits_style)
]

lipid_profile_list = [
    html.Div("Total Cholesterol : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_tc'},type="number",placeholder="Type Tc..",style={**input_style,"left":"500px"}),
    html.Div("High Density Lipoprotein ( HDL ) : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_hdl'},type="number",placeholder="Type HDL...",style={**input_style,"left":"500px"}),
    html.Div("Low Density Lipoprotein : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_ldl'},type="number",placeholder="Type LDL...",style={**input_style,"left":"500px"}),
    html.Div("Very Low Density Lipoprotein : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_vldl'},type="number",placeholder="Type VLDL",style={**input_style,"left":"500px"}),
    html.Div("Triglyceride (F): ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_tri'},type="number",placeholder="Type Triglyceride...",style={**input_style,"left":"500px"})
]

blood_for_aec_list = [
    html.Div("Blood for AEC Count : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'aec-count'},type="number",placeholder="460",style=input_style),
    html.Div(" (50 - 450 cells/cumm ) ",style=limits_style)
]

ra_factor_list = [
    html.Div("ra-factor :".upper(),style=text_style),
    html.Div(dcc.Dropdown(["positive".upper(),"negative".upper()],"negative".upper(),id={'type':'dynamic-input','name':'ra-factor'}),style=dict(position="relative",width="200px",left="300px",bottom="25px")),
    html.Div(" ( 1 : ",style={**limits_style,"bottom":"50px"}),
    dcc.Input(id={'type':'dynamic-input','name':'ra-dilutions'},type="number",placeholder="None",style={**limits_style,"bottom":"75px","left":"620px","width":"100px"}),
    html.Div(" dilutions ) ",style={**limits_style,"left":"730px","bottom":"95px"})
]

aso_titre_list = [
    html.Div("ASO TITRE : ",style=text_style),
    html.Div([dcc.Dropdown(["POSITIVE","NEGATIVE"],"NEGATIVE",id={'type':'dynamic-input','name':'aso_titre'})],style=input_style),
    html.Div([
        "( 1 : ",
        dcc.Input(id={'type':'dynamic-input','name':'aso_titre_dilutions'},type="number"),
        " dilutions"
    ],style=limits_style)
]

serum_amylase_list = [
    html.Div("Serum Amylase : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_amylase'}, type="number", placeholder="Type amylase", style=input_style),
    html.Div(" (30 - 110 U/L) ", style=limits_style)
]

serum_lipase_list = [
    html.Div("Serum Lipase : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_lipase'}, type="number", placeholder="Type lipase", style=input_style),
    html.Div(" (23 - 300 U/L) ", style=limits_style)
]

serum_protein_list = [
    html.Div("Serum Protein : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_protein'}, type="number", placeholder="Type protein", style=input_style),
    html.Div(" (6.6 - 8.3 g/dl) ", style=limits_style)
]

serum_albumin_list = [
    html.Div("Serum Albumin : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_albumin'}, type="number", placeholder="Type albumin", style=input_style),
    html.Div(" (3.5 - 5.0 g/dl) ", style=limits_style)
]

serum_globulin_list = [
    html.Div("Serum Globulin : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_globulin'}, type="number", placeholder="Type globulin", style=input_style),
    html.Div(" (2.0 - 3.5 g/dl) ", style=limits_style)
]

serum_ag_ratio_list = [
    html.Div("Serum A/G Ratio : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_ag_ratio'}, type="number", placeholder="Type A/G ratio", style=input_style),
    html.Div(" (0.9 - 2.0 g/dl) ", style=limits_style)
]

serum_sodium_list = [
    html.Div("Serum Sodium : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_sodium'}, type="number", placeholder="Type sodium", style=input_style),
    html.Div(" (135 - 155 mmol/L) ", style=limits_style)
]

serum_potassium_list = [
    html.Div("Serum Potassium : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_potassium'}, type="number", placeholder="Type potassium", style=input_style),
    html.Div(" (3.5 - 5.5 mmol/L) ", style=limits_style)
]

serum_chloride_list = [
    html.Div("Serum Chloride : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_chloride'}, type="number", placeholder="Type chloride", style=input_style),
    html.Div(" (98 - 107 mmol/L) ", style=limits_style)
]

serum_calcium_list = [
    html.Div("Serum Calcium : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_calcium'}, type="number", placeholder="Type calcium", style=input_style),
    html.Div(" (8.5 - 10.5 mmol/L) ", style=limits_style)
]

vdrl_list = [
    html.Div("V.D.R.L : ",style=text_style),
    html.Div([dcc.Dropdown(["reactive".upper(),"non-reactive".upper()],"non-reactive".upper(),id={'type':'dynamic-input','name':'vdrl'})],style=input_style)
]

hbsag_list = [
    html.Div("HBsAg : ",style=text_style),
    html.Div([dcc.Dropdown(["reactive".upper(),"non-reactive".upper()],"non-reactive".upper(),id={'type':'dynamic-input','name':'hbsag'})],style=input_style)
]

hiv_list = [
    html.Div("HIV I & II Antibodies Test : ",text_style),
    html.Div([dcc.Dropdown(["reactive".upper(),"non-reactive".upper()],"non-reactive".upper(),id={'type':'dynamic-input','name':'hiv_ant'})],style=input_style)
]

hcv_list = [
    html.Div("HCV I & II Antibodies Test : ",text_style),
    html.Div([dcc.Dropdown(["reactive".upper(),"non-reactive".upper()],"non-reactive".upper(),id={'type':'dynamic-input','name':'hcv_ant'})],style=input_style)
]

reports_original_dict = {
    "Hb": hb_list,
    "Total Count (TC)": tc_list,
    "Platelet Count": plt_list,
    "Differential Count (DC)": dc_list,
    "ESR": esr_list,
    "CRP": crp_list,
    "Widal": widal_list,
    "Full CBP": full_cbp_list,
    "Malaria":malaria_list,
    "PCV(HCT)":hct_list,
    "Blood Group": blood_group_list,
    "Total Bilirubin": total_bilirubin_list,
    "Direct & Indirect Bilirubin": direct_indirect_bilirubin_list,
    "SGOT":sgot_list,
    "SGPT":sgpt_list,
    "ALKP":alkp_list,
    "DENGUE":dengue_list,
    "Heamogram": heamogram_list,
    "HBA1C": hba1c_list,
    "Blood Urea": blood_urea_list,
    "Serum Creatinine": serum_creatinine_list,
    "Uric Acid": uric_acid_list,
    "Urine Analysis": urine_analysis_list,
    "Urine Pregnancy": urine_pregnency_list,
    "Mantaoux": mantaoux_list,
    "Random Sugar": sugar_random_list,
    "Fasting Sugar": sugar_fasting_list,
    "Blood for AEC Count": blood_for_aec_list,
    "RA Factor": ra_factor_list,
    "ASO Titre": aso_titre_list,
    "PT APTT": pt_aptt_list,
    "Lipid Profile": lipid_profile_list,
    "Serum Amylase": serum_amylase_list,
    "Serum Lipase": serum_lipase_list,
    "Serum Protein": serum_protein_list,
    "Serum Albumin": serum_albumin_list,
    "Serum Globulin": serum_globulin_list,
    "Serum A/G Ratio": serum_ag_ratio_list,
    "Serum Sodium": serum_sodium_list,
    "Serum Potassium": serum_potassium_list,
    "Serum Chloride": serum_chloride_list,
    "Serum Calcium": serum_calcium_list,
    "V.D.R.L":vdrl_list,
    "HBsAg":hbsag_list,
    "HIV I & II Antibodies Test":hiv_list,
    "HCV I & II Antibodies Test":hcv_list,
}



def get_df_item(p_sn:int,item_name:str):
    return copy_df.loc[copy_df.loc[:,"S.No."] == p_sn,item_name].item()


@callback(
    [
        Output("output-report","children"),
        Output("output-report-boxes","children"),
        Output("patient-data-store","data"),
        Output("data-present","children")
    ],
    [
        Input("patients-dropdown","value"),
        Input("reports-dropdown","value"),
        Input("template-dropdown","value")
    ],
    State("patient-data-store","data"),
)
def submit_report(patients_sno, reports_value,template_value,all_patients_values):
    is_present = False
    s = ""
    if patients_sno:
        if all_patients_values is None:
            all_patients_values = {}
        print(all_patients_values)
        if all_patients_values.get(str(patients_sno),{}) == {}:
            all_patients_values[str(patients_sno)] = {"tests":[]}
        if len(all_patients_values[str(patients_sno)]) > 1:
            is_present = True
        report_details = []
        patients_details = [
                html.Div(f"Patient Name: {get_df_item(patients_sno,item_name='Patient Name')}"),
                html.Div(f"Age: {get_df_item(patients_sno,item_name='Patient Age')}"),
                html.Div(f"Reference By: {get_df_item(patients_sno,item_name='Reference By')}"),
                html.Div(f"Date: {get_df_item(patients_sno,item_name="Date")}")
            ]
        if reports_value:
            for x in reports_value:
                report_details += reports_original_dict[x]
                if x not in all_patients_values[str(patients_sno)]["tests"]:
                    all_patients_values[str(patients_sno)]["tests"].append(x)
        if template_value:
            template_value = json.loads(template_value)
            for x in template_value:
                report_details += reports_original_dict[x]
                if x not in all_patients_values[str(patients_sno)]["tests"]:
                    all_patients_values[str(patients_sno)]["tests"].append(x)
        if is_present:
            s = "*Data is present, Please Preview to see old values or Storage Clear to enter new values"
        else:
            s = ""
        return patients_details,report_details,all_patients_values,s
    return "Select a Serial Number to Display....","Select a Test to Display....",all_patients_values,s



@callback(
    [
        Output("patient-data-store","data",allow_duplicate=True),
        Output("data-present","children",allow_duplicate=True)
    ],
    Input("clear-storage","n_clicks"),
    [
        State("patients-dropdown","value"),
        State("patient-data-store","data")
    ],
    prevent_initial_call="initial_duplicate"
)
def clear_storage_data(n_clicks,patients_sno,all_patients_values):
    if not n_clicks:
        raise PreventUpdate
    if n_clicks:
        all_patients_values[str(patients_sno)] = {"tests":[]}
        return all_patients_values,f"Storage Cleared for Serial No. {patients_sno}"

def cal_string_width(c:canvas.Canvas,total_string,font_name,font_size):
    return c.stringWidth(total_string,font_name,font_size)

small_left_extreme = 42
small_value_point = 182
small_right_extreme = 375
small_font_name = "Times-BoldItalic"
small_font_size = 12
small_limits_font_size = 10
big_left_extreme = 43
big_right_extreme = 540
big_value_point = 240
big_font_name = "CenturySchoolBook-BoldItalic"
big_font_size = 14
big_limits_font_size = 12

size_dict = {
    "font_size":{
        0:small_font_size,
        1:big_font_size
    },
    "font_name":{
        0:small_font_name,
        1:big_font_name
    },
    "left_extreme":{
        0:small_left_extreme,
        1:big_left_extreme
    },
    "value_point":{
        0:small_value_point,
        1:big_value_point
    },
    "limits_font":{
        0:small_limits_font_size,
        1:big_limits_font_size
    },
    "right_extreme":{
        0:small_right_extreme,
        1:big_right_extreme
    }
}

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
        frmt_time:str,
        left_extreme,
        midpoint,
        right_extreme,
        drop_height
    ):
    c.setFont(font_name,font_size)
    c.drawString(left_extreme,page_height-drop_height,f"Pt. Name : {patient_name.upper()}")
    c.drawString(left_extreme,page_height-(drop_height + patient_details_space),f"Gender : {patient_gender}")                  
    age_string = f"Age: {patient_age} {patient_age_group}"
    c.drawString(right_extreme-cal_string_width(c,age_string,font_name,font_size),page_height-(drop_height + patient_details_space),age_string)     # s
    c.drawString(left_extreme,page_height-(drop_height + 2*patient_details_space),f"Ref.Dr.By. : {doctor_name}")                                                # 99 + 24
    c.drawString(left_extreme,page_height-(drop_height + 3*patient_details_space),f"Serial No: 000{patient_serial_no}")
    time_string = f"Collection Time: {collection_time}"
    c.drawString(right_extreme-cal_string_width(c,time_string,font_name,font_size),page_height-(drop_height + 3*patient_details_space),time_string)        # s
    c.drawString(left_extreme,page_height-(drop_height + 4*patient_details_space),f"Specimen: {patient_specimen}")
    date_string = f"Date: {frmt_time}"
    c.drawString(right_extreme-cal_string_width(c,date_string,font_name,font_size),page_height-(drop_height + 4*patient_details_space),date_string)                         # s
    c.setDash()
    c.line(left_extreme - 2,page_height-(drop_height + 4.5 * patient_details_space),right_extreme+2,page_height-(drop_height + 4.5 * patient_details_space))
    c.line(left_extreme - 2,page_height-(drop_height + 5.2 * patient_details_space),right_extreme+2,page_height-(drop_height + 5.2 * patient_details_space))
    c.setFont(font_name,font_size-4)
    c.drawString(left_extreme,page_height-(drop_height + 5 * patient_details_space),"test".upper())
    c.drawString(midpoint,page_height-(drop_height + 5 * patient_details_space),"value".upper())
    reference_string = "reference range".upper()
    c.drawString(right_extreme-cal_string_width(c,reference_string,font_name,font_size-4),page_height-(drop_height + 5 * patient_details_space),reference_string)
    return c

def if_draw_bold(c:canvas.Canvas,value,value_string,limit_a,limit_b,x,y):
    if (value < limit_a) | (value > limit_b):
        for offset in [0,0.25,-0.25,0.35,-0.35]:
            c.drawString(x+offset,y,f":  {value_string}")
    else:
        c.drawString(x,y,f":  {value_string}")
    return c

def mundane_things(c:canvas.Canvas,x,text_string,value,value_string,limits_string,limit_a,limit_b,h,if_limits=True):
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["left_extreme"][x],h,text_string)
    if if_limits:
        c = if_draw_bold(c,value,value_string,limit_a,limit_b,size_dict["value_point"][x],h)
    else:
        c.drawString(size_dict["value_point"][x],h,f":  * {value.replace(" "," * ")}")
    c.setFont(size_dict["font_name"][x],size_dict["limits_font"][x])
    c.drawString(size_dict["right_extreme"][x]-cal_string_width(c,limits_string,size_dict["font_name"][x],size_dict["limits_font"][x]),h,limits_string)
    return c

def hb_canvas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height = 18):
    limits_string = "( 11.0 - 16.8 Grams% )"
    text_string = "Heamoglobin"
    limit_a = 11.0
    limit_b = 16.8
    value_string = float(value)
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

def tc_canvas(c:canvas.Canvas,value:int,page_size:str,h:int,entity_height = 18):
    limits_string = "( 5,000 - 10,000 Cells/cumm )"
    text_string = "Total WBC Count"
    value_string = f"{value//1000},000"
    limit_a = 5000
    limit_b = 10000
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

def plt_canvas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height = 18):
    limits_string = "( 1.5 - 4.0 Lakhs/cumm )"
    text_string = "Platelet Count : "
    limit_a = 1.5
    limit_b = 4.0
    if value < 1:
        value_string = f"{int(value * 100)},000"
    else:
        value_string = str(value)
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

def dc_canvas(
        c:canvas.Canvas,
        dc_count:list,
        page_size:str,
        h:int,
        entity_height=18
    ):
    
    def p(v):
        if v < 10:
            s = f"0{v}"
        else:
            s = f"{v}"
        return s

    polymo_value,lympho_value,esino_value = dc_count
    if polymo_value + lympho_value + esino_value == 100:
        esino_value -= 1
    mono_value = 100 - (polymo_value + lympho_value + esino_value)
    dc_string = "Differential Count: "
    poly_string = "Polymorphs"
    lympho_string = "Lymphocytes"
    eosino_string = "Eosinophils"
    mono_string = "Monocytes"
    if page_size == "SMALL/A5":
        c.setFont(small_font_name,small_font_size)
        c.drawString(small_left_extreme,h,dc_string)
        c.line(small_left_extreme,h-(0.2 * entity_height),small_left_extreme+cal_string_width(c,dc_string,small_font_name,small_font_size),h-5)
        c.drawString(142,h-(1.2 * entity_height),poly_string)
        c.drawString(142,h-(2.2 * entity_height),lympho_string)
        c.drawString(142,h-(3.2 * entity_height),eosino_string)
        c.drawString(142,h-(4.2 * entity_height),mono_string)
        c = if_draw_bold(c,polymo_value,p(polymo_value),40,70,260,h-(1.2 * entity_height))
        c = if_draw_bold(c,lympho_value,p(lympho_value),20,40,260,h-(2.2 * entity_height))
        c = if_draw_bold(c,esino_value,p(esino_value),2,6,260,h-(3.2 * entity_height))
        c = if_draw_bold(c,mono_value,p(mono_value),1,4,260,h-(4.2 * entity_height))
        c.setFont(small_font_name,small_limits_font_size)
        c.drawString(small_right_extreme-cal_string_width(c,"( 40 - 70 %)",small_font_name,small_limits_font_size),h-(1.2 * entity_height),"( 40 - 70 %)")
        c.drawString(small_right_extreme-cal_string_width(c,"( 40 - 70 %)",small_font_name,small_limits_font_size),h-(2.2 * entity_height),"( 20 - 40 %)")
        c.drawString(small_right_extreme-cal_string_width(c,"( 40 - 70 %)",small_font_name,small_limits_font_size),h-(3.2 * entity_height),"( 02 - 06 %)")
        c.drawString(small_right_extreme-cal_string_width(c,"( 40 - 70 %)",small_font_name,small_limits_font_size),h-(4.2 * entity_height),"( 01 - 04 %)")
        h -= (entity_height * 5.5)
    else:
        c.setFont(big_font_name,big_font_size)
        c.drawString(big_left_extreme,h,dc_string)
        c.line(big_left_extreme,h-5,big_left_extreme+cal_string_width(c,dc_string,big_font_name,big_font_size),h-5)
        c.drawString(182,h-(1.2 * entity_height),poly_string)
        c.drawString(182,h-(2.2 * entity_height),lympho_string)
        c.drawString(182,h-(3.2 * entity_height),eosino_string)
        c.drawString(182,h-(4.2 * entity_height),mono_string)
        c = if_draw_bold(c,polymo_value,p(polymo_value),40,70,300,h-(1.2 * entity_height))
        c = if_draw_bold(c,lympho_value,p(lympho_value),20,40,300,h-(2.2 * entity_height))
        c = if_draw_bold(c,esino_value,p(esino_value),2,6,300,h-(3.2 * entity_height))
        c = if_draw_bold(c,mono_value,p(mono_value),1,4,300,h-(4.2 * entity_height))
        c.setFont(big_font_name,big_limits_font_size)
        c.drawString(big_right_extreme-cal_string_width(c,"( 40 - 70 %)",big_font_name,big_limits_font_size),h-(1.2 * entity_height),"( 40 - 70 %)")
        c.drawString(big_right_extreme-cal_string_width(c,"( 40 - 70 %)",big_font_name,big_limits_font_size),h-(2.2 * entity_height),"( 20 - 40 %)")
        c.drawString(big_right_extreme-cal_string_width(c,"( 40 - 70 %)",big_font_name,big_limits_font_size),h-(3.2 * entity_height),"( 02 - 06 %)")
        c.drawString(big_right_extreme-cal_string_width(c,"( 40 - 70 %)",big_font_name,big_limits_font_size),h-(4.2 * entity_height),"( 01 - 04 %)")
        h -= (entity_height * 6)
    return c,h

def crp_canvas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height=18):
    limits_string = " ( < 6 ) "
    text_string = "CRP"
    value_string = value
    limit_a = 0
    limit_b = 6
    if page_size == "SMALL/A5":
        x = 0
        c.setFont(small_font_name,small_limits_font_size-2)
        c.drawString(small_left_extreme,h-10,"(Turbidmetric Immunoassay)")
    else:
        x = 1
        entity_height += 5
        c.setFont(big_font_name,big_limits_font_size-2)
        c.drawString(big_left_extreme,h-10,"(Turbidmetric Immunoassay)")
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c, h - entity_height - 5

def widal_canvas(c:canvas.Canvas,widal_values,page_size:str,h:int,entity_height=18):
    widal_value,widal_form,ot_value,ht_value = widal_values
    widal_string = "Blood for Widal"
    ot_string = f"OT - 1 : {ot_value} dilutions"
    ht_string = f"HT - 1 : {ht_value} dilutions"
    ah_string = "AH - 1 : 40 dilutions"
    bh_string = "BH - 1 : 40 dilutions"
    def bold_it(x,y):
        for offset in [0.25,-0.25,0.35,-0.35]:
            c.drawString(x+offset,y,":  reactive".upper())
        return c
    if page_size == "SMALL/A5":
        c.setFont(small_font_name,small_font_size)
        c.drawString(small_left_extreme,h,widal_string)
        if widal_value == "reactive".upper():
            c = bold_it(small_value_point,h)
            c.setFont(small_font_name,small_limits_font_size)
            c.drawString(small_right_extreme-cal_string_width(c,ot_string,small_font_name,small_limits_font_size)-100,h-(entity_height * 0.8),ot_string)
            c.drawString(small_right_extreme-cal_string_width(c,ht_string,small_font_name,small_limits_font_size)-100,h-(entity_height * 1.5),ht_string)
            c.drawString(small_right_extreme-cal_string_width(c,ah_string,small_font_name,small_limits_font_size),h-(entity_height * 0.8),ah_string)
            c.drawString(small_right_extreme-cal_string_width(c,bh_string,small_font_name,small_limits_font_size),h-(entity_height * 1.5),bh_string)
            h -= (entity_height * 2.5)
        else:
            c.drawString(small_value_point,h,":  non-reactive".upper())
            h -= entity_height
    else:
        entity_height += 5
        c.setFont(big_font_name,big_font_size)
        c.drawString(big_left_extreme,h,widal_string)
        if widal_value == "reactive".upper():
            c = bold_it(big_value_point,h)
            c.setFont(big_font_name,big_limits_font_size)
            if widal_form == "SHORT":
                c.drawString(big_right_extreme-cal_string_width(c,ot_string,big_font_name,big_font_size) - 130,h-(entity_height * 0.8),ot_string)
                c.drawString(big_right_extreme-cal_string_width(c,ht_string,big_font_name,big_font_size) - 130,h-(entity_height * 1.5),ht_string)
                c.drawString(big_right_extreme-cal_string_width(c,ah_string,big_font_name,big_font_size),h-(entity_height * 0.8),ah_string)
                c.drawString(big_right_extreme-cal_string_width(c,bh_string,big_font_name,big_font_size),h-(entity_height * 1.5),bh_string)
                h -= (entity_height * 2.5)
            else:
                c.drawString(big_right_extreme-cal_string_width(c,ot_string,big_font_name,big_font_size),h-(entity_height * 0.8),ot_string)
                c.drawString(big_right_extreme-cal_string_width(c,ht_string,big_font_name,big_font_size),h-(entity_height * 1.5),ht_string)
                c.drawString(big_right_extreme-cal_string_width(c,ah_string,big_font_name,big_font_size),h-(entity_height * 2.2),ah_string)
                c.drawString(big_right_extreme-cal_string_width(c,bh_string,big_font_name,big_font_size),h-(entity_height * 2.9),bh_string)
                h -= (entity_height * 4)
        else:
            c.drawString(big_value_point,h,":  non-reactive".upper())
            h -= (entity_height)
    return c,h

def hct_canvas(c:canvas.Canvas,value,page_size:str,h:int,entity_height=18):
    limits_string = "( 40% - 45% )"
    text_string = "PCV(Heamatocrit)"
    value_string = value
    limit_a = 40
    limit_b = 45
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

def esr_canvas(c:canvas.Canvas,value,page_size:str,h:int,entity_height=18):
    text_string = "E.S.R"
    limits_string = "( 02 - 10 mm/Hr )"
    value_string = int(value)
    limit_a = 2
    limit_b = 11
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h - entity_height

def full_cbp_canvas(c:canvas.Canvas,cbp_values:list,page_size:str,h:int,entity_height=18):
    entity_height += 5
    hb,rbc_count,hct,tc_count,plt_count,esr,polymo,lympho,esino = cbp_values
    if page_size == "BIG/A4":
        c,h = hb_canvas(c,hb,page_size,h,entity_height-5)
        x = 1
        text_string = "Total RBC Count"
        limits_string = "( 4.0 - 5.0 millions/cumm)"
        value_string = rbc_count
        limit_a = 4.0
        limit_b = 5.0
        c = mundane_things(c,x,text_string,rbc_count,value_string,limits_string,limit_a,limit_b,h)
        h -= entity_height
        c,h = hct_canvas(c,hct,page_size,h,entity_height-5)
        c,h = tc_canvas(c,tc_count,page_size,h,entity_height - 5)
        c,h = plt_canvas(c,plt_count,page_size,h,entity_height - 5)
        c,h = esr_canvas(c,esr,page_size,h,entity_height-5)
        c,h = dc_canvas(c,[polymo,lympho,esino],page_size,h,entity_height-5)
    return c,h-entity_height

def blood_group_canvas(c:canvas.Canvas,value:str,page_size:str,h:int,entity_height=18):
    text_string = "blood group".upper()
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value,limits_string="",limit_a="",limit_b="",h=h,if_limits=False)
    return c,h - entity_height

def total_bilirubin_canvas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height=18):
    text_string = "Total Bilirubin"
    limits_string = "( 0.2 - 1.0 mg/dl )"
    value_string = value
    limit_a = 0.2
    limit_b = 1.0
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h - entity_height

def heamogram_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    hb,rbc,hct,tc,plt,mcv,mch,mchc,esr,polymo,lympho,esino,heamo_rbc,blast_cells,plt_opinion,heamoparisites,total_opinion = values
    if page_size == "BIG/A4":
        entity_height -= 5
        c,h = hb_canvas(c,hb,page_size,h,entity_height-5)
        # rbc
        text_string = "Total RBC Count"
        limits_string = "( 4.0 - 5.0 millions/cumm)"
        value_string = rbc
        limit_a = 4.0
        limit_b = 5.0
        c = mundane_things(c,1,text_string,rbc,value_string,limits_string,limit_a,limit_b,h)
        h -= entity_height
        # end
        c,h = hct_canvas(c,hct,page_size,h,entity_height-5)
        c,h = tc_canvas(c,tc,page_size,h,entity_height-5)
        c,h = plt_canvas(c,plt,page_size,h,entity_height-5)
        # mcv
        text_string = "MCV"
        limits_string = "( 78 - 94 fl )"
        value_string = mcv
        limit_a = 78
        limit_b = 94
        c = mundane_things(c,1,text_string,mcv,value_string,limits_string,limit_a,limit_b,h)
        h -= entity_height 
        # mch
        text_string = "MCH"
        limits_string = "( 27 - 32 pg )"
        value_string = mch
        limit_a = 27
        limit_b = 32
        c = mundane_things(c,1,text_string,mch,value_string,limits_string,limit_a,limit_b,h)
        h -= entity_height 
        # mchc
        text_string = "MCHC"
        limits_string = "( 32 - 36 g/dl )"
        value_string = mchc
        limit_a = 32
        limit_b = 36
        c = mundane_things(c,1,text_string,mchc,value_string,limits_string,limit_a,limit_b,h)
        h -= entity_height
        c,h = esr_canvas(c,esr,page_size,h,entity_height-5)
        c,h = dc_canvas(c,[polymo,lympho,esino],page_size,h,entity_height+2)
        c.drawString(size_dict["left_extreme"][1],h+10,"peripheral smear examination".upper())
        c.line(size_dict["left_extreme"][1],h+5,size_dict["left_extreme"][1] - 55 + c.stringWidth("peripheral smear examination".upper(),size_dict["font_name"][1],size_dict["font_size"][1]),h+5)
        entity_height -= 5
        h -= (entity_height - 5)
        c.drawString(size_dict["left_extreme"][1],h,f"RBC:  {heamo_rbc}")
        h -= entity_height
        c.drawString(size_dict["left_extreme"][1],h,f"WBC:  {total_opinion}")
        h -= entity_height
        c.drawString(size_dict["left_extreme"][1],h,blast_cells)
        h -= entity_height
        c.drawString(size_dict["left_extreme"][1],h,f"Platelets:  {plt_opinion}")
        h -= entity_height
        c.drawString(size_dict["left_extreme"][1],h,f"Heamoparasites:  {heamoparisites}")
        h -= entity_height
        c.drawString(size_dict["left_extreme"][1],h,f"Impression:  “ {total_opinion} ”")
    return c, h - entity_height

    



    return c,h

def direct_and_indirect_bilirubin_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    total_value,direct_value = values
    direct_text_string = "Direct Bilirubin"
    indirect_text_strig = "Indirect Bilirubin"
    direct_limits_string = "( 0.2 - 0.4 mg/dl )"
    indirect_limits_string = "( 0.2 - 0.6 mg/dl )"
    indirect_value = total_value - direct_value
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,direct_text_string,direct_value,direct_value,direct_limits_string,0.2,0.4,h)
    h -= entity_height
    c = mundane_things(c,x,indirect_text_strig,indirect_value,indirect_value,indirect_limits_string,0.2,0.6,h)
    return c, h - entity_height

def hb1ac_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    first_value,second_value,drop_value = values
    first_string = "Glycosylated Hb (HbA1c) Test"
    second_string = "Estimated Average Glucose (eAG)"
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["left_extreme"][x],h,first_string)
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x]+5)
    c.drawString(size_dict["value_point"][x]+60,h,f":  {first_value}%")
    h -= entity_height
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["left_extreme"][x],h,second_string)
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x]+5)
    c.drawString(size_dict["value_point"][x]+60,h,f":  {second_value}")
    c.setFont(size_dict["font_name"][x],size_dict["limits_font"][x])
    h -= (entity_height + 1)
    _temp_x = size_dict["right_extreme"][x] - cal_string_width(c,"(Non-Biabetic Adults > 18 Years - < 5.7 %)",size_dict["font_name"][x],size_dict["limits_font"][x])
    c.drawString(_temp_x,
        h,
        "(Non-Biabetic Adults > 18 Years - < 5.7 %)"
    )
    h -= (entity_height - 10)
    c.drawString(size_dict["right_extreme"][x] - cal_string_width(c,
        "(AT Risk (Prediabetes)   - 5.7 % - 6.4%)",
    size_dict["font_name"][x],size_dict["limits_font"][x]),
        h,
        "(AT Risk (Prediabetes)   - 5.7 % - 6.4%)"
    )
    h -= (entity_height - 10)
    c.drawString(size_dict["right_extreme"][x] - cal_string_width(c,
        "(Diagnising Diabetes   - > 6.5 %)",
    size_dict["font_name"][x],size_dict["limits_font"][x]),
        h,
        "(Diagnising Diabetes   - > 6.5 %)"
    )
    h -= (entity_height - 5)
    if drop_value == "LONG":
        c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
        c.drawString(_temp_x,h,"diabetics: ".upper())
        h -= (entity_height - 10)
        c.drawString(size_dict["right_extreme"][x] - cal_string_width(c,
            "( Excellent Control     - 6.0 % - 7.0% )",
        size_dict["font_name"][x],size_dict["limits_font"][x]),
            h,
            "( Excellent Control     - 6.0 % - 7.0% )"
        )    
        h -= (entity_height - 10)
        c.drawString(size_dict["right_extreme"][x] - cal_string_width(c,
            "( Excellent Control     - 6.0 % - 7.0% )",
        size_dict["font_name"][x],size_dict["limits_font"][x]),
            h,
            "( Excellent Control     - 6.0 % - 7.0% )"
        )
        h -= (entity_height - 10)
        c.drawString(size_dict["right_extreme"][x] - cal_string_width(c,
            "( Excellent Control     - 6.0 % - 7.0% )",
        size_dict["font_name"][x],size_dict["limits_font"][x]),
            h,
            "( Excellent Control     - 6.0 % - 7.0% )"
        )
    return c,h-entity_height

def dengue_canvas(c:canvas.Canvas,values,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def sgot_canvas(c:canvas.Canvas,values,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def sgpt_canvas(c:canvas.Canvas,values,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def alkp_canvas(c:canvas.Canvas,values,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def malaria_canvas(c:canvas.Canvas,values,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def blood_urea_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def serum_creat_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def uric_acid_cavnas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def urine_analysis_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def mantaux_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def random_sugar_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def fasting_sugar_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height


def lipid_profile_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def urine_preg_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height


def blood_for_aec_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def ra_factor_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def aso_titre_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def pt_aptt_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def serum_amylase_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def serum_lipase_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def serum_protein_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def serum_albumin_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def serum_globulin_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def serum_ag_ratio_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def serum_sodium_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def serum_pottassium_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def serum_chloride_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def serum_calcium_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def vdrl_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def hbsag_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def hiv_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height

def hcv_canvas(c:canvas.Canvas,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    return c,h-entity_height



reports_canvas_dict = {
    "Hb":hb_canvas,
    "Total Count (TC)":tc_canvas,
    "Platelet Count":plt_canvas,
    "Differential Count (DC)":dc_canvas,
    "Widal":widal_canvas,
    "CRP":crp_canvas,
    "ESR":esr_canvas,
    "Malaria":malaria_canvas,
    "Full CBP":full_cbp_canvas,
    "Blood Group":blood_group_canvas,
    "Total Bilirubin":total_bilirubin_canvas,
    "Direct & Indirect Bilirubin":direct_and_indirect_bilirubin_canvas,
    "SGPT":sgpt_canvas,
    "SGOT":sgot_canvas,
    "ALKP":alkp_canvas,
    "Heamogram":heamogram_canvas,
    "HBA1C":hb1ac_canvas,
    "Fasting Sugar":fasting_sugar_canvas,    
    "Random Sugar":random_sugar_canvas,
    "Blood Urea":blood_urea_canvas,
    "Serum Creatinine":serum_creat_canvas,
    "Uric Acid":uric_acid_cavnas,
    "Urine Analysis":urine_analysis_canvas,
    "Urine Pregnancy":urine_preg_canvas,
    "Lipid Profile":lipid_profile_canvas,
    "Mantaoux":mantaux_canvas,
    "Blood for AEC Count":blood_for_aec_canvas,
    "RA Factor":ra_factor_canvas,
    "ASO Titre":aso_titre_canvas,
    "PT APTT":pt_aptt_canvas,
    "Serum Amylase":serum_amylase_canvas,
    "Serum Lipase":serum_lipase_canvas,
    "Serum Protein":serum_protein_canvas,
    "Serum Albumin":serum_albumin_canvas,
    "Serum Globulin":serum_globulin_canvas,
    "Serum A/G Ratio":serum_ag_ratio_canvas,
    "Serum Sodium":serum_sodium_canvas,
    "Serum Potassium":serum_pottassium_canvas,
    "Serum Chloride":serum_chloride_canvas,
    "Serum Calcium":serum_calcium_canvas,
    "V.D.R.L":vdrl_canvas,
    "HBsAg":hbsag_canvas,
    "HIV I & II Antibodies Test":hiv_canvas,
    "HCV I & II Antibodies Test":hcv_canvas,
}

report_canvas_values_dict = {
    "Hb":"hb",
    "Total Count (TC)":"tc_count",
    "Platelet Count":"plt_count",
    "Differential Count (DC)":"dc_count",
    "Widal":"widal",
    "CRP":"crp",
    "ESR":"esr",
    "Malaria":"malaria-test",
    "Full CBP":"cbp",
    "Blood Group":"blood-group",
    "Total Bilirubin":"total-bili",
    "Direct & Indirect Bilirubin":"direct-bili",
    "SGPT":"sgpt",
    "SGOT":"sgot",
    "ALKP":"alkp",
    "Heamogram":"heamo",
    "HBA1C":"hba1c",
    "Fasting Sugar":"fasting_sugar",    
    "Random Sugar":"random_sugar",
    "Blood Urea":"blood-urea",
    "Serum Creatinine":"serum-creat",
    "Uric Acid":"uric-acid",
    "Urine Analysis":"full-urine",
    "Urine Pregnancy":"preg_test",
    "Lipid Profile":"full-lipid",
    "Mantaoux":"mantoux_test",
    "Blood for AEC Count":"aec-count",
    "RA Factor":"full-ra-factor",
    "ASO Titre":"full-aso-titre",
    "PT APTT":"full-pt-aptt",
    "Serum Amylase":"serum_amylase",
    "Serum Lipase":"serum_lipase",
    "Serum Protein":"serum_protien",
    "Serum Albumin":"serum_albumin",
    "Serum Globulin":"serum_globulin",
    "Serum A/G Ratio":"serum_ag_ratio",
    "Serum Sodium":"serum_sodium",
    "Serum Potassium":"serum_potassium",
    "Serum Chloride":"serum_chloride",
    "Serum Calcium":"serum_calcium",
    "V.D.R.L":"vdrl",
    "HBsAg":"hbsag",
    "HIV I & II Antibodies Test":"hiv_ant",
    "HCV I & II Antibodies Test":"hcv_ant",
}

def create_pdf(serial_no,top_space,report_details_space,page_size,all_patients_values):

    global copy_df
    collection_date = str(get_df_item(serial_no,"Date"))
    collection_time = get_df_item(serial_no,"Time")
    patient_name = get_df_item(serial_no,"Patient Name")
    patient_age = get_df_item(serial_no,"Patient Age")
    patient_age_group = get_df_item(serial_no,"Age Group")
    patient_gender = get_df_item(serial_no,"Gender")
    patient_specimen = "Blood & Urine" if (any(["Urine Analysis","Urine Pregnancy"]) in all_patients_values[str(serial_no)]["tests"]) else "Blood"
    doctor_name = get_df_item(serial_no,"Reference By")
    patient_details_space = 18
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
        c = canvas.Canvas(filename,pagesize=portrait(A5))
        small_page_width, small_page_height = A5
        # c.rect(40,20,page_width - 2 * 40, page_height - 2 * 40)
        # grid
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
            small_font_name,
            small_font_size,
            small_page_height,
            patient_name,
            patient_details_space,
            patient_age,
            patient_age_group,
            patient_gender,
            doctor_name,
            serial_no,
            collection_time,
            patient_specimen,
            frmt_time,
            small_left_extreme,
            small_value_point+8,
            small_right_extreme,
            drop_height=75
        )
        h = 410-top_space
        serial_no = str(serial_no)
        tests_list = all_patients_values[serial_no]["tests"]
        for t in tests_list:
            c,h = reports_canvas_dict[t](c,all_patients_values[serial_no][report_canvas_values_dict[t]],page_size,h,report_details_space)
        c.save()
    else:
        c = canvas.Canvas(filename,pagesize=portrait(A4))
        big_page_width,big_page_height = A4

        # grid

        c.rect(40,45,big_page_width - 2 * 40, big_page_height - 2 * 50)
        # c.setDash(6,3)
        # c.setFont(small_font_name,5)
        # for x in range(0,int(big_page_width),10):
        #     if x % 20 == 0:
        #         c.line(x,big_page_height,x,0)
        #         c.drawString(x+2,big_page_height-30,str(x))
        # for x in range(0,int(big_page_height),10):
        #     if x % 20 == 0:
        #         c.line(0,x,big_page_width,x)
        #         c.drawString(30,x+2,str(x))
        
        c = patient_details_canvas(
            c,
            big_font_name,
            big_font_size,
            big_page_height,
            patient_name,
            patient_details_space+3,
            patient_age,
            patient_age_group,
            patient_gender,
            doctor_name,
            serial_no,
            collection_time,
            patient_specimen,
            frmt_time,
            big_left_extreme,
            big_value_point+30,
            big_right_extreme+12,
            drop_height = 116
        )
        h = 600 - top_space
        serial_no = str(serial_no)
        tests_list = all_patients_values[serial_no]["tests"]
        for t in tests_list:
            c,h = reports_canvas_dict[t](c,all_patients_values[serial_no][report_canvas_values_dict[t]],page_size,h,report_details_space)
        c.save()
    return filename

@callback(
    Output("patient-data-store","data",allow_duplicate=True),
    Input("submit-report-button","n_clicks"),
    [
        State("patients-dropdown","value"),
        State("page-size-dropdown","value"), 
        State({'type':'dynamic-input','name':ALL},'value'),
        State({'type':'dynamic-input','name':ALL},'id'),
        State("patient-data-store","data"),
    ],
    prevent_initial_call=True
)
def lodge_inputs_to_dict(n_clicks,patients_sno,page_size_value,input_values,input_ids,all_patients_values):
    if not input_values:
        raise PreventUpdate
    if n_clicks:
        patients_sno = str(patients_sno)
        temp_dict = {}
        for id,value in zip(input_ids,input_values):
            if id['name'] in ['polymo','lympho','esino']:
                temp_dict["dc_count"] = temp_dict.get("dc_count",[])
                temp_dict["dc_count"].append(value)
            if ("Widal" in all_patients_values[patients_sno]["tests"]) & (id['name'] in ['widal','widal-form','widal-ot-react','widal-ht-react']):
                temp_dict['widal'] = temp_dict.get('widal',[])
                temp_dict['widal'].append(value)
            if ("Direct & Indirect Bilirubin" in all_patients_values[patients_sno]["tests"]) & (id["name"] in ["total-bili","direct-bili","indirect-bili"]):
                temp_dict["direct-bili"] = temp_dict.get("direct-bili",[])
                temp_dict["direct-bili"].append(value)
            if("Full CBP" in all_patients_values[patients_sno]["tests"]) & (id['name'] in ['hb','rbc-count','hct','tc_count','plt_count','esr','polymo','lympho','esino']):
                temp_dict["cbp"] = temp_dict.get("cbp",[])
                temp_dict["cbp"].append(value)
            if ("Heamogram" in all_patients_values[patients_sno]["tests"]) & (id["name"] in ['hb','rbc-count','hct','tc_count','plt_count','mcv','mch','mchc','esr','polymo','lympho','esino','heamo-rbc','blast-cells','platelet-opinion','hemoparasites-opinion','total-opinion']):
                temp_dict["heamo"] = temp_dict.get("heamo",[])
                temp_dict["heamo"].append(value)
            if ("HBA1C" in all_patients_values[patients_sno]["tests"]) & (id['name'] in ['hba1c_first','hba1c_second','hba1c_dropdown']):
                temp_dict["hba1c"] = temp_dict.get("hba1c",[])
                temp_dict["hba1c"].append(value)
            temp_dict[id['name']] = value
        all_patients_values[patients_sno] = {**all_patients_values[patients_sno],**temp_dict}
        all_patients_values[patients_sno] = {**all_patients_values[patients_sno],'page_size':page_size_value}
        return all_patients_values
    


@callback(
    Output("report-preview","children"),
    Input("preview-button","n_clicks"),
    [
        State("top-slider","value"),
        State("slider","value"),
        State("patient-data-store","data"),
        State("patients-dropdown","value"),
        State("page-size-dropdown","value")
    ]
)
def preview_report(n_clicks,top_slider_value,slider_value,data,patient_sno,page_size):
    if not n_clicks:
        raise PreventUpdate
    if n_clicks:
        filename = create_pdf(patient_sno,top_slider_value,slider_value,page_size,data)
        return html.Iframe(
            src=filename,
            style=dict(width="100%",height="1650px")
        )


register_page(
    "Reports",
    layout=layout,
    path="/reports"
)