"""
Simple utility to load data into a postgres database
"""


import os

from sqlalchemy import create_engine, text
from registry_codes.utils import TABLE_MODEL_MAP, create_table, load_data


def sort_tables_by_dependencies(tables_dict):
    """
    Sort tables based on their dependencies.
    Iterates through tables and ensures dependencies appear before dependents.
    """
    ordered = list(tables_dict.keys())
    
    changed = True
    max_iterations = len(ordered) * len(ordered)  # Prevent infinite loops
    iterations = 0
    
    while changed and iterations < max_iterations:
        changed = False
        iterations += 1
        
        for i, table in enumerate(ordered):
            dependencies = tables_dict[table].get("dependencies", [])
            
            for dep in dependencies:
                if dep in ordered:
                    dep_index = ordered.index(dep)
                    
                    # If dependency comes after this table, move it before
                    if dep_index > i:
                        ordered.remove(dep)
                        ordered.insert(i, dep)
                        changed = True
                        break
            
            if changed:
                break
    
    if iterations >= max_iterations:
        raise ValueError("Could not resolve table dependencies - possible circular dependency")
    
    return ordered


def main():
    # set url for local testing 
    url = os.getenv("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:8000/postgres")
    print(f"DATABASE_URL: {url}")
    engine = create_engine(url = url)
    with engine.connect() as conn:
        conn.execute(text(
            """
               DROP SCHEMA IF EXISTS "extract" CASCADE;
               CREATE SCHEMA "extract"
                 AUTHORIZATION postgres;

               GRANT ALL ON SCHEMA "extract" TO postgres;

               GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA extract TO postgres;

               -- set search path for the database 
               ALTER DATABASE "postgres" SET search_path TO "$user",extract;"""
        ))
        conn.commit()
        print("created extract schema")

    # Sort tables based on dependencies
    tables = sort_tables_by_dependencies(TABLE_MODEL_MAP)
    print(f"Table creation order: {tables}")
    
    # First pass: set schema on all models
    for table in tables:
        model = TABLE_MODEL_MAP[table]["sqla_model"]
        model.__table__.schema = "extract"
    
    # Second pass: create tables and load data
    for table in tables:
        create_table(table, engine, schema="extract")
        load_data(table, engine, schema="extract")
        print(table)
    

if __name__ == '__main__':
    main()