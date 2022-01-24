FROM python:3.7-alpine

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt
CMD ["gunicorn", "-w 4", "--bind=0.0.0.0:8000", "main:app"]