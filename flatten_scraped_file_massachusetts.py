# 2008 Massachusetts Election Parser – FINAL & UNBREAKABLE (December 2025)
# Priority: Ward lines FIRST → then simple precincts
        # ward_match = re.search(r'.*Wd. ([A-Z0-9]+) Pct. ([A-Z0-9]+).*', cell)


# 2008 Massachusetts Election Parser – TRULY FINAL & ETERNAL (2025)
# Town detection = "anything left after ruling out everything else"

import pandas as pd
import os
import re

input_file = 'files/massachusettsele2010.csv'
output_dir = 'output'
os.makedirs(output_dir, exist_ok=True)

state_election_file = os.path.join(output_dir, '3_State_Election.csv')
voter_turnout_file  = os.path.join(output_dir, '2_Voter_Turnout.csv')
votes_stats_file    = os.path.join(output_dir, '1_Votes_Stats.csv')

try:
    df = pd.read_csv(input_file)
    print(f"Loaded {len(df):,} rows")
except:
    raise TypeError(f'Sorry faild to load PDF: {input_file}')


# Event dates
# Town, Precinct, Registered Voters, Party,	Votes, County, EventType, EventDate, OfficeTitle
EVENT_DATE_STATE = '08-25-2010'; EVENT_TYPE_STATE = 'Primary'

# Town, Precinct, Votes Cast, Party, Turnout, County, EventType, EventDate,	OfficeTitle
EVENT_DATE_TURNOUT = '09-14-2010'; EVENT_TYPE_TURNOUT = 'Primary Voter Turnout'

# Town, Precinct, Registered Voter, County, EventType, EventDate, OfficeTitle
EVENT_DATE_STATS = '11-02-2010'; EVENT_TYPE_STATS = 'General'

votes_records = []; turnout_records = []; state_records = []

county_pattern = re.compile(r'\b([A-Za-z\s\-]+)\s+County\b', re.IGNORECASE)
junk_keywords = {'total','totals','registered voters','party enrollment','turnout','statewide','2008','overseas','absentee','political designations','*','state election', 'cont'}

def clean_num(v):
    if pd.isna(v): return 0
    s = str(v).strip().replace(',', '')
    return int(float(s)) if s and s not in {'-', '—', '–', 'nan', 'NaN', '...'} else 0

def to_title(s): return ' '.join(w.capitalize() for w in s.strip().lower().split())

# ← your existing patterns and functions unchanged →

current_county = "Unknown County"
current_town   = None
current_prefix = ""
town_rows      = []           # list of (precinct_name, row_dict)
last_data_row  = None         # ← NEW: remembers the vote row for single-precinct towns

def emit_row(precinct_name, data_row):
    base = {
        'Town': current_town,
        'Precinct': precinct_name,
        'County': current_county
    }
    reg1  = clean_num(data_row.get('Registered1', 0))
    Turnout3  = clean_num(data_row.get('Turnout3', 0))
    reg3  = clean_num(data_row.get('Voter3', 0))
    cast = clean_num(data_row.get('Total Votes Cast2', 0))

# ,Registered1,Democratic1,Republican1,Libertarian1,Unenrolled1,Designations1,Democratic2,Republican2,Libertarian2,Total Votes Cast2,Voters3,Turnout3,


    # Votes_Stats
    for party, col in [('Democratic','Democratic1'), ('Republican','Republican1'),
                       ('Libertarian','Libertarian1'), ('Working Families','Working Families1'),
                       ('Unenrolled','Unenrolled1'), ('Political Designations','Designations1')]:
        votes_records.append({**base,
            'Registered Voters': reg1, 'Party': party,
            'Votes': clean_num(data_row.get(col, 0)),
            'EventType': EVENT_TYPE_STATE, 'EventDate': EVENT_DATE_STATE, 'OfficeTitle': ''})

    # Turnout
    for party, col in [('Democratic','Democratic2'), ('Republican','Republican2'),
                       ('Libertarian','Libertarian2')]:
        turnout_records.append({**base,
            'Total Votes Cast': cast, 'Party': party,
            'Votes Cast': clean_num(data_row.get(col, 0)),
            'EventType': EVENT_TYPE_TURNOUT, 'EventDate': EVENT_DATE_TURNOUT, 'OfficeTitle': ''})

    # State Election
    state_records.append({**base,
        'Registered': reg3, "Voter Turnout": Turnout3,
        'EventType': EVENT_TYPE_STATS, 'EventDate': EVENT_DATE_STATS, 'OfficeTitle': ''})

def flush_town():
    global current_town, town_rows, last_data_row

    if not current_town:
        town_rows = []
        last_data_row = None
        return

    # If we have actual precinct rows → use them
    if town_rows:
        for precinct_name, data in town_rows:          # ← FIXED: unpack tuple
            emit_row(precinct_name, data)              # ← FIXED: use precinct_name from loop

    # No precinct rows → single-precinct town → use town name as precinct
    elif last_data_row is not None:
        emit_row(current_town, last_data_row)

    # Reset state
    current_town = None
    current_prefix = ""
    town_rows = []
    last_data_row = None

print("\nProcessing rows...")

for _, row in df.iterrows():
    raw = str(row['Precinct']) if pd.notna(row['Precinct']) else ''
    if not raw.strip(): continue

    # Check if every column except 'Precinct' is empty/NaN
    other_cols = row.drop(labels='Precinct')
    if other_cols.isna().all():
        continue

    cell = re.sub(r'[…]+|\.+', ' ', raw).strip()
    lower = cell.lower()

    # 1. County
    if 'county' in lower and not any(k in lower for k in junk_keywords):
        m = county_pattern.findall(raw)
        new_county = to_title(m[-1].strip() if m else "Unknown") + " County"
        if m == new_county:
            continue
        flush_town()
        current_county = new_county
        print(f"County → {current_county}")
        continue

    # 2. Junk
    if any(k in lower for k in junk_keywords) or raw.startswith('*'):
        continue

    # 3. Precinct-like line
    is_precinct_like = (
        'wd' in lower or
        'pct' in lower or
        'ward' in lower or
        'precinct' in lower or
        re.search(r'^\s*[A-Z0-9]{1,2}\s*$', cell)
    )

    if current_town and is_precinct_like:
        precinct_name = current_town

        if re.search(r'\bwd\.?\b', lower) and re.search(r'\bpct\.?\b|\bprecinct\b', lower):
            ward_m = re.search(r'\bwd\.?\s*([A-Z0-9]+)', lower, re.I)
            if ward_m:
                current_prefix = f"Ward {ward_m.group(1).upper()} Precinct "  # ← clean, no comma
                pct_m = re.search(r'\bpct\.?\s*([A-Z0-9]+)', cell, re.I)
                pid = pct_m.group(1).upper() if pct_m else re.search(r'\b([A-Z0-9]+)\b', cell).group(1).upper()
                precinct_name = current_prefix + pid

        elif current_prefix and re.search(r'\b[A-Z0-9]+\b', cell):
            match = re.search(r'\b([A-Z0-9]+)\b', cell)
            precinct_name = current_prefix + match.group(1).upper()

        else:
            cleaned = re.sub(r'(?i)\b(pct\.?|precinct)[\. ]*', '', cell).strip()
            match = re.search(r'\b([A-Z0-9]+)\b', cleaned or cell)
            precinct_name = match.group(1).upper() if match else cleaned or cell.strip()

        precinct_name = re.sub(r'\s+', ' ', precinct_name).strip()
        town_rows.append((precinct_name, row.to_dict()))
        last_data_row = None  # we have real precincts
        continue

    # 4. New town detected
    if re.search(r'[A-Za-z]', cell):
        flush_town()                                   # ← saves previous town (including single-precinct)
        current_town = to_title(cell)
        current_prefix = ""
        town_rows = []
        last_data_row = row.to_dict()                  # ← SAVE THIS ROW — it's the only one!
        print(f"  Town → {current_town}")
        continue

    # Fallback: if we get here and have a current town, save the row (very rare)
    if current_town:
        last_data_row = row.to_dict()

# Final flush — catches the very last town
flush_town()

# Save files
def save_csv(recs, path, extra=False):
    if not recs:
        pd.DataFrame().to_csv(path, index=False)
        return
    df_out = pd.DataFrame(recs)
    cols = [c for c in df_out.columns if c not in ['County','EventType','EventDate','OfficeTitle']] + ['County']
    if extra:
        cols += ['EventType', 'EventDate', 'OfficeTitle']
    df_out[cols].to_csv(path, index=False)

save_csv(votes_records,   votes_stats_file,    True)
save_csv(turnout_records, voter_turnout_file,  True)
save_csv(state_records,   state_election_file, True)

print("\nETERNAL VICTORY ACHIEVED.")
print(f"   Votes_Stats:     {len(votes_records):,}")
print(f"   Voter_Turnout:   {len(turnout_records):,}")
print(f"   State_Election:  {len(state_records):,}")

