from dash import Dash
from dash_bootstrap_components.themes import MATERIA
import sqlite3
import pandas as pd
import load_data as l
from src.components.frontend.layout import create_layout

if __name__ == "__main__":
    conn = sqlite3.connect('market_tracker.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM {l.table_names['metro']}"
    # row_count = cursor.execute(f"SELECT count(*) FROM {l.table_names['metro']}")
    # print(f'row count of table {row_count}')
    data = pd.read_sql_query(query, conn)

    app = Dash(external_stylesheets=[MATERIA])
    app.title = "purlieu"
    app.layout = create_layout(app, data)
    app.run()
    conn.close()

