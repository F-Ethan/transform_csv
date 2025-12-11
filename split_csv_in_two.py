#!/usr/bin/env python3
"""
split_csv_flexible.py

Advanced CSV splitter with multiple split strategies:
- Split at a specific line number
- Split when a keyword first appears in a column
- Split into "has value" vs "empty" in a column
- Always sorts by chosen column first

Just edit the config section at the top!
"""

import csv
from pathlib import Path
import glob
from collections import defaultdict

# ----------------------------------------------------------------------
# GLOBAL CONFIGURATION – EDIT THESE SETTINGS
# ----------------------------------------------------------------------
INPUT_CSV       = "files/none.csv"
AUTO_DETECT     = True                                  # Auto-find the only .csv in folder

# === SORTING ===
SORT_FIELD      = "CandidateParty"                          # Column to sort by (case-insensitive)

# === SPLIT MODE === Choose ONE of the three modes below
SPLIT_MODE = "keyword"  # Options: "line", "keyword", "non_empty"

# Mode: "line" → split at specific line number (including header)
SPLIT_LINE = 230721

# Mode: "keyword" → split when this keyword first appears (case-insensitive)
KEYWORD_COLUMN  = "OfficeName"       # Column to search for keyword
KEYWORD         = "Voting Statistics"            # First row containing this (in KEYWORD_COLUMN) starts Part 2

# Mode: "non_empty" → all rows with value in column → Part 1, empty → Part 2
NON_EMPTY_COLUMN = "CandidateParty"      # Rows with non-empty value here go to Part 1

# === OUTPUT ===
OUTPUT_PREFIX   = "output/split"     # Will create: split_part1.csv, split_part2.csv (or more if keyword creates multiple)
# ----------------------------------------------------------------------


def main():
    input_path = resolve_input_path()
    if not input_path:
        return

    print(f"Reading: {input_path.name}")
    rows, fieldnames = read_csv_rows(input_path)
    if not rows:
        return

    print(f"Sorting by '{SORT_FIELD}'...")
    rows.sort(key=lambda r: (r.get(SORT_FIELD) or "").strip().lower())

    if SPLIT_MODE == "line":
        split_by_line_number(rows, fieldnames, input_path)
    elif SPLIT_MODE == "keyword":
        split_by_keyword(rows, fieldnames, input_path)
    elif SPLIT_MODE == "non_empty":
        split_by_non_empty(rows, fieldnames, input_path)
    else:
        print(f"Error: Unknown SPLIT_MODE: {SPLIT_MODE}")
        print("   Choose from: 'line', 'keyword', 'non_empty'")


def resolve_input_path():
    if AUTO_DETECT:
        csv_files = glob.glob("*.csv") + glob.glob("files/*.csv")
        csv_files = [f for f in csv_files if Path(f).is_file()]
        if len(csv_files) == 1:
            path = Path(csv_files[0])
            print(f"Auto-detected input: {path}")
            return path
        elif len(csv_files) > 1:
            print("Multiple CSVs found. Please set AUTO_DETECT=False and specify INPUT_CSV.")
            print("Found:", csv_files)
            return None

    path = Path(INPUT_CSV)
    if not path.exists():
        print(f"Error: Input file not found: {path}")
        return None
    return path


def read_csv_rows(input_path):
    with open(input_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames:
            print("Error: No columns detected in CSV.")
            return [], None

        if SORT_FIELD not in fieldnames:
            print(f"Warning: SORT_FIELD '{SORT_FIELD}' not in CSV.")
            print(f"Available: {fieldnames}")
            return [], None

        rows = list(reader)
        print(f"Loaded {len(rows):,} data rows + header")
        return rows, fieldnames


def split_by_line_number(rows, fieldnames, input_path):
    total_rows = len(rows)
    split_idx = min(SPLIT_LINE - 1, total_rows)  # -1 because header is line 1

    part1 = rows[:split_idx]
    part2 = rows[split_idx:]

    stem = input_path.stem
    write_split_files(part1, part2, fieldnames, stem, suffix1="_part1", suffix2="_part2")


def split_by_keyword(rows, fieldnames, input_path):
    if KEYWORD_COLUMN not in rows[0]:
        print(f"Error: KEYWORD_COLUMN '{KEYWORD_COLUMN}' not found in CSV.")
        return

    keyword_lower = KEYWORD.strip().lower()
    split_idx = None

    for i, row in enumerate(rows):
        value = (row.get(KEYWORD_COLUMN) or "").strip().lower()
        if keyword_lower in value:
            split_idx = i
            print(f"Keyword '{KEYWORD}' first found at row {i+2} (data row {i+1})")
            print(f"   Value: '{row.get(KEYWORD_COLUMN)}'")
            break

    if split_idx is None:
        print(f"Warning: Keyword '{KEYWORD}' not found. Writing all to part1.")
        part1 = rows
        part2 = []
    else:
        part1 = rows[:split_idx]
        part2 = rows[split_idx:]

    stem = input_path.stem
    write_split_files(part1, part2, fieldnames, stem,
                      suffix1=f"_before_{KEYWORD.replace(' ', '_')}",
                      suffix2=f"_from_{KEYWORD.replace(' ', '_')}_onward")


def split_by_non_empty(rows, fieldnames, input_path):
    if NON_EMPTY_COLUMN not in rows[0]:
        print(f"Error: NON_EMPTY_COLUMN '{NON_EMPTY_COLUMN}' not found.")
        return

    has_value = []
    no_value = []

    for row in rows:
        val = row.get(NON_EMPTY_COLUMN) or ""
        if val.strip():
            has_value.append(row)
        else:
            no_value.append(row)

    print(f"Split by non-empty '{NON_EMPTY_COLUMN}':")
    print(f"   {len(has_value):,} rows WITH value")
    print(f"   {len(no_value):,} rows EMPTY")

    stem = input_path.stem
    col_clean = NON_EMPTY_COLUMN.replace(" ", "_")
    write_split_files(has_value, no_value, fieldnames, stem,
                      suffix1=f"_{col_clean}_filled",
                      suffix2=f"_{col_clean}_empty")


def write_split_files(part1, part2, fieldnames, stem, suffix1="_part1", suffix2="_part2"):
    Path(OUTPUT_PREFIX).parent.mkdir(parents=True, exist_ok=True)

    out1 = Path(OUTPUT_PREFIX).parent / f"{stem}{suffix1}.csv"
    out2 = Path(OUTPUT_PREFIX).parent / f"{stem}{suffix2}.csv"

    # Write Part 1
    with open(out1, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(part1)

    # Write Part 2 (only if it has data)
    if part2:
        with open(out2, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(part2)
        print(f"Success! Part 2 → {out2.name} ({len(part2) + 1} lines)")
    else:
        print("Part 2 is empty — not created.")

    print(f"Success! Part 1 → {out1.name} ({len(part1) + 1} lines)")


if __name__ == "__main__":
    main()