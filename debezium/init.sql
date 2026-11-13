-- Runs once, on first start of the database (POSTGRES_DB, default `inventory`).
CREATE TABLE IF NOT EXISTS customers (
    id         SERIAL PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name  TEXT NOT NULL,
    email      TEXT NOT NULL UNIQUE
);

INSERT INTO customers (first_name, last_name, email) VALUES
    ('Sally',  'Thomas',  'sally.thomas@acme.com'),
    ('George', 'Bailey',  'gbailey@foobar.com')
ON CONFLICT DO NOTHING;
