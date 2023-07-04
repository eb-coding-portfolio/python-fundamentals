import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

def state_code_drop_render(app: Dash, data: pd.DataFrame):
    all_state_codes = data['state_code'].tolist()
    unique_state_codes = sorted(set(all_state_codes))

    @app.callback(
        
    )