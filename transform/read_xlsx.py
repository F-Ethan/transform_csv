# read_xlsx.py
import pandas as pd
import csv
from pathlib import Path
from collections import defaultdict
import glob

def extract_contest_precincts(xlsx_path, output_csv=None):
    """
    One row = one contest
    Column A = contest title
    Column B, C, D, … = precincts (one per column)
    """
    xls = pd.ExcelFile(xlsx_path)

    # contest → list of precincts (order preserved)
    contest_to_precincts = defaultdict(list)

    for sheet_name in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet_name, header=None)

        contest_title = None
        for cell in df.iloc[:, 0].dropna():
            cell_str = str(cell).strip()

            if cell_str == "Total Votes":
                continue

            if cell_str == "Early Voting":
                contest_title = None          # end current contest
                continue

            if contest_title is None:
                contest_title = cell_str      # first non-empty → title
                continue

            # precinct under the current contest
            contest_to_precincts[contest_title].append(cell_str)

    # ------------------------------------------------------------------
    # Build a list of rows: [title, prec1, prec2, prec3, …]
    # ------------------------------------------------------------------
    rows = []
    for title, precincts in contest_to_precincts.items():
        row = [title] + precincts
        rows.append(row)

    # ------------------------------------------------------------------
    # Write CSV
    # ------------------------------------------------------------------
    output_path = output_csv or Path("../output") / (Path(xlsx_path).stem + "_contests_by_precinct.csv")
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        # Header: Contest Title, Precinct 1, Precinct 2, …
        header = ["Contest Title"] + [f"Precinct {i+1}" for i in range(max(len(p) for p in contest_to_precincts.values()))]
        writer.writerow(header)

        for row in rows:
            writer.writerow(row)   # pandas will pad missing columns with empty strings

    print(f"Done! → {output_path}")
    return contest_to_precincts


# ----------------------------------------------------------------------
# QUICK DRIVER – drop any .xlsx file in the folder and run
# ----------------------------------------------------------------------
if __name__ == "__main__":
    xlsx_files = glob.glob("../files/*.xlsx")
    if not xlsx_files:
        print("No .xlsx file found in the current folder.")
    else:
        extract_contest_precincts(xlsx_files[0])

# extract_contest_precincts('files/Election+Results+(11-05-2024).xlsx')