#!/bin/bash
# Registry Codes Postgres Database Builder
# Creates tables from schema files and imports CSV data into PostgreSQL

set -e

mkdir -p /output

# Initialize the extract schema
echo "Creating extract schema..."
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c 'CREATE SCHEMA IF NOT EXISTS "extract";'
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -c "ALTER USER "$POSTGRES_USER" WITH SUPERUSER;"

# Build each of the internal tables
# code_exclusion
echo "Processing code_exclusion..."
echo "# Code exclusion defines codes to be excluded from processing"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f tables/code_exclusion/schema.sql

# Loop through CSV files in code_exclusion
for csv_file in tables/code_exclusion/*.csv; do
    if [ -f "$csv_file" ]; then
        echo "  Importing data from $(basename "$csv_file")"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOF
\copy extract.code_exclusion FROM '$csv_file' WITH (FORMAT csv)
EOF
    fi
done


# code_list
echo "Processing code_list: TODO after testing"
echo "# Code list contains various coding standards and their descriptions"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f tables/code_list/schema.sql

# Loop through CSV files in code_list
for csv_file in tables/code_list/*.csv; do
    if [ -f "$csv_file" ]; then
        echo "  Importing data from $(basename "$csv_file")"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOF
\copy extract.code_list(coding_standard, code, description, object_type, units, pkb_reference_range, pkb_comment) FROM '$csv_file' WITH (FORMAT csv)
EOF
    fi
done


# code_map
echo "TODO: Processing code_map..."
echo "# Code map defines relationships between different coding systems"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f tables/code_map/schema.sql

# Loop through CSV files in code_map
for csv_file in tables/code_map/*.csv; do
    if [ -f "$csv_file" ]; then
        echo "  Importing data from $(basename "$csv_file")"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOF
\copy extract.code_map(source_coding_standard, source_code, destination_coding_standard, destination_code) FROM '$csv_file' WITH (FORMAT csv)
EOF
    fi
done

# facility
echo "Processing facility..."
echo "# Facility codes identify healthcare facilities"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f tables/facility/schema.sql

# Loop through CSV files in facility
for csv_file in tables/facility/*.csv; do
    if [ -f "$csv_file" ]; then
        echo "  Importing data from $(basename "$csv_file")"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOF
\copy extract.facility FROM '$csv_file' WITH (FORMAT csv)
EOF
    fi
done

# modality_codes
echo "Processing modality_codes..."
echo "# Modality codes define treatment types for renal replacement therapy"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f tables/modality_codes/schema.sql

# Loop through CSV files in modality_codes
# TODO: remove v5 exception once all the coulmns have been filled out
for csv_file in tables/modality_codes/*.csv; do
    if [ -f "$csv_file" ] && [ "$(basename "$csv_file")" != "v5.csv" ]; then
        echo "  Importing data from $(basename "$csv_file")"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOF
\copy extract.modality_codes FROM '$csv_file' WITH (FORMAT csv)
EOF
    elif [ "$(basename "$csv_file")" = "v5.csv" ]; then
        echo "  Skipping v5.csv as requested"
    fi
done


# rr_codes
echo "Processing rr_codes..."
echo "# RR codes are specific to the Renal Registry"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f tables/rr_codes/schema.sql

# Loop through CSV files in rr_codes
for csv_file in tables/rr_codes/*.csv; do
    if [ -f "$csv_file" ]; then
        echo "  Importing data from $(basename "$csv_file")"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOF
\copy extract.rr_codes FROM '$csv_file' WITH (FORMAT csv)
EOF
    fi
done

# rr_data_definition
echo "Processing rr_data_definition..."
echo "# RR data definitions describe the structure of registry data"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f tables/rr_data_definition/schema.sql

# Loop through CSV files in rr_data_definition
for csv_file in tables/rr_data_definition/*.csv; do
    if [ -f "$csv_file" ]; then
        echo "  Importing data from $(basename "$csv_file")"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOF
\copy extract.rr_data_definition FROM '$csv_file' WITH (FORMAT csv)
EOF
    fi
done


# satellite_map
echo "Processing satellite_map..."
echo "# Satellite map links satellite units to main renal centers"
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f tables/satellite_map/schema.sql

# Loop through CSV files in satellite_map
for csv_file in tables/satellite_map/*.csv; do
    if [ -f "$csv_file" ]; then
        echo "  Importing data from $(basename "$csv_file")"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOF
\copy extract.satellite_map(satellite_code, main_unit_code) FROM '$csv_file' WITH (FORMAT csv)
EOF
    fi
done


# ukrdc_ods_gp_codes
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -f tables/ukrdc_ods_gp_codes/schema.sql

# Process GP data
awk -v type=GP -f scripts/process_ods_codes.awk tables/ukrdc_ods_gp_codes/egpcur/egpcur.csv > /tmp/gp_processed.csv

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOF
\copy extract.ukrdc_ods_gp_codes(code, name, address1, postcode, phone, type) FROM '/tmp/gp_processed.csv' WITH (FORMAT csv, DELIMITER ';')
EOF


# Process Practice data
awk -v type=PRACTICE -f scripts/process_ods_codes.awk tables/ukrdc_ods_gp_codes/epraccur/epraccur.csv > /tmp/practice_processed.csv

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<EOF
\copy extract.ukrdc_ods_gp_codes(code, name, address1, postcode, phone, type) FROM '/tmp/practice_processed.csv' WITH (FORMAT csv, DELIMITER ';')
EOF


# Dump all data from extract schema
echo "Creating database dump..."
pg_dump --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" --schema=extract --clean --if-exists --no-owner --no-privileges -Fc > /output/registry_codes.dump

echo "Done! Database dump created at /output/registry_codes.dump"

# Signal the container to stop now that the script is complete and message is printed
# TODO: this probably doesn't do anything...investigate
kill 1