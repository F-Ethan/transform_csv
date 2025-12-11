import pandas as pd
import os

# =============================================================================
# CONFIGURATION - Edit these variables at the top before running the script
# =============================================================================

# Directory containing input/output files
files_dir = "files/"

# Input CSV filename
input_filename = "tarranttx--2022-03-01_Primary_no_bqs.csv"

# Copy column settings
do_copy = True  # Set to False to skip copying
source_col = 'Office'
new_col_name = "District Type"

# Add columns settings
do_add = False  # Set to False to skip adding columns
col_names = ['2024-03-19', 'Primary']  # List of new column names
default_values = ['2024-03-19', 'Primary']  # List of default values (must match col_names length)

# Output settings
output_filename = "fixed.csv"

# General settings
always_overwrite = True  # Set to False to skip overwriting existing columns (will print skips instead)

# =============================================================================
# SCRIPT LOGIC - Do not edit below unless you know what you're doing
# =============================================================================

# Build paths
input_path = os.path.join(files_dir, input_filename)
output_path = os.path.join(files_dir, output_filename)

# Check if input file exists
if not os.path.exists(input_path):
    print(f"Error: File '{input_path}' not found.")
    exit(1)

# Read the CSV file
df = pd.read_csv(input_path)
print(f"Loaded CSV with shape: {df.shape}")
print(f"Current columns: {list(df.columns)}")

# Step 1: Copy column if enabled
if do_copy:
    print(f"Available columns: {list(df.columns)}")
    if source_col not in df.columns:
        print(f"Error: Column '{source_col}' not found.")
        exit(1)
    
    if new_col_name in df.columns:
        if always_overwrite:
            print(f"Overwriting existing column '{new_col_name}'.")
        else:
            print(f"Skipping copy: Column '{new_col_name}' already exists and overwrite=False.")
            do_copy = False  # Effectively skip
    if do_copy:
        df[new_col_name] = df[source_col]
        print(f"Copied '{source_col}' to '{new_col_name}'.")

# Step 2: Add columns if enabled
if do_add:
    # Ensure lengths match
    if len(col_names) != len(default_values):
        print("Error: Number of column names must match number of default values.")
        exit(1)
    
    # Add each column
    added_count = 0
    for name, value in zip(col_names, default_values):
        if name in df.columns:
            if always_overwrite:
                print(f"Overwriting existing column '{name}' with '{value}'.")
            else:
                print(f"Skipping '{name}': Column already exists and overwrite=False.")
                continue
        df[name] = value
        print(f"Added column '{name}' filled with '{value}'.")
        added_count += 1
    
    print(f"Added/updated {added_count} columns.")

# Save the edited DataFrame
df.to_csv(output_path, index=False)
print(f"Edited CSV saved to '{output_path}' with shape: {df.shape}")
print(f"Final columns: {list(df.columns)}")