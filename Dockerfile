# Get base debian image for now this might need to be a python image once ods
# exporter gets added
FROM python:3.12-slim-bookworm

WORKDIR /app
ENV PYTHONPATH="/app:${PYTHONPATH}"

COPY . ./

RUN pip install .