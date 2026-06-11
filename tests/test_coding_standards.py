# test_standards.py

import os
from collections import defaultdict

import pandas as pd
import pytest

from tests.test_csv_formatting import find_csv_files

_HERE = os.path.dirname(os.path.abspath(__file__))
_TABLES = os.path.join(_HERE, "..", "tables")

ROOT_DIRS = [
    os.path.join(_TABLES, "code_map"),
    os.path.join(_TABLES, "code_list"),
    os.path.join(_TABLES, "code_exclusion"),
    os.path.join(_TABLES, "facility_new"),
]

MASTER_CSV = os.path.join(_TABLES, "coding_standards", "coding_standards.csv")


def normalize(value):
    if pd.isna(value):
        return ""
    return str(value).strip().lower()


def find_matching_columns(columns, match_terms):
    """
    Return all columns whose name contains any term in match_terms.

    Example:
        find_matching_columns(df.columns, ["standard", "control"])
    """
    matches = []

    for col in columns:
        col_lower = col.lower()

        if any(col_lower.endswith(term.lower()) for term in match_terms):
            matches.append(col)

    return matches


@pytest.fixture(scope="session")
def master_data():
    master_df = pd.read_csv(MASTER_CSV)

    if "coding_standard" not in master_df.columns:
        pytest.fail("master.csv missing required column: 'name'")

    if "description" not in master_df.columns:
        pytest.fail("master.csv missing required column: 'description'")

    master_names = {normalize(v) for v in master_df["coding_standard"] if normalize(v)}

    return master_df, master_names


def test_all_standards_exist_in_master(master_data):
    """
    Ensure every standard value in all CSVs exists in master.csv:name
    """
    _, master_names = master_data

    csv_files = find_csv_files(ROOT_DIRS)

    # global accumulator across ALL files
    missing_by_value = defaultdict(set)
    read_errors = []

    for csv_file in csv_files:
        if os.path.abspath(csv_file) == os.path.abspath(MASTER_CSV):
            continue

        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            read_errors.append(f"{csv_file}: failed to read CSV ({e})")
            continue

        matching_cols = find_matching_columns(df.columns, ["standard", "std"])

        values = set()  # type: ignore
        for col in matching_cols:
            values.update(
                v for v in df[col].dropna().astype(str).unique() if normalize(v)
            )

        missing = {v for v in values if normalize(v) not in master_names}

        # accumulate globally (NOT per file reset)
        for value in missing:
            missing_by_value[value].add(csv_file)

    error_lines = []

    # include read errors first (optional but useful)
    if read_errors:
        error_lines.append("CSV READ ERRORS:\n")
        error_lines.extend(read_errors)
        error_lines.append("")

    if missing_by_value:
        error_lines.append("Missing standards grouped by value:\n")

        for value in sorted(missing_by_value.keys()):
            error_lines.append(value)

            for f in sorted(missing_by_value[value]):
                error_lines.append(f"  - {f}")

            error_lines.append("")

    if error_lines:
        pytest.fail("\n".join(error_lines))


def test_master_standards_have_description(master_data):
    """
    Ensure every standard in master.csv has a description
    """
    master_df, _ = master_data
    errors = []

    for idx, row in master_df.iterrows():
        name = normalize(row.get("name"))
        description = row.get("description")

        if name and (pd.isna(description) or not str(description).strip()):
            errors.append(
                f"master.csv row {idx}: standard '{name}' missing description"
            )

    if errors:
        pytest.fail("\n".join(errors))


def test_no_unused_standards_in_master(master_data):
    """
    Ensure every standard in master.csv is referenced in at least one CSV
    in the root directories (code_map, code_list, code_exclusion, facility_new).
    """
    master_df, master_names = master_data

    csv_files = find_csv_files(ROOT_DIRS)

    referenced_standards: set[str] = set()
    read_errors = []

    for csv_file in csv_files:
        if os.path.abspath(csv_file) == os.path.abspath(MASTER_CSV):
            continue

        try:
            df = pd.read_csv(csv_file)
        except Exception as e:
            read_errors.append(f"{csv_file}: failed to read CSV ({e})")
            continue

        matching_cols = find_matching_columns(df.columns, ["standard", "std"])

        for col in matching_cols:
            referenced_standards.update(
                normalize(v)
                for v in df[col].dropna().astype(str).unique()
                if normalize(v)
            )

    # Compare normalized, but report original casing from master_df
    unused_original = [
        v
        for v in master_df["coding_standard"]
        if normalize(v) and normalize(v) not in referenced_standards
    ]

    error_lines = []

    if read_errors:
        error_lines.append("CSV READ ERRORS:\n")
        error_lines.extend(read_errors)
        error_lines.append("")

    if unused_original:
        error_lines.append(
            f"Found {len(unused_original)} standard(s) in master.csv not referenced anywhere:\n"
        )
        for standard in sorted(unused_original):
            error_lines.append(f"  - {standard}")

    if error_lines:
        pytest.fail("\n".join(error_lines))
