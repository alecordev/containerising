# The official dxflrs/garage image is `scratch` (only the static /garage binary): no shell, so it cannot
# run the bootstrap script. Copy the same pinned binary into a tiny Alpine image instead (python3 runs the
# Python bootstrap, init.py; curl is used by the healthcheck).
ARG GARAGE_VERSION=v2.5.0
FROM dxflrs/garage:${GARAGE_VERSION} AS garage

FROM alpine:3.23
RUN apk add --no-cache curl python3
COPY --from=garage /garage /usr/local/bin/garage
COPY init.py /usr/local/bin/garage-init
RUN chmod +x /usr/local/bin/garage-init
ENV RUST_LOG=garage=info
CMD ["garage", "server"]
