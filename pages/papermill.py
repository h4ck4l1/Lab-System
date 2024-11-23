import io
import numpy as np
from dash import register_page,callback,Output,Input,html,dcc,State
from dash.exceptions import PreventUpdate
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import portrait,A4
from reportlab.pdfbase.pdfmetrics import registerFont,getRegisteredFontNames
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader,PdfWriter



registerFont(TTFont("Arial-regular","assets/Arial/arial.ttf"))
registerFont(TTFont("Arial-Bold","assets/Arial/arialbd.ttf"))
registerFont(TTFont("Arial-Bold","assets/Arial/arialbd.ttf"))
registerFont(TTFont("cbs","assets/schlbkbi.ttf"))




layout = html.Div(
    [
        html.Div(html.H1("papermil health reports".upper(),className="page-heading"),className="heading-divs"),
        html.Div(["Enter Name: ",dcc.Input(id="papermill-name",type="text",placeholder="Enter Name..",style=dict(width="500px",height="75px",fontSize=35,position="relative",left="110px",))],style=dict(padding="50px")),
        html.Div(["Enter Age: ",dcc.Input(id="papermill-age",type="number",placeholder="Enter Age...",style=dict(width="200px",height="75px",fontSize=35,position="relative",left="120px"))],style=dict(padding="50px")),
        html.Div("Enter Blood Group: ",style=dict(position="relative",left="50px")),
        html.Div([dcc.Dropdown(options=["O POSITIVE","A POSITIVE","B POSITIVE","AB POSITIVE","O NEGATIVE","A NEGATIVE","B NEGATIVE","AB NEGATIVE"],id="papermill-blood")],style=dict(width="300px",height="50px",fontSize=25,position="relative",left="280px",bottom="25px")),
        html.Div(["Enter Date: ",dcc.Input(id="papermill-date",type="text",placeholder="Enter Date...",style=dict(width="200px",height="75px",fontSize=35,position="relative",left="110px"))],style=dict(padding="50px")),
        html.Div(["Enter Patients ID: ",dcc.Input(id="papermill-id",type="number",placeholder="Enter Patients Id",style=dict(width="300px",height="75px",fontSize=35,position="relative",left="40px"))],style=dict(padding="50px")),
        html.Button("submit".upper(),id="papermill-submit-button",style=dict(position="relative",fontSize=30,borderRadius="10px",backgroundColor="cyan",bottom="20px",left="300px",height="100px",width="200px")),
        html.Div(html.H1("papermill report preview".upper(),className="page-heading"),className="heading-divs"),
        html.Div("Submit details to preview..",id="papermill-output-container",style=dict(padding="50px",border="10px solid #4b70f5",marginTop="50px",width="75%",height="2100px",alignItems="center"))
    ],
    className="subpage-content"
)

d = None
top_height = None


def make_pdf(pt_name:str,pt_age:int,input_date:str,pt_id:int,pt_blood_group:str):
    global d,top_height
    input_date = " / ".join(input_date.split("/"))
    pt_height = np.random.randint(low=160,high=176,size=1).item()
    pt_weight = np.random.randint(low=60,high=86,size=1).item()
    reader = PdfReader("assets/full_rotated.pdf")
    writer = PdfWriter()
    pt_name = pt_name.upper()
    packet = io.BytesIO()
    d = canvas.Canvas(packet,pagesize=portrait(A4))
    page_width, page_height = A4
    font_name = "cbs"
    d.setFont(font_name,14)
    pt_height = np.random.randint(low=160,high=176,size=1).item()
    pt_weight = np.random.randint(low=60,high=86,size=1).item()

    # details 
    font_size = 14
    details_space = 25
    left_extreme = 540
    starting_point = 62
    top_height = 735
    d.drawString(starting_point,top_height,f"Pt. Name: Mr. {pt_name}")
    d.drawString(starting_point,top_height-details_space,f"Gender:   Male")
    age_string = f"Age :   {pt_age} Y"
    d.drawString(left_extreme - d.stringWidth(age_string,font_name,font_size),top_height-details_space,age_string)
    d.drawString(starting_point,top_height - 2 * details_space,"Ref.Dr.By:  Medical officer, APPMILLS")
    d.drawString(starting_point,top_height - 3 * details_space,"Specimen: Blood")
    date_string = f"Date:   {input_date.replace("/","-")}"
    d.drawString(left_extreme - d.stringWidth(date_string,font_name,font_size), top_height - 3 * details_space,date_string)
    d.setDash()
    d.line(43,top_height - 4 * details_space,page_width-43,top_height - 4 * details_space)
    d.setFont(font_name,12)
    d.drawString(43,top_height - 4.5 * details_space,"Test")
    d.drawString(240,top_height - 4.5 * details_space,"Value")
    reference_string = "Reference Range"
    d.drawString(left_extreme - d.stringWidth(reference_string,font_name,12),top_height - 4.5 * details_space,reference_string)
    d.line(43,top_height - 4.8 * details_space,page_width - 43, top_height - 4.8 * details_space)

    # tests
    value_point = 240
    top_height -= (6 * details_space)
    details_space = 25
    d.setFont(font_name,font_size)

    def calc_width(text_string:str):
        return left_extreme - d.stringWidth(text_string,font_name,font_size)

    def draw_section(name_string,value_string,limits_string=None):
        global top_height,d
        d.drawString(starting_point,top_height,name_string)
        d.drawString(value_point,top_height,value_string)
        if limits_string:
            d.drawString(calc_width(limits_string),top_height,limits_string)
        top_height -= details_space

    draw_section(
        "Heamoglobin",
        f":   {np.random.uniform(low=12.0,high=14.0,size=1).item():.1f}",
        "( 11. 0 - 16.8 Grams %)"
    )

    draw_section(
        "Total WBC Count",
        f":  {str(np.random.uniform(low=7.0,high=9.0,size=1).item().__round__(1)).replace(".",",")}00",
        "( 5,000 - 10,000 Cells/cumm )"
    )

    draw_section(
        "E.S.R",
        ":  05",
        "( 02 - 10mm / 1 hour )"
    )


    dc_string = "Differential Count"
    d.drawString(starting_point,top_height,dc_string)
    d.line(starting_point,top_height-6,starting_point+135,top_height - 6)
    d.drawString(starting_point + 100,top_height - 35,"Polymorphs")
    d.drawString(starting_point + 100,top_height - 60,"Lymphocytes")
    d.drawString(starting_point + 100,top_height - 85,"Esinophils")
    polymo = int(np.random.uniform(low=56,high=63,size=1).item())
    if polymo <= 60:
        l_limit = 37
        h_limit = 39
    else:
        l_limit = 30
        h_limit = 35
    lympho = int(np.random.uniform(low=l_limit,high=h_limit,size=1).item())
    mono = 100 - (polymo + lympho)
    d.drawString(starting_point + 280,top_height - 35,f":  {polymo}%")
    d.drawString(starting_point + 280,top_height - 60,f":  {lympho}%")
    d.drawString(starting_point + 280,top_height - 85,f":  {mono if mono >= 10 else "0"+str(mono)}%")
    top_height -= 110

    value_point += 50

    draw_section(
        "blood group".upper(),
        f":  * {pt_blood_group.replace(" "," * ")}"
    )

    draw_section(
        "V.D.R.L",
        f":  non-reactive".upper()
    )

    draw_section(
        "HBsAg",
        f":  non-reactive".upper()
    )

    draw_section(
        "HIV I & II Antibodies Test",
        f":  non-reactive".upper()
    )

    draw_section(
        "HCV I & II Antibodies Test",
        f":  non-reactive".upper()
    )

    draw_section(
        "Blood Sugar(Random)",
        f":  {int(np.random.uniform(low=85,high=100,size=1).item())} mg/dl",
        "( 70 - 140 mg/dl )"
    )

    d.rect(starting_point-2,top_height-18,starting_point+110,18)
    d.drawString(starting_point,top_height-14,"urine examination".upper())
    top_height -= 40
    draw_section(
        "Sugar",
        ":  NIL"
    )
    draw_section(
        "Albumin",
        ": NIL"
    )
    draw_section(
        "Micro",
        ":  0-1 Pus Cells Present."
    )
    d.drawString(value_point,top_height,"  No RBC, No Casts, No Cystals.")
    top_height -= details_space
    d.drawString(value_point,top_height,"  1-2 Epitheleal Cells Present.")
    d.save()
    packet.seek(0)
    writer.add_page(PdfReader(packet).pages[0])
    font_name = "Arial-Bold"
    for i,page in enumerate(reader.pages):
        packet = io.BytesIO()
        c = canvas.Canvas(packet)
        page_width = float(page.mediabox.width)
        page_height = float(page.mediabox.height)
        c.setPageSize((page_width,page_height))
        if i == 0:
            c.setFont(font_name,14)
            c.drawString(480,page_height-250,input_date)
            c.drawString(270,page_height-352,pt_name)
        if i == 1:
            c.setFont(font_name,14)
            c.drawString(160,page_height-127,pt_name)
            c.setFont(font_name,12)
            c.drawString(160,page_height-140,f"{pt_age} Y / M")
            c.drawString(160,page_height-155,input_date)
        if i == 2:
            c.setFont(font_name,11)
            c.drawString(48,page_height-116,f"Name: {pt_name}")
            c.setFont(font_name,9)
            c.drawString(48,page_height-126,f"{pt_age}Y/Male/Ht {pt_height}cms/{pt_weight}Kgs/Non-Smoker")
            c.drawString(330,page_height-127,f"Dt: {"".join(input_date.split(" "))}")
        if i == 3:
            c.setFont(font_name,11)
            c.drawString(40,page_height-118,f"Name: {pt_name}")
            c.setFont(font_name,9)
            c.drawString(40,page_height-128,f"{pt_age}Y/Male/Ht {pt_height}cms/{pt_weight}Kgs/Non-Smoker")
            c.drawString(323,page_height-129,f"Dt: {"".join(input_date.split(" "))}")
        if i == 4:
            c.setFont(font_name,11)
            c.drawString(170,page_height-157,str(pt_id))
            c.drawString(170,page_height-173,pt_name)
            c.setFont(font_name,15)
            c.drawString(450,page_height-157,input_date)
            c.drawString(450,page_height-171,f"{pt_age} Y / M")
        c.save()
        packet.seek(0)
        new_pdf = PdfReader(packet)
        overlay_page = new_pdf.pages[0]
        page.merge_page(overlay_page)
        writer.add_page(page)



    with open(f"assets/papermill_reports/{pt_name}.pdf","wb") as f:
        writer.write(f)

    return f"assets/papermill_reports/{pt_name}.pdf"


@callback(
    Output("papermill-output-container","children"),
    Input("papermill-submit-button","n_clicks"),
    [
        State("papermill-name","value"),
        State("papermill-age","value"),
        State("papermill-date","value"),
        State("papermill-id","value"),
        State("papermill-blood","value")
    ]
)
def papermill_report_output(n_clicks,*vals):
    if not n_clicks:
        raise PreventUpdate
    if n_clicks:
        file_name = make_pdf(*vals)
        return html.Iframe(
            src=file_name,
            style=dict(width="95%",height="2000px")
        )


register_page(
    "Papermill",
    layout=layout,
    path="/papermill"
)