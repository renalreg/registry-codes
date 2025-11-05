"""
Simple utility to load data into a postgres database
"""


import os

from sqlalchemy import create_engine
from registry_codes.utils import TABLE_MODEL_MAP, create_table, load_data


def main():
    url = os.getenv("DATABASE_URL")
    print(f"DATABASE_URL: {url}")
    if url is None:
        # passthrough for local development
        url = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"

    engine = create_engine(url = url)
    tables = TABLE_MODEL_MAP.keys()
    print(tables)
    for table in tables:
        create_table(table, engine)
        load_data(table, engine)

if __name__ == '__main__':
    main()