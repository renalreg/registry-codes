import os
from collections import defaultdict

import pandas as pd
import pytest

import ukrdc_sqla.ukrdc

from tests.test_csv_formatting import find_csv_files

_HERE = os.path.dirname(os.path.abspath(__file__))
_TABLES = os.path.join(_HERE, "..", "tables")

# Each directory name must match a table name in ukrdc_sqla.ukrdc
ROOT_DIRS = [
    os.path.join(_TABLES, "code_map"),
    os.path.join(_TABLES, "code_list"),
    os.path.join(_TABLES, "code_exclusion"),
    os.path.join(_TABLES, "facility_new"),
]


def normalize(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def _get_sqla_tables():
    """
    Return {table_name: sqlalchemy.Table} for every model in ukrdc_sqla.ukrdc.

    Uses the declarative Base metadata where available, otherwise falls back
    to scanning the module for mapped classes.
    """
    base = getattr(ukrdc_sqla.ukrdc, "Base", None)
    if base is not None and hasattr(base, "metadata"):
        tables = base.metadata.tables.values()
    else:
        tables = {
            obj.__table__
            for obj in vars(ukrdc_sqla.ukrdc).values()
            if hasattr(obj, "__table__")
        }

    # key by bare table name (ignoring schema, e.g. "extract.code_map")
    return {table.name.lower(): table for table in tables}


SQLA_TABLES = _get_sqla_tables()


def primary_key_columns(table):
    """Return the primary key column names for a SQLAlchemy Table, in order."""
    return [col.name for col in table.primary_key.columns]


def table_name_for_dir(root_dir):
    return os.path.basename(os.path.normpath(root_dir)).lower()


@pytest.mark.parametrize("root_dir", ROOT_DIRS, ids=table_name_for_dir)
def test_duplicates(root_dir):
    """
    Ensure no two rows across all CSVs in a table directory share the same
    primary key combination (as defined by the ukrdc_sqla model).
    """
    table_name = table_name_for_dir(root_dir)
    table = SQLA_TABLES.get(table_name)

    if table is None:
        pytest.fail(f"No SQLAlchemy table named '{table_name}' in ukrdc_sqla.ukrdc")

    pk_cols = primary_key_columns(table)
    if not pk_cols:
        pytest.fail(f"Table '{table_name}' has no primary key defined")

    csv_files = find_csv_files([root_dir])

    # global accumulator across ALL files in this directory:
    # pk combo -> [(file, line_number), ...]
    occurrences = defaultdict(list)
    read_errors = []
    column_errors = []

    for csv_file in csv_files:
        try:
            # read everything as strings so "01" and "1" aren't silently merged
            df = pd.read_csv(csv_file, dtype=str, keep_default_na=False)
        except Exception as e:
            read_errors.append(f"{csv_file}: failed to read CSV ({e})")
            continue

        # case/whitespace-insensitive header lookup
        col_lookup = {c.strip().lower(): c for c in df.columns}
        missing = [pk for pk in pk_cols if pk.lower() not in col_lookup]

        if missing:
            column_errors.append(
                f"{csv_file}: missing primary key column(s) {missing} "
                f"(expected {pk_cols})"
            )
            continue

        csv_pk_cols = [col_lookup[pk.lower()] for pk in pk_cols]

        for idx, row in enumerate(df[csv_pk_cols].itertuples(index=False, name=None)):
            key = tuple(normalize(v) for v in row)
            # +2: one for the header row, one for 1-based line numbers
            occurrences[key].append((csv_file, idx + 2))

    duplicates = {k: v for k, v in occurrences.items() if len(v) > 1}

    error_lines = []

    if read_errors:
        error_lines.append("CSV READ ERRORS:\n")
        error_lines.extend(read_errors)
        error_lines.append("")

    if column_errors:
        error_lines.append("PRIMARY KEY COLUMN ERRORS:\n")
        error_lines.extend(column_errors)
        error_lines.append("")

    if duplicates:
        total_lines = sum(len(v) for v in duplicates.values())
        error_lines.append(
            f"Found {len(duplicates)} duplicated primary key combo(s) "
            f"across {total_lines} line(s) in '{table_name}' "
            f"(primary key: {', '.join(pk_cols)}):\n"
        )

        for key in sorted(duplicates):
            combo = ", ".join(f"{col}={val!r}" for col, val in zip(pk_cols, key))
            error_lines.append(combo)

            for f, line in sorted(duplicates[key]):
                error_lines.append(f"  - {f}:{line}")

            error_lines.append("")

    if error_lines:
        pytest.fail("\n".join(error_lines))
