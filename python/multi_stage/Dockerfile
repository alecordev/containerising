FROM python:3.9 as builder

RUN pip wheel --no-cache-dir --no-deps --wheel-dir /wheels jupyter pandas


FROM python:3.9-slim

WORKDIR /notebooks

COPY --from=builder /wheels /wheels
RUN pip install --no-cache /wheels/*