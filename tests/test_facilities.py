from registry_codes.utils import load_data_to_df
import pandas as pd

FACILITIES = load_data_to_df("facility_new")
CODELIST = load_data_to_df("code_list")
CODEMAP = load_data_to_df("code_map")


def test_facilities_are_rr1plus():
    # check all facility codes are rr1+
    assert all(FACILITIES.facilitycodestd == "RR1+")

    # check facilities are all in the rr1+ codelist
    FACILITIES_NOT_IN_CODELIST = FACILITIES[
        ~FACILITIES.facilitycode.isin(CODELIST.code[CODELIST.coding_standard == "RR1+"])
    ]
    assert len(FACILITIES_NOT_IN_CODELIST) == 0


def test_feedshare_match_main():
    """Ensure feedshare facilities metadata matches parent facility"""

    # Filter to feedshare facilities
    feedshare_facilities_map = CODEMAP[
        CODEMAP.source_coding_standard == "RR1+_FEEDSHARE_CHILD"
    ]

    # Join facilities table to itself via the feedshare mapping
    merged_df = FACILITIES.merge(
        feedshare_facilities_map,
        left_on="facilitycode",
        right_on="source_code",
        how="inner",
    )
    child_parent_joined = merged_df.merge(
        FACILITIES, left_on="destination_code", right_on="facilitycode", how="inner"
    )[
        [
            "facilitycode_x",
            "facilitycode_y",
            "firstdataquarter_x",
            "firstdataquarter_y",
            "startdate_x",
            "startdate_y",
            "enddate_x",
            "enddate_y",
        ]
    ]

    cols_to_compare = [
        "firstdataquarter_x",
        "firstdataquarter_y",
        "startdate_x",
        "startdate_y",
        "enddate_x",
        "enddate_y",
    ]

    child_parent_joined = child_parent_joined.dropna(subset=cols_to_compare, how="all")

    child_parent_diff = child_parent_joined[
        (
            child_parent_joined["firstdataquarter_x"]
            != child_parent_joined["firstdataquarter_y"]
        )
        | (child_parent_joined["startdate_x"] != child_parent_joined["startdate_y"])
        | (child_parent_joined["enddate_x"] != child_parent_joined["enddate_y"])
    ]

    assert len(child_parent_diff) == 0, (
        f"Found {len(child_parent_diff)} feedshare mismatches: "
        f"{child_parent_diff[['facilitycode_x', 'facilitycode_y']].to_dict('records')}"
    )
