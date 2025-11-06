# Change to tables directory
cd /tables/ukrdc_ods_gp_codes
echo "Working directory: $(pwd)"

BASE_URL="https://www.odsdatasearchandexport.nhs.uk/api"



# Download and unzip EGP file
curl -L -o egpcur.csv "$BASE_URL/getReport?report=egpcur"

# Download and unzip EPRA file
curl -L -o epraccur.csv "$BASE_URL/getReport?report=epraccur"
