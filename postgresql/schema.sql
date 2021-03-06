DROP DATABASE IF EXISTS blog;
CREATE DATABASE blog;

\connect blog;

CREATE TABLE IF NOT EXISTS user (
  id SERIAL PRIMARY KEY,
  username VARCHAR,
  email VARCHAR
);

CREATE TABLE IF NOT EXISTS post (
  id SERIAL PRIMARY KEY,
  userId INTEGER REFERENCES user(id),
  title VARCHAR,
  content TEXT,
  image VARCHAR,
  date DATE DEFAULT CURRENT_DATE
);