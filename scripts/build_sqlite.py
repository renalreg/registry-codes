from utils.utils import TABLE_MODEL_MAP, create_table, load_data
from sqlalchemy import create_engine
import argparse 

def create_db(output_db):
    engine = create_engine(f'sqlite:///{output_db}')
    return engine


def main():
    parser = argparse.ArgumentParser(description='Build SQLite database from ukrdc-sqla models and CSV data')
    parser.add_argument('output_db', help='Output SQLite database file path')
    parser.add_argument('--tables-dir', default='tables', help='Path to tables directory')
    args = parser.parse_args()

    # Create SQLite engine
    engine = create_db(args.output_db)

    # Load list of folders
    tables = TABLE_MODEL_MAP.keys()
    print(tables)
    for table in tables:
        create_table(table, engine)
        load_data(table, engine)
    
    # Simple verification query
    print("\nVerifying loaded data:")
    """
    with engine.connect() as conn:
        for table_name in TABLE_MODEL_MAP.keys():
            model = TABLE_MODEL_MAP[table_name]
            result = conn.execute(text(f"SELECT COUNT(*) AS row_count FROM {model.__tablename__}"))
            count = result.scalar()
            print(f"{model.__tablename__}: {count} rows")
    """
if __name__ == '__main__':
    main()