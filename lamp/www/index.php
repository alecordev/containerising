<?php
// Connectivity check: PHP -> MariaDB using the env vars set in docker-compose.yml
$host = getenv('DB_HOST') ?: 'mariadb';
$name = getenv('DB_NAME') ?: 'testdb';
$user = getenv('DB_USER') ?: 'username';
$pass = getenv('DB_PASSWORD') ?: 'password';

echo '<h1>LAMP stack</h1>';
echo '<p>PHP ' . htmlspecialchars(PHP_VERSION) . '</p>';

try {
    $pdo = new PDO("mysql:host=$host;dbname=$name;charset=utf8mb4", $user, $pass, [
        PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
    ]);
    $version = $pdo->query('SELECT VERSION()')->fetchColumn();
    echo '<p>Database connection OK: ' . htmlspecialchars($version) . '</p>';
} catch (PDOException $e) {
    http_response_code(500);
    echo '<p>Database connection failed: ' . htmlspecialchars($e->getMessage()) . '</p>';
}
