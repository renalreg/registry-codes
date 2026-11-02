from typing import TypedDict

import pandas as pd
from sqlalchemy import Boolean, DateTime, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import ARRAY, BIT
from ukrdc_sqla.ukrdc import (
    Base,
    Code,
    CodeExclusion,
    CodeMap,
    CodingStandards,
    Facility,
    GPInfo,
    Locations,
    ModalityCodes,
    RRCodes,
    RRDataDefinition,
)


class TableInfo(TypedDict):
    sqla_model: type[Base]
    excluded_columns: list[str]
    unique_columns: list[str]
    dependencies: list[str]


# Map SQLAlchemy types to pandas dtypes for CSV reading
# Use explicit pandas dtype objects for proper nullable handling
SQLA_TO_PANDAS_DTYPE = {
    String: pd.StringDtype(),
    Integer: pd.Int64Dtype(),  # Nullable integer
    Boolean: pd.BooleanDtype(),  # Read as string, convert to bool after
    DateTime: pd.StringDtype(),  # Read as string, convert to datetime after
    Numeric: pd.Float64Dtype(),  # Nullable float
    BIT: pd.StringDtype(),  # Postgres bit string, passed to the database as text
    ARRAY: pd.StringDtype(),  # Arrays stored as strings in CSV
}

# Map directory names to ukrdc-sqla models, define automatically filled columns
# (not in csv files) and specify the key relationship
TABLE_MODEL_MAP: dict[str, TableInfo] = {
    "coding_standards": {
        "sqla_model": CodingStandards,
        "excluded_columns": [],
        "unique_columns": ["coding_standard"],
        "dependencies": [],
    },
    "code_exclusion": {
        "sqla_model": CodeExclusion,
        "excluded_columns": [],
        "unique_columns": ["code", "coding_standard"],
        "dependencies": [],
    },
    "code_list": {
        "sqla_model": Code,
        "excluded_columns": ["creation_date", "update_date"],
        "unique_columns": ["code", "coding_standard"],
        "dependencies": [],
    },
    "code_map": {
        "sqla_model": CodeMap,
        "excluded_columns": ["creation_date", "update_date"],
        "unique_columns": [
            "source_coding_standard",
            "source_code",
            "destination_coding_standard",
            "destination_code",
        ],
        "dependencies": [],
    },
    # "facility": {
    # },
    "facility": {
        "sqla_model": Facility,
        "excluded_columns": ["creation_date", "update_date"],
        "unique_columns": ["facilitycode", "facilitycodestd"],
        "dependencies": ["code_list"],
    },
    "modality_codes": {
        "sqla_model": ModalityCodes,
        "excluded_columns": [],
        "unique_columns": ["registry_code"],
        "dependencies": [],
    },
    "rr_codes": {
        "sqla_model": RRCodes,
        "excluded_columns": [],
        "unique_columns": ["id", "rr_code"],
        "dependencies": [],
    },
    "rr_data_definition": {
        "sqla_model": RRDataDefinition,
        "excluded_columns": [],
        "unique_columns": ["upload_key"],
        "dependencies": [],
    },
    "ukrdc_ods_gp_codes": {
        "sqla_model": GPInfo,
        "excluded_columns": ["creation_date", "update_date"],
        "unique_columns": ["code"],
        "dependencies": [],
    },
    "locations": {
        "sqla_model": Locations,
        "excluded_columns": [],
        "unique_columns": [],
        "dependencies": [],
    },
}

LARGE_TABLES = ["ukrdc_ods_gp_codes"]
