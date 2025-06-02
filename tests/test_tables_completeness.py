import csv
from pathlib import Path
    
def loop_though_csv(items_per_line:int, table_name:str, allow_empty:bool=False):
    """
    Function to loop through the csvs in the directory defined by table name and check each
    row has the number of entries we expect. It should return a dictionary of line numbers and what each line contains where there are less or more than items_per_line
    
    Parameters:
        items_per_line: The expected number of items per row
        table_name: The name of the table directory to check
        allow_empty: If False, remove any empty strings from rows before checking count
    """

    # Dictionary to store errors
    errors = {}
    
    # Table directory path
    table_dir = Path(f"tables/{table_name}")
    
    if not table_dir.exists():
        raise FileNotFoundError(f"Table directory {table_dir} does not exist")
    
    # Loop through all CSV files in the directory
    for file_path in table_dir.glob("*.csv"):
        #print(file_path)
        relative_path = file_path.relative_to(Path("."))
        
        with open(file_path, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            for line_num, row in enumerate(reader, 1):
                # If allow_empty is False, filter out empty fields
                filtered_row = row
                if not allow_empty:
                    filtered_row = [field for field in row if field.strip() != '']
                
                # Check if the row has the expected number of fields
                if len(filtered_row) < items_per_line:
                    errors[f"{relative_path}:{line_num}"] = {
                        "file": str(relative_path),
                        "line_number": line_num,
                        "content": row,
                        "filtered_content": filtered_row,
                        "expected_count": items_per_line,
                        "actual_count": len(filtered_row),
                        "note": "Empty fields were removed" if len(filtered_row) != len(row) else ""
                    }
    
    return errors


def test_modality_codes():
    # Test for modality_codes (13 fields)
    errors = loop_though_csv(13, "modality_codes", allow_empty=False)
    
    # Print details of any errors found
    for key, details in errors.items():
        print(f"Error in {details['file']} at line {details['line_number']}")
        print(f"  Expected {details['expected_count']} items, found {details['actual_count']}")
        print(f"  Content: {details['content']}")
    
    assert errors == {}


def test_code_map():
    # Test for code_map (4 fields)
    errors = loop_though_csv(4, "code_map", allow_empty=False)
    
    # Print details of any errors found
    for key, details in errors.items():
        print(f"Error in {details['file']} at line {details['line_number']}")
        print(f"  Expected {details['expected_count']} items, found {details['actual_count']}")
        print(f"  Content: {details['content']}")
    
    assert errors == {}


def test_code_exclusion():
    # Test for code_exclusion (3 fields)
    errors = loop_though_csv(3, "code_exclusion")
    
    # Print details of any errors found
    for key, details in errors.items():
        print(f"Error in {details['file']} at line {details['line_number']}")
        print(f"  Expected {details['expected_count']} items, found {details['actual_count']}")
        print(f"  Content: {details['content']}")
    
    assert errors == {}


def test_code_list():
    # Test for code_list (7 fields)
    errors = loop_though_csv(3, "code_list", allow_empty=False)
    
    # Print details of any errors found
    for key, details in errors.items():
        print(f"Error in {details['file']} at line {details['line_number']}")
        print(f"  Expected {details['expected_count']} items, found {details['actual_count']}")
        print(f"  Content: {details['content']}")
    
    assert errors == {}


def test_rr_codes():
    # Test for rr_codes (8 fields)
    errors = loop_though_csv(8, "rr_codes")
    
    # Print details of any errors found
    for key, details in errors.items():
        print(f"Error in {details['file']} at line {details['line_number']}")
        print(f"  Expected {details['expected_count']} items, found {details['actual_count']}")
        print(f"  Content: {details['content']}")
    
    assert errors == {}


def test_rr_data_definition():
    # Test for rr_data_definition (21 fields - based on schema analysis)
    errors = loop_though_csv(21, "rr_data_definition")
    
    # Print details of any errors found
    for key, details in errors.items():
        print(f"Error in {details['file']} at line {details['line_number']}")
        print(f"  Expected {details['expected_count']} items, found {details['actual_count']}")
        print(f"  Content: {details['content']}")
    
    assert errors == {}


def test_facility():
    # Test for facility (1 field in CSV)
    errors = loop_though_csv(1, "facility")
    
    # Print details of any errors found
    for key, details in errors.items():
        print(f"Error in {details['file']} at line {details['line_number']}")
        print(f"  Expected {details['expected_count']} items, found {details['actual_count']}")
        print(f"  Content: {details['content']}")
    
    assert errors == {}


def test_satellite_map():
    # Test for satellite_map (2 fields)
    errors = loop_though_csv(2, "satellite_map")
    
    # Print details of any errors found
    for key, details in errors.items():
        print(f"Error in {details['file']} at line {details['line_number']}")
        print(f"  Expected {details['expected_count']} items, found {details['actual_count']}")
        print(f"  Content: {details['content']}")
    
    assert errors == {}
