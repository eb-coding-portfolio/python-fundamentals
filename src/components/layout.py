import pandas as pd
from dash import Dash, html
from src.components.unique_dropdown import state_code_render
def create_layout(app: Dash, data: pd.DataFrame):
    return html.Div(
        className='app-Div',
        children=[
            html.H1(app.title),
            html.Hr(),
            html.Div(
                className='dropdown-container',
                children=[
                    state_code_render(app, data),
                ],
            ),

        ],
    )