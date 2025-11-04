import os
import datetime 

import pandas as pd
from sqlalchemy import inspect
from pathlib import Path

from ukrdc_sqla.ukrdc import Code, CodeMap  

# Map directory names to ukrdc-sqla models
TABLE_MODEL_MAP = {
    "code_list": {
        "sqla_model" : Code,
        "excluded_columns" : ["creation_date", "update_date"]
    },
    "code_map": {
        "sqla_model" : CodeMap,
        "excluded_columns" : ["creation_date", "update_date"]
    }
}

def create_table(table_name: str, engine) -> None:
    """Create the database table for the specified table name if it doesn't exist.
    
    Args:
        table_name: Name of the table to create (e.g., 'code_list')
        engine: SQLAlchemy engine instance
    """
    if table_name not in TABLE_MODEL_MAP:
        raise ValueError(f"Unknown table: {table_name}")
        
    model = TABLE_MODEL_MAP[table_name]["sqla_model"]
    inspector = inspect(engine)
    
    # Check if table already exists
    if not inspector.has_table(table_name):
        model.__table__.create(engine)
        print(f"Created table: {table_name}")
    else:
        print(f"Table already exists: {table_name}")

def load_data(table_name: str, engine) -> int:
    """Load all CSV files from the specified table directory and insert into database.
    
    Args:
        table_name: Name of the table directory (e.g., 'code_list')
        engine: SQLAlchemy engine instance
        
    Returns:
        Number of rows inserted
    """
    if table_name not in TABLE_MODEL_MAP:
        raise ValueError(f"Unknown table: {table_name}")
        
    table_info = TABLE_MODEL_MAP[table_name]
    table = table_info["sqla_model"].__table__
    excluded_columns = table_info["excluded_columns"]
    table_dir = Path("tables") / table_name

    if not os.path.exists(table_dir):
        raise FileNotFoundError(f"Table directory not found: {table_dir}")
    
    total_rows = 0
    for filename in os.listdir(table_dir):
        if filename.endswith(".csv"):
            filepath = table_dir / filename
            print(filepath)
            df = pd.read_csv(filepath, header = None)
            df.columns = [col for col in table.columns.keys() if col not in excluded_columns]
            
            # due to limitations to sqlite we use pandas to fill in automated
            # datetime fields
            for col in excluded_columns:
                df[col] = datetime.datetime.now()

            # Insert data in chunks for better performance
            chunksize = 1000
            for i in range(0, len(df), chunksize):
                chunk = df[i:i+chunksize]
                chunk.to_sql(
                    name=table_name,
                    con=engine,
                    if_exists="append",
                    index=False,
                    method="multi"
                )
            total_rows += len(df)
            print(f"Inserted {len(df)} rows from {filename}")
    
    if total_rows == 0:
        raise ValueError(f"No CSV files found in directory: {table_dir}")
        
    print(f"Total rows inserted for {table_name}: {total_rows}")
    return total_rows
