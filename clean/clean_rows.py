#!/usr/bin/env python3

"""
Filter rows from INPUT_CSV: remove any row whose PRECINCT_COLUMN value appears
in the first column of REMOVE_CSV.  Detailed logging (progress + final stats)
is written to LOGS_FOLDER.
All paths / settings are global variables at the top for easy reuse.
"""

import csv
import logging
from datetime import datetime
from pathlib import Path

# ====================== CONFIGURATION ======================
# Update these variables for different files or columns

# Folders
FILES_FOLDER   = Path("../files")       # Input / output CSVs
LOGS_FOLDER    = Path("../logs")        # Log files
FILES_OUTPUT   = Path("../output")      # (kept for compatibility – not used)

# File names
INPUT_CSV      = FILES_FOLDER / "contracostaca--2002-03-05_Special_two.csv"
REMOVE_CSV     = FILES_FOLDER / "rows_to_remove.csv"
OUTPUT_CSV     = FILES_OUTPUT / "filtered_output.csv"

# Column to check
PRECINCT_COLUMN = "CandidateName"

# CSV format
INPUT_ENCODING   = "utf-8"
REMOVE_ENCODING  = "utf-8"
OUTPUT_ENCODING  = "utf-8"
INPUT_DELIMITER  = ","
REMOVE_DELIMITER = ","
OUTPUT_DELIMITER = ","

# Logging settings
LOG_PROGRESS_EVERY = 100          # Log a line every N rows processed
# ===========================================================


def setup_logging() -> Path:
    """Create LOGS_FOLDER if needed and configure logger. Return log file path."""
    LOGS_FOLDER.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_FOLDER / f"filter_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()          # also print to console
        ]
    )
    logging.info("Logging initialized – %s", log_file)
    return log_file


def load_remove_set(remove_csv_path: Path) -> set:
    """Load first column of remove CSV into a set for O(1) lookup."""
    remove_values = set()
    logging.info("Loading removal list from: %s", remove_csv_path)
    with open(remove_csv_path, mode='r', encoding=REMOVE_ENCODING, newline='') as f:
        reader = csv.reader(f, delimiter=REMOVE_DELIMITER)
        for row in reader:
            if row:  # skip empty rows
                val = row[0].strip()
                remove_values.add(val)
                
    logging.info("Loaded %d values to remove.", len(remove_values))
    return remove_values


def filter_csv(input_csv_path: Path, output_csv_path: Path, remove_set: set) -> tuple[int, int]:
    """
    Filter CSV and return (rows_kept, rows_removed).
    Logs progress and final statistics.
    """
    total_read = 0
    kept       = 0
    removed    = 0

    logging.info("Starting filtering – input: %s → output: %s", input_csv_path, output_csv_path)

    with open(input_csv_path, mode='r', encoding=INPUT_ENCODING, newline='') as infile, \
         open(output_csv_path, mode='w', encoding=OUTPUT_ENCODING, newline='') as outfile:

        reader = csv.DictReader(infile, delimiter=INPUT_DELIMITER)
        fieldnames = reader.fieldnames
        if PRECINCT_COLUMN not in fieldnames:
            raise ValueError(f"Column '{PRECINCT_COLUMN}' not found in input CSV. Available: {fieldnames}")

        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=OUTPUT_DELIMITER)
        writer.writeheader()

        for row in reader:
            total_read += 1

            precinct_val = row[PRECINCT_COLUMN].strip()
            if precinct_val in remove_set:
                removed += 1
            else:
                writer.writerow(row)
                kept += 1

            # Progress logging
            if total_read % LOG_PROGRESS_EVERY == 0:
                logging.info("Processed %d rows (kept: %d, removed: %d)", total_read, kept, removed)

        # Final line for any remainder
        if total_read % LOG_PROGRESS_EVERY != 0:
            logging.info("Processed %d rows (kept: %d, removed: %d)", total_read, kept, removed)

    logging.info("Filtering complete – %d rows read, %d kept, %d removed.", total_read, kept, removed)
    return kept, removed


def main() -> None:
    # ---- Validate files -------------------------------------------------
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Input CSV not found: {INPUT_CSV}")
    if not REMOVE_CSV.exists():
        raise FileNotFoundError(f"Remove CSV not found: {REMOVE_CSV}")

    # ---- Logging --------------------------------------------------------
    log_file = setup_logging()

    # ---- Load removal list -----------------------------------------------
    remove_set = load_remove_set(REMOVE_CSV)

    # ---- Filter ---------------------------------------------------------
    kept, removed = filter_csv(INPUT_CSV, OUTPUT_CSV, remove_set)

    # ---- Final console summary -------------------------------------------
    print("\n=== FILTER SUMMARY ===")
    print(f"Log file       : {log_file}")
    print(f"Input rows     : {kept + removed}")
    print(f"Rows kept      : {kept}")
    print(f"Rows removed   : {removed}")
    print(f"Output saved to: {OUTPUT_CSV}")
    print("======================\n")


if __name__ == "__main__":
    main()