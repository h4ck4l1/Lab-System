from dash import dcc,html,register_page



index_layout = html.Div(
    [
        html.Div(
            html.H1("andhra diagonostics center".upper(),className="main-heading"),
            className="heading-divs",
            style=dict(
                color="cyan",
                position="relative",
                top="45vh",
                left="20vw",
                fontSize=20
            )
        ),
    ],
    className="subpage-content"
)


register_page("index".upper(),path="/",layout=index_layout)