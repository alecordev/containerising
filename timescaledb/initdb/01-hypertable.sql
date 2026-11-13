-- Runs once on the first start of an empty data volume.
CREATE EXTENSION IF NOT EXISTS timescaledb;

CREATE TABLE IF NOT EXISTS conditions (
  time        TIMESTAMPTZ      NOT NULL,
  device      TEXT             NOT NULL,
  temperature DOUBLE PRECISION NULL
);
SELECT create_hypertable('conditions', 'time', if_not_exists => TRUE);
INSERT INTO conditions (time, device, temperature) VALUES (now(), 'sensor-1', 21.5);
