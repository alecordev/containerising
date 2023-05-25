FROM python:3.10 as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc \
    libpq-dev

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY ./src/api /app
COPY requirements-api.txt /app

WORKDIR /app
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements-api.txt

FROM python:3.10-slim-bullseye

COPY --from=builder /opt/venv /opt/venv
COPY ./src/api /app
WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH"
EXPOSE 8081

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8081"]
