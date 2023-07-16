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


if __name__ == "__main__":
    conn = sqlite3.connect('market_tracker.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM {l.table_names['metro']}"
    # row_count = cursor.execute(f"SELECT count(*) FROM {l.table_names['metro']}")
    # print(f'row count of table {row_count}')
    data = pd.read_sql_query(query, conn)
    print(get_stat_val(data, 'period_end', 'max'))
