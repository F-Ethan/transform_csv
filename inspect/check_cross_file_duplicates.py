import os
import csv
from collections import defaultdict

folder = "../2002-03-05"
# Page + Row + Column uniquely identify each row from the source PDF
key_cols = ['Page', 'Row', 'Column']
# Extra context columns for display only
display_cols = ['CandidateName', 'PrecinctName', 'CandidateParty']

# key -> set of filenames that contain it
key_to_files = defaultdict(set)
# key -> display info (from first occurrence)
key_to_display = {}

for filename in sorted(os.listdir(folder)):
    if not filename.endswith('.csv'):
        continue
    if '_pdf.csv' in filename:
        continue  # skip the original source file
    filepath = os.path.join(folder, filename)
    with open(filepath, 'r', newline='', encoding='utf-8', errors='replace') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            key = tuple(row.get(col, '').strip() for col in key_cols)
            if not any(key):
                continue  # skip rows with no page/row/col
            key_to_files[key].add(filename)
            if key not in key_to_display:
                key_to_display[key] = tuple(row.get(col, '').strip() for col in display_cols)

# Find keys that appear in more than one file
duplicates = {k: v for k, v in key_to_files.items() if len(v) > 1}

print(f"Key columns: {key_cols}")
print(f"Total unique source rows across all party files: {len(key_to_files):,}")
print(f"Rows found in 2+ party files (true duplicates): {len(duplicates):,}")
print()

if duplicates:
    print(f"{'Page':>5} {'Row':>4} {'Col':>4}  {'CandidateName':<35} {'PrecinctName':<30} {'Party':<20}  Files")
    print("-" * 140)
    for key, files in sorted(duplicates.items(), key=lambda x: (-len(x[1]), x[0])):
        page, row, col = key
        candidate, precinct, party = key_to_display[key]
        files_str = ", ".join(sorted(f.replace('contracostaca--2002-03-05_Special_', '').replace('.csv', '') for f in files))
        print(f"{page:>5} {row:>4} {col:>4}  {candidate:<35} {precinct:<30} {party:<20}  {files_str}")
else:
    print("No cross-file duplicates found.")
