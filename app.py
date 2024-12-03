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
                html.Img(src="assets/paper.png"),
                dcc.Link("papermill".upper(),href="/papermill",className="dropdown-link")
            ]
        )
    )
]

app.layout = dcc.Loading(
    [
        dcc.Store(id="data-store",storage_type="local"),
        dcc.Store(id="patient-data-store",storage_type="local"),
        dcc.Location("url",refresh=False),
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
    app.run()