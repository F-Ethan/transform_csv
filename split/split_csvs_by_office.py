#!/usr/bin/env python3

"""
Flexible CSV splitter – split election contest files into any number of buckets
based on regex patterns in the Office column (or any other column).

Example use cases:
  - Propositions / Bonds / Measures
  - Judicial races
  - Federal / State / Local contests
  - Retention questions, etc.
"""

import csv
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# ====================== CONFIGURATION ======================
FILES_FOLDER   = Path("../files")
LOGS_FOLDER    = Path("../logs")
OUTPUT_FOLDER  = Path("../output")

def _find_input_csvs() -> List[Path]:
    matches = sorted(FILES_FOLDER.glob("*.csv"))
    if not matches:
        raise FileNotFoundError(f"No CSV files found in {FILES_FOLDER}/")
    return matches

INPUT_CSVS = _find_input_csvs()

# Column that contains the contest name
OFFICE_COLUMN = "PrimaryParty"

# --------------------- CATEGORY DEFINITIONS ---------------------
@dataclass
class Category:
    name: str                     # Human readable name – also used as the output file suffix
    pattern: re.Pattern           # Compiled regex
    description: Optional[str] = None  # Optional longer description

# Define your buckets here – order matters! First match wins.
# Output files are named automatically: {input_stem}-{category.name}.csv
CATEGORIES: List[Category] = [

    Category(
        name="Democratic",
        pattern=re.compile(r"Dem", re.IGNORECASE),
    ),
    Category(
        name="Republican",
        pattern=re.compile(r"Rep", re.IGNORECASE),
    ),
    # Category(
    #     name="Non_Partisan",
    #     pattern=re.compile(r"Non.Partisan", re.IGNORECASE),
    #     output_file=OUTPUT_FOLDER / "Non_Partisan.csv",
    # ),
    # Category(
    #     name="Green",
    #     pattern=re.compile(r"Green", re.IGNORECASE),
    #     output_file=OUTPUT_FOLDER / "Green.csv",
    # ),
    # Category(
    #     name="Libertarian",
    #     pattern=re.compile(r"Libertarian", re.IGNORECASE),
    #     output_file=OUTPUT_FOLDER / "Libertarian.csv",
    # ),
    # Category(
    #     name="American_Independent",
    #     pattern=re.compile(r"American.Independent", re.IGNORECASE),
    #     output_file=OUTPUT_FOLDER / "American_Independent.csv",
    # ),
    # Category(
    #     name="Libertarian",
    #     pattern=re.compile(r"Libertarian", re.IGNORECASE),
    #     output_file=OUTPUT_FOLDER / "Libertarian.csv",
    # ),
    # Category(
    #     name="Natural Law",
    #     pattern=re.compile(r"Natural.Law", re.IGNORECASE),
    #     output_file=OUTPUT_FOLDER / "Natural_Law.csv",
    # ),
    # Category(
    #     name="Reform",
    #     pattern=re.compile(r"Reform", re.IGNORECASE),
    #     output_file=OUTPUT_FOLDER / "Reform.csv",
    # ),
    # Catch-all bucket – MUST BE LAST
    Category(
        name="Other",
        pattern=re.compile(r".*", re.IGNORECASE),   # matches anything
        description="Fallback bucket for rows that didn't match earlier rules"
    ),
    # Category(
    #     name="Propositions & Bonds",
    #     pattern=re.compile(r"Proposition|Prop|Bond|Measure|MEAS|Referendum|Amendment|Council", re.IGNORECASE),
    #     output_file=OUTPUT_FOLDER / "01_propositions_bonds.csv",
    #     description="All ballot measures, propositions, bonds, etc."
    # ),
    # Category(
    #     name="Federal Contests",
    #     pattern=re.compile(r"President|United States|U\.S\.|Senate|Representative|Criminal", re.IGNORECASE),
    #     output_file=OUTPUT_FOLDER / "01_federal.csv",
    # ),
    # Category(
    #     name="Judicial Races",
    #     pattern=re.compile(r"Judge", re.IGNORECASE),
    #     output_file=OUTPUT_FOLDER / "02_judicial.csv",
    #     description="Any contest with Judge/Justice/Court in the title"
    # ),
    # Category(
    #     name="Statewide Executive",
    #     pattern=re.compile(r"Governor|Lt\. Governor|Attorney General|Comptroller|Treasurer|Commissioner|Clerk|Attorney|Council", re.IGNORECASE),
    #     output_file=OUTPUT_FOLDER / "03_state_executive.csv",
    # ),
    # # Catch-all bucket – MUST BE LAST
    # Category(
    #     name="Everything Else",
    #     pattern=re.compile(r".*", re.IGNORECASE),   # matches anything
    #     output_file=OUTPUT_FOLDER / "99_other_contests.csv",
    #     description="Fallback bucket for rows that didn't match earlier rules"
    # ),
]

# CSV settings
INPUT_ENCODING    = "utf-8"
OUTPUT_ENCODING   = "utf-8"
INPUT_DELIMITER   = ","
OUTPUT_DELIMITER  = ","

# Logging
LOG_PROGRESS_EVERY = 5_000
# ===========================================================


def setup_logging() -> Path:
    LOGS_FOLDER.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_FOLDER / f"split_contests_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging started – %s", log_file)
    return log_file


def split_csv(input_path: Path, categories: List[Category]) -> Dict[str, int]:
    """
    Split the input CSV according to the ordered list of categories.
    Returns a dict: category.name → rows written
    """
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    # Prepare output folder
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    # Counters
    counters = {cat.name: 0 for cat in categories}
    total_read = 0

    logging.info("Starting split of %s", input_path)
    logging.info("Defined %d categories (order matters)", len(categories))

    # Files are opened lazily — only created when the first matching row is written
    writers: Dict[str, csv.DictWriter] = {}
    file_handles = {}
    output_paths: Dict[str, Path] = {}

    def get_writer(cat, fieldnames):
        if cat.name not in writers:
            out_path = OUTPUT_FOLDER / f"{input_path.stem}-{cat.name}.csv"
            output_paths[cat.name] = out_path
            fp = open(out_path, "w", encoding=OUTPUT_ENCODING, newline="")
            file_handles[cat.name] = fp
            writer = csv.DictWriter(fp, fieldnames=fieldnames, delimiter=OUTPUT_DELIMITER)
            writer.writeheader()
            writers[cat.name] = writer
        return writers[cat.name]

    with open(input_path, "r", encoding=INPUT_ENCODING, newline="") as infile:
        reader = csv.DictReader(infile, delimiter=INPUT_DELIMITER)
        fieldnames = reader.fieldnames

        if OFFICE_COLUMN not in fieldnames:
            raise ValueError(f"Column '{OFFICE_COLUMN}' not found. Available columns: {fieldnames}")

        for row in reader:
            total_read += 1
            office = row[OFFICE_COLUMN].strip()

            # Find first category that matches
            matched = False
            for cat in categories:
                if cat.pattern.search(office):
                    get_writer(cat, fieldnames).writerow(row)
                    counters[cat.name] += 1
                    matched = True
                    break

            if not matched:
                logging.warning("Row %d had no match (this shouldn't happen with a catch-all): %s", total_read, office)

            if total_read % LOG_PROGRESS_EVERY == 0:
                logging.info("Processed %d rows so far...", total_read)

    # Final progress log
    logging.info("Finished reading %d rows", total_read)

    # Close all open file handles
    for fp in file_handles.values():
        fp.close()

    return counters, output_paths


def main() -> None:
    log_file = setup_logging()
    logging.info("Found %d input file(s) in %s", len(INPUT_CSVS), FILES_FOLDER)

    for input_csv in INPUT_CSVS:
        logging.info("Processing: %s", input_csv.name)

        counters, output_paths = split_csv(input_csv, CATEGORIES)

        print("\n" + "="*60)
        print(f"SPLIT COMPLETED: {input_csv.name}")
        print("="*60)
        print(f"Total rows read: {sum(counters.values())}")
        print("Rows written per bucket:")
        for cat in CATEGORIES:
            if counters[cat.name] == 0:
                print(f"  {cat.name:30} →      0 rows → (no file created)")
            else:
                print(f"  {cat.name:30} → {counters[cat.name]:6} rows → {output_paths[cat.name].name}")
        print("="*60)

    print(f"\nLog file: {log_file}\n")


if __name__ == "__main__":
    main()