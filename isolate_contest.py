import pandas as pd
import logging
import csv
import os

# Set up logging
logging.basicConfig(filename='logs/isolate_contest.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

input_file = 'files/madisonil--2024-03-19_Primary.csv'
isolated_output_file = 'output/isolated_contest.csv'
remaining_output_file = 'output/remaining_contest.csv'

office_to_keep = ['Tarrant County College - Trustee, District 4']

# Configuration: Set to True to isolate rows where the designated column is empty instead of using office_to_keep
ISOLATE_EMPTY = True

# Column name for the office/designated field (alter this to change the column used for filtering)
OFFICE_COLUMN = 'Party'
 
def isolate_contests(input_file, isolated_output_file, remaining_output_file, offices_to_isolate):
    # Read the input CSV using DictReader for easier column access
    with open(input_file, 'r') as infile:
        reader = csv.DictReader(infile)
        rows = list(reader)
        
        # Determine if we're isolating empty offices
        is_empty_mode = offices_to_isolate == ['']
        
        # Filter rows
        matching_rows = []
        non_matching_rows = []
        unique_offices_found = set()
        for row in rows:
            office = row.get(OFFICE_COLUMN, '').strip()
            if (is_empty_mode and office == '') or (not is_empty_mode and office in offices_to_isolate):
                matching_rows.append(row)
                unique_offices_found.add(office)
            else:
                non_matching_rows.append(row)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(isolated_output_file) if os.path.dirname(isolated_output_file) else '.', exist_ok=True)
        os.makedirs(os.path.dirname(remaining_output_file) if os.path.dirname(remaining_output_file) else '.', exist_ok=True)
        
        headers = rows[0].keys()  # Assume first row defines headers
        
        # Write matching rows to isolated CSV
        if matching_rows:
            with open(isolated_output_file, 'w', newline='') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=headers)
                writer.writeheader()
                writer.writerows(matching_rows)
        else:
            logging.warning("No matching rows found for isolation.")
        
        # Write non-matching rows to remaining CSV
        with open(remaining_output_file, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=headers)
            writer.writeheader()
            writer.writerows(non_matching_rows)
        
        if is_empty_mode:
            office_desc = f"empty '{OFFICE_COLUMN}' field"
        else:
            office_desc = f"offices: {unique_offices_found}"
        
        logging.info(f"Filtered {len(matching_rows)} rows for {office_desc}. Remaining: {len(non_matching_rows)} rows.")
        print(f"Successfully isolated {len(matching_rows)} rows for {office_desc}.")
        print(f"Remaining {len(non_matching_rows)} rows written to '{remaining_output_file}'.")
            
def main():
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return
    
    # Determine offices to isolate based on mode
    if ISOLATE_EMPTY:
        offices_to_isolate = ['']
    else:
        offices_to_isolate = office_to_keep
    
    try:
        isolate_contests(input_file, isolated_output_file, remaining_output_file, offices_to_isolate)
        print(f"Isolated output written to '{isolated_output_file}'")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()