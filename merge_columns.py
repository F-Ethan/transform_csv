import pandas as pd

# Load the CSV file
df = pd.read_csv('files/tarranttx--2020-03-03_Primary.csv')

# Print the column names to debug
print(df.columns.tolist())

# Define the column names (adjusted based on actual columns)
office_col = 'Contest Title'
add_col = 'Office Modifier'
# new_col = 'District Type'

# Create the new column values
df[add_col] = df[office_col] 
# df[new_col] = df[office_col] 

# Find the position of the office column and insert new columns right after it
idx = df.columns.get_loc(office_col) + 1
df.insert(idx + 2, add_col, df.pop(add_col))
# df.insert(idx + 1, new_col, df.pop(new_col))

# Save to output CSV
df.to_csv('output/output.csv', index=False)

print("Processing complete. Output saved to output.csv")