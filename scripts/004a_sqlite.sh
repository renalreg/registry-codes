#!/bin/bash
mkdir -p /tmp
DB_FILE="/output/registry_codes.sqlite"

# Find all subdirectories in /tables, each representing a table
find /tables -mindepth 1 -maxdepth 1 -type d | while read TABLE_PATH; do
    TABLE_NAME=$(basename "$TABLE_PATH")

    SCHEMA_FILE="$TABLE_PATH/schema.sql"
    echo "Processing table: $TABLE_NAME"

    if [ ! -f "$SCHEMA_FILE" ]; then
        echo "Schema file $SCHEMA_FILE not found for table $TABLE_NAME. Skipping."
        continue
    fi


    # Convert to correct sqlite syntax and apply schema
    echo "Transforming schema for $TABLE_NAME..."
    cat "$SCHEMA_FILE" | sed -E \
        -e 's/"extract"\.//g' \
        -e 's/character varying\([0-9]+\)/TEXT/Ig' \
        -e 's/bit\(1\)/INTEGER/Ig' \
        -e 's/DEFAULT[[:space:]]*now\s*\(\)[[:space:]]*NOT[[:space:]]*NULL//Ig' \
        > "/tmp/${TABLE_NAME}_schema.sql"

    # Skip following steps for ukrdc_ods_gp_codes
    if [ "$TABLE_NAME" = "ukrdc_ods_gp_codes" ]; then
        echo "Skipping processing for directory: $TABLE_NAME"
        continue
    fi

    echo "Applying schema for $TABLE_NAME..."
    echo "Contents of /tmp/${TABLE_NAME}_schema.sql:"
    cat "/tmp/${TABLE_NAME}_schema.sql"
    sqlite3 "$DB_FILE" ".read /tmp/${TABLE_NAME}_schema.sql"

    # Find and process all CSV files for this table
    CSV_FILE_LIST=$(find "$TABLE_PATH" -maxdepth 1 -type f -name '*.csv')

    if [ -z "$CSV_FILE_LIST" ]; then
        echo "No CSV files found in $TABLE_PATH for table $TABLE_NAME."
    else
        echo "Found CSV files to process for $TABLE_NAME:"
        echo "$CSV_FILE_LIST"
        
        PROCESSED_ANY_CSV=false
        echo "$CSV_FILE_LIST" | while IFS= read -r CURRENT_CSV_FILE; do
            # Ensure CURRENT_CSV_FILE is not empty (robustness for empty lines from find, though unlikely)
            if [ -z "$CURRENT_CSV_FILE" ]; then
                continue
            fi
            # Basic check for file existence (find should ensure this, but good for safety)
            if [ ! -f "$CURRENT_CSV_FILE" ]; then
                echo "Warning: CSV file '$CURRENT_CSV_FILE' listed by find but not found during loop. Skipping."
                continue
            fi

            echo "Loading data for $TABLE_NAME from $CURRENT_CSV_FILE..."
            sqlite3 "$DB_FILE" <<IMPORT_EOF
.mode csv
.headers off
.import "$CURRENT_CSV_FILE" "$TABLE_NAME"
IMPORT_EOF
            PROCESSED_ANY_CSV=true
        done
        
        # Check if any CSVs were actually processed by the loop
        # Note: PROCESSED_ANY_CSV is in a subshell, so this check needs to be smarter or done via file count.
        ACTUAL_NUM_FILES=$(echo "$CSV_FILE_LIST" | grep -c . || true) # Count non-empty lines, '|| true' to prevent script exit if grep finds nothing and returns 1
        if [ "$ACTUAL_NUM_FILES" -gt 0 ]; then
             echo "Attempted to process $ACTUAL_NUM_FILES CSV file(s) for table $TABLE_NAME."
        else
             # This case implies CSV_FILE_LIST was not empty but grep found no non-empty lines (very unlikely)
             echo "No valid CSV files were processed for table $TABLE_NAME from the list, though the list was not empty."
        fi
    fi

    echo "Finished processing $TABLE_NAME."
    echo "------------------------------------"
done

echo "All tables processed."
