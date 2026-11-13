-- Runs once, on first start of an empty data volume (docker-entrypoint-initdb.d).
-- The database named by POSTGRES_DB already exists; add your schema to it.

CREATE TABLE IF NOT EXISTS users (
  id       SERIAL PRIMARY KEY,
  username VARCHAR NOT NULL,
  email    VARCHAR
);

CREATE TABLE IF NOT EXISTS posts (
  id      SERIAL PRIMARY KEY,
  user_id INTEGER REFERENCES users(id),
  title   VARCHAR,
  content TEXT,
  image   VARCHAR,
  date    DATE DEFAULT CURRENT_DATE
);
