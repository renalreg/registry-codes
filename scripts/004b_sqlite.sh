#!/bin/bash

# Create database excluding ods codes
echo "Creating ods exclusive database..."
/scripts/004a_sqlite.sh "/output/registry_codes.sqlite"

# Create database that will include ods codes
echo "Creating ods include database..."
/scripts/004a_sqlite.sh "/output/registry_codes_ods.sqlite"

# Import the ODS codes
sqlite3 "/output/registry_codes_ods.sqlite" ".read /tmp/ukrdc_ods_gp_codes_schema.sql"
ODS_DIR="/tables/ukrdc_ods_gp_codes"

# Import GP CSV file
if [ -f "$ODS_DIR/gp_processed.csv" ]; then
    echo "Loading GP data from gp_processed.csv..."
    sqlite3 "/output/registry_codes_ods.sqlite" <<IMPORT_EOF
.mode csv
.separator ";"
.headers off
.import "$ODS_DIR/gp_processed.csv" "ukrdc_ods_gp_codes"
IMPORT_EOF
else
    echo "WARNING: GP CSV file not found"
fi

# Import Practice CSV file
if [ -f "$ODS_DIR/practice_process.csv" ]; then
    echo "Loading Practice data from practice_process.csv..."
    sqlite3 "/output/registry_codes_ods.sqlite" <<IMPORT_EOF
.mode csv
.separator ";"
.headers off
.import "$ODS_DIR/practice_process.csv" "ukrdc_ods_gp_codes"
IMPORT_EOF
else
    echo "WARNING: Practice CSV file not found"
fi

echo "ODS codes added to database."
echo "All SQLite databases built."