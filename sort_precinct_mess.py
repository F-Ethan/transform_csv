#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import re

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------
input_file  = 'output/standardized_precincts-2003.csv'
output_file = 'output/standardized_precincts.csv'

os.makedirs(os.path.dirname(output_file), exist_ok=True)

# ----------------------------------------------------------------------
# REGEX PATTERNS
# ----------------------------------------------------------------------
# 1. ABS pattern: 80000...-ABS ...
abs_pattern = re.compile(r'^(80000[0-9]+)\s*-?\s*ABS\s+([0-9]+)$', re.IGNORECASE)

# 2. General pattern: xx-[A-Z]+ xx
letter_pattern = re.compile(r'^([0-9]+)\s*-?\s*([A-Z]+)\s+([0-9]+)$', re.IGNORECASE)

# ----------------------------------------------------------------------
# PROCESS
# ----------------------------------------------------------------------
matched_rows   = []
unmatched_rows = []

with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
    print(f"Reading file: {input_file}")
    reader = csv.DictReader(csvfile)

    for row in reader:
        original = row['standardized'].strip()
        status   = 'Bad'
        standardized = original

        # ---------- 1. ABS pattern ----------
        m = abs_pattern.fullmatch(original)
        if m:
            base, trail = m.group(1), m.group(2)
            # Extract last len(trail) digits from base
            if len(base) >= len(trail) and base[-len(trail):] == trail:
                status = 'Good'
                standardized = f"{base}-ABS {trail}"
            else:
                status = 'Bad - ABS numbers differ'
            entry = {
                'standardized': standardized,
                'original'    : original,
                'Status'      : status
            }
            (matched_rows if status == 'Good' else unmatched_rows).append(entry)
            continue

        # ---------- 2. General letter pattern ----------
        m = letter_pattern.fullmatch(original)
        if m:
            num1, code_raw, num2 = m.group(1), m.group(2), m.group(3)
            code = code_raw.upper()

            if num1 != num2:
                unmatched_rows.append({
                    'standardized': original,
                    'original'    : original,
                    'Status'      : 'Bad - Numbers differ'
                })
                continue

            if not (1 <= len(code) <= 3):
                unmatched_rows.append({
                    'standardized': original,
                    'original'    : original,
                    'Status'      : f'Bad - Code length {len(code)}'
                })
                continue

            status = 'Good'
            standardized = f"{num1}-{code} {num2}"
            matched_rows.append({
                'standardized': standardized,
                'original'    : original,
                'Status'      : status
            })
            continue

        # ---------- No match ----------
        unmatched_rows.append({
            'standardized': original,
            'original'    : original,
            'Status'      : 'Bad - No pattern'
        })

# ----------------------------------------------------------------------
# WRITE OUTPUT
# ----------------------------------------------------------------------
with open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    fieldnames = ['standardized', 'original', 'Status']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(matched_rows)
    writer.writerows(unmatched_rows)

# ----------------------------------------------------------------------
# SUMMARY
# ----------------------------------------------------------------------
total = len(matched_rows) + len(unmatched_rows)
print(f"\nDone!")
print(f"Total precincts processed : {total}")
print(f"Good                      : {len(matched_rows)}")
print(f"Bad / needs review        : {len(unmatched_rows)}")
print(f"Output saved to           : {output_file}")