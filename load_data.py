import pandas as pd
import sqlite3
import os

dataset_files = [
    'https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/redfin_metro_market_tracker.tsv000.gz',
    'https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/state_market_tracker.tsv000.gz',
    'https://redfin-public-data.s3.us-west-2.amazonaws.com/redfin_market_tracker/us_national_market_tracker.tsv000.gz'
]

table_names = {
    'metro': 'redfin_metro_market_tracker',
    'state': 'redfin_state_market_tracker',
    'national': 'redfin_us_market_tracker'
}

column_definitions = {
    'period_begin': 'TEXT',
    'period_end': 'TEXT',
    'period_duration': 'INTEGER',
    'region_type': 'TEXT',
    'region_type_id': 'INTEGER',
    'table_id': 'INTEGER',
    'is_seasonally_adjusted': 'TEXT',
    'region': 'TEXT',
    'city': 'TEXT',
    'state': 'TEXT',
    'state_code': 'TEXT',
    'property_type': 'TEXT',
    'property_type_id': 'INTEGER',
    'median_sale_price': 'REAL',
    'median_sale_price_mom': 'REAL',
    'median_sale_price_yoy': 'REAL',
    'median_list_price': 'REAL',
    'median_list_price_mom': 'REAL',
    'median_list_price_yoy': 'REAL',
    'median_ppsf': 'REAL',
    'median_ppsf_mom': 'REAL',
    'median_ppsf_yoy': 'REAL',
    'median_list_ppsf': 'REAL',
    'median_list_ppsf_mom': 'REAL',
    'median_list_ppsf_yoy': 'REAL',
    'homes_sold': 'REAL',
    'homes_sold_mom': 'REAL',
    'homes_sold_yoy': 'REAL',
    'pending_sales': 'REAL',
    'pending_sales_mom': 'REAL',
    'pending_sales_yoy': 'REAL',
    'new_listings': 'REAL',
    'new_listings_mom': 'REAL',
    'new_listings_yoy': 'REAL',
    'inventory': 'REAL',
    'inventory_mom': 'REAL',
    'inventory_yoy': 'REAL',
    'months_of_supply': 'REAL',
    'months_of_supply_mom': 'REAL',
    'months_of_supply_yoy': 'REAL',
    'median_dom': 'REAL',
    'median_dom_mom': 'REAL',
    'median_dom_yoy': 'REAL',
    'avg_sale_to_list': 'REAL',
    'avg_sale_to_list_mom': 'REAL',
    'avg_sale_to_list_yoy': 'REAL',
    'sold_above_list': 'REAL',
    'sold_above_list_mom': 'REAL',
    'sold_above_list_yoy': 'REAL',
    'price_drops': 'REAL',
    'price_drops_mom': 'REAL',
    'price_drops_yoy': 'REAL',
    'off_market_in_two_weeks': 'REAL',
    'off_market_in_two_weeks_mom': 'REAL',
    'off_market_in_two_weeks_yoy': 'REAL',
    'parent_metro_region': 'TEXT',
    'parent_metro_region_metro_code': 'INTEGER',
    'last_updated': 'TEXT'
}


def read_datasets(files):
    datasets = []
    column_names = None

    for file in files:
        dataset = pd.read_csv(file, delimiter='\t')
        datasets.append(dataset)

    combined_dataset = pd.concat(datasets, ignore_index=True)
    return combined_dataset


def create_database(database_name):
    conn = sqlite3.connect(database_name)
    return conn


def create_table(conn, table_name):
    conn.execute(f'DROP TABLE IF EXISTS {table_name}')

    column_definitions_str = ', '.join([f'{column} {column_definitions[column]}' for column in column_definitions])

    query = f'CREATE TABLE {table_name} ({column_definitions_str})'
    conn.commit()
    conn.execute(query)


def load_data(conn, table_name, dataset):
    columns = ', '.join(dataset.columns)
    placeholders = ', '.join(['?' for _ in dataset.columns])
    query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
    conn.executemany(query, dataset.values.tolist())

def test_queries(conn, name):
    # Create a cursor object
    cursor = conn.cursor()

    # Execute the query
    cursor.execute(f'SELECT count(*) as row_count_{name} FROM {name}')
    rows = cursor.fetchall()
    cursor.close()
    return rows

def main():
    dataset = read_datasets(dataset_files)
    conn = create_database('market_tracker.db')

    for region_type, table_name in table_names.items():
        region_data = dataset[dataset['region_type'] == region_type]
        create_table(conn, table_name)
        load_data(conn, table_name, region_data)

    for table in list(table_names.values()):
       results = test_queries(conn, table)
       print(results)

    conn.close()


if __name__ == '__main__':
    main()