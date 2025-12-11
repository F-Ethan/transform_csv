import os
import csv
import glob

# Automatically find CSV files in 'files' folder (excluding any output-like files)
input_files = [f for f in glob.glob('files/*.csv') 
               if not f.endswith('_BQ.csv') and not f.endswith('_CC.csv')]

# If you want to hardcode exactly two, replace the above with:
# input_files = [
#     'files/your_first_input.csv',
#     'files/your_second_input.csv'
# ]

if len(input_files) != 2:
    print(f"Warning: Found {len(input_files)} CSV files in 'files/'. Expected 2. Proceeding anyway.")
    if not input_files:
        print("No input files found. Exiting.")
        exit(1)

output_bqs = "peoriail--2012-11-06_General_BQ.csv"  # Adjust base name if needed for your data
output_cc = "peoriail--2012-11-06_General_CC.csv"

# Define the key column for the check (using title-based access)
key_column = "OfficeName"

# Specify the subset of columns to include in output (consistent across all inputs/outputs)
output_columns = ["OfficeName", "DistrictName", "DistrictType", "PrecinctName", "TBC", "RetainerName", "CandidateName", "CandidateParty", "NVotes", "Votes", "Channel", "OfficeModifier", "ElectionDate", "ElectionType", "BallotQuestionType", "BallotQuestionText"]

# Process each input file
total_output_rows = 0
output_fieldnames = output_columns  # Fixed fieldnames for consistent outputs
for input_file in input_files:
    print(f"Processing {input_file}...")
    output_rows = 0
    with open(input_file, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        # No need to capture input fieldnames; we'll map to output_columns
        for row in reader:
            # Access data by column title (robust to extra/missing columns via .get())
            office_name = row.get(key_column, '').strip()
            output_rows += 1
            total_output_rows += 1
            if output_rows % 10 == 0:
                print(f"  Processed {output_rows} rows from this file. Current {key_column}: {office_name}")
            
            # Create output row dict with only the specified columns (missing = empty string)
            row_out = {col: row.get(col, '') for col in output_columns}
            
            # Simple check: if "Proposition" (case-insensitive) in OfficeName, route to BQ, else CC
            is_proposition = "proposition" in office_name.lower()
            output_path = output_bqs if is_proposition else output_cc
            
            file_exists = os.path.exists(output_path)
            with open(output_path, 'a', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=output_fieldnames)
                if not file_exists:
                    writer.writeheader()
                writer.writerow(row_out)  # Outputs only the specified columns

print(f"Processing complete. Total rows processed: {total_output_rows}")
print(f"All BQs written to: {output_bqs}")
print(f"All CCs written to: {output_cc}")