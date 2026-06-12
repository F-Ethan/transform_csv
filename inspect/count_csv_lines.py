import os
import glob
import csv

folder = "../files"

all_csv_files = sorted(glob.glob(os.path.join(folder, "*.csv")))

if not all_csv_files:
    print(f"No CSV files found in '{folder}'")
else:
    source_files = [f for f in all_csv_files if "_pdf.csv" in os.path.basename(f)]
    party_files = [f for f in all_csv_files if "_pdf.csv" not in os.path.basename(f)]

    def count_non_null_rows(filepath):
        """Count data rows where at least one field is non-empty (excludes header)."""
        count = 0
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            next(reader, None)  # skip header
            for row in reader:
                if any(field.strip() for field in row):
                    count += 1
        return count

    print(f"{'File':<55} {'Non-Null Data Rows':>18}")
    print("-" * 75)

    # Original source file(s)
    source_total = 0
    for filepath in source_files:
        filename = os.path.basename(filepath)
        n = count_non_null_rows(filepath)
        source_total += n
        print(f"[ORIGINAL] {filename:<44} {n:>18,}")

    print()

    # Party files
    party_total = 0
    for filepath in party_files:
        filename = os.path.basename(filepath)
        n = count_non_null_rows(filepath)
        party_total += n
        print(f"           {filename:<44} {n:>18,}")

    print("-" * 75)
    print(f"{'Party files total':<55} {party_total:>18,}")
    print(f"{'Original file total':<55} {source_total:>18,}")
    print()

    if source_total == 0:
        print("WARNING: Original file has 0 rows, cannot compare.")
    elif party_total <= source_total:
        diff = source_total - party_total
        print(
            f"OK: Party files total ({party_total:,}) <= original ({source_total:,}). Difference: {diff:,}"
        )
    else:
        diff = party_total - source_total
        print(
            f"WARNING: Party files total ({party_total:,}) > original ({source_total:,}). Overage: {diff:,}"
        )
