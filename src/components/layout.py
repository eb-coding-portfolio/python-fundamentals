import pandas as pd
from dash import Dash, html

def create_layout(app: Dash, data: pd.DataFrame):
    return html.Div(
        className='app-Div',
        children=[
            html.H1(app.title),
            html.Hr(),

        ]
    )