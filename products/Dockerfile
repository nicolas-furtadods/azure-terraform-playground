FROM python:3.12-slim AS builder

ENV APP_PORT=8000

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

EXPOSE ${APP_PORT}

CMD ["fastapi", "run", "main:app", "--proxy-headers", "--port", "${APP_PORT}"]