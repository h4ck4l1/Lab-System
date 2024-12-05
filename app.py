import os,sys,time
from glob import glob
from dash import Dash,html,dcc,register_page,page_container
import dash_bootstrap_components as dbc



app = Dash(
    __name__,
    assets_folder="assets",
    pages_folder="pages",
    use_pages=True,
    suppress_callback_exceptions=True
)

dropdown_options = [
    html.Li(
        html.Span(
            [
                html.Img(src="assets/index.png"),
                dcc.Link("index".upper(),href="/",className="dropdown-link")
            ]
        )
    ),
    html.Li(
        html.Span(
            [
                html.Img(src="assets/register.png"),
                dcc.Link("register".upper(),href="/register",className="dropdown-link")
            ]
        )
    ),
    html.Li(
        html.Span(
            [
                html.Img(src="assets/reports.png"),
                dcc.Link("reports".upper(),href="/reports",className="dropdown-link")
            ]
        )
    ),
    html.Li(
        html.Span(
            [
                html.Img(src="assets/all_reports.jpeg"),
                dcc.Link("all reports".upper(),href="/all_reports",className="dropdown-link")
            ]
        )
    ),
    html.Li(
        html.Span(
            [
                html.Img(src="assets/paper.png"),
                dcc.Link("papermill".upper(),href="/papermill",className="dropdown-link")
            ]
        )
    )
]

app.layout = dcc.Loading(
    [
        dcc.Location("url",refresh=False),
        dcc.Store(id="tab-id-store",storage_type="session"), 
        html.Div(
            [
                html.Ul(
                    html.Li(
                        html.Span(
                            [
                                html.H1("Lab Menu".upper(),className="dropdown-button-title"),
                                html.Img(src="assets/doctors.png")
                            ]
                        )
                    ),
                    className="dropdown-button"
                ),
                html.Div(html.Span(className="arrow"),className="arrow-space"),
                html.Ul(dropdown_options,className="dropdown-box")
            ],
            className="total-dropdown"
        ),
        page_container
    ],
    type="cube",
    className="loading-cube"
)

server = app.server

# gunicorn -b 0.0.0.0:8050 --log-level debug app:server

if __name__ == '__main__':
    app.run_server(host="0.0.0.0",port=8050)
    # app.run()