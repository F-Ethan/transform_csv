import polars as pl
from pathlib import Path

# Configuration
input_folder = Path("../files")        # Folder containing .parquet files
output_csv = Path("../output/parquet.csv")    # Desired output CSV file

# Find all .parquet files in the input folder
parquet_files = list(input_folder.glob("*.parquet"))

if not parquet_files:
    print("No .parquet files found in the 'files' folder.")
else:
    print(f"Found {len(parquet_files)} Parquet file(s): {[p.name for p in parquet_files]}")

    # Read and concatenate all files
    df_combined = pl.concat(
        [pl.read_parquet(f) for f in parquet_files],
        how="vertical"  # Stack rows; use "vertical_relaxed" if minor schema differences exist
    )

    # Write to CSV
    df_combined.write_csv(output_csv)
    print(f"Combined data written to '{output_csv}' ({df_combined.shape[0]:,} rows, {df_combined.shape[1]} columns).")