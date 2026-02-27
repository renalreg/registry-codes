"""
Small utility script to load data into a table in an ad-hoc way by specifying a table and a
db-url. Care should be taken in using this script as it failing can lead to all
the data in a table being dropped.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

from registry_codes.utils import load_data

load_dotenv()
URL = os.getenv("URL")
TABLE_NAME = "facility_new"

if not URL:
    raise RuntimeError("Missing required environment variable: URL")

engine = create_engine(URL)

try:
    inserted_rows = load_data(TABLE_NAME, engine)
    print(f"Inserted {inserted_rows} rows into {TABLE_NAME}")
except Exception as e:
    print(f"Error loading data into {TABLE_NAME}: {e}")
