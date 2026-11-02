import pytest
from sqlalchemy import Boolean, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from registry_codes.utils import coerce_sqla_types


class _Base(DeclarativeBase):
    pass


class _FlagRow(_Base):
    __tablename__ = "flag_row"
    code: Mapped[str] = mapped_column(String, primary_key=True)
    flag: Mapped[bool] = mapped_column(Boolean)


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
    result = coerce_sqla_types({"code": "X", "flag": raw}, _FlagRow)
    assert result["flag"] is expected


def test_unknown_boolean_value_raises():
    with pytest.raises(ValueError, match="flag"):
        coerce_sqla_types({"code": "X", "flag": "yes please"}, _FlagRow)
