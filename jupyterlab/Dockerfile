# syntax=docker/dockerfile:1
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Non-root user; its home holds the notebooks bind mount
ARG UID=1000
ARG GID=1000
RUN groupadd --gid ${GID} jupyter \
    && useradd --uid ${UID} --gid ${GID} --create-home --shell /bin/bash jupyter

WORKDIR /home/jupyter
COPY requirements.txt .
RUN pip install -r requirements.txt

USER jupyter
RUN mkdir -p /home/jupyter/notebooks
EXPOSE 8888

# Auth: the server reads JUPYTER_TOKEN from the environment (empty = no token).
CMD ["jupyter", "lab", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--notebook-dir=/home/jupyter/notebooks"]
