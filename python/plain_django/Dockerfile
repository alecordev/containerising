# pull the official base image
FROM python:3.8.3-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app
RUN pip install -r requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app/example

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]