import os
import csv

# Directory containing the CSV files
directory = '../files'

# Check if directory exists
if not os.path.exists(directory):
    print(f"Directory '{directory}' not found.")
else:
    # List all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith('.csv'):
            filepath = os.path.join(directory, filename)
            try:
                with open(filepath, 'r', newline='') as file:
                    reader = csv.reader(file)
                    header = next(reader)  # Read the first row (header)
                    print(f"Header for {filename}: {', '.join(header)}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")