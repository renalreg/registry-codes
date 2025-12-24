"""
Utility script which is useful for doing one of table syncs to an arbitary
table.
"""

from sqlalchemy import create_engine
from registry_codes.utils import load_data

TABLE_NAME = "modality_codes"
URL = "*****"
engine = create_engine(URL)


try:
    inserted_rows = load_data(TABLE_NAME, engine)
    print(f"Inserted {inserted_rows} rows into {TABLE_NAME}")
except Exception as e:
    print(f"Error loading data into {TABLE_NAME}: {e}")
