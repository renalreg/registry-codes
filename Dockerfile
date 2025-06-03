# Get base debian image for now this might need to be a python image once ods
# exporter gets added
FROM debian:latest

RUN apt-get update && apt-get install -y sqlite3
CMD ["/bin/bash", "/scripts/004_sqlite.sh"]