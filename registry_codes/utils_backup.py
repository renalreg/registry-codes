import os
import datetime 
import logging
from sqlalchemy.exc import SQLAlchemyError
import datetime
import pandas as pd
from sqlalchemy import inspect
from pathlib import Path
from sqlalchemy import Integer, Boolean
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import BIT, ARRAY


from registry_codes.schema import LARGE_TABLES, TABLE_MODEL_MAP, SQLA_TO_PANDAS_DTYPE

def map_sqla_dtypes(table, cols):
    """Map SQLAlchemy column types to pandas dtypes for CSV reading."""
    dtypes = {}
    for col in cols:
        col_sqla_type = table.columns[col].type
        
        # Match against type classes in mapping
        pandas_dtype = str  # Default fallback
        for sqla_type_class, pandas_type in SQLA_TO_PANDAS_DTYPE.items():
            if isinstance(col_sqla_type, sqla_type_class):
                pandas_dtype = pandas_type
                break
        
        dtypes[col] = pandas_dtype
    
    return dtypes     

def create_table(table_name: str, engine, schema=None) -> None:
    """Create the database table for the specified table name if it doesn't
    exist. Probably not necessary as pandas can create the tables.
    """
    if table_name not in TABLE_MODEL_MAP:
        raise ValueError(f"Unknown table: {table_name}")
    
    model = TABLE_MODEL_MAP[table_name]["sqla_model"]
    inspector = inspect(engine)

    # SQLite: replace BIT columns with Integer equivalents
    if engine.dialect.name == 'sqlite':
        for column in model.__table__.columns:
            if isinstance(column.type, BIT) or isinstance(column.type, ARRAY):
                # Replace column type in-place for SQLite
                column.type = Integer()

        TABLE_MODEL_MAP[table_name]["sqla_model"] = model
    
    # Schema should already be set by caller, but set it if not
    if schema and not model.__table__.schema:
        model.__table__.schema = schema
    
    if not inspector.has_table(table_name, schema=schema):
        model.__table__.create(engine)
        print(f"Created table: {schema}.{table_name}" if schema else f"Created table: {table_name}")
    else:
        print(f"Table already exists: {schema}.{table_name}" if schema else f"Table already exists: {table_name}")


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
            dtypes = map_sqla_dtypes(table, columns)
            
            df = pd.read_csv(filepath, header=None, names=columns, dtype = dtypes, index_col=False)
            
            # Convert boolean and BIT columns from string to bool
            for col in columns:
                col_type = table.columns[col].type
                if isinstance(col_type, (Boolean)):
                    # Map string values to boolean, then convert dtype
                    df[col] = df[col].map({'True': True, 'False': False, '': False, 'true': True, 'false': False})
                    df[col] = df[col].astype('bool')
            
            all_dfs.append(df)
    
    if not all_dfs:
        print(f"WARNING: No CSV files found in directory {table_dir}")
        return
    
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Add excluded columns
    for col in excluded_columns:
        combined_df[col] = datetime.datetime.now()
        
    return combined_df


def insert_data_to_table(table_name: str, df: pd.DataFrame, engine, schema=None) -> int:
    """Insert DataFrame into table using SQLAlchemy ORM for proper type handling
    """

    
    model_class = TABLE_MODEL_MAP[table_name]["sqla_model"]
    
    # Delete existing data
    print(f"Deleting existing data from {table_name}")
    with Session(engine) as session:
        session.query(model_class).delete()
        session.commit()
    
    # Insert new data
    print(f"Inserting {len(df)} rows into {table_name}")
    total_rows = 0
    chunksize = 1000
    
    with Session(engine) as session:
        for i in range(0, len(df), chunksize):
            chunk = df[i:i+chunksize]
            
            # Convert each row to dict and create model instances
            instances = []
            for _, row in chunk.iterrows():
                # Convert row to dict, handling NaN/NaT values
                row_dict = row.to_dict()
                # Replace pandas NA values with None
                row_dict = {k: (None if pd.isna(v) else v) for k, v in row_dict.items()}
                instances.append(model_class(**row_dict))
            
            try:
                session.add_all(instances)
                session.commit()
                total_rows += len(instances)
                print(f"  Inserted {total_rows}/{len(df)} rows")
            except SQLAlchemyError as e:
                session.rollback()
                logging.error(f"Error inserting chunk into {table_name}: {e}")
                raise
        
    return total_rows


def clean_data(table_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Clean DataFrame by removing duplicates and rows with missing key values.
    """
    if table_name not in TABLE_MODEL_MAP:
        return df
        
    unique_columns = TABLE_MODEL_MAP[table_name].get("unique_columns", [])
    print(unique_columns)
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


def load_data(table_name: str, engine, schema = None) -> int:
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
    total_rows = insert_data_to_table(table_name, df, engine, schema = schema)
    
    print(f"Total rows inserted for {table_name}: {total_rows}")
    return total_rows
