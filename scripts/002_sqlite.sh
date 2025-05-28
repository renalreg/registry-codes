apt-get update 
apt-get install sqlite3

# remove reference to extract schema and create tables

mkdir -p /tmp
cat /tables/modality_codes/schema.sql | sed 's/"extract"\.//g' > /tmp/schema.sql
sqlite3 /output/registry_codes.sqlite  .read /tmp/schema.sql

cat /tables/satellite_map/schema.sql | sed 's/"extract"\.//g' > /tmp/schema.sql
sqlite3 /output/registry_codes.sqlite  .read /tmp/schema.sql


# load data from csv
sqlite3 /output/registry_codes.sqlite <<EOF
.mode csv
.import tables/modality_codes/v4.csv modality_codes
.import tables/modality_codes/v5.csv modality_codes
EOF