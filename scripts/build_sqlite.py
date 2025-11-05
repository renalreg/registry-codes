from registry_codes.utils import TABLE_MODEL_MAP, create_table, load_data
from sqlalchemy import create_engine
import argparse 

def create_db(output_db):
    engine = create_engine(f'sqlite:///{output_db}')
    return engine


def main():
    parser = argparse.ArgumentParser(description='Build SQLite database from ukrdc-sqla models and CSV data')
    parser.add_argument('output_db', help='Output SQLite database file path')
    parser.add_argument('--large-tables', action='store_true', help='Load large tables')
    args = parser.parse_args()

    # Create SQLite engine
    engine = create_db(args.output_db)

    # Load list of folders
    tables = TABLE_MODEL_MAP.keys()

    if args.large_tables:
        tables = [table for table in tables if table in LARGE_TABLES]

    for table in tables:
        create_table(table, engine)
        load_data(table, engine)    


if __name__ == '__main__':
    main()