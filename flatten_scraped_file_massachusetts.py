# 2008 Massachusetts Election Parser – FINAL & UNBREAKABLE (December 2025)
# Priority: Ward lines FIRST → then simple precincts
        # ward_match = re.search(r'.*Wd. ([A-Z0-9]+) Pct. ([A-Z0-9]+).*', cell)


# 2008 Massachusetts Election Parser – TRULY FINAL & ETERNAL (2025)
# Town detection = "anything left after ruling out everything else"

import pandas as pd
import os
import re

input_file = 'files/massachusettsele1996.csv'
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
# Town, Precinct, Registered Voters, Party,	Votes, County, EventType, EventDate, OfficeTitle 14-Sep-82
EVENT_DATE_STATE = '09-20-1994'; EVENT_TYPE_STATE = 'Primary' 

# Town, Precinct, Votes Cast, Party, Turnout, County, EventType, EventDate,	OfficeTitle 
EVENT_DATE_TURNOUT = '09-20-1994'; EVENT_TYPE_TURNOUT = 'Primary Voter Turnout'

# Town, Precinct, Registered Voter, County, EventType, EventDate, OfficeTitle 
EVENT_DATE_STATS = '11-08-1994'; EVENT_TYPE_STATS = 'General'

votes_records = []; turnout_records = []; state_records = []

county_pattern = re.compile(r'\b([A-Za-z\s\-]+)\s+County\b', re.IGNORECASE)
junk_keywords = {
    'total', 'aggregate', 'totals','registered voters','party enrollment', 'community',
    'turnout','statewide','2008','overseas','absentee','political designations',
    '*','state election', 'cont', 'registered voters, party enrollment and turnout'}

def clean_num(v):
    if pd.isna(v): return 0
    try:
        s = str(v).strip().replace(',', '')
        return int(float(s)) if s and s not in {'-', '—', '–', 'nan', 'NaN', '...'} else 0\
        
    except:
        print(f"Not a number:{s}")
        TypeError(f"{s}: is not a number")
        

def to_title(s): return ' '.join(w.capitalize() for w in s.strip().lower().split())

# ← your existing patterns and functions unchanged →

current_county = "Unknown County"
current_town   = None
current_prefix = ""
town_rows      = []           # list of (precinct_name, row_dict)
last_data_row  = None         # ← NEW: remembers the vote row for single-precinct towns

def emit_row(base_dict, target_list, specific_fields):
    """
    Append a single standardised record to the specified target list.
    
    Parameters:
        base_dict:        Dictionary containing common fields (Town, Precinct, County).
        target_list:      The global list to append to (e.g., votes_records, turnout_records, state_records).
        specific_fields:  Dictionary of event-specific fields to merge into the record.
    """
    record = {
        **base_dict,
        **specific_fields,
        'EventDate': specific_fields.get('EventDate', ''),  # Ensure consistent keys if needed
        'OfficeTitle': ''
    }
    target_list.append(record)


def flush_town():
    global current_town, town_rows, last_data_row

    if not current_town:
        town_rows = []
        last_data_row = None
        return

    # Indicator column sets
    reg_party_columns = ['Democratic1', 'Republican1', 'Unenrolled1']
    turnout_columns = ['Total Votes Cast2', 'Democratic2', 'Republican2']

    # Detect presence of precinct-level data
    has_precinct_registration = any(
        sum(clean_num(data.get(col, 0)) for col in reg_party_columns) > 0
        for _, data in town_rows
    )

    has_precinct_turnout = any(
        sum(clean_num(data.get(col, 0)) for col in turnout_columns) > 0
        for _, data in town_rows
    )

    # Helper to create base dictionary
    def make_base(precinct_name):
        return {
            'Town': current_town,
            'Precinct': precinct_name,
            'County': current_county
        }

    # === Emit registration-by-party records (EVENT_TYPE_STATE) ===
    if has_precinct_registration and town_rows:
        # Use precinct-level rows
        for precinct_name, data in town_rows:
            base = make_base(precinct_name)
            reg1 = clean_num(data.get('Registered1', 0))

            for party, col in [
                ('Democratic', 'Democratic1'),
                ('Republican', 'Republican1'),
                ('Unenrolled', 'Unenrolled1'),
            ]:
                emit_row(
                    base,
                    votes_records,
                    {
                        'Registered Voters': reg1,
                        'Party': party,
                        'Votes': clean_num(data.get(col, 0)),
                        'EventType': EVENT_TYPE_STATE,
                        'EventDate': EVENT_DATE_STATE
                    }
                )
    elif last_data_row is not None:
        # Fall back to town-level row
        base = make_base(current_town)
        reg1 = clean_num(last_data_row.get('Registered1', 0))

        for party, col in [
            ('Democratic', 'Democratic1'),
            ('Republican', 'Republican1'),
            ('Unenrolled', 'Unenrolled1'),
        ]:
            emit_row(
                base,
                votes_records,
                {
                    'Registered Voters': reg1,
                    'Party': party,
                    'Votes': clean_num(last_data_row.get(col, 0)),
                    'EventType': EVENT_TYPE_STATE,
                    'EventDate': EVENT_DATE_STATE
                }
            )

    # === Emit turnout-by-party records (EVENT_TYPE_TURNOUT) ===
    if has_precinct_turnout and town_rows:
        # Use precinct-level rows
        for precinct_name, data in town_rows:
            base = make_base(precinct_name)
            cast = clean_num(data.get('Total Votes Cast2', 0))

            for party, col in [
                ('Democratic', 'Democratic2'),
                ('Republican', 'Republican2'),
            ]:
                emit_row(
                    base,
                    turnout_records,
                    {
                        'Total Votes Cast': cast,
                        'Party': party,
                        'Votes Cast': clean_num(data.get(col, 0)),
                        'EventType': EVENT_TYPE_TURNOUT,
                        'EventDate': EVENT_DATE_TURNOUT
                    }
                )
    elif last_data_row is not None:
        # Fall back to town-level row
        base = make_base(current_town)
        cast = clean_num(last_data_row.get('Total Votes Cast2', 0))

        for party, col in [
            ('Democratic', 'Democratic2'),
            ('Republican', 'Republican2'),
        ]:
            emit_row(
                base,
                turnout_records,
                {
                    'Total Votes Cast': cast,
                    'Party': party,
                    'Votes Cast': clean_num(last_data_row.get(col, 0)),
                    'EventType': EVENT_TYPE_TURNOUT,
                    'EventDate': EVENT_DATE_TURNOUT
                }
            )

        # === Emit overall statistics (EVENT_TYPE_STATS) ===
    # Emit a statistics record for every precinct row when precinct data is available;
    # otherwise, emit a single record using the town-level row.
    if town_rows:
        # Precinct rows exist → emit one statistics record per precinct
        for precinct_name, data in town_rows:
            base = make_base(precinct_name)
            reg3 = clean_num(data.get('Registered Voters3', 0))
            turnout3 = clean_num(data.get('Voter Turnout3', 0))

            emit_row(
                base,
                state_records,
                {
                    'Registered': reg3,
                    'Voter Turnout': turnout3,
                    'EventType': EVENT_TYPE_STATS,
                    'EventDate': EVENT_DATE_STATS
                }
            )
    elif last_data_row is not None:
        # No precinct rows → emit a single record for the town
        base = make_base(current_town)
        reg3 = clean_num(last_data_row.get('Registered Voters3', 0))
        turnout3 = clean_num(last_data_row.get('Voter Turnout3', 0))

        emit_row(
            base,
            state_records,
            {
                'Registered': reg3,
                'Voter Turnout': turnout3,
                'EventType': EVENT_TYPE_STATS,
                'EventDate': EVENT_DATE_STATS
            }
        )

    # Reset state
    current_town = None
    town_rows = []
    last_data_row = None

for index, row in df.iterrows():
    raw = str(row['Precinct']) if pd.notna(row['Precinct']) else ''
    if not raw.strip(): 
        continue

    cell = re.sub(r'[…]+|\.+', ' ', raw).strip()
    lower = cell.lower()

    if index < 2:
        continue

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

    # New: Check if other columns are all empty/NaN (header-like ward line)
    other_cols = row.drop(labels='Precinct')
    if other_cols.isna().all():
        # Attempt to detect and set ward prefix (e.g., "Wd. 1")
        if re.search(r'\bwd\.?\b', lower):
            ward_m = re.search(r'\bwd\.?\s*([A-Z0-9]+)', lower, re.I)
            if ward_m:
                current_prefix = f"Ward {ward_m.group(1).upper()} Precinct "
                print(f"    Set ward prefix from header line: {current_prefix}")
        # If no ward match, ignore this empty row (as before)
        continue

    # 3. Precinct-like line (now only for data-containing rows)
    is_precinct_like = (
        'wd' in lower or
        'pct' in lower or
        'ward' in lower or
        'precinct' in lower or
        re.search(r'^\s*[A-Z0-9]{1,3}\s*$', cell)
    )

    if current_town and is_precinct_like:
        precinct_name = current_town

        if re.search(r'\bwd\.?\b', lower):
            ward_m = re.search(r'\bwd\.?\s*([A-Z0-9]+)', lower, re.I)
            if ward_m:
                current_prefix = f"Ward {ward_m.group(1).upper()} Precinct "  # ← clean, no comma
                pct_m = re.search(r'\bpct\.?\s*([A-Z0-9]+)', cell, re.I)
                pid = pct_m.group(1).upper() if pct_m else "0"
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

