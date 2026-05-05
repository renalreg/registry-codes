# fix_csv_whitespace.py

import os
import re

ROOT_DIR = "../tables/code_map"

def find_csv_files(root_dir):
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(".csv"):
                yield os.path.join(root, file)


def clean_line(line):
    # replace non-breaking spaces with normal spaces (or remove entirely)
    line = line.replace("\u00A0", " ")

    # remove leading whitespace
    line = line.lstrip(" \t")

    result = []
    in_quotes = False
    i = 0

    while i < len(line):
        char = line[i]

        if char == '"':
            in_quotes = not in_quotes
            result.append(char)

        elif char == "," and not in_quotes:
            result.append(char)
            i += 1

            while i < len(line) and line[i] in (" ", "\t"):
                i += 1

            continue

        else:
            result.append(char)

        i += 1

    return "".join(result)


def clean_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    cleaned = [clean_line(line) for line in lines]

    with open(filepath, "w", encoding="utf-8") as f:
        f.writelines(cleaned)


def main():
    for filepath in find_csv_files(ROOT_DIR):
        print(f"Cleaning {filepath}")
        clean_file(filepath)


if __name__ == "__main__":
    main()