from dash import Dash, no_update, dash_table
from dash_bootstrap_components.themes import MATERIA, QUARTZ, COSMO, LITERA
import sqlite3
import pandas as pd
import load_data as ld
from src.components.frontend.layout import create_layout
from dash.dependencies import Input, Output
import plotly.express as px
from utils import get_stat_val, create_stats_table
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

    @app.callback(
        Output(ui_ids.HOUSING_TABLE_ID, 'data'),
        Output(ui_ids.HOUSING_TABLE_ID, 'columns'),
        Input(ui_ids.US_MAP, 'clickData'),
        Input(ui_ids.PROPERTY_TYPE_DROP, 'value'),
    )
    def update_table(clickData, selected_property_type_table):
        print(clickData)
        if clickData is None:
            # If no state has been clicked, don't update the table.
            state_code = 'CA'
        else:
            # Extract the state code from the clicked data.
            state_code = clickData['points'][0]['location']
            print(f'this is the extracted state code: {state_code}')

        # Call your create_table function to get the DataFrame.
        df = create_stats_table(data, state_code, selected_property_type_table)
        df['period_end'] = df['period_end'].dt.strftime('%Y-%m-%d')

        # Convert the DataFrame to the data and columns needed for the DataTable.
        table_data = df.to_dict('records')

        table_columns = [{"name": i, "id": i, 'type': 'numeric', 'format': {'specifier': '.2%'}}
                         if i in percentage_metric_list else {"name": i, "id": i} for i in df.columns]
        # Return the data and columns to be used in the DataTable component in the layout.

        return table_data, table_columns

    app.title = "purlieu"
    app.layout = create_layout(app, data, prop_type_options)
    app.run()
    conn.close()
