import io
import numpy as np
from dash import register_page,callback,Output,Input,html,dcc,State
from dash.exceptions import PreventUpdate
from reportlab.pdfgen import canvas
from reportlab.pdfbase.pdfmetrics import registerFont,getRegisteredFontNames
from reportlab.pdfbase.ttfonts import TTFont
from PyPDF2 import PdfReader,PdfWriter



registerFont(TTFont("Arial-regular","assets/Arial/arial.ttf"))
registerFont(TTFont("Arial-Bold","assets/Arial/arialbd.ttf"))




layout = html.Div(
    [
        html.Div(html.H1("papermil health reports".upper(),className="page-heading"),className="heading-divs"),
        html.Div(["Enter Name: ",dcc.Input(id="papermill-name",type="text",placeholder="Enter Name..",style=dict(width="500px",height="75px",fontSize=35,position="relative",left="110px",))],style=dict(padding="50px")),
        html.Div(["Enter Age: ",dcc.Input(id="papermill-age",type="number",placeholder="Enter Age...",style=dict(width="200px",height="75px",fontSize=35,position="relative",left="120px"))],style=dict(padding="50px")),
        html.Div(["Enter Date: ",dcc.Input(id="papermill-date",type="text",placeholder="Enter Date...",style=dict(width="200px",height="75px",fontSize=35,position="relative",left="110px"))],style=dict(padding="50px")),
        html.Div(["Enter Patients ID: ",dcc.Input(id="papermill-id",type="number",placeholder="Enter Patients Id",style=dict(width="300px",height="75px",fontSize=35,position="relative",left="40px"))],style=dict(padding="50px")),
        html.Button("submit".upper(),id="papermill-submit-button",style=dict(position="relative",fontSize=30,borderRadius="10px",backgroundColor="cyan",bottom="20px",left="300px",height="100px",width="200px")),
        html.Div(html.H1("papermill report preview".upper(),className="page-heading"),className="heading-divs"),
        html.Div("Submit details to preview..",id="papermill-output-container",style=dict(padding="50px",border="10px solid #4b70f5",marginTop="50px",width="75%",height="2100px",alignItems="center"))
    ],
    className="subpage-content"
)



def make_pdf(pt_name:str,pt_age:int,input_date:str,pt_id:int):
    input_date = " / ".join(input_date.split("/"))
    pt_height = np.random.randint(low=160,high=176,size=1).item()
    pt_weight = np.random.randint(low=60,high=86,size=1).item()
    reader = PdfReader("assets/full_rotated.pdf")
    writer = PdfWriter()
    font_name = "Arial-Bold"
    pt_name = pt_name.upper()
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
        State("papermill-id","value")
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