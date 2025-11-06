# basic python image
FROM python:3.12-slim-bookworm

WORKDIR /app
ENV PYTHONPATH="/app:${PYTHONPATH}"

COPY . ./

RUN pip install .