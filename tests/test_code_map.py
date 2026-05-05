# test_csv_whitespace.py

import os
import pytest

ROOT_DIR = "../tables/code_map"


def find_csv_files(root_dir):
    csv_files = []
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    return csv_files


def has_leading_whitespace(line):
    return line.startswith((" ", "\t", "\u00a0"))


def find_comma_whitespace_issues(line):
    in_quotes = False

    for i, char in enumerate(line):
        if char == '"':
            in_quotes = not in_quotes
        elif char == "," and not in_quotes:
            if i + 1 < len(line) and line[i + 1] in (" ", "\t", "\u00a0"):
                return True

    return False


def check_file(filepath):
    issues = []

    with open(filepath, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            if has_leading_whitespace(line):
                issues.append(f"{filepath}:{lineno} -> leading whitespace")

            if find_comma_whitespace_issues(line):
                issues.append(f"{filepath}:{lineno} -> whitespace after comma")

    return issues


def test_csv_whitespace():
    csv_files = find_csv_files(ROOT_DIR)

    all_issues = []

    for file in csv_files:
        all_issues.extend(check_file(file))

    if all_issues:
        pytest.fail("Whitespace issues found:\n" + "\n".join(all_issues))
