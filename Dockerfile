FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libssl-dev \
    libbz2-dev \
    libffi-dev \
    gcc \
    g++ \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p /data

ENV DJANGO_SETTINGS_MODULE=mumble_rest.settings_docker
ENV DB_PATH=/data/db.sqlite3

CMD ["sh", "-c", "python manage.py migrate && gunicorn mumble_rest.wsgi:application --bind 0.0.0.0:8000 --workers 2"]
