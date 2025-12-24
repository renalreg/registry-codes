from ukrdc_sqla.ukrdc import (
    Code,
    CodeMap,
    CodeExclusion,
    ModalityCodes,
    RRCodes,
    RRDataDefinition,
    GPInfo,
    Facility,
    Base,
)
from typing import TypedDict
from sqlalchemy import String, Integer, Boolean, DateTime, Numeric
from sqlalchemy.dialects.postgresql import ARRAY, BIT
import pandas as pd


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
    Boolean: pd.StringDtype(),  # Read as string, convert to bool after
    DateTime: pd.StringDtype(),  # Read as string, convert to datetime after
    Numeric: pd.Float64Dtype(),  # Nullable float
    BIT: pd.StringDtype(),  # Read as string, convert to bool after
    ARRAY: pd.StringDtype(),  # Arrays stored as strings in CSV
}

# Map directory names to ukrdc-sqla models, define automatically filled columns
# (not in csv files) and specify the key relationship
TABLE_MODEL_MAP: dict[str, TableInfo] = {
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
    "facility_new": {
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
}

LARGE_TABLES = ["ukrdc_ods_gp_codes"]
