FROM python:3.12-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    libssl-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --upgrade pip \
    && pip install -r requirements.txt

EXPOSE 1234

ENTRYPOINT ["python", "-m", "gateway", "--ip", "0.0.0.0"]
