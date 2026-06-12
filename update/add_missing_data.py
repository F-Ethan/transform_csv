#!/usr/bin/env python3

"""
Fill missing PrimaryParty with "NA" and conditionally replace DistrictName
when OfficeName contains "President" and DistrictName contains "Congressional".

Uses regex (case-insensitive) for flexible matching.
"""

import csv
import logging
import re
from datetime import datetime
from pathlib import Path

# ====================== CONFIGURATION ======================
# Folders
FILES_FOLDER   = Path("../files")
LOGS_FOLDER    = Path("../logs")
FILES_OUTPUT   = Path("../output")

# Files
INPUT_CSV  = FILES_FOLDER / "contracostaca--2002-03-05_Special_State_CC.csv"
OUTPUT_CSV = FILES_OUTPUT / "voters_edited_State_CC.csv"

# Party fill
PARTY_COLUMN  = "CandidateParty"
DEFAULT_PARTY = "NA"

# ------------------- CONDITIONAL EDIT -------------------
ENABLE_CONDITIONAL_EDIT = False

COND_CHECK_COLUMN = "OfficeName"
COND_TARGET_COLUMN = "DistrictName"
COND_TARGET_NEW    = "California"

# Regex patterns (case-insensitive)
COND_CHECK_PATTERN  = re.compile(r"President", re.IGNORECASE)
COND_TARGET_PATTERN = re.compile(r"^\d+\s+Congressional\s+District$", re.IGNORECASE)
# -------------------------------------------------------

# CSV settings
INPUT_ENCODING   = "utf-8"
OUTPUT_ENCODING  = "utf-8"
INPUT_DELIMITER  = ","
OUTPUT_DELIMITER = ","

# Logging
LOG_PROGRESS_EVERY = 500
# ===========================================================


def setup_logging() -> Path:
    LOGS_FOLDER.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_FOLDER / f"edit_party_{timestamp}.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler()
        ]
    )
    logging.info("Logging initialized – %s", log_file)
    return log_file


def apply_edits(
    input_path: Path,
    output_path: Path,
    default_party: str
) -> tuple[int, int, int, int]:
    total = cond_updated = party_filled = unchanged = 0

    logging.info("Processing %s → %s", input_path, output_path)

    with open(input_path, mode='r', encoding=INPUT_ENCODING, newline='') as infile, \
         open(output_path, mode='w', encoding=OUTPUT_ENCODING, newline='') as outfile:

        reader = csv.DictReader(infile, delimiter=INPUT_DELIMITER)
        fieldnames = reader.fieldnames

        required = {PARTY_COLUMN}
        if ENABLE_CONDITIONAL_EDIT:
            required.update({COND_CHECK_COLUMN, COND_TARGET_COLUMN})
        missing = required - set(fieldnames or [])
        if missing:
            raise ValueError(f"Missing columns: {missing}. Found: {fieldnames}")

        writer = csv.DictWriter(outfile, fieldnames=fieldnames, delimiter=OUTPUT_DELIMITER)
        writer.writeheader()

        for row in reader:
            total += 1
            changed = False

            # ---- 1. Conditional edit (regex + debug) -------------------------
            if ENABLE_CONDITIONAL_EDIT:
                office   = row.get(COND_CHECK_COLUMN, "").strip()
                district = row.get(COND_TARGET_COLUMN, "").strip()

                office_match   = COND_CHECK_PATTERN.search(office)
                district_match = COND_TARGET_PATTERN.search(district)

                if office_match and district_match:
                    old_val = district
                    row[COND_TARGET_COLUMN] = COND_TARGET_NEW
                    cond_updated += 1
                    changed = True

                    # DEBUG: Log first 5 matches
                    if cond_updated <= 5:
                        logging.info(
                            "MATCH & UPDATE: Office='%s' | District='%s' → '%s'",
                            office, old_val, COND_TARGET_NEW
                        )

            # ---- 2. Fill empty party -----------------------------------------
            party_val = row[PARTY_COLUMN].strip()
            if not party_val:
                row[PARTY_COLUMN] = default_party
                party_filled += 1
                changed = True

            # ---- Write row ---------------------------------------------------
            writer.writerow(row)
            if not changed:
                unchanged += 1

            # ---- Progress ----------------------------------------------------
            if total % LOG_PROGRESS_EVERY == 0:
                logging.info(
                    "Processed %d rows (cond: %d, filled: %d, unchanged: %d)",
                    total, cond_updated, party_filled, unchanged
                )

        if total % LOG_PROGRESS_EVERY != 0:
            logging.info(
                "Processed %d rows (cond: %d, filled: %d, unchanged: %d)",
                total, cond_updated, party_filled, unchanged
            )

    logging.info(
        "Finished – total:%d  cond_updated:%d  party_filled:%d  unchanged:%d",
        total, cond_updated, party_filled, unchanged
    )
    return total, cond_updated, party_filled, unchanged


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_CSV}")

    log_file = setup_logging()
    total, cond, filled, unchanged = apply_edits(INPUT_CSV, OUTPUT_CSV, DEFAULT_PARTY)

    print("\n=== EDIT SUMMARY ===")
    print(f"Log file          : {log_file}")
    print(f"Rows processed    : {total}")
    if ENABLE_CONDITIONAL_EDIT:
        print(f"Conditional updates: {cond}  →  {COND_TARGET_COLUMN} = '{COND_TARGET_NEW}'")
    print(f"Party filled      : {filled}  →  '{DEFAULT_PARTY}'")
    print(f"Rows unchanged    : {unchanged}")
    print(f"Output saved to   : {OUTPUT_CSV}")
    print("====================\n")


if __name__ == "__main__":
    main()