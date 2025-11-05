import os
import datetime 

import pandas as pd
from sqlalchemy import inspect
from pathlib import Path
from sqlalchemy import Integer
from sqlalchemy.dialects.postgresql import BIT

from ukrdc_sqla.ukrdc import (
    Code, CodeMap, CodeExclusion, ModalityCodes, RRCodes, RRDataDefinition, SatelliteMap  
)

# Map directory names to ukrdc-sqla models, define automatically filled columns
# (not in csv files) and specify the key relationship
TABLE_MODEL_MAP = {
    "code_exclusion": {
        "sqla_model" : CodeExclusion,
        "excluded_columns" : [],
        "unique_columns" : ["code", "coding_standard"]
    },
    "code_list": {
        "sqla_model" : Code,
        "excluded_columns" : ["creation_date", "update_date"],
        "unique_columns" : ["code", "coding_standard"]
    },
    "code_map": {
        "sqla_model" : CodeMap,
        "excluded_columns" : ["creation_date", "update_date"],
        "unique_columns" : ["source_coding_standard", "source_code", "destination_coding_standard", "destination_code"]
    },
    #"facility": {
    #},
    "modality_codes": {
        "sqla_model" : ModalityCodes,
        "excluded_columns" : [],
        "unique_columns" : ["registry_code"]
    },
    "rr_codes": {
        "sqla_model" : RRCodes,
        "excluded_columns" : [],
        "unique_columns" : ["id", "rr_code"]
    },
    "rr_data_definition":{
        "sqla_model" : RRDataDefinition,
        "excluded_columns" : [],
        "unique_columns" : ["upload_key"]
    },
    "satellite_map":{
        "sqla_model" : SatelliteMap,
        "excluded_columns" : ["creation_date", "update_date"],
        "unique_columns" : ["satellite_code", "main_unit_code"]
    },
}

EXTERNAL_TABLE_LIST = ["ukrdc_ods_gp_codes"]

def download_external(table_name:str):
    return

def create_table(table_name: str, engine) -> None:
    """Create the database table for the specified table name if it doesn't
    exist.
    """
    if table_name not in TABLE_MODEL_MAP:
        raise ValueError(f"Unknown table: {table_name}")
    
    model = TABLE_MODEL_MAP[table_name]["sqla_model"]
    inspector = inspect(engine)

    # SQLite: replace BIT columns with Integer equivalents
    if engine.dialect.name == 'sqlite':
        for column in model.__table__.columns:
            if isinstance(column.type, BIT):
                # Replace column type in-place for SQLite
                column.type = Integer()

        TABLE_MODEL_MAP[table_name]["sqla_model"] = model
    
    if not inspector.has_table(table_name):
        model.__table__.create(engine)
        print(f"Created table: {table_name}")
    else:
        print(f"Table already exists: {table_name}")


def load_data_to_df(table_name: str) -> pd.DataFrame:
    """Takes data defined in the tables directories and loads them into a
    pandas dataframe.
    """
    if table_name not in TABLE_MODEL_MAP:
        raise ValueError(f"Unknown table: {table_name}")
        
    table_info = TABLE_MODEL_MAP[table_name]
    table = table_info["sqla_model"].__table__
    excluded_columns = table_info["excluded_columns"]
    table_dir = Path("tables") / table_name

    if not os.path.exists(table_dir):
        raise FileNotFoundError(f"Table directory not found: {table_dir}")
    
    all_dfs = []
    for filename in os.listdir(table_dir):
        if filename.endswith(".csv"):
            filepath = table_dir / filename
            print(f"Reading {filepath}")
            columns = [col for col in table.columns.keys() if col not in excluded_columns]
            #dtypes = {col: sqlalchemy_to_pandas_type(table.columns[col].type) for col in columns}
            df = pd.read_csv(filepath, header=None, names=columns, dtype = str)
            all_dfs.append(df)
    
    if not all_dfs:
        print(f"WARNING: No CSV files found in directory {table_dir}")
        return
    
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Add excluded columns
    for col in excluded_columns:
        combined_df[col] = datetime.datetime.now()
        
    return combined_df


def insert_data_to_table(table_name: str, df: pd.DataFrame, engine) -> int:
    """Insert DataFrame dataframe into table
    """
    chunksize = 1000
    total_rows = 0

    # Delete existing data
    print(f"Deleting existing data from {table_name}")
    table = TABLE_MODEL_MAP[table_name]["sqla_model"].__table__
    columns = table.columns.keys()
    dtypes = {col: table.columns[col].type for col in columns}
    with engine.connect() as conn:
        conn.execute(table.delete())
        conn.commit()
    
    
    for i in range(0, len(df), chunksize):
        chunk = df[i:i+chunksize]
        chunk.to_sql(
            name=table_name,
            con=engine,
            dtype = dtypes,
            if_exists="append",
            index=False,
            method="multi"
        )
        total_rows += len(chunk)
        
    return total_rows


def clean_data(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Clean DataFrame by removing duplicates and rows with missing key values.
    """
    if table_name not in TABLE_MODEL_MAP:
        return df
        
    unique_columns = TABLE_MODEL_MAP[table_name].get("unique_columns", [])
    
    if not unique_columns:
        return df
        
    # Remove rows with missing key values
    cleaned_df = df.dropna(subset=unique_columns)
    missing_count = len(df) - len(cleaned_df)

    # Remove duplicates (keep first occurrence)
    cleaned_df = cleaned_df.drop_duplicates(subset=unique_columns, keep="first")
    duplicate_count = len(df) - missing_count - len(cleaned_df)
    
    if duplicate_count > 0:
        print(f"WARNING: Removed {duplicate_count} duplicate rows in {table_name}")

    elif missing_count > 0:
        print(f"WARNING: Removed {missing_count} rows with missing key values in {table_name}")
    else:
        print(f"No data cleaning applied to data loaded into {table_name}")
        
    return cleaned_df


def load_data(table_name: str, engine) -> int:
    """Load all CSV files from the specified table directory and insert into database.
    """
    # Load data into DataFrame
    df = load_data_to_df(table_name)
    
    # Validate and clean data
    if df is not None:
        df = clean_data(table_name, df)
    else:
        return
    
    # Insert data into table
    total_rows = insert_data_to_table(table_name, df, engine)
    
    print(f"Total rows inserted for {table_name}: {total_rows}")
    return total_rows
