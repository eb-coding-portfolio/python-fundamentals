from dash import Dash
from dash_bootstrap_components.themes import MATERIA, QUARTZ, COSMO, LITERA
import sqlite3
import pandas as pd
import load_data as ld
from src.components.frontend.layout import create_layout
from dash.dependencies import Input, Output
import plotly.express as px
from utils import get_stat_val, rank, convert_to_percent
from src.components.frontend import ui_ids
from config import percentage_metric_list

if __name__ == "__main__":
    conn = sqlite3.connect('market_tracker.db')
    cursor = conn.cursor()
    query = f"""

               SELECT * FROM {ld.table_names['metro']}
               UNION ALL 
               SELECT * FROM {ld.table_names['state']}
               UNION ALL 
               SELECT * FROM {ld.table_names['national']}

               """
    data = pd.read_sql_query(query, conn)
    external_stylesheets = ['https://bootswatch.com/5/litera/bootstrap.css', 'custom.css']
    app = Dash(__name__, external_stylesheets=external_stylesheets)
    data_filters_prop_type = data['property_type'].unique()
    prop_type_options = [{'label': prop_type, 'value': prop_type} for prop_type in data_filters_prop_type]

    # callbacks
    # @app.callback(
    #     Output(ui_ids.PROPERTY_TYPE_DROP, 'options'),
    #     Input(ui_ids.STATE_CODE_DROP, 'value'),
    #     # Input('data-filters-store', 'data')
    # )
    # def update_property_type_options( data_filters_prop_type):
    #     data_filters_prop_type = data['property_type'].unique()
    #     options = [{'label': prop_type, 'value': prop_type} for prop_type in data_filters_prop_type]
    #     print("Updated options:", options)
    #     return options


    @app.callback(
        Output(ui_ids.US_MAP, 'figure'),
        Input(ui_ids.METRIC_DROP, 'value'),
        Input(ui_ids.PROPERTY_TYPE_DROP, 'value'),
    )
    def update_us_map(selected_metric, selected_property_type):
        map_input_df = pd.DataFrame(data)

        max_date = get_stat_val(map_input_df, 'period_end', 'max')

        map_df = map_input_df[(map_input_df['period_end'] == max_date) &
                              (map_input_df['region_type'] == 'state') &
                              (map_input_df['property_type'] == selected_property_type)][['state_code', selected_metric]]

        if selected_metric in percentage_metric_list:
            hover_data = {selected_metric: ':.2%'}
            tickformat = '.2%'
        else:
            hover_data = None
            tickformat = None
        fig = px.choropleth(map_df, locations='state_code',  # DataFrame column with locations
                            color=selected_metric,  # DataFrame column with color values
                            locationmode="USA-states",  # built-in location mode for U.S. states
                            scope="usa",
                            color_continuous_scale='deep',
                            hover_data=hover_data,
                            )
        fig.update_coloraxes(colorbar_tickformat=tickformat)
        return fig


    app.title = "purlieu"
    app.layout = create_layout(app, data, prop_type_options)
    app.run()
    conn.close()
