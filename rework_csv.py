#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import os
from collections import defaultdict
from pathlib import Path

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
MAPPING_FILE = 'output/standardized_precincts-2003.csv'   # original → standardized
INPUT_DIR    = 'files'
OUTPUT_DIR   = 'output'

# Ensure output directories exist
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------
# 1. Load precinct mapping (original → standardized) once
# ----------------------------------------------------------------------
precinct_map = {}
with open(MAPPING_FILE, newline='', encoding='utf-8') as mf:
    reader = csv.DictReader(mf)
    for row in reader:
        original = row['original'].strip()
        standard = row['standardized'].strip()
        if original:  # skip empty rows
            precinct_map[original] = standard

print(f"Loaded {len(precinct_map)} precinct mappings from {MAPPING_FILE}\n")

# ----------------------------------------------------------------------
# Header-like candidate names to avoid when picking template row
# ----------------------------------------------------------------------
HEADER_LIKE = {
    'candidate', 'candidates', 'name', 'party', 'total',
    'votes cast', 'ballots cast', 'overvotes', 'undervotes',
    'registered voters', 'yes', 'no'
}

# ----------------------------------------------------------------------
# Process each CSV file in the files/ folder
# ----------------------------------------------------------------------
input_path = Path(INPUT_DIR)
csv_files = list(input_path.glob("*.csv"))

if not csv_files:
    print(f"No CSV files found in '{INPUT_DIR}/'")
    exit(1)

print(f"Found {len(csv_files)} file(s) to process...\n")

for input_file in csv_files:
    print(f"Processing: {input_file.name}")

    # Define output filename: contracostaca--originalname.csv
    output_filename = f"contracostaca--2002-03-05_Special_{input_file.name}"
    output_file = Path(OUTPUT_DIR) / output_filename

    rows_to_keep = []

    # ------------------------------------------------------------------
    # 2. Read input, apply precinct mapping, drop DELETE rows
    # ------------------------------------------------------------------
    try:
        with open(input_file, newline='', encoding='utf-8') as inf:
            reader = csv.DictReader(inf)
            fieldnames = reader.fieldnames  # preserve original column order

            if 'PrecinctName' not in fieldnames:
                print(f"  Warning: Skipping {input_file.name} – no 'PrecinctName' column")
                continue

            for row in reader:
                old_name = row['PrecinctName'].strip()
                new_name = precinct_map.get(old_name, old_name)

                if new_name.upper() == 'DELETE':
                    continue

                row['PrecinctName'] = new_name
                rows_to_keep.append(row)

    except Exception as e:
        print(f"  Error reading {input_file.name}: {e}")
        continue

    print(f"   → {len(rows_to_keep)} rows after mapping & DELETE removal")

    # ------------------------------------------------------------------
    # 3. Group by (OfficeName, PrecinctName, CandidateParty), sum votes
    # ------------------------------------------------------------------
    vote_sums   = defaultdict(int)
    key_to_rows = defaultdict(list)

    for row in rows_to_keep:
        key = (row['OfficeName'], row['PrecinctName'], row.get('CandidateParty', ''))
        key_to_rows[key].append(row)

        try:
            votes = int(row.get('Votes', 0) or 0)
            vote_sums[key] += votes
        except ValueError:
            print(f"   Warning: Non-integer 'Votes' value in {input_file.name}")

    final_rows = []

    for key, rows in key_to_rows.items():
        office, precinct, party = key

        # Append all original candidate rows
        final_rows.extend(rows)

        # Skip adding "ballots cast" for statistics or measures
        office_lower = office.lower()
        if 'voting statistics' in office_lower or 'bond measure' in office_lower:
            continue

        # Find a clean candidate row to use as template
        template = None
        for r in rows:
            cand = r['CandidateName'].strip().lower()
            if cand and cand not in HEADER_LIKE and not cand.startswith('write-in'):
                template = r.copy()
                break

        if template is None:
            # Fallback: use first row
            template = rows[0].copy()
            print(f"   Warning: Used fallback template for {office} / {precinct}")

        # Create "ballots cast" row
        ballots_row = template.copy()
        ballots_row['CandidateName'] = 'ballots cast'
        ballots_row['Votes'] = str(vote_sums[key])

        # Clear candidate-specific fields
        for col in ('CandidateParty', 'Party', 'Incumbent', 'WriteIn', 'District', 'Seat'):
            if col in ballots_row:
                ballots_row[col] = ''

        final_rows.append(ballots_row)

    # ------------------------------------------------------------------
    # 4. Write output CSV
    # ------------------------------------------------------------------
    try:
        with open(output_file, 'w', newline='', encoding='utf-8') as outf:
            writer = csv.DictWriter(outf, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(final_rows)

        ballots_added = sum(1 for k in key_to_rows if 'voting statistics' not in k[0].lower() and 'bond measure' not in k[0].lower())

        print(f"   → Output saved: {output_file.name}")
        print(f"     • Groups: {len(key_to_rows)}, Ballots-cast rows added: {ballots_added}, Total rows: {len(final_rows)}\n")

    except Exception as e:
        print(f"  Error writing {output_file}: {e}\n")

print("All files processed!")