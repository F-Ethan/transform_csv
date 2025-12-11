import pandas as pd
import os

# =============================================================================
# CONFIGURATION - Edit these variables at the top before running
# =============================================================================

# Directory containing input/output files
files_dir = "files/"

# Input CSV filename
input_filename = "contracostaca--2002-03-05_Special_two.csv"

# Output CSV filename
output_filename = "cleaned.csv"

# Column to check for candidate names
check_column = "CandidateName"  # Column to scan

# List of phrases that indicate no candidate
no_candidate_phrases = ["No candidate has filed", "No candidate file", "No candidate filed"]

# Column to update when a match is found
update_column = "CandidateParty"

# Value to set when a match is found
new_value = ""

# Case-sensitive matching? (False = case-insensitive)
case_sensitive = False

# =============================================================================
# SCRIPT LOGIC - Do not edit below unless necessary
# =============================================================================

# Build paths
input_path = os.path.join(files_dir, input_filename)
output_path = os.path.join(files_dir, output_filename)

# Check if input file exists
if not os.path.exists(input_path):
    print(f"Error: File '{input_path}' not found.")
    exit(1)

# Read the CSV
df = pd.read_csv(input_path)
print(f"Loaded CSV: {df.shape[0]} rows, {df.shape[1]} columns")

# Validate columns exist
if check_column not in df.columns:
    print(f"Error: Column '{check_column}' not found in CSV.")
    print(f"Available columns: {list(df.columns)}")
    exit(1)

if update_column not in df.columns:
    print(f"Warning: Column '{update_column}' not found. It will be created.")
    df[update_column] = ""  # Create if missing

# Prepare phrases for matching
if not case_sensitive:
    # Convert everything to lowercase for comparison
    df_lower = df[check_column].astype(str).str.lower()
    phrases_lower = [phrase.lower() for phrase in no_candidate_phrases]
else:
    df_lower = df[check_column].astype(str)
    phrases_lower = no_candidate_phrases

# Create mask: True where any phrase matches
mask = df_lower.isin(phrases_lower)

# Count matches
matches_found = mask.sum()
print(f"Found {matches_found} rows where '{check_column}' matches no-candidate phrases.")

# Apply update
df.loc[mask, update_column] = new_value
print(f"Updated '{update_column}' to '{new_value}' in {matches_found} rows.")

# Save result
df.to_csv(output_path, index=False)
print(f"Cleaned CSV saved to: {output_path}")
print(f"Final columns: {list(df.columns)}")