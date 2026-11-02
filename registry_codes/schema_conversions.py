from collections.abc import Callable
from dataclasses import dataclass, field
from decimal import Decimal

import pandas as pd
from pandas.api.extensions import ExtensionDtype
from sqlalchemy import (
    ARRAY, Boolean, Date, DateTime, Float, Integer, Numeric, String, inspect,
)
from sqlalchemy.dialects.postgresql import BIT
from sqlalchemy.types import TypeEngine

# Order matters: subclasses before their parents (Float before Numeric)
_PANDAS_DTYPES = [
    (Boolean, pd.BooleanDtype()),
    (BIT, pd.BooleanDtype()),
    (Float, pd.Float64Dtype()),
    (Integer, pd.Int64Dtype()),    # nullable integer
    (Numeric, pd.Float64Dtype()),  # only reached when asdecimal=False
    (String, pd.StringDtype()),
    (ARRAY, pd.StringDtype()),     # arrays stored as strings in CSV
]


def _case_variants(*words: str) -> list[str]:
    """'yes' -> ['yes', 'Yes', 'YES']; matching in read_csv is case-sensitive."""
    return sorted({v for w in words for v in (w.lower(), w.capitalize(), w.upper())})


# pandas already accepts True/TRUE/true/1 and False/FALSE/false/0; these extend it
TRUE_VALUES = _case_variants("true", "t", "yes", "y")
FALSE_VALUES = _case_variants("false", "f", "no", "n")


def _to_decimal(value: str):
    value = value.strip()
    return Decimal(value) if value else None


@dataclass
class ModelSchema:
    pandas_dtypes: dict[str, ExtensionDtype] = field(default_factory=dict)
    parse_dates: list[str] = field(default_factory=list)
    converters: dict[str, Callable] = field(default_factory=dict)
    sqla_dtypes: dict[str, TypeEngine] = field(default_factory=dict)

    @property
    def read_csv_kwargs(self) -> dict:
        return {
            "dtype": self.pandas_dtypes,
            "parse_dates": self.parse_dates,
            "converters": self.converters,
            "true_values": TRUE_VALUES,
            "false_values": FALSE_VALUES,
        }


def model_schema(model) -> ModelSchema:
    """Build pandas read and SQLAlchemy write mappings from a SQLAlchemy model."""
    schema = ModelSchema()

    for column in inspect(model).columns:
        name, col_type = column.name, column.type
        schema.sqla_dtypes[name] = col_type  # keeps length/precision/scale

        if isinstance(col_type, (DateTime, Date)):
            schema.parse_dates.append(name)
        elif isinstance(col_type, Numeric) and not isinstance(col_type, Float) and col_type.asdecimal:
            schema.converters[name] = _to_decimal  # object column of Decimal
        else:
            schema.pandas_dtypes[name] = next(
                (dtype for sqla_type, dtype in _PANDAS_DTYPES if isinstance(col_type, sqla_type)),
                pd.StringDtype(),
            )

    return schema