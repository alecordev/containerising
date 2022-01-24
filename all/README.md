# Running locally

1. Clone the repo.
2. Ensure you have `docker` and `docker-compose` available.
3. Create `.env` in the same directory as the `docker-compose.yml` to define required docker-compose variables.
4. Create `.env` inside the `src` directory that contains the secrets and env vars required for the application (including AWS).
5. Run `docker-compose up` or `docker-compose --compatibility up`.

# .env

```
REDIS_PASSWORD=password

RABBITMQ_DEFAULT_USER=guest
RABBITMQ_DEFAULT_PASS=guest

RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
RABBITMQ_USERNAME=guest
RABBITMQ_PASSWORD=guest

RABBITMQ_EXCHANGE=test
RABBITMQ_EXCHANGE_TYPE=topic
RABBITMQ_QUEUE_NAME=test
RABBITMQ_ROUTING_KEY=test
```

## RabbitMQ

Username: guest
Password: guest

## Redis

## PostgreSQL

Username: postgres
Password: postgres

## Kibana

- http://localhost:5601/app/home

## ElasticSearch

ElasticSearch container requires specific permissions:

- `sudo chown -R 1000:1000 .docker/data/elastic`

## MongoDB

Username: admin
Password: admin

Host: localhost
Port: 27017

## Mongo Express

Port: 8081

## Cleaning docker-compose

- To clear containers: `docker rm -f $(docker ps -a -q)`
- To clear images: `docker rmi -f $(docker images -a -q)`
- To clear volumes: `docker volume rm $(docker volume ls -q)`
- To clear networks: `docker network rm $(docker network ls | tail -n+2 | awk '{if($2 !~ /bridge|none|host/){ print $1 }}')`
