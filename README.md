# CSV Transform Scripts

A collection of Python scripts for processing, transforming, and inspecting election CSV data.

All scripts are organized into folders by what they do. Each script has a configuration block at the top — edit the variables there to point at your files before running.

Input files go in `files/`, output goes to `output/`, and logs go to `logs/`.

---

## inspect/
Read-only analysis tools. Safe to run at any time — they do not modify any files.

| Script | What it does |
|---|---|
| `headers.py` | Prints the header row of every CSV in `files/` |
| `count_csv_lines.py` | Counts non-empty data rows per file in `files/`, separates `_pdf.csv` originals from derived files, and checks if totals are consistent |
| `check_cross_file_duplicates.py` | Detects rows that appear in more than one party CSV using a Page/Row/Column composite key |
| `list_unique_offices.py` | Lists all unique office names found in a source file (reads column index 9) |

---

## split/
Split one CSV into multiple output files.

| Script | What it does |
|---|---|
| `split_csv_in_two.py` | Flexible splitter with four modes: by line number, by keyword in a column, by whether a column is empty, or by a column's value. Sorts by a chosen column first. |
| `split_csvs_by_office.py` | Splits all CSVs in `files/` into separate output files based on regex patterns matched against a column (e.g. Democrat vs Republican). One output file per category, named `{input}-{category}.csv`. Files with 0 matching rows are not created. |

---

## merge/
Combine multiple CSV files into one.

| Script | What it does |
|---|---|
| `merge_multiple_csv.py` | Merges all CSVs in `files/` into a single `output/merged.csv`. Uses the file without a trailing number as the header source; appends the rest in numeric order. |

---

## transform/
Reshape or reformat data — changes the structure of the rows or columns.

| Script | What it does |
|---|---|
| `aggregate_votes_by_precinct.py` | Groups rows by precinct/office/candidate/channel, sums vote counts, and adds a computed `Total` channel row where one is missing |
| `flatten_scraped_file_massachusetts.py` | Parses a Massachusetts election CSV with ward/precinct hierarchy and outputs three separate files: party registration, voter turnout, and overall stats |
| `parquet_to_csv.py` | Reads all `.parquet` files in `files/` and concatenates them into a single CSV |
| `read_xlsx.py` | Reads `.xlsx` files in `files/` and outputs one row per contest listing all associated precincts |

---

## update/
Add or patch data in an existing file — the row structure stays the same, values change.

| Script | What it does |
|---|---|
| `add_missing_data.py` | Fills empty `CandidateParty` cells with `"NA"` and optionally replaces `DistrictName` when `OfficeName` matches a regex |
| `add_under_over_votes.py` | Calculates Undervotes/Overvotes per office and precinct by subtracting candidate totals from a `TBC` total row, and appends the result |
| `clear_column_on_phrase_match.py` | Scans a column for "no candidate" phrases and clears a target column on matching rows |
| `update_county_from_master.py` | Updates the `County` column in all CSVs in `output/` by looking up each row's `Town` in a master mapping file |

---

## clean/
Remove or fix bad rows and columns.

| Script | What it does |
|---|---|
| `clean_rows.py` | Removes rows from all CSVs in `files/` where a specified column is empty or matches a list of values |
| `add_or_copy_column.py` | Copies an existing column to a new column name, or adds new columns filled with a fixed default value |
