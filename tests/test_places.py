"""
Validation of codes which refer to places
"""
from registry_codes.utils import load_data_to_df
import pytest

FACILITIES = load_data_to_df("facility_new")
CODELIST = load_data_to_df("code_list")
CODEMAP = load_data_to_df("code_map")

def test_check_facility_codelist():
    """
    Verify all facilities match to corresponding codes in codelist
    """
    
    # Verify all facilities exist in code list by joining on code and coding standard
    merged_df = FACILITIES.merge(
        CODELIST,
        left_on=["facilitycode", "facilitycodestd"],
        right_on=["code", "coding_standard"],
        how="left",
        indicator=True
    )
    
    missing_facilities = merged_df[merged_df["_merge"] == "left_only"]
    assert len(missing_facilities) == 0, (
        f"Found {len(missing_facilities)} facilities not in code list: "
        f"{missing_facilities[['facilitycode','facilitycodestd']].to_dict('records')}"
    )

def test_first_data_quarter_only_for_renal_centers():
    """Verify first_data_quarter is only set for adult/paediatric renal centers"""

    non_rda_facilities = FACILITIES[
        FACILITIES["firstdataquarter"].notna() & 
        ~FACILITIES["facilitytype"].isin(["Adult Renal Centre", "Paediatric Renal Centre"])
    ]
    
    assert len(non_rda_facilities) == 0, (
        f"Found {len(non_rda_facilities)} facilities with first_data_quarter set but not adult/paediatric renal center: "
        f"{non_rda_facilities[['facilitycode','facilitycodestd']].to_dict('records')}"
    )

def test_satellites_match_main():
    """Ensure satellite facilities metadata matches main facility"""
    
    # Join facilities table to itself via the satellite mapping
    merged_df = FACILITIES.merge(
        CODEMAP[CODEMAP.source_coding_standard == "RR1+_SATELLITE"], 
        left_on="facilitycode", 
        right_on="source_code", 
        how="inner"
    )
    satellite_main_joined = merged_df.merge(FACILITIES, left_on="destination_code", right_on="facilitycode", how="inner")[
        ["facilitycode_x",
        "facilitycode_y",
        "firstdataquarter_x",
        "firstdataquarter_y",
        "startdate_x",
        "startdate_y",
        "enddate_x",
        "enddate_y"]
    ]

    satellite_main_diff = satellite_main_joined[
        (satellite_main_joined["firstdataquarter_x"] != satellite_main_joined["firstdataquarter_y"]) |
        (satellite_main_joined["startdate_x"] != satellite_main_joined["startdate_y"]) |
        (satellite_main_joined["enddate_x"] != satellite_main_joined["enddate_y"]) 
    ]

    assert len(satellite_main_diff) == 0, (
        f"Found {len(satellite_main_diff)} satellites with different metadata to main facility: "
        f"{satellite_main_diff[['facilitycode_x','facilitycode_y']].to_dict('records')}"
    )

def test_feedshare_match_main():
    """Ensure feedshare facilities metadata matches parent facility"""
    
    # Join facilities table to itself via the feedshare mapping
    merged_df = FACILITIES.merge(
        CODEMAP[CODEMAP.source_coding_standard=="FEEDSHARE_CHILD"], 
        left_on="facilitycode", 
        right_on="source_code", 
        how="inner"
    )
    child_parent_joined = merged_df.merge(FACILITIES, left_on="destination_code", right_on="facilitycode", how="inner")[
        ["facilitycode_x",
        "facilitycode_y",
        "firstdataquarter_x",
        "firstdataquarter_y",
        "startdate_x",
        "startdate_y",
        "enddate_x",
        "enddate_y"]
    ]

    child_parent_diff = child_parent_joined[
        (child_parent_joined["firstdataquarter_x"] != child_parent_joined["firstdataquarter_y"]) |
        (child_parent_joined["startdate_x"] != child_parent_joined["startdate_y"]) |
        (child_parent_joined["enddate_x"] != child_parent_joined["enddate_y"]) 
    ]

    assert len(child_parent_diff) == 0, (
        f"Found {len(child_parent_diff)} feedshare mismatches: "
        f"{child_parent_diff[['facilitycode_x','facilitycode_y']].to_dict('records')}"
    )