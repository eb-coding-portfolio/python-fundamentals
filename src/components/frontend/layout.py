import pandas as pd
from dash import Dash, html, dcc
from src.components.frontend import ui_ids
from dash.dependencies import Input, Output
from config import metric_list
import plotly.express as px
from utils import get_stat_val, rank


def create_layout(app: Dash, data: pd.DataFrame):
    data_filters = data[['state_code', 'region', 'property_type']].drop_duplicates().sort_values(
        by=['state_code', 'region'])

    # callbacks
    # @app.callback(
    #     Output(ui_ids.REGION_DROP, 'options'),
    #     Input(ui_ids.STATE_CODE_DROP, 'value'),
    #     Input('data-filters-store', 'data')
    # )
    # def update_region_options(selected_state_code, data_filters_region):
    #     data_filters_region = pd.DataFrame(data_filters_region)
    #     filtered_regions = data_filters_region[data_filters_region['state_code'] == selected_state_code][
    #         'region'].unique()
    #     options = [{'label': region, 'value': region} for region in filtered_regions]
    #     print("Updated options:", options)
    #     return options

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
        filtered_df = bar_df.loc[(bar_df['period_end'] == max_date) &
                                 (bar_df['state_code'] == selected_state_code) &
                                 (bar_df['property_type'] == selected_property_type), ['region', selected_metric]]

        plot_dataframe = rank(filtered_df, 5, selected_metric)

        fig = px.bar(plot_dataframe, x=selected_metric, y='region')
        return fig

    return html.Div(
        className='app-Div',
        children=[
            html.H1(app.title),
            html.Hr(),
            dcc.Store(id='data-filters-store', data=data_filters.to_dict('records')),
            # dcc.Store(id='data-full', data=data.to_dict('records')),
            html.Div(
                className='dropdown-container',
                children=[
                    html.H6('State Code'),
                    dcc.Dropdown(
                        id=ui_ids.STATE_CODE_DROP,
                        options=[
                            {"label": state_code, "value": state_code}
                            for state_code in data_filters['state_code'].unique()
                        ],
                        style={"width": "300px", "font-size": "16px"},
                        value=data_filters['state_code'].unique()[0],
                        multi=False,
                        placeholder='Select a two-digit state code',
                    ),
                    # html.H6('Region'),
                    # dcc.Dropdown(
                    #     id=ui_ids.REGION_DROP,
                    #     options=[],
                    #     style={"width": "300px", "font-size": "16px"},
                    #     multi=False,
                    #     placeholder='Select a region',
                    # ),
                    html.H6('Property Type'),
                    dcc.Dropdown(
                        id=ui_ids.PROPERTY_TYPE_DROP,
                        options=[],
                        style={"width": "300px", "font-size": "16px"},
                        multi=False,
                        placeholder='Select a property type',
                    ),
                    html.H6('Metric'),
                    dcc.Dropdown(
                        id=ui_ids.METRIC_DROP,
                        options=[
                            {"label": metric, "value": metric}
                            for metric in metric_list
                        ],
                        style={"width": "300px", "font-size": "16px"},
                        value=metric_list,
                        multi=False,
                        placeholder='Select a metric',
                    )
                ],
            ),
            html.Div(
                className='bar-chart-container',
                children=[
                    dcc.Graph(id=ui_ids.TOP_N_CHART)
                ],
            ),
        ],
    )
