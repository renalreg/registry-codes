"""
Simple utility to load data into a postgres database
"""


import os

from sqlalchemy import create_engine, text
from registry_codes.utils import TABLE_MODEL_MAP, create_table, load_data


def main():
    url = os.getenv("DATABASE_URL")
    print(f"DATABASE_URL: {url}")
    if url is None:
        # passthrough for local development
        url = "postgresql+psycopg://postgres:postgres@localhost:8000/postgres"

    engine = create_engine(url = url)
    with engine.connect() as conn:
        conn.execute(text(
            """CREATE SCHEMA "extract"
                 AUTHORIZATION postgres;

               GRANT ALL ON SCHEMA "extract" TO postgres;

               GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA extract TO postgres;

               -- set search path for the database 
               ALTER DATABASE "postgres" SET search_path TO "$user",extract;"""
        ))
        conn.commit()
        print("created extract schema")

    tables = TABLE_MODEL_MAP.keys()
    print(tables)
    for table in tables:
        create_table(table, engine, schema="extract")
        load_data(table, engine, schema="extract")
    

if __name__ == '__main__':
    main()