import pandas as pd
import sqlite3
import load_data as ld
from config import table_columns, percentage_metric_list


def get_stat_val(input_dataframe: pd.DataFrame, column: str, stat: str):
    if column in ('period_end', 'period_begin'):
        input_dataframe[column] = pd.to_datetime(input_dataframe[column])

    column_stats = input_dataframe[column].describe()

    value = column_stats[stat]

    return value


def rank(df: pd.DataFrame, rank_num: int, metric: str):
    df['Rank'] = df[metric].rank(ascending=False)
    df_ranked = df.sort_values(by='Rank', ascending=False)
    top_n = df_ranked.head(rank_num).sort_values(by='Rank', ascending=True)
    bottom_n = df_ranked.tail(rank_num).sort_values(by='Rank', ascending=True)
    df_plot = pd.concat([top_n, bottom_n]).drop_duplicates()
    df_plot = df_plot.sort_values(by='Rank', ascending=False)
    return df_plot


def convert_to_percent(df: pd.DataFrame, column_name: str):
    """
    Convert a column in a DataFrame from decimal to percent.

    Parameters:
        df (pd.DataFrame): The input DataFrame.
        column_name (str): The name of the column to convert to percent.

    Returns:
        pd.DataFrame: A new DataFrame with the specified column converted to percent.

    Raises:
        ValueError: If the column_name is not present in the DataFrame or if the column contains non-numeric values.
    """
    if column_name not in df.columns:
        raise ValueError(f"The column '{column_name}' does not exist in the DataFrame.")

    # Check if the column contains numeric values
    if not pd.api.types.is_numeric_dtype(df[column_name]):
        raise ValueError(f"The column '{column_name}' does not contain numeric values.")

    # Multiply the column by 100 to convert from decimal to percent
    converted_df = df.copy()
    converted_df[column_name] *= 100

    return converted_df


def create_stats_table(data, state_code, property_type):

    metric_list = [column for column in table_columns if 'yoy' in column]

    max_date = get_stat_val(data, 'period_end', 'max')

    us_data = data[(data['region_type'] == 'national') &
                   (data['period_end'] == max_date) &
                   (data['property_type'] == property_type)][table_columns]
    state_data = data[(data['region_type'] == 'state') &
                      (data['state_code'] == state_code) &
                      (data['period_end'] == max_date) &
                      (data['property_type'] == property_type)][table_columns]

    top_metro = data[(data['region_type'] == 'metro') &
                     (data['state_code'] == state_code) &
                     (data['period_end'] == max_date) &
                     (data['property_type'] == property_type)]['region'].sort_values().iloc[0]

    metro_data = data[(data['region_type'] == 'metro') &
                      (data['state_code'] == state_code) &
                      (data['region'] == top_metro) &
                      (data['period_end'] == max_date) &
                      (data['property_type'] == property_type)][table_columns]


    us_data_filtered = us_data[metric_list]
    state_data_filtered = state_data[metric_list]
    metro_data_filtered = metro_data[metric_list]

    state_diff = (state_data_filtered - us_data_filtered.values)
    metro_diff = (metro_data_filtered - state_data_filtered.values)

    # Concatenate the original data with the calculated differences
    result = pd.concat([us_data, state_data, state_diff, metro_data, metro_diff])

    # Reset the index for proper ordering
    result = result.reset_index(drop=True)

    return result


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
    state_code = 'CA'
    property_type = 'All Residential'  # replace with the desired property type
    result = create_stats_table(data, state_code, property_type)
    result.to_csv(r'C:\Users\Eric C. Balduf\Documents\tabel_test.csv')

    # conn = sqlite3.connect('market_tracker.db')
    # cursor = conn.cursor()
    # query = f"SELECT * FROM {l.table_names['metro']}"
    # data = pd.read_sql_query(query, conn)
    # print(get_stat_val(data, 'period_end', 'max'))
