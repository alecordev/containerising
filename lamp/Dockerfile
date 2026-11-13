# syntax=docker/dockerfile:1
ARG PHP_VERSION=8.4
FROM php:${PHP_VERSION}-apache

# MySQL/MariaDB drivers (mysqli + PDO) are not bundled in the base image
RUN docker-php-ext-install -j"$(nproc)" mysqli pdo_mysql \
    && cp "$PHP_INI_DIR/php.ini-development" "$PHP_INI_DIR/php.ini"
