-- Runs once as SYS on the first start (after the database is ready).
-- Objects are created in the APP_USER schema of the pluggable database.
-- Init scripts run as SYS in the CDB root: switch into the pre-created pluggable database first.
ALTER SESSION SET CONTAINER = FREEPDB1;
ALTER SESSION SET CURRENT_SCHEMA = app;

CREATE TABLE notes (
  id   NUMBER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  body VARCHAR2(255) NOT NULL
);

INSERT INTO notes (body) VALUES ('hello from initdb');
COMMIT;
