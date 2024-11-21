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
    html.Div(dcc.Dropdown(["positive".upper(),"negative".upper()],"negative".upper(),id={'type':'dynamic-input','name':'ra-factor'}),style=dict(position="relative",width="200px",left="300px",bottom="25px")),
    html.Div(" ( 1 : ",style={**limits_style,"bottom":"50px"}),
    dcc.Input(id={'type':'dynamic-input','name':'ra-dilutions'},type="number",placeholder="None",style={**limits_style,"bottom":"75px","left":"620px","width":"100px"}),
    html.Div(" dilutions ) ",style={**limits_style,"left":"730px","bottom":"95px"})
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



def hb_canvas(c:canvas.Canvas,hb_value:str,r_space):
    c.drawString(62,)
    return c



def create_pdf(serial_no,page_size,details_dict):

    global copy_df,all_patients_values
    def cal_string_width(total_string,font_name,font_size):
        return c.stringWidth(total_string,font_name,font_size)
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
        c.setDash(6,3)
        c.setFont(font_name,5)
        for x in range(0,int(page_width),10):
            if x % 20 == 0:
                c.line(x,page_height,x,0)
                c.drawString(x+2,page_height-30,str(x))
        for x in range(0,int(page_height),10):
            if x % 20 == 0:
                c.line(0,x,page_width,x)
                c.drawString(30,x+2,str(x))
        c.setFont(font_name,font_size)
        c.drawString(42,page_height-75,f"Pt. Name : {patient_name.upper()}")
        c.drawString(42,page_height-(75 + patient_details_space),f"Gender : {patient_gender}")                  
        age_string = f"Age: {patient_age} {patient_age_group}"
        c.drawString(375-cal_string_width(age_string,font_name,font_size),page_height-(75 + patient_details_space),age_string)     # s
        c.drawString(42,page_height-(75 + 2*patient_details_space),f"Ref.Dr.By. : {doctor_name}")                                                # 99 + 24
        c.drawString(42,page_height-(75 + 3*patient_details_space),f"Serial No: 000{patient_serial_no}")
        time_string = f"Collection Time: {collection_time}"
        c.drawString(375-cal_string_width(time_string,font_name,font_size),page_height-(75 + 3*patient_details_space),time_string)        # s
        c.drawString(42,page_height-(75 + 4*patient_details_space),f"Specimen: {patient_specimen}")
        date_string = f"Date: {frmt_time}"
        c.drawString(375-cal_string_width(date_string,font_name,font_size),page_height-(75 + 4*patient_details_space),date_string)                         # s
        c.setDash()
        c.line(40,page_height-(75 + 4 * patient_details_space) - 5,379,page_height-(75 + 4 * patient_details_space) - 5)
        c.line(40,page_height-(75 + 4 * patient_details_space) - 18,379,page_height-(75 + 4 * patient_details_space) - 20)
        c.setFont(font_name,8)
        c.drawString(42,page_height-(75 + 4 * patient_details_space) - 15,"test".upper())
        c.drawString(190,page_height-(75 + 4 * patient_details_space) - 15,"value".upper())
        reference_string = "reference range".upper()
        c.drawString(375-cal_string_width(reference_string,font_name,8),page_height-(75 + 4 * patient_details_space) - 15,reference_string)
        c.save()
    else:
        pass
    print(all_patients_values)
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
        temp_dict = {id['name']: value for id,value in zip(input_ids,input_values)}
        all_patients_values[patients_sno] = {**all_patients_values[patients_sno],**temp_dict}
        all_patients_values[patients_sno] = {**all_patients_values[patients_sno],'page_size':page_size_value}
        return all_patients_values
    


@callback(
    Output("report-preview","children"),
    Input("preview-button","n_clicks"),
    [
        State("patients-dropdown","value"),
        State("page-size-dropdown","value")
    ]
)
def preview_report(n_clicks,patient_sno,page_size):
    global all_patients_values
    if not n_clicks:
        raise PreventUpdate
    if n_clicks:
        filename = create_pdf(patient_sno,page_size,all_patients_values)
        return html.Iframe(
            src=filename,
            style=dict(width="100%",height="1650px")
        )


register_page(
    "Reports",
    layout=layout,
    path="/reports"
)