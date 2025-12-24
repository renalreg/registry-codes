import os
import datetime
import logging
import json

from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
from sqlalchemy import inspect
from pathlib import Path
from sqlalchemy import Integer, Boolean, DateTime
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import BIT, ARRAY
from ukrdc_sqla.ukrdc import Base

from registry_codes.schema import TABLE_MODEL_MAP


def coerce_sqla_types(data_row: dict, sqla_model: Base) -> dict:
    """Data from csv files is loaded into python as strings. To keep sqla happy
    we need to cast some of the types.
    """

    coerced_data = {}
    for key, value in data_row.items():
        if pd.isna(value) or value == "":
            value = None

        match sqla_model.__table__.columns[key].type:
            case Boolean():
                value = bool(value)
            case ARRAY():
                if value:
                    value = json.loads(value)
            case DateTime():
                # if (key == "startdate" or key == "enddate") and value:
                if value and isinstance(value, pd.Timestamp):
                    value = value.to_pydatetime()
                elif value and isinstance(value, str):
                    value = pd.to_datetime(value).to_pydatetime()

        coerced_data[key] = value

    return coerced_data


def create_table(table_name: str, engine, schema=None) -> None:
    """Build tables from sqla models"""
    if table_name not in TABLE_MODEL_MAP:
        raise ValueError(f"Unknown table: {table_name}")

    model = TABLE_MODEL_MAP[table_name]["sqla_model"]
    inspector = inspect(engine)

    # SQLite: replace BIT columns with Integer equivalents
    if engine.dialect.name == "sqlite":
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
        print(
            f"Created table: {schema}.{table_name}"
            if schema
            else f"Created table: {table_name}"
        )
    else:
        print(
            f"Table already exists: {schema}.{table_name}"
            if schema
            else f"Table already exists: {table_name}"
        )


def load_data_to_df(table_name: str) -> pd.DataFrame:
    """Data is defined using csv folders named after the table names on the
    database. This function loads all of the csv files for a given table into a
    dataframe for further processing.
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
            columns = [
                col for col in table.columns.keys() if col not in excluded_columns
            ]
            df = pd.read_csv(
                filepath, header=None, names=columns, dtype=str, index_col=False
            )
            all_dfs.append(df)

    if not all_dfs:
        print(f"WARNING: No CSV files found in directory {table_dir}")
        return pd.DataFrame()

    combined_df = pd.concat(all_dfs, ignore_index=True)

    # Add excluded columns
    for col in excluded_columns:
        combined_df[col] = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    return combined_df


def insert_data_to_table(table_name: str, df: pd.DataFrame, engine) -> int:
    """Insert DataFrame into table using SQLAlchemy ORM. Previous versions used
    pandas.to_sql functionality but this proved opaque and tricky to debug.
    """

    sqla_model = TABLE_MODEL_MAP[table_name]["sqla_model"]

    # Delete existing data
    print(f"Deleting existing data from {table_name}")
    with Session(engine) as session:
        session.query(sqla_model).delete()
        session.commit()

    # Insert new data
    print(f"Inserting {len(df)} rows into {table_name}")
    total_rows = 0
    chunksize = 1000

    with Session(engine) as session:
        for i in range(0, len(df), chunksize):
            chunk = df[i : i + chunksize]

            # Convert each row to dict and create model instances
            instances = []
            for _, row in chunk.iterrows():
                # Convert row to dict, handling NaN/NaT values
                row_dict = row.to_dict()
                instances.append(sqla_model(**coerce_sqla_types(row_dict, sqla_model)))

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
    """Applies some light cleaning. At the moment this is just code
    deduplication but it could be expanded in the future.
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
        print(
            f"WARNING: Removed {missing_count} rows with missing key values in {table_name}"
        )
    else:
        print(f"No data cleaning applied to data loaded into {table_name}")

    return cleaned_df


def load_data(table_name: str, engine) -> int:
    """Load all CSV files from the specified table directory and insert into database."""
    # Load data into DataFrame
    df = load_data_to_df(table_name)

    # Validate and clean data
    if len(df) > 0:
        df = clean_data(table_name, df)
    else:
        return 0

    # Insert data into table
    total_rows = insert_data_to_table(table_name, df, engine)

    print(f"Total rows inserted for {table_name}: {total_rows}")
    return total_rows
