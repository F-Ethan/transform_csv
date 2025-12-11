import pandas as pd
import os
import numpy as np   # <-- added

# Global constants
COLUMN_NAME = "CandidateName"
UPDATE_COLUMN_NAMES = ["Office", "District Name", "District Type"]
REMOVE_ROWS = True          # Set to True to remove matched rows
VALUES_TO_EDIT = [""]       # keep your original list (or leave empty)

FOLDER_PATH = "files"

# Process CSV files in the folder
for filename in os.listdir(FOLDER_PATH):
    if filename.endswith('.csv'):
        file_path = os.path.join(FOLDER_PATH, filename)
        
        # Read the CSV file
        df = pd.read_csv(file_path)
        
        rows_matched = 0  # Counter for rows that will be removed/updated
        
        if COLUMN_NAME in df.columns:
            # ------------------------------------------------------------------
            # 1. Identify rows that are *empty* in CandidateName
            # ------------------------------------------------------------------
            #   - NaN                → pd.isna()
            #   - empty string ''    → == ''
            #   - whitespace only    → .str.strip() == ''
            empty_mask = (
                pd.isna(df[COLUMN_NAME]) |
                (df[COLUMN_NAME] == '') |
                (df[COLUMN_NAME].astype(str).str.strip() == '')
            )
            
            # 2. (Optional) also keep your original VALUES_TO_EDIT logic
            values_mask = df[COLUMN_NAME].isin(VALUES_TO_EDIT)
            
            # Combine the two conditions
            rows_to_drop = empty_mask | values_mask
            rows_matched = rows_to_drop.sum()
            
            # ------------------------------------------------------------------
            # 3. Remove rows (or update them – your existing code)
            # ------------------------------------------------------------------
            if REMOVE_ROWS:
                df = df[~rows_to_drop]
            else:
                # ---- your original UPDATE logic (unchanged) -----------------
                modifier_value = VALUES_TO_EDIT[0].strip("[]'") if VALUES_TO_EDIT else ""
                for col in UPDATE_COLUMN_NAMES:
                    if col in df.columns:
                        df.loc[rows_to_drop, col] = (
                            df.loc[rows_to_drop, col].astype(str) + " " + modifier_value
                        )
                df.loc[rows_to_drop, COLUMN_NAME] = ''   # clear the column
                # -----------------------------------------------------------

        # Save the result
        edited_filename = f"Edited--{filename}"
        df.to_csv(edited_filename, index=False)
        
        action = "Dropped" if REMOVE_ROWS else "Updated"
        print(f"Processed {filename}: {action} {rows_matched} matched rows, saved as {edited_filename}")
    else:
        print(f"No CSV files found in the '{FOLDER_PATH}' folder.")
        break   # avoid printing the message for every non-CSV file