import pandas as pd
import sys

# Hardcoded mapping: key = full office name, value = (new_office_name, district, district_type)
mapping = {
    "Chief Justice, Supreme Court": ("Chief Justice of the Supreme Court", "Texas", "State"),
    "County Chair": ("County Chair", "Tarrant", "County"),
    "County Commissioner, Precinct 1": ("County Commissioner", "Precinct 1", "County Commissioner Precinct"),
    "County Commissioner, Precinct 3": ("County Commissioner", "Precinct 3", "County Commissioner Precinct"),
    "County Constable, Precinct 1": ("Constable", "Precinct 1", "Constable Precinct"),
    "County Constable, Precinct 2": ("Constable", "Precinct 2", "Constable Precinct"),
    "County Constable, Precinct 3": ("Constable", "Precinct 3", "Constable Precinct"),
    "County Constable, Precinct 4": ("Constable", "Precinct 4", "Constable Precinct"),
    "County Constable, Precinct 5": ("Constable", "Precinct 5", "Constable Precinct"),
    "County Constable, Precinct 6": ("Constable", "Precinct 6", "Constable Precinct"),
    "County Constable, Precinct 7": ("Constable", "Precinct 7", "Constable Precinct"),
    "County Constable, Precinct 8": ("Constable", "Precinct 8", "Constable Precinct"),
    "County Tax Assessor-Collector": ("County Tax Assessor-Collector", "Tarrant", "County"),
    "Criminal District Judge, Court No. 2": ("Criminal District Judge", "Court 2", "County Criminal Court"),
    "District Judge, 153rd Judicial District": ("District Judge", "153rd Judicial District", "Judicial District"),
    "District Judge, 17th Judicial District": ("District Judge", "17th Judicial District", "Judicial District"),
    "District Judge, 213th Judicial District": ("District Judge", "213rd Judicial District", "Judicial District"),
    "District Judge, 342nd Judicial District": ("District Judge", "342nd Judicial District", "Judicial District"),
    "District Judge, 348th Judicial District": ("District Judge", "348th Judicial District", "Judicial District"),
    "District Judge, 352nd Judicial District": ("District Judge", "352nd Judicial District", "Judicial District"),
    "District Judge, 360th Judicial District": ("District Judge", "360th Judicial District", "Judicial District"),
    "District Judge, 396th Judicial District": ("District Judge", "396th Judicial District", "Judicial District"),
    "District Judge, 48th Judicial District": ("District Judge", "48th Judicial District", "Judicial District"),
    "District Judge, 67th Judicial District": ("District Judge", "67th Judicial District", "Judicial District"),
    "District Judge, 96th Judicial District": ("District Judge", "96th Judicial District", "Judicial District"),
    "Judge, Court of Criminal Appeals, Place 3": ("Judge, Court of Criminal Appeals, Place 3", "Judge, Court of Criminal Appeals, Place 3", "Court of Criminal Appeals District"),
    "Judge, Court of Criminal Appeals, Place 4": ("Judge, Court of Criminal Appeals, Place 4", "Judge, Court of Criminal Appeals, Place 4", "Court of Criminal Appeals District"),
    "Judge, Court of Criminal Appeals, Place 9": ("Judge, Court of Criminal Appeals, Place 9", "Judge, Court of Criminal Appeals, Place 9", "Court of Criminal Appeals District"),
    "Justice, 2nd Court of Appeals District, Place 2": ("Justice, 2nd Court of Appeals District, Place 2", "Justice, 2nd Court of Appeals District, Place 2", "Court of Criminal Appeals District"),
    "Justice, 2nd Court of Appeals District, Place 6 (Unexpired Term)": ("Justice, 2nd Court of Appeals District, Place 6", "Justice, 2nd Court of Appeals District, Place 6", "Court of Criminal Appeals District"),
    "Justice, 2nd Court of Appeals District, Place 7": ("Justice, 2nd Court of Appeals District, Place 7", "Justice, 2nd Court of Appeals District, Place 7", "Court of Criminal Appeals District"),
    "Justice, Supreme Court, Place 6 (Unexpired Term)": ("Justice of the Supreme Court", "Texas", "State"),
    "Justice, Supreme Court, Place 7": ("Justice of the Supreme Court", "Justice, Supreme Court, Place 7", "Supreme Court"),
    "Justice, Supreme Court, Place 8": ("Justice of the Supreme Court", "Justice, Supreme Court, Place 8", "Supreme Court"),
    "Precinct Chair, Precinct 1197": ("Precinct Chair", "Precinct 1197", "Precinct"),
    "Precinct Chair, Precinct 1377": ("Precinct Chair", "Precinct 1377", "Precinct"),
    "Precinct Chair, Precinct 2007": ("Precinct Chair", "Precinct 2007", "Precinct"),
    "Precinct Chair, Precinct 2181": ("Precinct Chair", "Precinct 2181", "Precinct"),
    "Precinct Chair, Precinct 2220": ("Precinct Chair", "Precinct 2220", "Precinct"),
    "Precinct Chair, Precinct 2266": ("Precinct Chair", "Precinct 2266", "Precinct"),
    "Precinct Chair, Precinct 2319": ("Precinct Chair", "Precinct 2319", "Precinct"),
    "Precinct Chair, Precinct 2466": ("Precinct Chair", "Precinct 2466", "Precinct"),
    "Precinct Chair, Precinct 2524": ("Precinct Chair", "Precinct 2524", "Precinct"),
    "Precinct Chair, Precinct 2541": ("Precinct Chair", "Precinct 2541", "Precinct"),
    "Precinct Chair, Precinct 3035": ("Precinct Chair", "Precinct 3035", "Precinct"),
    "Precinct Chair, Precinct 3054": ("Precinct Chair", "Precinct 3054", "Precinct"),
    "Precinct Chair, Precinct 3072": ("Precinct Chair", "Precinct 3072", "Precinct"),
    "Precinct Chair, Precinct 3193": ("Precinct Chair", "Precinct 3193", "Precinct"),
    "Precinct Chair, Precinct 3282": ("Precinct Chair", "Precinct 3282", "Precinct"),
    "Precinct Chair, Precinct 3323": ("Precinct Chair", "Precinct 3323", "Precinct"),
    "Precinct Chair, Precinct 3330": ("Precinct Chair", "Precinct 3330", "Precinct"),
    "Precinct Chair, Precinct 3367": ("Precinct Chair", "Precinct 3367", "Precinct"),
    "Precinct Chair, Precinct 3384": ("Precinct Chair", "Precinct 3384", "Precinct"),
    "Precinct Chair, Precinct 3386": ("Precinct Chair", "Precinct 3386", "Precinct"),
    "Precinct Chair, Precinct 3390": ("Precinct Chair", "Precinct 3390", "Precinct"),
    "Precinct Chair, Precinct 3392": ("Precinct Chair", "Precinct 3392", "Precinct"),
    "Precinct Chair, Precinct 3421": ("Precinct Chair", "Precinct 3421", "Precinct"),
    "Precinct Chair, Precinct 3465": ("Precinct Chair", "Precinct 3465", "Precinct"),
    "Precinct Chair, Precinct 3529": ("Precinct Chair", "Precinct 3529", "Precinct"),
    "Precinct Chair, Precinct 3698": ("Precinct Chair", "Precinct 3698", "Precinct"),
    "Precinct Chair, Precinct 4256": ("Precinct Chair", "Precinct 4256", "Precinct"),
    "Precinct Chair, Precinct 4350": ("Precinct Chair", "Precinct 4350", "Precinct"),
    "Preference for Presidential Nominee": ("President of the United States", "Texas", "State"),
    "Proposition 1": ("Proposition 1", "Proposition 1", "Proposition 1"),
    "Proposition 10": ("Proposition 10", "Proposition 10", "Proposition 10"),
    "Proposition 11": ("Proposition 11", "Proposition 11", "Proposition 11"),
    "Proposition 2": ("Proposition 2", "Proposition 2", "Proposition 2"),
    "Proposition 3": ("Proposition 3", "Proposition 3", "Proposition 3"),
    "Proposition 4": ("Proposition 4", "Proposition 4", "Proposition 4"),
    "Proposition 5": ("Proposition 5", "Proposition 5", "Proposition 5"),
    "Proposition 6": ("Proposition 6", "Proposition 6", "Proposition 6"),
    "Proposition 7": ("Proposition 7", "Proposition 7", "Proposition 7"),
    "Proposition 8": ("Proposition 8", "Proposition 8", "Proposition 8"),
    "Proposition 9": ("Proposition 9", "Proposition 9", "Proposition 9"),
    "Railroad Commissioner": ("Railroad Commissioner", "Texas", "State"),
    "Sheriff": ("Sheriff", "Tarrant", "County"),
    "State Representative, District 101": ("State Representative", "District 101", "State Representative"),
    "State Representative, District 90": ("State Representative", "District 90", "State Representative"),
    "State Representative, District 91": ("State Representative", "District 91", "State Representative"),
    "State Representative, District 92": ("State Representative", "District 92", "State Representative"),
    "State Representative, District 93": ("State Representative", "District 93", "State Representative"),
    "State Representative, District 94": ("State Representative", "District 94", "State Representative"),
    "State Representative, District 95": ("State Representative", "District 95", "State Representative"),
    "State Representative, District 96": ("State Representative", "District 96", "State Representative"),
    "State Representative, District 97": ("State Representative", "District 97", "State Representative"),
    "State Representative, District 98": ("State Representative", "District 98", "State Representative"),
    "State Representative, District 99": ("State Representative", "District 99", "State Representative"),
    "State Senator, District 12": ("State Senate", "12", "State Senate District"),
    "State Senator, District 22": ("State Senate", "22", "State Senate District"),
    "United States Representative, District 12": ("United States Representative", "District 12", "Congressional District"),
    "United States Representative, District 24": ("United States Representative", "District 24", "Congressional District"),
    "United States Representative, District 25": ("United States Representative", "District 25", "Congressional District"),
    "United States Representative, District 26": ("United States Representative", "District 26", "Congressional District"),
    "United States Representative, District 33": ("United States Representative", "District 33", "Congressional District"),
    "United States Representative, District 6": ("United States Representative", "District 6", "Congressional District"),
    "United States Senator": ("United States Senator", "Texas", "State"),
}

input_file = "files/output.csv"  # Change this to your input CSV file path

output_file = "output/updated.csv"

try:
    df = pd.read_csv(input_file)
    
    # Ensure required columns exist
    if 'Contest Title' not in df.columns:
        print("Error: 'Contest Title' column not found.")
        sys.exit(1)
    
    # Optional columns, create if missing
    for col in ['District', 'District Type']:
        if col not in df.columns:
            df[col] = ""
    
    # Update rows
    unmapped = []
    for idx, row in df.iterrows():
        full_office = str(row['Contest Title']).strip()
        if full_office in mapping:
            new_office, district, d_type = mapping[full_office]
            df.at[idx, 'Contest Title'] = new_office
            df.at[idx, 'District'] = district
            df.at[idx, 'District Type'] = d_type
        else:
            unmapped.append(full_office)
    
    if unmapped:
        print(f"Warning: {len(set(unmapped))} unique unmapped offices found: {set(unmapped)}")
    
    # Save updated CSV
    df.to_csv(output_file, index=False)
    print(f"Updated CSV saved to '{output_file}'")
    
except FileNotFoundError:
    print(f"Error: File '{input_file}' not found. Please provide the correct path.")
except Exception as e:
    print(f"Error processing file: {e}")