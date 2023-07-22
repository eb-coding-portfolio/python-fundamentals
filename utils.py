import pandas as pd
import sqlite3
import load_data as l


def get_stat_val(input_dataframe: pd.DataFrame, column: str, stat: str):
    if column in ('period_end', 'period_begin'):
        input_dataframe[column] = pd.to_datetime(input_dataframe[column])

    column_stats = input_dataframe[column].describe()
    print(column_stats)
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


if __name__ == "__main__":
    data = {
        'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eva'],
        'Decimal_Column': [0.25, 0.5, 0.75, 0.1, 0.9],
        'Non_Numeric_Column': ['A', 'B', 'C', 'D', 'E'],
        'Age': [21, 20, 22, 19, 20]
    }
    df = pd.DataFrame(data)
    try:
        # Test with the 'Decimal_Column'
        converted_df = convert_to_percent(df, 'Decimal_Column')
        print("\nDataFrame with 'Decimal_Column' converted to percent:")
        print(converted_df)

        # Test with the 'Non_Numeric_Column' (should raise a ValueError)
        converted_df = convert_to_percent(df, 'Non_Numeric_Column')

    except ValueError as e:
        print("\nError:", e)

    # conn = sqlite3.connect('market_tracker.db')
    # cursor = conn.cursor()
    # query = f"SELECT * FROM {l.table_names['metro']}"
    # data = pd.read_sql_query(query, conn)
    # print(get_stat_val(data, 'period_end', 'max'))
