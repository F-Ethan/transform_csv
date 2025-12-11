import pandas as pd
import os
from collections import Counter  # Note: This is unused in the script; you can remove it if not needed elsewhere


# Centralized configuration
folder = "files"
output_prefix = "fixed--"

# Column names (update these for new files)
PRECINCT_COL = 'PrecinctName'
OFFICE_COL = 'OfficeName'
CANDIDATE_COL = 'CandidateName'
CHANNEL_COL = 'Channel'
VOTES_COL = 'Votes'

# Vote-specific numeric columns to sum (per channel)
vote_specific_numeric = [VOTES_COL]

# Prepare summary list
files_summary = []

# Loop through all CSV files in the folder
for filename in os.listdir(folder):
    if not filename.endswith('.csv'):
        continue
    
    # Load the CSV file
    filepath = os.path.join(folder, filename)
    df = pd.read_csv(filepath, low_memory=False)
    print(f"Processing file: {filename}")
    print("Input columns:", df.columns.tolist())
    
    # Check if required columns exist
    missing_cols = [col for col in [PRECINCT_COL, OFFICE_COL, CANDIDATE_COL, CHANNEL_COL, VOTES_COL] if col not in df.columns]
    if missing_cols:
        print(f"Warning: Missing required columns in {filename}: {missing_cols}. Skipping file.")
        continue
    
    # Save original column order
    original_columns = df.columns.tolist()
    
    # Aggregate by precinct, office, candidate, channel
    # Sum vote-specific numerics, take first for others
    group_cols = [PRECINCT_COL, OFFICE_COL, CANDIDATE_COL, CHANNEL_COL]
    agg_dict = {}
    for col in df.columns:
        if col in group_cols:
            continue
        if df[col].dtype == 'object':
            agg_dict[col] = 'first'
        else:
            if col in vote_specific_numeric:
                agg_dict[col] = 'sum'
            else:
                agg_dict[col] = 'first'
    
    df_agg = df.groupby(group_cols).agg(agg_dict).reset_index()
    
    # Now sort the aggregated dataframe
    df_agg = df_agg.sort_values(by=[PRECINCT_COL, OFFICE_COL, CANDIDATE_COL, CHANNEL_COL])

    # Group by precinct, office, and candidate
    grouped = df_agg.groupby([PRECINCT_COL, OFFICE_COL, CANDIDATE_COL])

    # Prepare a list to hold the output rows
    output_rows = []

    # Track skipped groups
    skipped_groups = 0

    # Iterate over each group
    for name, group in grouped:
        vote_channels = group[CHANNEL_COL].unique()
        has_total = 'Total' in vote_channels
        
        if has_total:
            # Already has total, just add the rows
            for _, row in group.iterrows():
                output_rows.append(row.to_dict())
        elif len(group) == 3:
            # Add the original (aggregated) rows to output
            for _, row in group.iterrows():
                output_rows.append(row.to_dict())
            
            # Calculate the sum of votes across channels
            votes_sum = group[VOTES_COL].sum()
            
            # Copy the last row (Election equivalent, after sorting) as base for Total
            total_row = group.iloc[-1].copy()
            total_row[CHANNEL_COL] = 'Total'
            total_row[VOTES_COL] = votes_sum
            
            # Sum other vote-specific numerics for the Total row
            for col in vote_specific_numeric:
                if col != VOTES_COL:
                    total_row[col] = group[col].sum()
            
            # Add the new Total row
            output_rows.append(total_row.to_dict())
        else:
            print(f"Warning: Group {name} has {len(group)} rows and no 'Total' channel. Skipping addition of total.")
            # Add the original rows as is
            for _, row in group.iterrows():
                output_rows.append(row.to_dict())
            skipped_groups += 1

    # Create a new dataframe from the output rows
    output_df = pd.DataFrame(output_rows)

    # Reorder columns to match original order
    output_df = output_df[original_columns]

    # Save to output CSV 
    output_filename = f"{output_prefix}{filename}"
    output_df.to_csv(output_filename, index=False)

    print(f"Output columns: {output_df.columns.tolist()}")
    print(f"Processing complete for {filename}. Output saved to {output_filename}")

    # Add to summary
    files_summary.append({
        'filename': filename,
        'rows_added': len(output_rows),
        'skipped_groups': skipped_groups
    })

# Print summary at the end
print("\n" + "="*50)
print("Processing Summary:")
print("="*50)
total_files = len(files_summary)
total_rows = sum(s['rows_added'] for s in files_summary)
total_skipped = sum(s['skipped_groups'] for s in files_summary)
print(f"Total files processed: {total_files}")
print(f"Total rows added across all files: {total_rows}")
print(f"Total skipped groups across all files: {total_skipped}")
print("\nPer file details:")
for summary in files_summary:
    print(f"File: {summary['filename']}, Rows added: {summary['rows_added']}, Skipped groups: {summary['skipped_groups']}")
print("="*50)