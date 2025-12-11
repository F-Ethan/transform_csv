import pdfplumber
import pandas as pd
import re
import logging
import csv
import os

# Set up logging
logging.basicConfig(filename='column_update.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
 
def find_all_offices(input_file):
    # Read the input CSV
    with open(input_file, 'r') as infile:
        reader = csv.reader(infile)
        # Read all rows into memory
        # rows = list(reader)
        unique_office = set()
        for row in reader:
            office = row[9]
            if office not in unique_office:
                unique_office.add(office)
            
        logging.info(f"offices found: {unique_office}")
        print("all offices checked.")
            
def main():
    input_file = "Election_Results.pdf" 
    # output_file = "Delta_2004_flattened_output.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found")
        return
    
    try:
        find_all_offices(input_file)
        print(f"Successfully created Office List")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()