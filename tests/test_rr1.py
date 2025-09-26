
import requests
import time
import csv

def test_rr1plus_facilities():
    BASE_URL = "https://uat.directory.spineservices.nhs.uk/ORD/2-0-0/organisations/"
    errors = {}
    
    with open('tables/code_list/rr1plus_facilities.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            org_code = row[1]  # assuming 'code' is a column in your CSV
            response = requests.get(BASE_URL + org_code)
            
            if response.status_code != 200:
                errors[org_code] = f"Error: {response.status_code}"
            #else:
            # here we should potentially add an extra check to ensure the name
            # matches the nhs spline
                
                
            # Ensure not more than 5 requests per second
            time.sleep(0.2)
    
    assert not errors, f"Errors occurred: {errors}"

test_rr1plus_facilities()