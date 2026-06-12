import pandas as pd
from pathlib import Path
import sys
from typing import Dict, Tuple


# Configuration ───────────────────────────────────────────────────────────────
FILES_FOLDER_PATH = Path("../files")                       # folder containing all CSV files
OUTPUT_FOLDER_PATH = Path("../output")                     # folder containing all CSV files
MASTER_FILE = "county_town_city_list.csv"            # name of the master file
TOWN_COL = "Town"                                    # column name for town (case-sensitive)
COUNTY_COL = "County"                                # column name for county (case-sensitive)
BACKUP_SUFFIX  = ".bak"                  # backup files get this suffix (optional safety)

# ──────────────────────────────────────────────────────────────────────────────

def load_master_mapping(master_path: Path) -> Dict[str, str]:
    """Load master.csv → {normalized_town: county} dictionary."""
    if not master_path.exists():
        print(f"Error: Master file not found: {master_path}", file=sys.stderr)
        sys.exit(1)

    try:
        df = pd.read_csv(master_path, dtype=str)
    except Exception as e:
        print(f"Error reading master file: {e}", file=sys.stderr)
        sys.exit(1)

    if TOWN_COL not in df.columns or COUNTY_COL not in df.columns:
        print(f"Error: Master must contain columns '{TOWN_COL}' and '{COUNTY_COL}'", file=sys.stderr)
        sys.exit(1)

    df[TOWN_COL] = df[TOWN_COL].str.strip().str.title()
    df[COUNTY_COL] = df[COUNTY_COL].str.strip()

    # Last occurrence wins if duplicate towns exist
    mapping = dict(zip(df[TOWN_COL], df[COUNTY_COL]))

    print(f"Loaded {len(mapping):,} unique towns from master file.")
    return mapping


def update_file(file_path: Path, master_map: Dict[str, str]) -> Tuple[int, int, int]:
    """
    Update one CSV file in place.
    Returns: (rows_processed, rows_updated, rows_unknown_town)
    """
    try:
        df = pd.read_csv(file_path, dtype=str)
    except Exception as e:
        print(f"  Failed to read: {e}")
        return 0, 0, 0

    if TOWN_COL not in df.columns or COUNTY_COL not in df.columns:
        print(f"  Missing required columns '{TOWN_COL}' / '{COUNTY_COL}'")
        return 0, 0, 0

    # Normalize for matching
    original_count = len(df)
    df[TOWN_COL] = df[TOWN_COL].str.strip().str.title()
    original_counties = df[COUNTY_COL].copy()  # for comparison

    # Perform the update
    updated_mask = df[TOWN_COL].isin(master_map.keys())
    df.loc[updated_mask, COUNTY_COL] = df.loc[updated_mask, TOWN_COL].map(master_map)

    rows_updated = updated_mask.sum()
    rows_unknown = original_count - rows_updated

    # Only write if changes were actually made
    if not df[COUNTY_COL].equals(original_counties):
        # Optional: create backup (uncomment if desired)
        # backup_path = file_path.with_suffix(file_path.suffix + BACKUP_SUFFIX)
        # file_path.rename(backup_path)
        # print(f"  Backup created: {backup_path.name}")

        df.to_csv(file_path, index=False)
        print(f"  Updated and saved ({rows_updated:,} rows changed)")
    else:
        print("  No changes needed")

    return original_count, rows_updated, rows_unknown


def main():
    if not FILES_FOLDER_PATH.is_dir():
        print(f"Error: Folder not found: {FILES_FOLDER_PATH}", file=sys.stderr)
        return
    if not OUTPUT_FOLDER_PATH.is_dir():
        print(f"Error: Folder not found: {OUTPUT_FOLDER_PATH}", file=sys.stderr)
        return

    master_path = FILES_FOLDER_PATH / MASTER_FILE
    master_map = load_master_mapping(master_path)

    # Find all CSVs except master
    csv_files = sorted(
        f for f in OUTPUT_FOLDER_PATH.glob("*.csv")
        if f.is_file() and f.name.lower() != MASTER_FILE.lower()
    )

    if not csv_files:
        print("No other CSV files found in the folder.")
        return

    print(f"\nProcessing {len(csv_files)} files...\n")

    total_rows = 0
    total_updated = 0
    total_unknown = 0
    files_changed = 0

    for file_path in csv_files:
        print(f"→ {file_path.name}")
        rows, updated, unknown = update_file(file_path, master_map)

        total_rows += rows
        total_updated += updated
        total_unknown += unknown

        if updated > 0:
            files_changed += 1

        print(f"  Rows processed: {rows:,}")
        print(f"  Rows updated:   {updated:,}")
        print(f"  Towns not in master: {unknown:,}\n")

    print("─" * 70)
    print("Final Summary:")
    print(f"  Files processed (excl. master): {len(csv_files):,}")
    print(f"  Files that were modified:       {files_changed:,}")
    print(f"  Total rows processed:           {total_rows:,}")
    print(f"  Total rows updated:             {total_updated:,}")
    print(f"  Total rows with unknown towns:  {total_unknown:,}")
    print("─" * 70)


if __name__ == "__main__":
    main()