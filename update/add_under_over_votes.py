import pandas as pd
import os
from pathlib import Path


def process_election_file(file_path: str) -> pd.DataFrame:
    """
    Process a single election CSV file and add Undervotes/Overvotes rows.
    """
    df = pd.read_csv(file_path)

    # Required columns
    required_cols = ["Office", "precinct"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(
                f"Missing required column: {col}. Available: {df.columns.tolist()}"
            )

    # Identify key columns (flexible matching)
    vote_col = None
    for possible in ["Votes", "votes", "Vote", "vote", "Total"]:
        if possible in df.columns:
            vote_col = possible
            break
    if not vote_col:
        raise ValueError(f"Could not find vote column in {file_path.name}")

    candidate_col = None
    for possible in ["Candidate", "candidate", "Cand", "Name"]:
        if possible in df.columns:
            candidate_col = possible
            break
    if not candidate_col:
        raise ValueError(f"Could not find candidate column in {file_path.name}")

    result_df = df.copy()
    new_rows = []

    # Group by Office and precinct
    grouped = result_df.groupby(["Office", "precinct"])

    for (office, precinct), group in grouped:
        # Get the TBC row
        tbc_rows = group[
            group[candidate_col].astype(str).str.strip().str.lower() == "tbc"
        ]

        if len(tbc_rows) == 0:
            print(
                f"Warning: No TBC row found for Office='{office}', Precinct='{precinct}'"
            )
            continue
        elif len(tbc_rows) > 1:
            print(
                f"Warning: Multiple TBC rows found for Office='{office}', Precinct='{precinct}' - using first one."
            )

        tbc_votes = tbc_rows[vote_col].iloc[0]

        # Sum votes for all candidates except TBC
        candidates_only = group[
            group[candidate_col].astype(str).str.strip().str.lower() != "tbc"
        ]
        total_candidate_votes = candidates_only[vote_col].sum()

        # Calculate difference
        difference = tbc_votes - total_candidate_votes

        # Create new Undervotes/Overvotes row
        new_row = tbc_rows.iloc[0].copy()  # Base on TBC row structure
        new_row[candidate_col] = "Undervotes/Overvotes"
        new_row[vote_col] = difference

        new_rows.append(new_row)

    # Append new rows to the result
    if new_rows:
        new_rows_df = pd.DataFrame(new_rows)
        result_df = pd.concat([result_df, new_rows_df], ignore_index=True)

    return result_df


def main():
    input_folder = Path("../files")
    output_folder = Path("../output")
    output_folder.mkdir(parents=True, exist_ok=True)
    output_file = output_folder / "under_over.csv"

    all_dfs = []
    csv_files = list(input_folder.glob("*.csv"))

    if not csv_files:
        print("No CSV files found in /files folder.")
        return

    print(f"Found {len(csv_files)} CSV file(s).")

    for file_path in csv_files:
        print(f"Processing: {file_path.name}")
        try:
            processed_df = process_election_file(file_path)
            all_dfs.append(processed_df)
        except Exception as e:
            print(f"Error processing {file_path.name}: {e}")

    if all_dfs:
        final_df = pd.concat(all_dfs, ignore_index=True)

        # Sort for better readability
        sort_cols = (
            ["Office", "precinct", candidate_col]
            if "candidate_col" in locals()
            else ["Office", "precinct"]
        )
        try:
            final_df = final_df.sort_values(by=["Office", "precinct"])
        except:
            pass

        final_df.to_csv(output_file, index=False)
        print(f"\nSuccess! Output written to: {output_file}")
        print(f"Total rows in final file: {len(final_df)}")
    else:
        print("No data processed successfully.")


if __name__ == "__main__":
    main()
