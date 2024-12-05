import json,os,time,re,duckdb
from datetime import date
import pandas as pd
from glob import glob
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait,A4,A5
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont
from dash import html,dcc,Input,Output,callback,register_page,State,ALL,ctx
from dash.exceptions import PreventUpdate

registerFont(TTFont("CenturySchoolBook-BoldItalic","assets/schlbkbi.ttf"))

big_break = [html.Br()] * 5
large_break = [html.Br()] * 10
small_break = [html.Br()] * 2
limits_style = dict(position="relative",left="550px",bottom="45px",fontSize=18)
input_style = dict(width="150px",height="25px",position="relative",left="360px",bottom="20px",fontSize=20)
text_style = dict(position="relative",left="80px",fontSize=20)

dtype_map = {
    "S.No.": str,         # Ensure "S.No." remains a string
    "Date": str,          # string in format "YYYY-MM-DD"
    "Time": str,          # string in format "HH:MM:SS AM/PM"
    "Patient Name": str,  # Patient Name as string
    "Reference By": str,  # string with options as given below
    "Patient Age": "Int8",  # Use Int16 for compactness and allow NaNs
    "Age Group": str,     # string with options as ["Y","M","D"]
    "Gender": str,        # string with options as ["Male","Female"]
    "Amount": "Float64",    # Amount as integer
    "Method": str,        # string with options as ["CASH","PHONE PAY"]
    "Phone No": "Int64",  # Phone number as integer
    "Paid": str,          # string with options ["PAID","NOT PAID","DUE"]
    "Due": "Float64",       # Due as integer as the due amount if due/not paid and full amount will be reflected as due if not paid
    "Sample": str         # string with options as ["SELF","RAJU","RAJESH","RAM"]
}

patients_dropdown = dcc.Dropdown(
    placeholder="Select Serial Number..,",
    id="patients-dropdown",
    style=dict(height="50px")
)

all_options = [
    "Hb",
    "Total Count (TC)",
    "Platelet Count",
    "Differential Count (DC)",
    "CRP",
    "Blood Group",
    "DENGUE",
    "Widal",
    "Full CBP",
    "PCV(HCT)",
    "ESR",
    "Malaria",
    "Total Bilirubin",
    "Direct & Indirect Bilirubin",
    "SGOT",
    "SGPT",
    "ALKP",
    "Heamogram",
    "HBA1C",
    "Fasting Sugar",      
    "Random Sugar",
    "Post Pandial Sugar",
    "Urine Sugar(Fasting)",
    "Urine Sugar(Random)",
    "Stool Test",
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
    "BT",
    "CT",
    "PT APTT",
    "Liver Function Test",
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
    "Electrolytes",
    "V.D.R.L",
    "HBsAg",
    "HIV I & II Antibodies Test",
    "HCV I & II Antibodies Test",
    "Semen Analysis",
    "XRAY Opinion",
    "BILL"
]

reports_dropdown = dcc.Dropdown(
    all_options,
    id="reports-dropdown",
    multi=True,
    style=dict(height="100px",width="600px")
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
        {"label":"TOTAL BILIRUBIN, INDIRECT AND DIRECT BILIRUBIN","value":json.dumps(["Total Bilirubin","Direct & Indirect Bilirubin"])},
        {"label":"BLOOD GROUP, CRP, TOTAL BILIRUBIN, DIRECT & INDIRECT BILIRUBIN","value":json.dumps(["Blood Group","CRP","Total Bilirubin","Direct & Indirect Bilirubin"])},
        {"label":"SRI DEVI GARU CBP","value":json.dumps(["Full CBP","Blood Group","V.D.R.L","HBsAg","HIV I & II Antibodies Test","HCV I & II Antibodies Test","Random Sugar","Serum Creatinine","Total Bilirubin","Urine Analysis"])},
        {"label":"SRI DEVI GARU HIV HB URINE","value":json.dumps(["Blood Group","Hb","BT","CT","V.D.R.L","HBsAg","HIV I & II Antibodies Test","HCV I & II Antibodies Test","Random Sugar","Serum Creatinine","Total Bilirubin","Urine Analysis"])},
        {"label":"HB, TC, PLATELET, DC, URINE","value":json.dumps(["Hb","Total Count (TC)","Platelet Count","Differential Count (DC)","Urine Analysis"])},
        {"label":"HB, TC, PLATELET, DC, RBS","value":json.dumps(["Hb","Total Count (TC)","Platelet Count","Differential Count (DC)","Random Sugar"])},
        {"label":"HB, TC, PLATELET, DC, WIDAL","value":json.dumps(["Hb","Total Count (TC)","Platelet Count","Differential Count (DC)","Widal"])},
        {"label":"Full CBP, MALARIA, WIDAL CRP","value":json.dumps(["Full CBP","Malaria","Widal","CRP"])},
        {"label":"PACK 1","value":json.dumps(["HBA1C","Random Sugar","Fasting Sugar"])},
        {"label":"PACK 2","value":json.dumps(["Blood Urea","Serum Creatinine","Lipid Profile"])},
        {"label":"RFT","value":json.dumps(["Blood Urea","Serum Creatinine","Uric Acid"])},
        {"label":"Lipid Profile","value":json.dumps(["Lipid Profile"])},
        {"label":"Liver Function Test","value":json.dumps(["Total Bilirubin","Direct & Indirect Bilirubin","SGOT","SGPT","ALKP"])},
        {"label":"Full Electrolytes","value":json.dumps(["Serum Amylase","Serum Lipase","Serum Protein","Serum Albumin","Serum Globulin","Serum A/G Ratio","Electrolytes"])},
        {"label":"All options","value":json.dumps(all_options)}
    ],
    id="template-dropdown"
)

layout = html.Div(
    [
        html.Div(html.H1("Patients report",className="page-heading"),className="heading-divs"),
        *big_break,
        html.Div(patients_dropdown,style=dict(width="400px",fontSize=20,fontWeight=700,alignItems="center")),
        dcc.DatePickerSingle(
            id="date-pick-reports",
            min_date_allowed=date(1995,8,5),
            max_date_allowed=date.today(),
            date=date.today(),
            style=dict(positon="relative",left="500px",bottom="120px")
        ),
        html.Button("clear data".upper(),id="clear-button",style=dict(position="relative",left="800px",width="200px",height="75px",fontSize=30,color="cyan",fontWeight=700,backgroundColor="red")),
        html.Div(id="clear-div",style=dict(position="relative",left="50px",fontSize=30)),
        *large_break,
        html.Div(reports_dropdown,style=dict(width="650px",fontWeight=700,alignItems="center")),
        html.Div(page_size_dropdown,style=dict(width="200px",fontWeight=700,alignItems="center",position="relative",left="650px",bottom="50px")),
        html.Div(templates_dropdown,style=dict(width="800px",fontWeight=700,alignItems="center",position="relative",left="900px",bottom="100px")),
        *large_break,
        html.Div(id="output-report",style=dict(border="2px solid rgba(0,255,255,0.7)",borderBottom=None,padding="20px",position="relative",left="100px",width="900px",fontSize=18)),
        html.Hr(style=dict(position="relative",left="100px",width="900px",border="1px solid cyan")),
        html.Div("Test Value Reference",style=dict(wordSpacing="300px",paddingTop="20px",paddingLeft="50px",border="2px solid rgba(0,255,255,0.7)",borderTop=None,borderBottom=None,width="900px",height="50px",position="relative",left="100px")),
        html.Hr(style=dict(position="relative",left="100px",width="900px",border="1px solid cyan")),
        html.Div(id="output-report-boxes",style=dict(border="2px solid rgba(0,255,255,0.7)",borderTop=None,padding="2px",position="relative",paddingTop="50px",alignItems="center",left="100px",width="900px",fontSize=18)),
        html.Button("Submit".upper(),id="submit-report-button",style=dict(width="200px",height="100px",position="relative",backgroundColor="cyan",left="800px",fontSize=25,borderRadius="20px")),
        html.Div(html.H1("report preview".upper(),className="page-heading"),className="heading-divs",style=dict(position="relative",top="50px")),
        html.Div(["top space slider  ".upper(),dcc.Slider(min=0,max=200,step=20,value=0,id="top-slider")],style=dict(left="50px",position="relative",width="550px",fontSize=15)),
        html.Div(["between space slider  ".upper(),dcc.Slider(min=10,max=80,step=5,value=24,id="slider")],style=dict(left="50px",position="relative",width="550px",top="20px",fontSize=15)),
        html.Div("type report to preview".upper(),id="report-preview",style=dict(color="cyan",border="10px solid #4b70f5",padding="50px",position="relative",width="60%",height="1300px",top="100px"),className="wrap"),
    ],
    className="subpage-content"
)

@callback(
    Output("patients-dropdown","options"),
    Input("date-pick-reports","date")
)
def append_report_options(date:str):
    path = f"assets/all_files/{date.replace("-","_")}.csv"
    if os.path.exists(path):
        df = pd.read_csv(path,dtype=dtype_map)
        df = df.iloc[:-1,:]
        return df["S.No."].to_list()
    return []



hb_list = [
    html.Div("Heamoglobin :",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'hb'},type="number",placeholder="Type Hb Value..",style=input_style),
    html.Div("( 11.0 - 16.8 Grams%)",style=limits_style),
]

tc_list = [
    html.Div("Total WBC Count :",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'tc_count'},type="number",placeholder="Type Tc value..",style=input_style),
    html.Div("( 5,000 - 10,000 Cells/cumm )",style=limits_style),
]

plt_list = [
    html.Div("Platelet Count :",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'plt_count'},type="number",placeholder="Type Plt Value..",style=input_style),
    html.Div("( 1.5 - 4.0 Lakhs/cumm )",style=limits_style),
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
    html.Div("( 01 - 04 %)",style=dict(position="relative",left="670px",bottom="40px",fontSize=18)),
]

crp_list = [
    html.Div("CRP :   ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'crp'},type="number",placeholder="Type CRP value..",style=input_style),
    html.Div(" ( < 6 ) ",style=limits_style)
]

malaria_list = [
    *small_break,
    html.Div("Test For Malaria Parasite (M.P): ",style=text_style),
    html.Div(dcc.Dropdown(["non-reactive".upper(),"reactive".upper()],"non-reactive".upper(),id={"type":"dynamic-input","name":"malaria-mp"}),style={**input_style,"left":"500px","width":"200px"}),
    html.Div([dcc.Dropdown(["Long".upper(),"Short".upper()],"Short".upper(),id={'type':'dynamic-input','name':'malaria-test'})],style={**input_style,"left":"750px","bottom":"25px"}),
    html.Div("PLasmodium Vivex: ",style=text_style),
    html.Div(dcc.Dropdown(["non-reactive".upper(),"reactive".upper()],"non-reactive".upper(),id={"type":"dynamic-input","name":"malaria-vivex"}),style={**input_style,"left":"500px","width":"200px"}),
    html.Br(),
    html.Div("PLasmodium Falciparum: ",style=text_style),
    html.Div(dcc.Dropdown(["non-reactive".upper(),"reactive".upper()],"non-reactive".upper(),id={"type":"dynamic-input","name":"malaria-falci"}),style={**input_style,"left":"500px","width":"200px"}),
    *small_break
]

widal_list = [
    html.Div("Blood for Widal : ",style=text_style),
    html.Div([dcc.Dropdown(["NON-REACTIVE","REACTIVE"],"REACTIVE",id={'type':'dynamic-input','name':'widal'})],style={**input_style,"width":"200px"}),
    html.Div([dcc.Dropdown(["SHORT","LONG"],"LONG",id={'type':'dynamic-input','name':'widal-form'})],style=dict(position="relative",left="600px",bottom="50px",width="150px",height="50px")),
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
    ),
]

total_bilirubin_list = [
    html.Div("Total Bilirubin : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'total-bili'},type="number",placeholder="Enter Total Bilirubin",style=input_style),
    html.Div(" ( 0.2 - 1.0 mg/dl)",style=limits_style),
]

direct_indirect_bilirubin_list = [
    html.Div("Direct Bilirubin: ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'direct-bili'},type="number",placeholder="Enter Direct Bilirubin",style=input_style),
    html.Div(" ( 0.2 - 0.4 mg/dl ) ",style=limits_style),
    html.Div("Indirect Bilirubin: ",style=text_style),
    html.Div("-----------",style=limits_style),
    html.Div(" ( 0.2 - 0.6 mg/dl )",style=limits_style),
]

sgot_list = [
    html.Div("Aspirate Amino Transferase (SGOT): ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'sgot'},type="number",placeholder="29 (normal)",style={**input_style,"left":"500px"}),
    html.Div("( < 40 )",style={**limits_style,"left":"700px"}),
]

sgpt_list = [
    html.Div("Alinine  Amino Transferase (SGPT): ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'sgpt'},type="number",placeholder="29 (normal)",style={**input_style,"left":"500px"}),
    html.Div("( < 40 )",style={**limits_style,"left":"700px"}),
]

alkp_list = [
    html.Div("Alkaline Phosphatase (ALKP): ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'alkp'},type="number",placeholder="29 (normal)",style={**input_style,"left":"500px"}),
    html.Div("( 37 - 147 )",style={**limits_style,"left":"700px"}),
]

x_ray_list = [
    html.P("""Rest of lung fields  are normal .

             Both hila normal in density .

           Cardiac shape are normal .

          Both CP angles are clear .
    
         Bony cage and soft tissues are normal .

         Opinion : NORMAL 
           
         For clinical correlation .
""",id={'type':'dynamic-input','name':'x-ray-opinion'}),
]

esr_list = [
    html.Div("E.S.R : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'esr'},type="number",placeholder="E.S.R..,",value=10,style=input_style),
    html.Div(" (02 - 10 mm/1 hour) ",style=limits_style),
]

hct_list = [
    html.Div("PCV (Haematocrit) : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'hct'},type="number",placeholder="HCT..",style=input_style),
    html.Div(" (40% - 45%) ",style=limits_style),
]

dengue_list = [
    *small_break,
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
    *small_break,
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
    *small_break,
    html.Div("Glycosylated Hb (HbA1c) Test: ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'hba1c_first'},type="number",placeholder="Type Hba1c %..",style={**input_style,"left":"500px"}),
    html.Div("%",style={**limits_style,"left":"700px"}),
    html.Div("Esitmiated Average Glucose (eAG): ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'hba1c_second'},type="number",placeholder="Type Hba1c mg/dl..",style={**input_style,"left":"500px"}),
    html.Div("mg/dl",style={**limits_style,"left":"700px"}),
    html.Div([dcc.Dropdown(["SMALL","LONG"],"LONG",id={'type':'dynamic-input','name':'hba1c_dropdown'})],style={**limits_style,"width":"150px","left":"800px","bottom":"75px"}),
]

blood_urea_list = [
    *small_break,
    html.Div("Blood Urea : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'blood-urea'},type="number",placeholder="Enter Urea",style=input_style),
    html.Div(" ( 10 - 40 mg/dl )",style=limits_style),
]

serum_creatinine_list = [
    *small_break,
    html.Div("Serum creatinine : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'serum-creat'},type="number",placeholder="Enter creatinine",style=input_style),
    html.Div("( 2.5 - 7.5 IU/L )",style=limits_style),
]

bt_list = [
    *small_break,
    html.Div("B.T : ",style=text_style),
    html.Div(
        [
            dcc.Input(id={'type':'dynamic-input','name':'bt_min'},type="text",placeholder="1",value="1",style=dict(width="50px")),
            " : ",
            dcc.Input(id={'type':'dynamic-input','name':'bt_sec'},type="text",placeholder="35 sec.",value="35",style=dict(width="50px")),
            "  Sec."
        ],
        style={**input_style,"text-align":"center","align-items":"center","display":"flex","flex-direction":"row"}
    ),
]

ct_list = [
    *small_break,
    html.Div("C.T : ",style=text_style),
    html.Div(
        [
            dcc.Input(id={'type':'dynamic-input','name':'ct_min'},type="text",placeholder="3",value="3",style=dict(width="50px")),
            " : ",
            dcc.Input(id={'type':'dynamic-input','name':'ct_sec'},type="text",placeholder="05 sec.",value="05",style=dict(width="50px")),
            "  Sec."
        ],
        style={**input_style,"text-align":"center","align-items":"center","display":"flex","flex-direction":"row"}
    )
]

uric_acid_list = [
    *small_break,
    html.Div("Uric Acid : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'uric-acid'},type="number",placeholder="Enter Uric Acid",style=input_style),
    html.Div(" ( 2.5 - 7.5 IU/L ) ",style=limits_style)
]

urine_analysis_list = [
    *small_break,
    html.Div("Urine analysis :",style=text_style),
    *small_break,
    html.Div(dcc.Dropdown(["short".upper(),"long".upper()],"long".upper(),id={'type':'dynamic-input','name':'urine-drop'}),style={**input_style,"bottom":"50px"}),
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
        dcc.Input(id={'type':'dynamic-input','name':'urine_first_pus'},type="number",value=1,style=dict(width="100px")),
        "-",
        dcc.Input(id={'type':'dynamic-input','name':'urine_second_pus'},type="number",value=3,style=dict(width="100px",marginRight="20px")),
        "Pus Cells"
    ],style=dict(position="relative",left="300px",margin="10px",wordSpacing="10px")),
    html.Div([
        dcc.Input(id={'type':'dynamic-input','name':'urine_first_rbc'},type="number",placeholder="No..",value=0,style=dict(width="100px")),
        "-",
        dcc.Input(id={'type':'dynamic-input','name':'urine_second_rbc'},type="number",placeholder="No..",value=0,style=dict(width="100px",marginRight="20px")),
        "RBC  *(leaving blank means No RBC)"
    ],style=dict(position="relative",left="300px",margin="10px",wordSpacing="10px")),
    html.Div([
        dcc.Input(id={'type':'dynamic-input','name':'urine_first_casts'},type="number",placeholder="No..",value=0,style=dict(width="100px")),
        "-",
        dcc.Input(id={'type':'dynamic-input','name':'urine_second_casts'},type="number",placeholder="No..",value=0,style=dict(width="100px",marginRight="20px")),
        "Casts  *(leaving blank means No Casts)"
    ],style=dict(position="relative",left="300px",margin="10px",wordSpacing="10px")),
    html.Div([
        dcc.Input(id={'type':'dynamic-input','name':'urine_first_crystals'},type="number",placeholder="No..",value=0,style=dict(width="100px")),
        "-",
        dcc.Input(id={'type':'dynamic-input','name':'urine_second_crystals'},type="number",placeholder="No..",value=0,style=dict(width="100px",marginRight="20px")),
        "Crystals  *(leaving blank means No Crystals)"
    ],style=dict(position="relative",left="300px",margin="10px",wordSpacing="10px")),
    html.Div([
        dcc.Input(id={'type':'dynamic-input','name':'urine_first_ep'},type="number",value=2,style=dict(width="100px")),
        "-",
        dcc.Input(id={'type':'dynamic-input','name':'urine_second_ep'},type="number",value=4,style=dict(width="100px",marginRight="20px")),
        "Epithelial Cells Present"
    ],style=dict(position="relative",left="300px",margin="10px",wordSpacing="10px"))
]

urine_pregnency_list = [
    *small_break,
    html.Div("Urine Test Report : ",style=text_style),
    html.Div("Urine Pregnancy Test : ",style=text_style),
    html.Div([dcc.Dropdown(["negative".upper(),"positive".upper()],"negative".upper(),id={'type':'dynamic-input','name':'preg_test'})],style=input_style)
]

pt_aptt_list = [
    *small_break,
    html.Div("Prothrombin Time Test",style={**text_style,"left":"400px","text-decoration":"underline"}),
    *big_break,
    html.Div("P.T Test:",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'pt_test'},type="number",placeholder="14.6 seconds",value=14.6,style=input_style),
    html.Div("P.T. Control : ",style=text_style),
    html.Div("13.4 seconds",style=input_style),
    html.Div("INR : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'pt_inr'},type="number",placeholder="1.2",style=input_style),
    *small_break,
    html.Div("Activate Partial Thromboplastin Time",style={**text_style,"left":"400px","text-decoration":"underline"}),
    *small_break,
    html.Div("APTT Test :",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'aptt_test'},type="number",placeholder="33.6 seconds...",value=32.7,style=input_style),
    html.Div(" ( Nor: 26 - 38 sec )",style=limits_style),
    html.Div("APTT Control : ",style=text_style),
    html.Div(" 33.6",style=input_style),
    html.Div("( Nor 26 - 38 sec )",style=limits_style)
]

mantaoux_list = [
    *small_break,
    html.Div("mantoux test :".upper(),style=text_style),
    html.Div([dcc.Dropdown(["positive".upper(),"negative".upper()],"negative".upper(),id={'type':'dynamic-input','name':'mantoux_test'})],style=input_style),
    *small_break
]

sugar_random_list = [
    *small_break,
    html.Div("Blood Sugar (Random):",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'random_sugar'},type="number",placeholder="Type RBS..",style=input_style),
    html.Div(" ( 70 - 140 mg/dl ) ",style=limits_style)
]

sugar_fasting_list = [
    *small_break,
    html.Div("Blood Sugar (Fasting):",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'fasting_sugar'},type="number",placeholder="Type FBS..",style=input_style),
    html.Div(" ( 70 - 110 mg/dl ) ",style=limits_style)
]

post_pandial_list = [
    *small_break,
    html.Div("Blood Sugar (Post Pandial):",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'pp_sugar'},type="number",placeholder="Type PP Sugar..",style=input_style),
    html.Div(" ( 70 - 180 mg/dl )",style=limits_style)
]

urine_sugar_random_list = [
    *small_break,
    html.Div("Urine Sugar (Random):",style=text_style),
    dcc.Input(id={"type":"dynamic-input","name":"urine_random_sugar"},type="number",placeholder="Type Random Urine",style=input_style),
]

urine_sugar_fasting_list = [
    *small_break,
    html.Div("Urine Sugar (Fasting):",style=text_style),
    dcc.Input(id={"type":"dynamic-input","name":"urine_fasting_sugar"},type="number")
]

lipid_profile_list = [
    *small_break,
    html.Div("Total Cholesterol : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_tc'},type="number",placeholder="Type Tc..",style={**input_style,"left":"500px"}),
    html.Div("Low Risk < 220.0 mg/dl",style={**limits_style,"left":"700px"}),
    html.Div("Border Line - 220 - 239",style={**limits_style,"left":"700px"}),
    html.Div("High Risk > 250",style={**limits_style,"left":"700px"}),
    html.Div("High Density Lipoprotein ( HDL ) : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_hdl'},type="number",placeholder="Type HDL...",style={**input_style,"left":"500px"}),
    html.Div("29.0 - 80 mg/dl",style={**limits_style,"left":"700px"}),
    html.Div("Low Density Lipoprotein : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_ldl'},type="number",placeholder="Type LDL...",style={**input_style,"left":"500px"}),
    html.Div("Desirable < 100",style={**limits_style,"left":"700px"}),
    html.Div("Border Line 110 - 129",style={**limits_style,"left":"700px"}),
    html.Div("High Risk > 130.0",style={**limits_style,"left":"700px"}),
    html.Div("Very Low Density Lipoprotein : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_vldl'},type="number",placeholder="Type VLDL",style={**input_style,"left":"500px"}),
    html.Div("7.0 - 35.0 mg/dl",style={**limits_style,"left":"700px"}),
    html.Div("Triglyceride (F): ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'lipid_tri'},type="number",placeholder="Type Triglyceride...",style={**input_style,"left":"500px"}),
    html.Div("Normal < 170.0 mg/dl",style={**limits_style,"left":"700px"}),
    html.Div("BorderLine 200 - 400",style={**limits_style,"left":"700px"}),
    html.Div("High 400 - 1000",style={**limits_style,"left":"700px"}),
]

blood_for_aec_list = [
    *small_break,
    html.Div("Blood for AEC Count : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'aec-count'},type="number",placeholder="460",style=input_style),
    html.Div(" (50 - 450 cells/cumm ) ",style=limits_style)
]

ra_factor_list = [
    *small_break,
    html.Div("ra-factor :".upper(),style=text_style),
    html.Div(dcc.Dropdown(["positive".upper(),"negative".upper()],"negative".upper(),id={'type':'dynamic-input','name':'ra-factor'}),style=dict(position="relative",width="200px",left="300px",bottom="25px")),
    html.Div(" ( 1 : ",style={**limits_style,"bottom":"50px"}),
    dcc.Input(id={'type':'dynamic-input','name':'ra-dilutions'},type="number",placeholder="None",style={**limits_style,"bottom":"75px","left":"620px","width":"100px"}),
    html.Div(" dilutions ) ",style={**limits_style,"left":"730px","bottom":"95px"})
]

aso_titre_list = [
    *small_break,
    html.Div("ASO TITRE : ",style=text_style),
    html.Div(dcc.Dropdown(["POSITIVE","NEGATIVE"],"NEGATIVE",id={'type':'dynamic-input','name':'aso_titre'}),style=dict(position="relative",width="200px",left="300px",bottom="25px")),
    html.Div("( 1 : ",style={**limits_style,"bottom":"50px"}),
    dcc.Input(id={'type':'dynamic-input','name':'aso_titre_dilutions'},type="number",placeholder="None",style={**limits_style,"bottom":"75px","left":"620px","width":"100px"}),
    html.Div(" dilutions ) ",style={**limits_style,"left":"730px","bottom":"95px"})
]

serum_amylase_list = [
    *small_break,
    html.Div("Serum Amylase : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_amylase'}, type="number", placeholder="Type amylase", style=input_style),
    html.Div(" (30 - 110 U/L) ", style=limits_style)
]

serum_lipase_list = [
    *small_break,
    html.Div("Serum Lipase : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_lipase'}, type="number", placeholder="Type lipase", style=input_style),
    html.Div(" (23 - 300 U/L) ", style=limits_style)
]

serum_protein_list = [
    *small_break,
    html.Div("Serum Protein : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_protein'}, type="number", placeholder="Type protein", style=input_style),
    html.Div(" (6.6 - 8.3 g/dl) ", style=limits_style)
]

serum_albumin_list = [
    *small_break,
    html.Div("Serum Albumin : ", style=text_style),
    dcc.Input(id={'type': 'dynamic-input', 'name': 'serum_albumin'}, type="number", placeholder="Type albumin", style=input_style),
    html.Div(" (3.5 - 5.0 g/dl) ", style=limits_style)
]

serum_globulin_list = [
    *small_break,
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
    *small_break,
    html.Div("V.D.R.L : ",style=text_style),
    html.Div([dcc.Dropdown(["reactive".upper(),"non-reactive".upper()],"non-reactive".upper(),id={'type':'dynamic-input','name':'vdrl'})],style={**input_style,"width":"300px"})
]

hbsag_list = [
    *small_break,
    html.Div("HBsAg : ",style=text_style),
    html.Div([dcc.Dropdown(["reactive".upper(),"non-reactive".upper()],"non-reactive".upper(),id={'type':'dynamic-input','name':'hbsag'})],style={**input_style,"width":"300px"})
]

hiv_list = [
    *small_break,
    html.Div("HIV I & II Antibodies Test : ",text_style),
    html.Div([dcc.Dropdown(["reactive".upper(),"non-reactive".upper()],"non-reactive".upper(),id={'type':'dynamic-input','name':'hiv_ant'})],style={**input_style,"width":"300px"})
]

hcv_list = [
    *small_break,
    html.Div("HCV I & II Antibodies Test : ",text_style),
    html.Div([dcc.Dropdown(["reactive".upper(),"non-reactive".upper()],"non-reactive".upper(),id={'type':'dynamic-input','name':'hcv_ant'})],style={**input_style,"width":"300px"})
]

semen_list = [
    *small_break,
    html.Div("Volume : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'semen-volume'},type="number",placeholder="3.0 ml",value=3.0,style=input_style),
    html.Div("( 1.5 - 5.0 ml )",style=limits_style),
    html.Div("Liquefaction : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'semen-liq'},type="number",placeholder="5 mts",value=5,style=input_style),
    html.Div(" with in 20 mts",style=limits_style),
    html.Div("PH : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'semen-ph'},type="number",placeholder="8.0",value=8.0,style=input_style),
    html.Div("Spermatozoa Count : ",style=limits_style),
    dcc.Input(id={'type':'dynamic-input','name':'semen-count'},type="number",placeholder="78 millions",value=78,style=input_style),
    html.Div("( 60 - 150 millions/ml )",style=limits_style),
    html.Div("Sperm motility : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'semen-mot'},type="number",placeholder="70%",value=70,style=input_style),
    html.Div(" > 60% motile forms",style=limits_style),
    html.Div("Sperm mrophology : ",style=text_style),
    dcc.Input(id={'type':'dynamic-input','name':'semen-morph'},type="number",placeholder="55%",value=55,style=input_style),
    html.Div(" > 70% normal",style=limits_style),
    html.Div("other finding : ".upper(),style=text_style),
    *small_break,
    html.Div("W.B.C/h.p.t : ",style=text_style),
    html.Div(
        [
            dcc.Input(id={'type':'dynamic-input','name':'semen-wbc-first'},type="number",placeholder="1",value=1),
            " - ",
            dcc.Input(id={'type':'dynamic-input','name':'semen-wbc-second'},type="number",placeholder="2",value=2),
        ],
        style={**input_style,"display":"flex"}
    ),
    html.Div("R.B.C/h.p.t : ",style=text_style),
    html.Div(
        [
            dcc.Input(id={'type':'dynamic-input','name':'semen-rbc-first'},type="number",placeholder="NIL",value=0),
            " - ",
            dcc.Input(id={'type':'dynamic-input','name':'semen-rbc-second'},type="number",placeholder="NIL",value=0),
        ],
        style={**input_style,"display":"flex"}
    ),
    html.Div("Comments : Suggestive of ",style=text_style),
    *small_break,
    dcc.Input(id={'type':'dynamic-input','name':'semen-comments'},type="text",placeholder="* normo seprmia *, oligozoo spermia",style={**input_style,"width":"500px"})
]

electrolytes_list = [
    *serum_sodium_list,
    *serum_potassium_list,
    *serum_chloride_list,
    *serum_calcium_list
]

liver_function_list = [
    *total_bilirubin_list,
    *direct_indirect_bilirubin_list,
    *sgot_list,
    *sgpt_list,
    *alkp_list
]


bill_list = [
    html.Button("ADD LINE",id="bill-add-line",style={**text_style,"width":"150px","height":"100px","borderRadius":"20px","backgroundColor":"cyan","font-weight":700}),
    *big_break,
    html.Div(id="bill-inputs")
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
    "Liver Function Test":liver_function_list,
    "BT":bt_list,
    "CT":ct_list,
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
    "Electrolytes":electrolytes_list,
    "V.D.R.L":vdrl_list,
    "HBsAg":hbsag_list,
    "HIV I & II Antibodies Test":hiv_list,
    "HCV I & II Antibodies Test":hcv_list,
    "Semen Analysis":semen_list,
    "XRAY Opinion":x_ray_list,
    "BILL":bill_list,
}

@callback(
    Output("bill-inputs","children"),
    Input("bill-add-line","n_clicks")
)
def add_bill_inputs(n_clicks):
    if not n_clicks:
        raise PreventUpdate
    if ctx.triggered_id == "bill-add-line":
        return [
            html.Div(
                [
                    f"{i+1}.  ",
                    dcc.Input(id={"type":"dynamic-input","name":f"bill-{i}-name"},type="text",placeholder="Test Name..",style=dict(fontSize=25,height="50px")),
                    "  -  ",
                    dcc.Input(id={"type":"dynamic-input","name":f"bill-{i}-value"},type="number",placeholder="Price..",style=dict(fontSize=25,height="50px")),
                    "  /-  "
                ],
                style=dict(fontSize=25,position="relative",left="100px")
            )
        for i in range(n_clicks)]

def get_df_item(p_sn:str,item_name:str,df:pd.DataFrame):
    return df.loc[df.loc[:,"S.No."] == p_sn,item_name].item()


@callback(
    [
        Output("output-report","children"),
        Output("output-report-boxes","children"),
        Output("clear-div","children")
    ],
    [
        Input("patients-dropdown","value"),
        Input("reports-dropdown","value"),
        Input("template-dropdown","value")
    ],
    State("date-pick-reports","date"),
    prevent_initial_call=True
)
def preview_report_divs(patients_sno,reports_value,template_value,date):
    if patients_sno:
        df = pd.read_csv(f"assets/all_files/{date.replace("-","_")}.csv",dtype=dtype_map)
        df = df.iloc[:-1,:]
        year,month,day = date.split("-")
        os.makedirs(f"assets/{year}/{month}/{day}",exist_ok=True)
        conn = duckdb.connect(f"assets/{year}/{month}/{day}/{date.replace("-","_")}.duckdb")
        conn.execute(
            """
            create table if not exists patients (
                id text primary key,
                tests text
            )
            """
        )
        patients_details = [
                html.Div(f"Patient Name: {get_df_item(patients_sno,item_name='Patient Name',df=df)}"),
                html.Br(),
                html.Div(f"Age: {get_df_item(patients_sno,item_name='Patient Age',df=df)} {get_df_item(patients_sno,item_name='Age Group',df=df)}"),
                html.Br(),
                html.Div(f"Reference By: {get_df_item(patients_sno,item_name='Reference By',df=df)}"),
                html.Br(),
                html.Div(f"Date: {get_df_item(patients_sno,item_name="Date",df=df)}   Collection Time: {get_df_item(patients_sno,item_name='Time',df=df)}")
            ]
        all_opts = []
        if (conn.query(f"select * from patients where id = {patients_sno}").df().shape[0] == 0):
            tests_names = []
            is_present = False
        else:
            tests_names = json.loads(conn.query(f"select * from patients where id = {patients_sno}").df()["tests"].item())
            if tests_names == []:
                is_present = False
            else:
                is_present = True
        if reports_value:
            for x in reports_value:
                all_opts.append(x)
                if x not in tests_names:
                    tests_names.append(x)
        print(f"\n\n final tests after reports: {tests_names}\n\n")
        if template_value:
            template_list = json.loads(template_value)
            for x in template_list:
                all_opts.append(x)
                if x not in tests_names:
                    tests_names.append(x)
        print(f"\n\n final tests after templates: {tests_names}\n\n")
        for x in tests_names:
            if x not in all_opts:
                tests_names.remove(x)
        print(f"\n\n final tests after all opts: {tests_names}\n\n")
        conn.execute(f"insert or replace into patients (id, tests) values ('{patients_sno}','{json.dumps(tests_names)}')")
        conn.close()
        report_details = []
        for x in tests_names:
            report_details += reports_original_dict[x]
        if is_present:
            present_string = ["Data is present with data:",html.Br(),re.sub(r'[\[\],\"]',' ',json.dumps(tests_names))]
        else:
            present_string = ""
        if len(report_details) == 0:
            return patients_details,"Select Test to Display",present_string
        else:
            return patients_details,report_details,present_string
    return "Select a Serial Number To Display","Select a Test wit Serial Number to Display",""


@callback(
    Output("clear-div","children",allow_duplicate=True),
    Input("clear-button","n_clicks"),
    [
        State("date-pick-reports","date"),
        State("patients-dropdown","value")
    ],
    prevent_initial_call=True
)
def clear_data_in_sno(n_clicks,date:str,patients_sno:str):
    if n_clicks:
        year,month,day = date.split("-")
        conn = duckdb.connect(f"assets/{year}/{month}/{day}/{date.replace("-","_")}.duckdb")
        conn.execute(f"delete from patients where id = '{patients_sno}'")
        conn.close()
        return "Data is cleared"
        


small_left_extreme = 42
small_value_point = 182
small_right_extreme = 375
small_font_name = "Times-BoldItalic"
small_font_size = 13
small_limits_font_size = 11
big_left_extreme = 43
big_right_extreme = 540
big_value_point = 240
big_font_name = "CenturySchoolBook-BoldItalic"
big_font_size = 12
big_limits_font_size = 11

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
        frmt_time:str,
        left_extreme,
        midpoint,
        right_extreme,
        drop_height
    ):
    c.setFont(font_name,font_size)

    if (patient_age_group == "M") | (patient_age_group == "D"):
        patient_title = "Chi" 
    else:
        if (patient_age < 18):
            patient_title = "Chi."
        if (patient_age > 13) & (patient_gender == "Female"):
            patient_title = "Kmr."
        if (patient_age >= 18) & (patient_gender == "Male"):
            patient_title = "Mr."
        if (patient_age >= 18) & (patient_gender == "Female"):
            patient_title = "Ms."
        if (patient_age >= 22) & (patient_gender == "Female"):
            patient_title = "Mrs."
    c.drawString(left_extreme,page_height-drop_height,f"Pt. Name : {patient_title} {patient_name.upper()}")
    c.drawString(left_extreme,page_height-(drop_height + patient_details_space),f"Age : {patient_age} {patient_age_group}")
    gender_string = f"Gender : {patient_gender}"
    c.drawString(right_extreme-cal_string_width(c,gender_string,font_name,font_size),page_height-(drop_height + patient_details_space),gender_string)     # s
    if doctor_name == "self".upper():
        c.drawString(left_extreme,page_height-(drop_height + 2*patient_details_space),f"Ref.Dr.By. : ")
    else:
        c.drawString(left_extreme,page_height-(drop_height + 2*patient_details_space),f"Ref.Dr.By. : {doctor_name}")
    c.drawString(left_extreme,page_height-(drop_height + 3*patient_details_space),f"Serial No: {patient_serial_no:0>4}")
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

def mundane_things(c:canvas.Canvas,x,text_string,value,value_string,limits_string,limit_a,limit_b,h,if_limits=True,left_offset=0):
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["left_extreme"][x],h,text_string)
    if if_limits:
        c = if_draw_bold(c,value,value_string,limit_a,limit_b,size_dict["value_point"][x]+left_offset,h)
    else:
        c.drawString(size_dict["value_point"][x]+left_offset,h,f":   {value_string}")
    c.setFont(size_dict["font_name"][x],size_dict["limits_font"][x])
    c.drawString(size_dict["right_extreme"][x]-cal_string_width(c,limits_string,size_dict["font_name"][x],size_dict["limits_font"][x]),h,limits_string)
    return c

# done
def hb_canvas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height = 18):
    limits_string = "( 11.0 - 16.8 Grams% )"
    text_string = "Heamoglobin"
    limit_a = 11.0
    limit_b = 16.8
    value_string = f"{value:.1f}"
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

# done
def tc_canvas(c:canvas.Canvas,value:int,page_size:str,h:int,entity_height = 18):
    limits_string = "( 5,000 - 10,000 Cells/cumm )"
    text_string = "Total WBC Count"
    value_string = f"{str(value/1000).replace(".",",")}00"
    limit_a = 5000
    limit_b = 10000
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

# done
def plt_canvas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height = 18):
    limits_string = "( 1.5 - 4.0 Lakhs/cumm )"
    text_string = "Platelet Count : "
    limit_a = 1.5
    limit_b = 4.0
    if value > 1000:
        value_string = f"{value//1000},000"
    else:
        value_string = f"{value:.2f}"
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

# done
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
        c.line(small_left_extreme,h-5,small_left_extreme+cal_string_width(c,dc_string,small_font_name,small_font_size),h-5)
        h -= (1.2 * entity_height)
        c.drawString(142,h,poly_string)
        c = if_draw_bold(c,polymo_value,p(polymo_value),40,70,260,h)
        c.setFont(small_font_name,small_limits_font_size)
        c.drawString(small_right_extreme-cal_string_width(c,"( 40 - 70 %)",small_font_name,small_limits_font_size),h,"( 40 - 70 %)")
        c.setFont(small_font_name,small_font_size)
        h -= entity_height
        c.drawString(142,h,lympho_string)
        c = if_draw_bold(c,lympho_value,p(lympho_value),20,40,260,h)
        c.setFont(small_font_name,small_limits_font_size)
        c.drawString(small_right_extreme-cal_string_width(c,"( 40 - 70 %)",small_font_name,small_limits_font_size),h,"( 20 - 40 %)")
        c.setFont(small_font_name,small_font_size)
        h -= entity_height
        c.drawString(142,h,eosino_string)
        c = if_draw_bold(c,esino_value,p(esino_value),2,6,260,h)
        c.setFont(small_font_name,small_limits_font_size)
        c.drawString(small_right_extreme-cal_string_width(c,"( 40 - 70 %)",small_font_name,small_limits_font_size),h,"( 02 - 06 %)")
        h -= entity_height
        c.drawString(142,h,mono_string)
        c = if_draw_bold(c,mono_value,p(mono_value),1,4,260,h)
        c.setFont(small_font_name,small_limits_font_size)
        c.drawString(small_right_extreme-cal_string_width(c,"( 40 - 70 %)",small_font_name,small_limits_font_size),h,"( 01 - 04 %)")
        return c, h - entity_height
    else:
        entity_height += 5
        c.setFont(big_font_name,big_font_size)
        c.drawString(big_left_extreme,h,dc_string)
        c.line(big_left_extreme,h-5,big_left_extreme+cal_string_width(c,dc_string,big_font_name,big_font_size),h-5)
        h -= (entity_height * 1.2)
        c.drawString(182,h,poly_string)
        c = if_draw_bold(c,polymo_value,p(polymo_value),40,70,300,h)
        c.setFont(big_font_name,big_limits_font_size)
        c.drawString(big_right_extreme-cal_string_width(c,"( 40 - 70 %)",big_font_name,big_limits_font_size),h,"( 40 - 70 %)")
        c.setFont(big_font_name,big_font_size)
        h -= entity_height
        c.drawString(182,h,lympho_string)
        c = if_draw_bold(c,lympho_value,p(lympho_value),20,40,300,h)
        c.setFont(big_font_name,big_limits_font_size)
        c.drawString(big_right_extreme-cal_string_width(c,"( 40 - 70 %)",big_font_name,big_limits_font_size),h,"( 20 - 40 %)")
        c.setFont(big_font_name,big_font_size)
        h -= entity_height
        c.drawString(182,h,eosino_string)
        c = if_draw_bold(c,esino_value,p(esino_value),2,6,300,h)
        c.setFont(big_font_name,big_limits_font_size)
        c.drawString(big_right_extreme-cal_string_width(c,"( 40 - 70 %)",big_font_name,big_limits_font_size),h,"( 02 - 06 %)")
        c.setFont(big_font_name,big_font_size)
        h -= entity_height
        c.drawString(182,h,mono_string)
        c = if_draw_bold(c,mono_value,p(mono_value),1,4,300,h)
        c.setFont(big_font_name,big_limits_font_size)
        c.drawString(big_right_extreme-cal_string_width(c,"( 40 - 70 %)",big_font_name,big_limits_font_size),h,"( 01 - 04 %)")
        return c,h-(entity_height * 0.5)

# done
def crp_canvas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height=18):
    limits_string = " ( < 6 ) "
    text_string = "CRP"
    value_string = f"{value:.1f}"
    limit_a = 0
    limit_b = 6
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    c.setFont(size_dict["font_name"][x],size_dict["limits_font"][x])
    h -= 10
    c.drawString(size_dict["left_extreme"][x],h,"(Turbidmetric Immunoassay)")
    return c, h - entity_height

# done
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
            if widal_form == "SHORT":
                c.drawString(small_right_extreme-cal_string_width(c,ot_string,small_font_name,small_limits_font_size)-100,h-(entity_height * 0.8),ot_string)
                c.drawString(small_right_extreme-cal_string_width(c,ht_string,small_font_name,small_limits_font_size)-100,h-(entity_height * 1.5),ht_string)
                c.drawString(small_right_extreme-cal_string_width(c,ah_string,small_font_name,small_limits_font_size),h-(entity_height * 0.8),ah_string)
                c.drawString(small_right_extreme-cal_string_width(c,bh_string,small_font_name,small_limits_font_size),h-(entity_height * 1.5),bh_string)
            else:
                c.drawString(small_right_extreme-cal_string_width(c,ot_string,small_font_name,small_limits_font_size),h-(entity_height * 0.8),ot_string)
                c.drawString(small_right_extreme-cal_string_width(c,ht_string,small_font_name,small_limits_font_size),h-(entity_height * 1.5),ht_string)
                c.drawString(small_right_extreme-cal_string_width(c,ah_string,small_font_name,small_limits_font_size),h-(entity_height * 2.2),ah_string)
                c.drawString(small_right_extreme-cal_string_width(c,bh_string,small_font_name,small_limits_font_size),h-(entity_height * 2.9),bh_string)
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

# done
def hct_canvas(c:canvas.Canvas,value,page_size:str,h:int,entity_height=18):
    limits_string = "( 40% - 45% )"
    text_string = "PCV(Heamatocrit)"
    value_string = f"{value:.1f}"
    limit_a = 40
    limit_b = 45
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

# done
def esr_canvas(c:canvas.Canvas,value,page_size:str,h:int,entity_height=18):
    text_string = "E.S.R"
    limits_string = "( 02 - 10 mm/Hr )"
    value_string = f"{value:0>2}"
    limit_a = 2
    limit_b = 11
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h - entity_height

# done
def full_cbp_canvas(c:canvas.Canvas,cbp_values:list,page_size:str,h:int,entity_height=18):
    entity_height += 5
    hb,rbc_count,hct,tc_count,plt_count,esr,polymo,lympho,esino = cbp_values
    if page_size == "BIG/A4":
        c,h = hb_canvas(c,hb,page_size,h,entity_height-5)
        x = 1
        text_string = "Total RBC Count"
        limits_string = "( 4.0 - 5.0 millions/cumm)"
        value_string = f"{rbc_count:.2f}"
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

# done
def blood_group_canvas(c:canvas.Canvas,value:str,page_size:str,h:int,entity_height=18):
    text_string = "blood group".upper()
    value_string = f" * {value.replace(" "," * ")}"
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string="",limit_a="",limit_b="",h=h,if_limits=False)
    return c,h - entity_height

# done
def total_bilirubin_canvas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height=18):
    text_string = "Total Bilirubin"
    limits_string = "( 0.2 - 1.0 mg/dl )"
    value_string = f"{value:.2f}"
    limit_a = 0.2
    limit_b = 1.0
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h,left_offset=20)
    return c,h - entity_height

# done
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
        value_string = f"{mcv:.1f}"
        limit_a = 78
        limit_b = 94
        c = mundane_things(c,1,text_string,mcv,value_string,limits_string,limit_a,limit_b,h)
        h -= entity_height 
        # mch
        text_string = "MCH"
        limits_string = "( 27 - 32 pg )"
        value_string = f"{mch:.1f}"
        limit_a = 27
        limit_b = 32
        c = mundane_things(c,1,text_string,mch,value_string,limits_string,limit_a,limit_b,h)
        h -= entity_height 
        # mchc
        text_string = "MCHC"
        limits_string = "( 32 - 36 g/dl )"
        value_string = f"{mchc:.1f}"
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
    return c, h - (entity_height * 1.5)


# done
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
    c = mundane_things(c,x,direct_text_string,direct_value,f"{direct_value:.2f}",direct_limits_string,0.2,0.4,h,left_offset=20)
    h -= entity_height
    c = mundane_things(c,x,indirect_text_strig,indirect_value,f"{indirect_value:.2f}",indirect_limits_string,0.2,0.6,h,left_offset=20)
    return c, h - entity_height

# done
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
        c.setFont(size_dict["font_name"][x],size_dict["limits_font"][x])
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

# done
def dengue_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    igm,igg,ns = values
    heading_string = "dengue test".upper()
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["value_point"][x]//1.2,h,heading_string)
    c.rect((size_dict["value_point"][x]//1.2)-5,h-5,cal_string_width(c,heading_string,size_dict["font_name"][x],size_dict["font_size"][x])+10,size_dict["font_size"][x]+5)
    h -= entity_height
    text_string = "IgM antibodies to Dengue Virus"
    c = mundane_things(c,x,text_string,igm,igm,"","","",h,if_limits=False,left_offset=20)
    h -= entity_height
    text_string = "IgG antibodies to Dengue Virus"
    c = mundane_things(c,x,text_string,igg,igg,"","","",h,if_limits=False,left_offset=20)
    h -= entity_height
    text_string = "NS1 antibodies to Dengue Virus"
    c = mundane_things(c,x,text_string,ns,ns,"","","",h,if_limits=False,left_offset=20)
    h -= entity_height
    c.drawString(size_dict["left_extreme"][x],h,"( Rapid Strip Method )")
    return c,h-entity_height

# done
def urine_analysis_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    drop,sugar,alb,bs,bp,fpus,spus,frbc,srbc,fcast,scast,fcryst,scryst,fep,sep = values
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["left_extreme"][x],h,"urine examination".upper())
    c.rect(size_dict["left_extreme"][x]-5,h-5,cal_string_width(c,"urine examination".upper(),size_dict["font_name"][x],size_dict["font_size"][x])+10,size_dict["font_size"][x]+5)
    h -= entity_height
    c.drawString(size_dict["left_extreme"][x],h,"Sugar")
    c.drawString((size_dict["value_point"][x]//1.5),h,f":  {sugar}")
    if drop == "long".upper(): 
        h -= (entity_height * 0.6)
        c.drawString(size_dict["left_extreme"][x],h,"Albumin")
        c.drawString((size_dict["value_point"][x]//1.5),h,f":  {alb}")
        h -= (entity_height * 0.6) 
        c.drawString(size_dict["left_extreme"][x],h,"Bile Salts")
        c.drawString((size_dict["value_point"][x]//1.5),h,f":  {bs}")
        h -= (entity_height * 0.6)
        c.drawString(size_dict["left_extreme"][x],h,"Bile Pigment")
        c.drawString((size_dict["value_point"][x]//1.5),h,f":  {bp}")
    else:
        c.drawString(size_dict["value_point"][x]//1.5 + cal_string_width(c,f":  {sugar}",size_dict["font_name"][x],size_dict["font_size"][x])+5,h,f", Albumin     :  {alb}")
        h -= (entity_height * 0.6)
        c.drawString(size_dict["left_extreme"][x],h,f"B.S,B.P")
        c.drawString(size_dict["value_point"][x]//1.5,h,f":  {bs}")
    h -= (entity_height * 0.6)
    c.drawString(size_dict["left_extreme"][x],h,"Micro")
    c.drawString((size_dict["value_point"][x]//1.5),h,f":  {fpus} - {spus} Pus Cells Present")
    h -= (entity_height * 0.6)
    if srbc == 0:
        c.drawString((size_dict["value_point"][x]//1.5),h,"  No RBC,")
        prev_string = "  No RBC,"
    else:
        c.drawString((size_dict["value_point"][x]//1.5),h,f": {frbc} - {srbc} RBC,")
        prev_string = f": {frbc} - {srbc} RBC,"
    if scast == 0:
        c.drawString((size_dict["value_point"][x]//1.5)+cal_string_width(c,prev_string,size_dict["font_name"][x],size_dict["font_size"][x]),h,"  No Casts,")
        prev_string += "  No Casts,"
    else:
        c.drawString((size_dict["value_point"][x]//1.5)+cal_string_width(c,prev_string,size_dict["font_name"][x],size_dict["font_size"][x]),h,f": {fcast} - {scast} Casts,")
        prev_string += f": {fcast} - {scast} Casts,"
    if scryst == 0:
        c.drawString((size_dict["value_point"][x]//1.5)+cal_string_width(c,prev_string,size_dict["font_name"][x],size_dict["font_size"][x]),h,"  No Crystals")
    else:
        c.drawString((size_dict["value_point"][x]//1.5)+cal_string_width(c,prev_string,size_dict["font_name"][x],size_dict["font_size"][x]),h,f": {fcryst} - {scryst} Casts,")
    h -= (entity_height * 0.6)
    c.drawString(size_dict["value_point"][x]//1.5,h,f"  {fep} - {sep} Epitheleal Cells Present")
    
    return c,h-entity_height

# done
def mantaux_canvas(c:canvas.Canvas,value:str,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    text_string = "mantoux test".upper()
    h -= 160
    c = mundane_things(c,x,text_string,value,value,"","","",h,if_limits=False)
    c.setFont(size_dict["font_name"][x],size_dict["limits_font"][x])
    c.drawString(size_dict["right_extreme"][x]-70-cal_string_width(c,"( After 72 Hrs )",size_dict["font_name"][x],size_dict["limits_font"][x]),h-20,"( After 72 Hrs )")
    return c,h-(entity_height + 20)

# done
def urine_preg_canvas(c:canvas.Canvas,value:str,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    h -= (entity_height * 5)
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["left_extreme"][x]//1.2,h,"Urine Test Report")
    c.rect((size_dict["left_extreme"][x]//1.2)-5,h-5,cal_string_width(c,"Urine Test Report",size_dict["font_name"][x],size_dict["font_size"][x])+10,size_dict["font_size"][x]+5)
    h -= (entity_height * 3)
    text_string = "Urine Pregnancy Test: "
    c = mundane_things(c,x,text_string,value,value,"","","",h,if_limits=False,left_offset=10)
    return c,h-entity_height

# done
def blood_for_aec_canvas(c:canvas.Canvas,value:int,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    text_string = "Blood for A.E.C Count"
    limits_string = "( 50 - 450 cells/cumm )"
    limit_a = 50
    limit_b = 450
    c = mundane_things(c,x,text_string,value,value,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

# done
def ra_factor_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    ra,dilutions = values
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,"RA FACTOR",ra,ra,"","","",h,if_limits=False)
    if ra == "positive".upper():
        c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
        limits_string = f"( 1 : {dilutions} dilutions )"
        c.drawString(size_dict["right_extreme"][x] - cal_string_width(c,limits_string,size_dict["font_name"][x],size_dict["font_size"][x]),h,limits_string)
    return c,h-entity_height

# done
def aso_titre_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    aso,dilutions = values
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,"ASO TITRE",aso,aso,"","","",h,if_limits=False)
    if aso == "positive".upper():
        c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
        limits_string = f"( 1 : {dilutions} dilutions )"
        c.drawString(size_dict["right_extreme"][x] - cal_string_width(c,limits_string,size_dict["font_name"][x],size_dict["font_size"][x]),h,limits_string)
    return c,h-entity_height

# done
def pt_aptt_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    pt_test,pt_inr,aptt_test = values
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    h -= (entity_height * 2)
    c.drawString(size_dict["value_point"][x]//1.2,h,"Prothrombin Time Test")
    c.rect((size_dict["value_point"][x]//1.2)-5,h-5,cal_string_width(c,"Prothrombin Time Test",size_dict["font_name"][x],size_dict["font_size"][x])+10,size_dict["font_size"][x]+5)
    h -= (entity_height * 1.5)
    c = mundane_things(c,x,"P.T. Test",pt_test,f"{pt_test:.1f} seconds","","","",h,if_limits=False)
    h -= (entity_height * 1.5)
    c = mundane_things(c,x,"P.T. Control",13.4,"13.4 seconds","","","",h,if_limits=False)
    h -= (entity_height * 1.5)
    c = mundane_things(c,x,"I N R",pt_inr,f"{pt_inr}","","","",h,if_limits=False)
    h -= (entity_height * 2.5)
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["value_point"][x]//1.5,h,"Activate Partial Thromboplastin Time")
    c.rect((size_dict["value_point"][x]//1.5)-5,h-5,cal_string_width(c,"Activate Partial Thromboplastin Time",size_dict["font_name"][x],size_dict["font_size"][x])+10,size_dict["font_size"][x]+5)
    h -= (entity_height * 2.5)
    c = mundane_things(c,x,"APTT Test",{aptt_test},f"{aptt_test:.1f} seconds","( Normal: 26 - 38 seconds )",26,38,h)
    h -= (entity_height * 2)
    c = mundane_things(c,x,"APTT Control",33.6,"33.6 seconds","( Normal 26 - 38 seconds )",26,38,h)
    return c,h-entity_height

# done
def sgot_canvas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height=18):
    text_string = "Aspirate Amino Transferase"
    limits_string = "( < 40 )"
    limit_a = 0
    limit_b = 40
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value,limits_string,limit_a,limit_b,h,left_offset=20)
    c.drawString(size_dict["left_extreme"][x]+150,h-16,"(sgot)".upper())
    return c,h-(entity_height + 10)

# done
def sgpt_canvas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height=18):
    text_string = "Alinine Amino Transferase"
    limits_string = "( < 40 )"
    limit_a = 0
    limit_b = 40
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value,limits_string,limit_a,limit_b,h,left_offset=20)
    c.drawString(size_dict["left_extreme"][x]+150,h-16,"(sgpt)".upper())
    return c,h-(entity_height + 10)

# done
def alkp_canvas(c:canvas.Canvas,value:int,page_size:str,h:int,entity_height=18):
    text_string = "Alkaline Phosphatase"
    limits_string = "( 37 - 147 )"
    limit_a = 37
    limit_b = 147
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value,limits_string,limit_a,limit_b,h,left_offset=20)
    c.drawString(size_dict["left_extreme"][x]+150,h-16,"( alkp )".upper())
    return c,h-(entity_height + 10)

# done
def uric_acid_cavnas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height=18):
    text_string = "Uric Acid"
    limits_string = "( 2.5 - 7.5 IU/L)"
    limit_a = 2.5
    limit_b = 7.5
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

# done
def malaria_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    mp,value,vivex,falci = values
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["left_extreme"][x],h,"Blood for M.P. Parasite")
    if value == "SHORT":
        c.drawString(size_dict["value_point"][x],h,f": {mp}  (kit method)".upper())
    else:
        c.drawString(size_dict["value_point"][x],h,f":  {mp}")
        h -= (entity_height)
        c.drawString(size_dict["left_extreme"][x],h,"Plasmodium Vivex")
        c.drawString(size_dict["value_point"][x],h,f":  {vivex}")
        h -= (entity_height)
        c.drawString(size_dict["left_extreme"][x],h,"Plasmodium Falciparum")
        c.drawString(size_dict["value_point"][x],h,f":  {falci}  (kit method)".upper())
    return c,h-(entity_height)

# done
def blood_urea_canvas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height=18):
    text_string = "Blood Urea"
    limits_string = "( 10 - 40 mg/dl )"
    limit_a = 10
    limit_b = 40
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

# done
def serum_creat_canvas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height=18):
    text_string = "Serum Creatinine"
    limits_string = "( 0.8 - 1.4 mg/dl )"
    limit_a = 0.8
    limit_b = 1.4
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,f"{value:.1f}",limits_string,limit_a,limit_b,h)
    return c,h-entity_height

# done
def fasting_sugar_canvas(c:canvas.Canvas,value:int,page_size:str,h:int,entity_height=18):
    text_string = "Blood Sugar ( Fasting )"
    value_string = value
    limits_string = "( 70 - 110 mg/dl )"
    limit_a = 70
    limit_b = 110
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

# done
def random_sugar_canvas(c:canvas.Canvas,value:int,page_size:str,h:int,entity_height=18):
    text_string = "Blood Sugar ( Random )"
    value_string = value
    limits_string = "( 70 - 140 mg/dl )"
    limit_a = 70
    limit_b = 140
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

# done
def lipid_profile_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    tc,hdl,ldl,vldl,tri = values
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["value_point"][x]//1.2,h,"total lipid profile".upper())
    c.rect((size_dict["value_point"][x]//1.2)-5,h-5,cal_string_width(c,"total lipid profile".upper(),size_dict["font_name"][x],size_dict["font_size"][x])+10,size_dict["font_size"][x]+5)
    h -= (entity_height + 10)
    text_string = "Total Cholesterol"
    limits_string = "Low Risk < 220.0 mg/dl"
    c = mundane_things(c,x,text_string,tc,tc,limits_string,limit_a=0,limit_b=250,h=h,left_offset=20)
    h -= 16
    c.drawString(size_dict["right_extreme"][x]-cal_string_width(c,"BorderLine - 220 - 239 mg/dl",size_dict["font_name"][x],size_dict["limits_font"][x]),h,"BorderLine - 220 - 239 mg/dl")
    h -= 16
    c.drawString(size_dict["right_extreme"][x]-cal_string_width(c,"High Risk > 130.0 mg/dl",size_dict["font_name"][x],size_dict["limits_font"][x]),h,"High Risk > 130.0 mg/dl")
    h -= (entity_height * 1.2)
    text_string = "High Density Lipoprotein"
    limits_string = "29 - 80 mg/dl"
    c = mundane_things(c,x,text_string,hdl,hdl,limits_string,limit_a=29,limit_b=80,h=h,left_offset=20)
    h -= 16
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["left_extreme"][x]+50,h,"(hdl)".upper())
    h -= (entity_height)
    text_string = "Low Density Lipoprotein"
    limits_string = "Desirable < 100"
    c = mundane_things(c,x,text_string,ldl,ldl,limits_string,limit_a=0,limit_b=130,h=h,left_offset=20)
    h -= 16
    c.drawString(size_dict["right_extreme"][x]-cal_string_width(c,"BorderLine - 110 - 129 mg/dl",size_dict["font_name"][x],size_dict["limits_font"][x]),h,"BorderLine - 220 - 239 mg/dl")
    h -= 16
    c.drawString(size_dict["right_extreme"][x]-cal_string_width(c,"High Risk > 130 mg/dl",size_dict["font_name"][x],size_dict["limits_font"][x]),h,"High Risk > 130 mg/dl")
    h -= (entity_height * 1.2)
    text_string = "Very Low Density Lipoprotein"
    limits_string = "7.0 - 35.0 mg/dl"
    c = mundane_things(c,x,text_string,vldl,vldl,limits_string,7.0,35.0,h,left_offset=20)
    h -= entity_height
    text_string = "Triglyceride (F)"
    limits_string = "Normal < 170.0 mg/dl"
    c = mundane_things(c,x,text_string,tri,tri,limits_string,0,170.0,h,left_offset=20)
    return c,h-entity_height


def liver_function_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    tb,db,sgot,sgpt,alkt = values
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["value_point"][x]//1.2,h,"liver function test".upper())
    c.rect((size_dict["value_point"][x]//1.2)-5,h-5,cal_string_width(c,"liver function test".upper(),size_dict["font_name"][x],size_dict["font_size"][x])+10,size_dict["font_size"][x]+5)
    h -= 30
    c,h = total_bilirubin_canvas(c,tb,page_size,h,entity_height)
    c,h = direct_and_indirect_bilirubin_canvas(c,[tb,db],page_size,h,entity_height)
    c,h = sgot_canvas(c,sgot,page_size,h,entity_height)
    c,h = sgpt_canvas(c,sgpt,page_size,h,entity_height)
    c,h = alkp_canvas(c,alkt,page_size,h,entity_height)
    return c,h-entity_height


# done
def serum_amylase_canvas(c:canvas.Canvas,value:float,page_size:str,h:int,entity_height=18):
    text_string = "Serum Amylase"
    limits_string = "( 30 - 110 U/L )"
    limit_a = 30
    limit_b = 110
    value_string = value
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,limits_string,limit_a,limit_b,h)
    return c,h-entity_height

# done
def serum_lipase_canvas(c: canvas.Canvas, value: float, page_size: str, h: int, entity_height=18):
    text_string = "Serum Lipase"
    limits_string = "( 23 - 300 U/L )"
    limit_a = 23
    limit_b = 300
    value_string = value
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c, x, text_string, value, value_string, limits_string, limit_a, limit_b, h)
    return c, h - entity_height

# done
def serum_protein_canvas(c: canvas.Canvas, value: float, page_size: str, h: int, entity_height=18):
    text_string = "Serum Protein"
    limits_string = "( 6.6 – 8.3 g/dl )"
    limit_a = 6.6
    limit_b = 8.3
    value_string = f"{value:.1f}"
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c, x, text_string, value, value_string, limits_string, limit_a, limit_b, h)
    return c, h - entity_height

# done
def serum_albumin_canvas(c: canvas.Canvas, value: float, page_size: str, h: int, entity_height=18):
    text_string = "Serum Albumin"
    limits_string = "( 3.5 – 5.0 g/dl )"
    limit_a = 3.5
    limit_b = 5.0
    value_string = f"{value:.1f}"
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c, x, text_string, value, value_string, limits_string, limit_a, limit_b, h)
    return c, h - entity_height

# done
def serum_globulin_canvas(c: canvas.Canvas, value: float, page_size: str, h: int, entity_height=18):
    text_string = "Serum Globulin"
    limits_string = "( 2.0 – 3.5 g/dl )"
    limit_a = 2.0
    limit_b = 3.5
    value_string = f"{value:.1f}"
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c, x, text_string, value, value_string, limits_string, limit_a, limit_b, h)
    return c, h - entity_height

# done
def serum_ag_ratio_canvas(c: canvas.Canvas, value: float, page_size: str, h: int, entity_height=18):
    text_string = "Serum A/G Ratio"
    limits_string = "( 0.9 – 2.0 )"
    limit_a = 0.9
    limit_b = 2.0
    value_string = f"{value:.1f}"
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c, x, text_string, value, value_string, limits_string, limit_a, limit_b, h)
    return c, h - entity_height

# done
def serum_sodium_canvas(c: canvas.Canvas, value: float, page_size: str, h: int, entity_height=18):
    text_string = "Serum Sodium"
    limits_string = "( 135 - 155 mmol/L )"
    limit_a = 135
    limit_b = 155
    value_string = value
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c, x, text_string, value, value_string, limits_string, limit_a, limit_b, h)
    return c, h - entity_height

# done
def serum_potassium_canvas(c: canvas.Canvas, value: float, page_size: str, h: int, entity_height=18):
    text_string = "Serum Potassium"
    limits_string = "( 3.5 - 5.5 mmol/L )"
    limit_a = 3.5
    limit_b = 5.5
    value_string = f"{value:.1f}"
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c, x, text_string, value, value_string, limits_string, limit_a, limit_b, h)
    return c, h - entity_height

# done
def serum_chloride_canvas(c: canvas.Canvas, value: float, page_size: str, h: int, entity_height=18):
    text_string = "Serum Chloride"
    limits_string = "( 98 - 107 mmol/L )"
    limit_a = 98
    limit_b = 107
    value_string = value
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c, x, text_string, value, value_string, limits_string, limit_a, limit_b, h)
    return c, h - entity_height

# done
def serum_calcium_canvas(c: canvas.Canvas, value: float, page_size: str, h: int, entity_height=18):
    text_string = "Serum Calcium"
    limits_string = "( 8.5 - 10.5 mmol/L )"
    limit_a = 8.5
    limit_b = 10.5
    value_string = f"{value:.1f}"
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c, x, text_string, value, value_string, limits_string, limit_a, limit_b, h)
    return c, h - entity_height

# done
def electrolytes_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height = 18):
    sod,pot,chl,cal = values
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c.drawString(size_dict["value_point"][x],h,"electrolytes".upper())
    h -= entity_height
    c,h = serum_sodium_canvas(c,sod,page_size,h,entity_height)
    c,h = serum_potassium_canvas(c,pot,page_size,h,entity_height)
    c,h = serum_chloride_canvas(c,chl,page_size,h,entity_height)
    c,h = serum_calcium_canvas(c,cal,page_size,h,entity_height)
    return c,h - entity_height

# done
def vdrl_canvas(c:canvas.Canvas,value:str,page_size:str,h:int,entity_height=18):
    text_string = "v.d.r.l".upper()
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value,"","","",h,if_limits=False)
    return c,h-entity_height

# done
def hbsag_canvas(c:canvas.Canvas,value:str,page_size:str,h:int,entity_height=18):
    text_string = "HBsAg"
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value,"","","",h,if_limits=False)
    return c,h-entity_height

# done
def hiv_canvas(c:canvas.Canvas,value:str,page_size:str,h:int,entity_height=18):
    text_string = "HIV I & II Antibodies Test".upper()
    value_string = f"{value}  (Tridot Method)"
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,"","","",h,if_limits=False,left_offset=22)
    return c,h-entity_height

# done
def hcv_canvas(c:canvas.Canvas,value:str,page_size:str,h:int,entity_height=18):
    text_string = "HCV I & II Antibodies Test".upper()
    value_string = f"{value}  (Tridot Method)"
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,text_string,value,value_string,"","","",h,if_limits=False,left_offset=25)
    return c,h-entity_height

# done
def bt_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    bt_min,bt_sec = values
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,"BT",bt_min,f"{bt_min} : {bt_sec} sec","","","",h,if_limits=False)
    return c,h

# done
def ct_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    ct_min,ct_sec = values
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c = mundane_things(c,x,"BT",ct_min,f"{ct_min} : {ct_sec} sec","","","",h,if_limits=False)
    return c,h

# done
def semen_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    val,lig,ph,count,mot,morph,fwbc,swbc,frbc,srbc,comments = values
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["value_point"][x]-20,h,"semen analysis".upper())
    c.rect(size_dict["value_point"][x] - 25,h-5,cal_string_width(c,"semen analysis".upper(),size_dict["font_name"][x],size_dict["font_size"][x])+10,size_dict["font_size"]+5)
    h -= entity_height
    c = mundane_things(c,x,"Volume",float(val),f"{val:.1f}","( 1.5 - 5.0 ml )",1.5,5.0,h)
    h -= entity_height
    c = mundane_things(c,x,"Liquefaction time",lig,lig,"( with in 20 mts )",0,20,h)
    h -= entity_height
    c = mundane_things(c,x,"PH",float(ph),f"{ph:.1f}","( > 7.0 )",7,14,h)
    h -= entity_height
    c = mundane_things(c,x,"Spermatozoa Count",count,count,"(60-150 millions/ml)",60,150,h)
    h -= entity_height
    c = mundane_things(c,x,"Sperm motility",mot,mot,"( > 60% motile forms)",60,100,h)
    h -= entity_height
    c = mundane_things(c,x,"Sperm morphology",morph,morph,"( > 70% normal sperms)",70,100)
    h -= entity_height
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["left_extreme"][x],h,"other findings".upper())
    h -= entity_height
    c.drawString(size_dict["left_extreme"][x],h,"W.B.C/h.p.t")
    if swbc == 0:
        c.drawString(size_dict["value_point"][x],h,f":  NIL")
    else:
        c.drawString(size_dict["value_point"][x],h,f":  {fwbc} - {swbc}")
    h -= entity_height
    c.drawString(size_dict["left_extreme"][x],h,"R.B.C/h.p.t")
    if srbc == 0:
        c.drawString(size_dict["value_point"][x],h,f":  NIL")
    else:
        c.drawString(size_dict["value_point"][x],h,f":  {frbc} - {srbc}")
    h -= entity_height
    c.drawString(size_dict["left_extreme"][x],h,"Comments")
    c.drawString(size_dict["value_point"][x],h,f"Suggestive of ")
    h -= entity_height
    c.drawString(size_dict["left_extreme"][x],h,comments)
    return c,h-entity_height

def x_ray_canvas(c:canvas.Canvas,value,page_size:str,h:int,entity_height=18):
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["value_point"][x]//1.5,h,"x-ray chest pa-view".upper())
    h -= (entity_height * 2)
    c.drawString(size_dict["value_point"][x]//2,h,"Rest of lung fields are normal.")
    h -= entity_height
    c.drawString(size_dict["value_point"][x]//2,h,"Both hila normal in density.")
    h -= entity_height
    c.drawString(size_dict["value_point"][x]//2,h,"Cardiac shape are normal.")
    h -= entity_height
    c.drawString(size_dict["value_point"][x]//2,h,"Both CP angles are clear.")
    h -= entity_height
    c.drawString(size_dict["value_point"][x]//2,h,"Bony cage and soft tissues are normal.")
    h -= entity_height
    c.drawString(size_dict["value_point"][x]//2,h,"Opinion: NORMAL")
    h -= entity_height
    c.drawString(size_dict["value_point"][x]//2,h,"For clinical correlation.")
    h -= entity_height
    return c, h - entity_height

def bill_canvas(c:canvas.Canvas,values:list,page_size:str,h:int,entity_height=18):
    test_names,test_prices = values
    if page_size == "SMALL/A5":
        x = 0
    else:
        x = 1
        entity_height += 5
    h -= (entity_height * 3)
    c.setFont(size_dict["font_name"][x],size_dict["font_size"][x])
    c.drawString(size_dict["value_point"][x]//1.2,h,"blood test bill".upper())
    c.rect((size_dict["value_point"][x]//1.2)-5,h-5,cal_string_width(c,"blood test bill".upper(),size_dict["font_name"][x],size_dict["font_size"][x])+10,size_dict["font_size"][x]+5)
    h -= (entity_height * 2)
    for i,(test,price) in enumerate(zip(test_names,test_prices)):
        c.drawString(size_dict["left_extreme"][x],h,f"{i+1}.")
        c.drawString(size_dict["value_point"][x]//2,h,test.upper())
        c.drawString(size_dict["right_extreme"][x]-50,h,f":  {price} /-")
        h -= entity_height
    total_sum = 0
    for i in test_prices:
        total_sum += int(i)
    c.line(size_dict["right_extreme"][x]-120,h,size_dict["right_extreme"][x],h)
    h -= entity_height
    c.drawString(size_dict["right_extreme"][x]-120,h,f"Total Amount:  {total_sum}")
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
    "DENGUE":dengue_canvas,
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
    "Liver Function Test":liver_function_canvas,
    "Mantaoux":mantaux_canvas,
    "Blood for AEC Count":blood_for_aec_canvas,
    "BT":bt_canvas,
    "CT":ct_canvas,
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
    "Serum Potassium":serum_potassium_canvas,
    "Serum Chloride":serum_chloride_canvas,
    "Serum Calcium":serum_calcium_canvas,
    "Electrolytes":electrolytes_canvas,
    "V.D.R.L":vdrl_canvas,
    "HBsAg":hbsag_canvas,
    "HIV I & II Antibodies Test":hiv_canvas,
    "HCV I & II Antibodies Test":hcv_canvas,
    "Semen Analysis":semen_canvas,
    "XRAY Opinion":x_ray_canvas,
    "BILL":bill_canvas
}

report_canvas_values_dict = {
    "Hb":"hb",
    "Total Count (TC)":"tc_count",
    "Platelet Count":"plt_count",
    "Differential Count (DC)":"dc_count",
    "Widal":"Widal",
    "CRP":"crp",
    "ESR":"esr",
    "Malaria":"malaria-full",
    "DENGUE":"dengue-test",
    "Full CBP":"cbp",
    "Blood Group":"blood-group",
    "Total Bilirubin":"total-bili",
    "Direct & Indirect Bilirubin":"all_bili",
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
    "Liver Function Test":"liver-function-test",
    "Mantaoux":"mantoux_test",
    "Blood for AEC Count":"aec-count",
    "BT":"full-bt",
    "CT":"full-ct",
    "RA Factor":"full-ra-factor",
    "ASO Titre":"full-aso-titre",
    "PT APTT":"full-pt-aptt",
    "Serum Amylase":"serum_amylase",
    "Serum Lipase":"serum_lipase",
    "Serum Protein":"serum_protein",
    "Serum Albumin":"serum_albumin",
    "Serum Globulin":"serum_globulin",
    "Serum A/G Ratio":"serum_ag_ratio",
    "Serum Sodium":"serum_sodium",
    "Serum Potassium":"serum_potassium",
    "Serum Chloride":"serum_chloride",
    "Serum Calcium":"serum_calcium",
    "Electrolytes":"electrolytes",
    "V.D.R.L":"vdrl",
    "HBsAg":"hbsag",
    "HIV I & II Antibodies Test":"hiv_ant",
    "HCV I & II Antibodies Test":"hcv_ant",
    "Semen Analysis":"full-semen",
    "XRAY Opinion":"x-ray-opinion",
    "BILL":"total-bill"
}

def create_pdf(serial_no,top_space,report_details_space,page_size,temp_dict,tests,df):
    collection_date = get_df_item(serial_no,"Date",df)
    collection_time = get_df_item(serial_no,"Time",df)
    patient_name = get_df_item(serial_no,"Patient Name",df)
    patient_age = get_df_item(serial_no,"Patient Age",df)
    patient_age_group = get_df_item(serial_no,"Age Group",df)
    patient_gender = get_df_item(serial_no,"Gender",df)
    patient_specimen  = "Blood"
    if ("Urine Analysis" in tests) | ("Urine Pregnancy" in tests):
        patient_specimen += " & Urine"
    doctor_name = get_df_item(serial_no,"Reference By",df)
    patient_details_space = 18
    frmt_time = "-".join(collection_date.split("-")[::-1])
    patient_name_save = patient_name.replace(".","_")
    year_extract,month_extract,day_extract = collection_date.split("-")
    base_dir = "assets"
    year_dir = os.path.join(base_dir,year_extract)
    month_dir = os.path.join(year_dir,month_extract)
    day_dir = os.path.join(month_dir,day_extract)
    os.makedirs(day_dir,exist_ok=True)
    filename = os.path.join(day_dir,f"{patient_name_save}__{" ".join(tests)}.pdf")
    if page_size == "SMALL/A5":
        c = canvas.Canvas(filename,pagesize=portrait(A5))
        _, small_page_height = A5
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
        h = 400-top_space
        for t in tests:
            c,h = reports_canvas_dict[t](c,temp_dict[report_canvas_values_dict[t]],page_size,h,report_details_space)
        c.save()
    else:
        c = canvas.Canvas(filename,pagesize=portrait(A4))
        _,big_page_height = A4    
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
        h = 600  - top_space
        for t in tests:
            c,h = reports_canvas_dict[t](c,temp_dict[report_canvas_values_dict[t]],page_size,h,report_details_space)
        c.save()
    return filename


@callback(
    Output("report-preview","children"),
    Input("submit-report-button","n_clicks"),
    [
        State("patients-dropdown","value"),
        State({"type":"dynamic-input","name":ALL},"id"),
        State({"type":"dynamic-input","name":ALL},"value"),
        State("page-size-dropdown","value"),
        State("top-slider","value"),
        State("slider","value"),
        State("date-pick-reports","date")
    ]
)
def submit_and_preview_report(
    n_clicks,
    patients_sno:str,
    input_ids:dict,
    input_values:list,
    page_size:str,
    top_slider_value:int,
    slider_value:int,
    date:str
):
    global tests_names
    if not n_clicks:
        raise PreventUpdate
    if ctx.triggered_id == "submit-report-button":
        year,month,day = date.split("-")
        conn = duckdb.connect(f"assets/{year}/{month}/{day}/{date.replace("-","_")}.duckdb")
        tests_names = json.loads(conn.query(f"select * from patients where id = {patients_sno}").df()["tests"].item())
        conn.close()
        name_pattern = re.compile(r"bill-\d+-name")
        value_pattern = re.compile(r"bill-\d+-value")
        bill_names_list = []
        bill_values_list = []
        temp_dict = {}
        for id,value in zip(input_ids,input_values):
            if id['name'] in ['polymo','lympho','esino']:
                temp_dict["dc_count"] = temp_dict.get("dc_count",[])
                temp_dict["dc_count"].append(value)
                continue
            if ("Widal" in tests_names) & (id['name'] in ['widal','widal-form','widal-ot-react','widal-ht-react']):
                temp_dict['Widal'] = temp_dict.get('Widal',[])
                temp_dict['Widal'].append(value)
                continue
            if ("Malaria" in tests_names) & (id['name'] in ["malaria-mp","malaria-vivex","malaria-falci","malaria-test"]):
                temp_dict["malaria-full"] = temp_dict.get("malaria-full",[])
                temp_dict["malaria-full"].append(value)
                continue
            if ("Direct & Indirect Bilirubin" in tests_names) & (id["name"] in ["total-bili","direct-bili"]):
                temp_dict["all_bili"] = temp_dict.get("all_bili",[])
                temp_dict["all_bili"].append(value)
                continue
            if("Full CBP" in tests_names) & (id['name'] in ['hb','rbc-count','hct','tc_count','plt_count','esr','polymo','lympho','esino']):
                temp_dict["cbp"] = temp_dict.get("cbp",[])
                temp_dict["cbp"].append(value)
                continue
            if ("Heamogram" in tests_names) & (id["name"] in ['hb','rbc-count','hct','tc_count','plt_count','mcv','mch','mchc','esr','polymo','lympho','esino','heamo-rbc','blast-cells','platelet-opinion','hemoparasites-opinion','total-opinion']):
                temp_dict["heamo"] = temp_dict.get("heamo",[])
                temp_dict["heamo"].append(value)
                continue
            if ("HBA1C" in tests_names) & (id['name'] in ['hba1c_first','hba1c_second','hba1c_dropdown']):
                temp_dict["hba1c"] = temp_dict.get("hba1c",[])
                temp_dict["hba1c"].append(value)
                continue
            if ("Electrolytes" in tests_names) & (id['name'] in ["serum_sodium","serum_potassium","serum_chloride","serum_calcium"]):
                temp_dict["electrolytes"] = temp_dict.get("electrolytes",[])
                temp_dict["electrolytes"].append(value)
                continue
            if ("Lipid Profile" in tests_names) & (id['name'] in ['lipid_tc','lipid_hdl','lipid_ldl','lipid_vldl','lipid_tri']):
                temp_dict["full-lipid"] = temp_dict.get("full-lipid",[])
                temp_dict["full-lipid"].append(value)
                continue
            if ("Liver Function Test" in tests_names) & (id['name'] in ['total-bili','direct-bili','sgot','sgpt','alkp']):
                temp_dict["liver-function-test"] = temp_dict.get("liver-function-test",[])
                temp_dict["liver-function-test"].append(value)
                continue
            if ("DENGUE" in tests_names) & (id['name'] in ['dengue_igm','dengue_igg','dengue_ns']):
                temp_dict["dengue-test"] = temp_dict.get("dengue-test",[])
                temp_dict["dengue-test"].append(value)
                continue
            if ("RA Factor" in tests_names) & (id['name'] in ['ra-factor','ra-dilutions']):
                temp_dict["full-ra-factor"] = temp_dict.get("full-ra-factor",[])
                temp_dict["full-ra-factor"].append(value)
                continue
            if ("ASO Titre" in tests_names) & (id['name'] in ['aso_titre','aso_titre_dilutions']):
                temp_dict["full-aso-titre"] = temp_dict.get("full-aso-titre",[])
                temp_dict["full-aso-titre"].append(value)
                continue
            if ("Urine Analysis" in tests_names) & (id['name'] in ['urine-drop','urine_sugar','urine_albumin','urine_bs','urine_bp','urine_first_pus','urine_second_pus','urine_first_rbc','urine_second_rbc','urine_first_casts','urine_second_casts','urine_first_crystals','urine_second_crystals','urine_first_ep','urine_second_ep']):
                temp_dict["full-urine"] = temp_dict.get("full-urine",[])
                temp_dict["full-urine"].append(value)
                continue
            if ("PT APTT" in tests_names) & (id['name'] in ['pt_test','pt_inr','aptt_test']):
                temp_dict["full-pt-aptt"] = temp_dict.get("full-pt-aptt",[])
                temp_dict["full-pt-aptt"].append(value)
                continue
            if ("BT" in tests_names) & (id['name'] in ['bt_min','bt_sec']):
                temp_dict["full-bt"] = temp_dict.get("full-bt",[])
                temp_dict["full-bt"].append(value)
                continue
            if ("CT" in tests_names) & (id['name'] in ['ct_min','ct_sec']):
                temp_dict["full-ct"] = temp_dict.get("full-ct",[])
                temp_dict["full-ct"].append(value)
                continue
            if ("Semen Analysis" in tests_names) & (id['name'] in ['semen-volume','semen-liq','semen-ph','semen-count','semen-mot','semen-morph','semen-wbc-first','semen-wbc-second','semen-rbc-first','semen-rbc-second','semen-comments']):
                temp_dict["full-semen"] = temp_dict.get("full-semen",[])
                temp_dict["full-semen"].append(value)
                continue
            if ("BILL" in tests_names):
                temp_dict["total-bill"] = temp_dict.get("total-bill",[])
                if name_pattern.match(id['name']):
                    bill_names_list.append(value)
                if value_pattern.match(id['name']):
                    bill_values_list.append(value)
                temp_dict["total-bill"] = [bill_names_list,bill_values_list]
            temp_dict[id['name']] = value
        temp_dict["page-size"] = page_size
        zoom_levels = {
        "BIG/A4": 1.0,
        "SMALL/A5": 1.0
        }
        df = pd.read_csv(f"assets/all_files/{date.replace("-","_")}.csv",dtype=dtype_map)
        zoom_level = zoom_levels.get(page_size,1.0)
        cache_buster = f"?v={int(time.time())}"
        filename = create_pdf(patients_sno,top_slider_value,slider_value,page_size,temp_dict,tests_names,df)
        return html.Iframe(
            src=f"{filename}{cache_buster}",
            style={
                "width":"100%",
                "height":"1150px",
                "transform":f"scale({zoom_level})",
                "transform-origin":"0 0"
            }
        )

register_page(
    "ReportsPage",
    path="/reports",
    layout=layout
)