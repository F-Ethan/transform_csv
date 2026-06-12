import os
import csv
import glob
import re

# Automatically find CSV files in 'files' folder
all_files = glob.glob('../files/*.csv')

# Identify the header file: the one whose filename does not end with a number before .csv
header_candidates = [f for f in all_files if not re.search(r'\d+\.csv$', os.path.basename(f))]

if not header_candidates:
    print("No header file found (file without a number at the end). Exiting.")
    exit(1)
elif len(header_candidates) > 1:
    print(f"Warning: Found multiple potential header files: {header_candidates}. Using the first one.")

header_file = header_candidates[0]

# The remaining files are data files (with numbers at the end)
data_files = [f for f in all_files if f != header_file]

# Sort data files by the trailing number in the filename (if present)
def get_trailing_number(filename):
    stem = os.path.splitext(os.path.basename(filename))[0]
    match = re.search(r'(\d+)$', stem)
    return int(match.group(1)) if match else float('inf')

data_files.sort(key=get_trailing_number)

# Output file
output_file = "../output/merged.csv"

print(f"Header file: {header_file}")
print(f"Data files: {data_files}")
print(f"Output will be written to: {output_file}")

# Process the files
total_rows = 0
with open(output_file, 'w', newline='') as outfile:
    writer = csv.writer(outfile)
    
    # Process header file (includes header row)
    print(f"Processing header file: {header_file}...")
    with open(header_file, 'r', newline='') as infile:
        reader = csv.reader(infile)
        header = next(reader)  # Read the header
        writer.writerow(header)
        rows_from_file = 1  # Count header as processed, but not as data
        for row in reader:
            writer.writerow(row)
            total_rows += 1
            rows_from_file += 1
            if rows_from_file % 100 == 0:
                print(f"  Processed {rows_from_file} rows from {header_file} (including header).")
    
    # Process each data file (no header, assume same column order and width)
    for data_file in data_files:
        print(f"Processing data file: {data_file}...")
        with open(data_file, 'r', newline='') as infile:
            reader = csv.reader(infile)
            rows_from_file = 0
            for row in reader:
                writer.writerow(row)
                total_rows += 1
                rows_from_file += 1
                if rows_from_file % 100 == 0:
                    print(f"  Processed {rows_from_file} rows from {data_file}.")

print(f"Processing complete. Total data rows merged: {total_rows}")
print(f"Output written to: {output_file}")