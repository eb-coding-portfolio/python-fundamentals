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


    # callbacks
    @app.callback(
        Output(ui_ids.PROPERTY_TYPE_DROP, 'options'),
        Input(ui_ids.STATE_CODE_DROP, 'value'),
        Input('data-filters-store', 'data')
    )
    def update_property_type_options(selected_state_code, data_filters_prop_type):
        data_filters_prop_type = pd.DataFrame(data_filters_prop_type)
        filtered_property_types = data_filters_prop_type[
            (data_filters_prop_type['state_code'] == selected_state_code)
        ]['property_type'].unique()
        options = [{'label': prop_type, 'value': prop_type} for prop_type in filtered_property_types]
        print("Updated options:", options)
        return options


    @app.callback(
        Output(ui_ids.TOP_N_CHART, 'figure'),
        Input(ui_ids.STATE_CODE_DROP, 'value'),
        Input(ui_ids.METRIC_DROP, 'value'),
        Input(ui_ids.PROPERTY_TYPE_DROP, 'value'),
    )
    def update_bar_chart(selected_state_code, selected_metric, selected_property_type):
        bar_df = pd.DataFrame(data)
        max_date = get_stat_val(bar_df, 'period_end', 'max')

        if selected_metric in bar_df.columns:
            filtered_df = bar_df.loc[(bar_df['period_end'] == max_date) &
                                     (bar_df['state_code'] == selected_state_code) &
                                     (bar_df['property_type'] == selected_property_type) &
                                     bar_df[selected_metric].notna(),
            ['region', selected_metric]]
        else:
            print(f"The selected metric '{selected_metric}' does not exist in the DataFrame.")
            filtered_df = pd.DataFrame()  # Return an empty DataFrame

        rank_dataframe = rank(filtered_df, 5, selected_metric)
        # plot_dataframe = convert_to_percent(rank_dataframe, selected_metric)
        fig = px.bar(rank_dataframe, x=selected_metric, y='region')
        if selected_metric in percentage_metric_list:
            fig.update_layout(xaxis_tickformat=".1%")
        return fig


    app.title = "purlieu"
    app.layout = create_layout(app, data)
    app.run()
    conn.close()
