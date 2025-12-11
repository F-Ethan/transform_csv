import pandas as pd

# Load the CSV file
df = pd.read_csv('files/updated_columns.csv')  # Fix path if needed, e.g., './tarranttx--2020-03-03_Primary.csv'

# Print the column names to debug
print(df.columns.tolist())

# Define the column names
check_col = 'Raw Title'
new_col = "Office Modifier"


# Vectorized assignment: Map values in check_col to filenames
# This creates the new column in one go, filling non-matches with NaN (or use .fillna('') if you want empty strings)
df[new_col] = df[check_col]

# Optional: Preview the new column
print(df[[check_col, new_col]].head())  # Shows first 5 rows of the relevant columns

# Save to output CSV
df.to_csv('output/updated_columns.csv', index=False)

print("Processing complete. Output saved to updated_columns.csv")