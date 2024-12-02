import time
from datetime import date
from glob import glob
import numpy as np
import pandas as pd
from reportlab.platypus import SimpleDocTemplate,Table,TableStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import portrait,A4
from dash import dcc,html,register_page,dash_table,callback,Input,Output,ctx,State
from dash.exceptions import PreventUpdate



columns = [
    "S.No.",
    "Date",
    "Patient Name",
    "Reference By",
    "Patient Age",
    "Age Group",
    "Gender",
    "Phone No",
    "Amount",
    "Method",
    "Paid",
    "Due",
    "Sample",
]

dtype_map = {
    "S.No.": str,         # Ensure "S.No." remains a string
    "Date": str,          # string in format "YYYY-MM-DD"
    "Time": str,          # string in format "HH:MM:SS AM/PM"
    "Patient Name": str,  # Patient Name as string
    "Reference By": str,  # string with options as given below
    "Patient Age": "Int8",  # Use Int16 for compactness and allow NaNs
    "Age Group": str,     # string with options as ["Y","M","D"]
    "Gender": str,        # string with options as ["Male","Female"]
    "Amount": "Int32",    # Amount as integer
    "Method": str,        # string with options as ["CASH","PHONE PAY"]
    "Phone No": "Int64",  # Phone number as integer
    "Paid": str,          # string with options ["PAID","NOT PAID","DUE"]
    "Due": "Int16",       # Due as integer as the due amount if due/not paid and full amount will be reflected as due if not paid
    "Sample": str         # string with options as ["SELF","RAJU","RAJESH","RAM"]
}


doctor_options = [
    "self".upper(),
    "NEELIMA AGARWAL GARU, MD(Homeo).,",
    "m rama krishna garu, mbbs, dch.,".upper(),
    "Smt. M.N. SRI DEVI GARU, MBBS, DGO.,",
    "akula satyanarayana garu, mbbs, dch.,".upper(),
    "Smt. A GANGA BHAVANI GARU, MBBS, DGO.,".upper(),
    "k. rajendra prasad garu, b.m.p.,".upper(),
    "ch. kiran kumar garu, b.m.p.,".upper(),
    "k. chiranjeevi raju garu, b.m.p.,".upper(),
    "S. Prasad garu, b.m.p".upper(),
    "a. satti babu garu, md, pgdm".upper(),
    "v ramakrishna garu, b.m.p".upper(),
    "ch. raghunadha rao garu, b.m.p".upper(),
    "c.v.s.s. sharma garu, bams".upper(),
    "b. suribabu garu, b.m.p".upper(),
    "addanki surya garu, b.m.p".upper(),
    "ajay kumar garu, p.m.p".upper(),
    "a. chandrasekhar garu, bsc, dph&s".upper(),
    "durga prasad garu, b.m.p".upper(),
    "jagadeesh garu, p.m.p".upper(),
    "r. rama chandra rao garu, p.m.p".upper(),
    "g. bhanuprakash garu, p.m.p".upper(),
    "pv. venkateswara rao garu, p.m.p".upper(),
    "a. gowrish babu garu, b.m.p".upper(),
    "v.v.v prasad garu, p.m.p".upper(),
    "dileep kumar garu, mbbs, medical officer".upper(),
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
                    style=dict(position="absolute",left="350px")
                ),
                html.Button("REFRESH",id="refresh-button",style=dict(position="absolute",height="100px",width="100px",left="600px",color="red",fontSize=20,borderRadius="20px",backgroundColor="#4b70f5"))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *big_break,
        html.Div(
            [
                html.Div("S. No. : ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="serial_number",type="text",placeholder="Enter Serial Number... ",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30))
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
                    style=dict(width="600px",position="relative",left="50px",fontSize=20,bottom="25px")
                ),
                dcc.Input(id="reference-doctor",type="text",placeholder="Enter Doctors Name...",style=dict(position="relative",left="150px",width="500px",bottom="25px",fontSize=30))
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
            style=dict(display="inline-block",alignItems="center",position="relative",left="530px",bottom="35px",fontSize=20,width="100px")
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
            style=dict(display="inline-block",alignItems="center",position="relative",width="150px",fontSize=20,left="350px",bottom="30px")
        ),
        *big_break,
        html.Div(
            [
                html.Div("Amount : ",style=dict(color="cyan",fontSize=30)),
                dcc.Input(id="amount",type="number",placeholder="Amount...",style=dict(display="inline-block",position="absolute",left="350px",fontSize=30,width="150px")),
                html.Div("Method of Payment : ",style=dict(color="cyan",fontSize=30,position="absolute",left="600px")),
                html.Div(dcc.Dropdown(["cash".upper(),"phone pay".upper()],"cash".upper(),id="pay-method"),style=dict(display="inline-block",position="absolute",left="950px",fontSize=20,width="300px"))
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
                html.Div("Paid Amount : ",style=dict(color="cyan",fontSize=30,position="relative",left="200px")),
                dcc.Input(id="paid-input",type="number",placeholder="Enter Paid Amount",value=0,style=dict(display="inline-block",width="200px",fontSize=30,height="50px",position="relative",left="300px"))
            ],
            style=dict(display="flex",alignItems="center")
        ),
        *big_break,
        html.Div(
            [
                html.Div("Sample Bougth by: ",style=dict(color="cyan",fontSize=30)),
                html.Div(dcc.Dropdown(["self".upper(),"outside".upper()],"self".upper(),id="sample-source-dropdown"),style=dict(display="inline-block",fontSize=20,width="200px",height="75px",position="relative",left="350px",bottom="25px")),
                dcc.Input(id="sample-source-input",type="text",placeholder="Enter Name",value="Outside".upper(),style=dict(display="inline-block",width="200px",fontSize=30,height="50px",position="relative",left="400px",bottom="75px"))
            ]
        ),
        *big_break,
        html.Button("Submit".upper(),id="submit-button",style=dict(fontSize=30,borderRadius="20px",height="100px",width="250px",backgroundColor="#4b70f5",color="cyan")),
        html.Div(id="inputs-warning",style=dict(position="relative",color="red",fontSize=40,left="500px",bottom="100px")),
        *big_break,
        dash_table.DataTable(
            id="data-table",
            columns=[{"name":i,"id":i} for i in columns],
            style_table=dict(fontSize=25,backgroundColor="#633fff"),
            style_cell=dict(backgroundColor="#633fff"),
            editable=True,
        ),
        *big_break,
        html.Button("Save Changes",id="save-changes-button",style=dict(position="relative",left="90vw",fontSize=30,borderRadius="20px",height="100px",width="250px",backgroundColor="#4b70f5",color="cyan")),
        *big_break,
        html.Button("show file".upper(),id="show-file-button",style=dict(position="relative",left="500px",width="200px",height="100px",fontSize=30,borderRadius="20px",color="cyan",backgroundColor="#4b70f5")),
        *big_break,
        html.Div(id="show-file",style=dict(position="relative",left="500px",width="1200px",height="1200px"))
    ],
    className="subpage-content"
)

def save_df(df,date_value:str):
    date_value = date_value.replace("-","_")
    df.loc[df.shape[0]+1,:] = [np.nan] * df.shape[1]
    df.loc[df.shape[0],"Amount"] = df.loc[:,"Amount"].sum()
    df.loc[df.shape[0],"Due"] = df.loc[:,"Due"].sum()
    df.to_csv(f"assets/all_files/{date_value}.csv",index=False)



@callback(
    [
        Output("data-table","data"),
        Output("data-store","data")
    ],
    Input("refresh-button","n_clicks"),
    State("date-pick-single","date")
)
def initialize_df(n_clicks,date_value:str):
    if not n_clicks:
        raise PreventUpdate
    if ctx.triggered_id == 'refresh-button':
        file = glob(f"assets/all_files/{date_value.replace("-","_")}.csv")
        if file != []:
            df = pd.read_csv(file[0],dtype=dtype_map)
            df = df.iloc[:-1,:]
            df.loc[df.shape[0]+1,:] = [np.nan] * df.shape[1]
            df.loc[df.shape[0],"Amount"] = df.loc[:,"Amount"].sum()
            df.loc[df.shape[0],"Due"] = df.loc[:,"Due"].sum()
        else:
            df = pd.DataFrame(
                {
                    "S.No.":pd.Series(dtype="str"),
                    "Date":pd.Series(dtype="str"),
                    "Time":pd.Series(dtype="str"),
                    "Patient Name":pd.Series(dtype="str"),
                    "Reference By":pd.Series(dtype="str"),
                    "Patient Age":pd.Series(dtype="int8"),
                    "Age Group":pd.Series(dtype="str"),
                    "Gender":pd.Series(dtype="str"),
                    "Amount":pd.Series(dtype="int32"),
                    "Method":pd.Series(dtype="str"),
                    "Phone No":pd.Series(dtype="int64"),
                    "Paid":pd.Series(dtype="str"),
                    "Due":pd.Series(dtype="int16"),
                    "Sample":pd.Series(dtype="str")
                }
            )
            save_df(df,date_value)
        return df.to_dict('records'),{"date":date_value.replace("-","_")}


input_vals_dict = {
    0:"age group",
    1:"gender",
    2:"doctor",
    3:"serial number",
    4:"patient name",
    5:"patient age",
    6:"amount",
    7:"phone number",
}


@callback(
    [
        Output("data-table","data",allow_duplicate=True),
        Output("inputs-warning","children")
    ],
    Input("submit-button","n_clicks"),
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
        State("pay-method","value")                 # 14
    ],
    prevent_initial_call=True
)
def append_name_to_dataframe(n_clicks,*vals):
    global doctor_options
    if not n_clicks:
        raise PreventUpdate
    if ctx.triggered_id == "submit-button":
        date_value = vals[3].replace("-","_")
        df = pd.read_csv(f"assets/all_files/{date_value}.csv",dtype=dtype_map)
        vals_list = [vals[0],vals[1],(vals[2] or vals[6]),vals[4],vals[5],vals[7],vals[8],vals[9]]
        if any([val is None for val in vals_list]):
            return df.to_dict("records"),f"Input for {input_vals_dict[vals_list.index(None)]} is not entered".upper()
        df = df.iloc[:-1,:]
        index_number = df.shape[0]
        index_number += 1
        df["S.No."] = df["S.No."].astype("str")
        df["Date"] = df["Date"].astype("str")
        df["Time"] = df["Time"].astype("str")
        df["Patient Name"] = df["Patient Name"].astype("str")
        df["Reference By"] = df["Reference By"].astype("str")
        df["Patient Age"] = df["Patient Age"].astype("int8")
        df["Age Group"] = df["Age Group"].astype("str")
        df["Gender"] = df["Gender"].astype("str")
        df["Amount"] = df["Amount"].astype("int32")
        df["Method"] = df["Method"].astype("str")
        df["Phone No"] = df["Phone No"].astype("int64")
        df["Paid"] = df["Paid"].astype("str")
        df["Due"] = df["Due"].astype("int16")
        df["Sample"] = df["Sample"].astype("str")
        df.loc[index_number,"S.No."] = vals[4]
        df.loc[index_number,"Date"] = vals[3]
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
        if vals[6] is None:
            df.loc[index_number,"Reference By"] = vals[2]
        else:
            df.loc[index_number,"Reference By"] = vals[6].upper()
            if vals[6] not in doctor_options:
                doctor_options.append(vals[6].upper())
        df.loc[index_number,"Age Group"] = vals[0]
        df.loc[index_number,"Patient Age",] = vals[7]
        df.loc[index_number,"Gender"] = vals[1]
        df.loc[index_number,"Amount"] = vals[8]
        df.loc[index_number,"Method"] = vals[14]
        df.loc[index_number,"Phone No"] = vals[9]
        df.loc[index_number,"Paid"] = vals[10]
        if vals[10] == "due".upper():
            df.loc[index_number,"Due"] = vals[8] - vals[11]
        elif vals[10] == "not paid".upper():
            df.loc[index_number,"Due"] = vals[8]
        else:
            df.loc[index_number,"Due"] = 0
        df.loc[index_number,"Sample"] = vals[12]
        if (vals[12] == "outside".upper()) & (vals[13] is not None):
            df.loc[index_number,"Sample"] = vals[13]
        save_df(df,vals[3])
        return df.to_dict('records'),""


@callback(
    Output("data-table","data",allow_duplicate=True),
    Input("save-changes-button","n_clicks"),
    [
        State("data-table","data"),
        State("data-store","data")
    ],
    prevent_initial_call=True
)
def save_table_changes(n_clicks,data,date_value:dict):
    if not n_clicks:
        raise PreventUpdate
    if n_clicks:
        pd.read_csv(f"assets/all_files/{date_value["date"]}.csv").to_csv(f"assets/pre_change_folder/{date_value["date"]}.csv",index=False)
        print(f"\nChanges have been made\n")
        df = pd.DataFrame(data=data)
        df = df.iloc[:-1,:]
        save_df(df,date_value["date"])
        return data

def convert_to_pdf(date_value):
    df = pd.read_csv(f"assets/all_files/{date_value}.csv",dtype=dtype_map)
    df = df.loc[:,["S.No.","Time","Amount","Method","Phone No","Paid","Due","Sample"]]
    indexes_at_cash = df[df["Method"] == "cash".upper()].index
    df.iloc[-1,3] = df.loc[indexes_at_cash,"Amount"].sum()
    filename=f"assets/all_files/{date_value}.pdf"
    doc = SimpleDocTemplate(filename)
    doc.pagesize = portrait(A4)
    data = [df.columns.to_list()] + df.values.tolist()
    table = Table(data)
    indexes_at_cash = df[df["Method"] == "phone pay".upper()].index
    all_elements = [("grid".upper(),(0,0),(-1,-1),1,colors.black)]
    for ind in indexes_at_cash:
        all_elements.append(("background".upper(),(0,ind+1),(-1,ind+1),colors.darkgrey))
        all_elements.append(("textcolor".upper(),(0,ind+1),(-1,ind+1),colors.white))
    table.setStyle(TableStyle(all_elements))
    doc.build([table])
    return filename


@callback(
    Output("show-file","children"),
    Input("show-file-button","n_clicks"),
    State("date-pick-single","date")
)
def show_pdf_out(n_clicks,date_value:str):
    if not n_clicks:
        raise PreventUpdate
    if ctx.triggered_id == "show-file-button":
        filename = convert_to_pdf(date_value.replace("-","_"))
        cache_buster = f"?v={int(time.time())}"
        return html.Iframe(
            src=f"{filename}{cache_buster}",
            style=dict(width="1000px",height="1000px")
        )

register_page(
    "Register",
    layout=register_layout,
    path="/register"
)

