# Change to tables directory
cd /tables/ukrdc_ods_gp_codes
echo "Working directory: $(pwd)"

BASE_URL="https://files.digital.nhs.uk/assets/ods/current"



# Download and unzip EGP file
curl -L -o egpcur.zip "$BASE_URL/egpcur.zip"
unzip egpcur.zip
rm egpcur.zip

# Download and unzip EPRA file
curl -L -o epraccur.zip "$BASE_URL/epraccur.zip"
unzip epraccur.zip
rm epraccur.zip

# Process raw files into a format which allow them to be directly loaded into
# tables 
echo "Transforming csvs for convenience"
awk -v type=GP -f /scripts/process_ods_codes.awk egpcur.csv > gp_processed.csv
awk -v type=PRACTICE -f /scripts/process_ods_codes.awk epraccur.csv > practice_processed.csv