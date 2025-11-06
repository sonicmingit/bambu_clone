# syntax=docker/dockerfile:1

FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY flask_stub ./flask_stub

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "backend.main:app"]
