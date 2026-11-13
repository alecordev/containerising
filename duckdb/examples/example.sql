-- DuckDB demo: run with `docker compose run --rm duckdb duckdb -f /work/examples/example.sql`
CREATE OR REPLACE TABLE trades AS
SELECT * FROM (VALUES
    ('AAPL', DATE '2026-01-02', 192.5, 100),
    ('AAPL', DATE '2026-01-03', 194.1, 150),
    ('MSFT', DATE '2026-01-02', 410.0,  80),
    ('MSFT', DATE '2026-01-03', 412.3,  60)
) AS t(symbol, trade_date, price, qty);

SELECT symbol, sum(price * qty) AS notional, avg(price) AS avg_price
FROM trades
GROUP BY symbol
ORDER BY symbol;

-- Query files directly (CSV / Parquet / JSON), including remote ones:
COPY trades TO '/work/data/trades.parquet' (FORMAT parquet);
SELECT count(*) AS rows_in_parquet FROM '/work/data/trades.parquet';
