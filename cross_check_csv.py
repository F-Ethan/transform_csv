import pandas as pd

'''
    This file takes two inport csv's and adds the missing column info for one to the other. 
'''

# File paths - update these as needed
processed_file = 'files/updated - peoria_county_2012-11-06_General.csv'  # Your output CSV with correct votes
master_file = 'files/original - peoria_county_2012-11-06_General.csv'  # The input file with correct office info (wrong votes)
output_file = 'merged.csv'  # Output merged file

# Read the CSVs
processed_df = pd.read_csv(processed_file)
master_df = pd.read_csv(master_file)

# Create a composite key for matching: PrecinctName | OfficeName | CandidateName
# Adjust these columns if your master file uses different names
processed_df['key'] = processed_df['PrecinctName'].fillna('') + '|' + processed_df['OfficeName'].fillna('') + '|' + processed_df['CandidateName'].fillna('')
master_df['key'] = master_df['PrecinctName'].fillna('') + '|' + master_df['OfficeName'].fillna('') + '|' + master_df['DistrictName'].fillna('') + '|' + master_df['DistrictType'].fillna('') + '|' + master_df['CandidateName'].fillna('')

# Merge: Keep all from processed (left), update office fields from master (right)
# Only update specific columns from master (office-related); keep votes from processed
office_columns = [
    'DistrictName', 'DistrictType', 'RetainerName', 'CandidateParty', 
    'PrimaryParty', 'NVotes', 'Channel', 'OfficeModifier', 
    'BallotQuestionType', 'BallotQuestionText', 'Registered Voters'
    # Add more columns from master if needed, e.g., 'DivisionType' if it's separate
]

merged_df = processed_df.copy()
for col in office_columns:
    if col in master_df.columns:
        merged_df = merged_df.merge(
            master_df[['key', col]].drop_duplicates(), 
            on='key', 
            how='left', 
            suffixes=('', '_master')
        )
        # Update with master value if available, else keep original
        merged_df[col] = merged_df[col].fillna(merged_df[col + '_master'])
        merged_df = merged_df.drop(columns=[col + '_master'])

# Drop the key column
merged_df = merged_df.drop(columns=['key'])

# Handle any remaining NaNs (optional: fill with empty string)
merged_df = merged_df.fillna('')

# Write to output
merged_df.to_csv(output_file, index=False)

print(f"Merged file saved to {output_file}")
print("Updated columns from master:", [col for col in office_columns if col in master_df.columns])