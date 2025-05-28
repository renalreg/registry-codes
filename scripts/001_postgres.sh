# intialise the extract schema
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB"  -c 'CREATE SCHEMA IF NOT EXISTS "extract";'
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -c "ALTER USER "$POSTGRES_USER" WITH SUPERUSER;"


# initialise the modality codes table from csv
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB"  -f tables/modality_codes/schema.sql

# copy data 
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<EOF
\copy extract.modality_codes FROM 'tables/modality_codes/v4.csv' WITH (FORMAT csv)
EOF

# dump data
pg_dump --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --schema=extract --clean --if-exists --no-owner --no-privileges > /output/registry_codes_dump.sql