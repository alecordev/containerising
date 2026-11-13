-- Runs once, on the first start of an empty data volume.
CREATE TABLE IF NOT EXISTS app.notes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  body VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO app.notes (body) VALUES ('hello from initdb');
