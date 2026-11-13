"""DuckDB from Python: SQL over a pandas DataFrame, then persist to a database file."""
import duckdb
import pandas as pd

df = pd.DataFrame({"symbol": ["AAPL", "MSFT", "AAPL"], "price": [192.5, 410.0, 194.1]})

# DuckDB can query DataFrames in scope by name.
print(duckdb.sql("SELECT symbol, avg(price) AS avg_price FROM df GROUP BY symbol ORDER BY symbol").df())

with duckdb.connect("/work/data/demo.duckdb") as con:
    con.execute("CREATE OR REPLACE TABLE prices AS SELECT * FROM df")
    print(con.execute("SELECT count(*) FROM prices").fetchone())
