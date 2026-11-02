import io
from typing import cast

import pandas as pd
import pytest
from sqlalchemy import Boolean, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from ukrdc_sqla.ukrdc import Base

from registry_codes.utils import coerce_sqla_types, pandas_dtypes_for_table


class _TestBase(DeclarativeBase):
    pass


class _FlagRow(_TestBase):
    __tablename__ = "flag_row"
    code: Mapped[str] = mapped_column(String, primary_key=True)
    flag: Mapped[bool] = mapped_column(Boolean)


# coerce_sqla_types expects a ukrdc_sqla model. The cast only tells mypy
# to accept the small test model. It changes nothing at runtime.
FLAG_MODEL = cast(type[Base], _FlagRow)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("True", True),
        ("False", False),
        ("true", True),
        ("false", False),
        ("", False),
        (None, False),
    ],
)
def test_boolean_values_are_parsed_by_text(raw, expected):
    result = coerce_sqla_types({"code": "X", "flag": raw}, FLAG_MODEL)
    assert result["flag"] is expected


def test_unknown_boolean_value_raises():
    with pytest.raises(ValueError, match="flag"):
        coerce_sqla_types({"code": "X", "flag": "yes please"}, FLAG_MODEL)


def test_facility_booleans_are_read_as_booleans():
    dtypes = pandas_dtypes_for_table("facility")
    csv = io.StringIO("pkbout\nTrue\nFalse\n\n")
    df = pd.read_csv(csv, dtype={"pkbout": dtypes["pkbout"]}, skip_blank_lines=False)
    values = df["pkbout"].tolist()
    assert values[0] is True
    assert values[1] is False
    assert pd.isna(values[2])
