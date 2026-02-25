"""
Small utility script to load data in an ad-hoc way by specifying a table and a
db-url.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

from registry_codes.utils import load_data

load_dotenv()
URL = os.getenv("URL")
TABLE_NAME = "code_map"

if not URL:
    raise RuntimeError("Missing required environment variable: URL")

engine = create_engine(URL)

try:
    inserted_rows = load_data(TABLE_NAME, engine)
    print(f"Inserted {inserted_rows} rows into {TABLE_NAME}")
except Exception as e:
    print(f"Error loading data into {TABLE_NAME}: {e}")
