# syntax=docker/dockerfile:1
ARG POSTGRES_VERSION=18.6
ARG PGVECTOR_VERSION=v0.8.7

# ---- build stage: compile pgvector (toolchain stays out of the final image) ----
FROM postgres:${POSTGRES_VERSION} AS builder
ARG PGVECTOR_VERSION

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        git \
        postgresql-server-dev-${PG_MAJOR} \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /tmp/pgvector
# OPTFLAGS="" avoids -march=native so the image runs on any x86-64/arm64 host
RUN git clone --branch "${PGVECTOR_VERSION}" --depth 1 https://github.com/pgvector/pgvector.git . \
    && make OPTFLAGS="" \
    && make install DESTDIR=/out

# ---- runtime stage: plain postgres + the compiled extension ----
FROM postgres:${POSTGRES_VERSION}
COPY --from=builder /out/ /
