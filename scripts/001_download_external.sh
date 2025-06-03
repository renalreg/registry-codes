# Change to tables directory
cd /tables/ukrdc_ods_gp_codes
echo "Working directory: $(pwd)"

BASE_URL="https://files.digital.nhs.uk/assets/ods/current"



# Download and unzip EGP file
curl -L -o egpcur.zip "$BASE_URL/egpcur.zip"
unzip egpcur.zip -d egpcur
rm egpcur.zip

# Download and unzip EPRA file
curl -L -o epraccur.zip "$BASE_URL/epraccur.zip"
unzip epraccur.zip -d epraccur
rm epraccur.zip
