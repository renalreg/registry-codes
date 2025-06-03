# TODO: use a loop and loop through all the tables

# convert to correct sqlite syntax
mkdir -p /tmp
cat /tables/modality_codes/schema.sql | sed -E \
    -e 's/"extract"\.//g' \
    -e 's/character varying\([0-9]+\)/TEXT/Ig' \
    -e 's/bit\(1\)/INTEGER/Ig' \
    > /tmp/schema.sql

sqlite3 /output/registry_codes.sqlite  ".read /tmp/schema.sql"

# load data from csv
sqlite3 /output/registry_codes.sqlite <<EOF
.mode csv
.headers off
.import /tables/modality_codes/v4.csv modality_codes
EOF

#sqlite3 /output/registry_codes.sqlite <<EOF
#.mode column
#.headers on
#SELECT * FROM modality_codes LIMIT 10;
#EOF
