# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "psycopg[binary]>=3.3",
#     "python-dotenv>=1.2",
# ]
# ///

import os

import psycopg
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

conninfo = (
    f"host={os.getenv('PG_HOST', 'localhost')} "
    f"port={os.getenv('PG_PORT', '5432')} "
    f"user={os.getenv('POSTGRES_USER', 'postgres')} "
    f"password={os.getenv('POSTGRES_PASSWORD', 'postgres')} "
    f"dbname={os.getenv('POSTGRES_DB', 'postgres')}"
)

with psycopg.connect(conninfo) as conn:
    with conn.cursor() as cur:
        cur.execute("CREATE TABLE IF NOT EXISTS demo (id SERIAL PRIMARY KEY, name TEXT)")
        cur.execute("INSERT INTO demo (name) VALUES (%s)", ("hello",))
        cur.execute("SELECT id, name FROM demo ORDER BY id DESC LIMIT 5")
        for row in cur.fetchall():
            print(row)
        print(conn.info.server_version)
