import pandas as pd
import os
import re
from typing import Tuple, Optional

input_file = '../files/massachusettsele1978-Nov-Cities.csv'
output_dir = '../output'
os.makedirs(output_dir, exist_ok=True)

state_election_file = os.path.join(output_dir, '3_State_Election.csv')
voter_turnout_file  = os.path.join(output_dir, '2_Voter_Turnout.csv')
votes_stats_file    = os.path.join(output_dir, '1_Primary.csv')

#skip the first lines (set to the first line (-1) with real data)
start_line = 0

try:
    df = pd.read_csv(input_file)
    df = df.reset_index(drop=True)
    print(f"Loaded {len(df):,} rows")
except():
    raise TypeError(f'Sorry faild to load PDF: {input_file}')


# Event dates
# Town, Precinct, Registered Voters, Party,	Votes, County, EventType, EventDate, OfficeTitle 14-Sep-82
EVENT_DATE_STATE = '02-11-1992'; EVENT_TYPE_STATE = 'Primary' 

# Town, Precinct, Votes Cast, Party, Turnout, County, EventType, EventDate,	OfficeTitle 
EVENT_DATE_TURNOUT = '09-18-1984'; EVENT_TYPE_TURNOUT = 'Primary Voter Turnout'

# Town, Precinct, Registered Voter, County, EventType, EventDate, OfficeTitle 
EVENT_DATE_STATS = '11-06-1984'; EVENT_TYPE_STATS = 'Town Election'

votes_records = []; turnout_records = []; state_records = []

county_pattern = re.compile(r'\b([A-Za-z\s\-]+)\s+County\b', re.IGNORECASE)
junk_keywords = [
    # 'total', 'aggregate', 'totals','registered voters','party enrollment', 'community',
    # 'turnout','statewide','2008','overseas','absentee','political designations',
    # '*','state election', 'cont', 'registered voters, party enrollment and turnout', 'cities, wards and', "CITIES, WARDS AND",
    # 'town elections', 'date of', 'date of election', 'election', 'towns and', "voting", "voting precincts", "village",
    # 'nov. 4, 1980', 'registered voters and people who voted at elections', 'towns and voting precincts', 
    # 'voting precincts', 'towns', 'counties', 'registered', 'cities, wards and cities', "Registered", "town at"
]

def clean_num(v):
    if pd.isna(v):
        return 0
    try:
        s = str(v).strip().replace(',', '')
        s = s.rstrip('.')
        invalid_strings = {'-', '—', '–', 'nan', 'NaN', '...', '.', '..', '.....', '-----', '---'}  
        if s in invalid_strings or not s:
            return 0
        return int(float(s))
    except (ValueError, TypeError):
        raise TypeError(f"{s}: is not a number")

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

# ────────────────────────────────────────────────
#  Helper: try to extract ward & precinct numbers
# ────────────────────────────────────────────────
def extract_ward_and_precinct(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Returns (ward_number, precinct_number) or (None, None)
    Handles most common orderings and abbreviations
    """
    # print("starting extract_ward_and_precinct" )
    # print("="* 10 )
    lower = text.lower()
    # print(lower)

    # Pattern 1: ward/wd first, then optional pct/precinct
    m = re.search( # Wd. 1 Pct. A . . . .
        r'\b(?:wd|ward)\.?\s*([A-Z0-9]+)'
        r'(?:\s*(?:pct\.?|precinct\.?)\s*([A-Z0-9]+))?',
        lower, re.IGNORECASE
    )
    # print("first step..." )

    if m:
        ward = m.group(1).upper()
        pct  = m.group(2).upper() if m.group(2) else None
        # print(f"    Ward, Pct → {ward}, {pct}")
        return ward, pct

    # Pattern 2: pct/precinct first, then ward/wd
    m = re.search(
        r'\b(?:pct\.?|precinct\.?)\s*([A-Z0-9]+)'
        r'(?:\s*(?:wd|ward)\.?\s*([A-Z0-9]+))?',
        lower, re.IGNORECASE
    )
    # print("Second step..." )

    if m:
        pct  = m.group(1).upper()
        ward = m.group(2).upper() if m.group(2) else None
        return ward, pct

    # Pattern 3: two standalone alphanum tokens (legacy style)
    m = re.match(r'^\s*([A-Z0-9]{1,4})\s+([A-Z0-9]{1,4})\s*$', lower)
    # print("Third step..." )

    if m:
        a, b = m.group(1).upper(), m.group(2).upper()
        return a, b
    # print("failed, returning none" )

    return None, None


def flush_town():
    global current_town, town_rows, last_data_row

    if not current_town:
        town_rows = []
        last_data_row = None
        return
    
    #  Current columns
    #  Precinct,Date,Registered Voters4,Voter Turnout4,Registered3,Turnout3

    # Centralized party-column mappings (tuples: (party_name, column_name))
    registration_parties = [
        ('Democratic', 'Democratic1'),
        ('Republican', 'Republican1'),
        ('Independent', 'Independent1'),
        # ('Reform', 'Reform1'),
        ('Libertarian', 'Libertarian1'),
        # ('American', 'American1'),
        ('Unenrolled', 'Unenrolled1'),
        # ('Green Rainbow', 'Green1'),
    ]

    turnout_parties = [
        ('Democratic', 'Democratic2'),
        ('Republican', 'Republican2'),
        # ('Green Rainbow', 'Green2'),
        # ('Libertarian', 'Libertarian2'),
        # ('Reform', 'Reform2'),
        # ('Independent', 'Independent2'),
    ]


    # Indicator column sets for detection
    reg_party_columns = [col for _, col in registration_parties]
    turnout_columns = [col for _, col in turnout_parties]

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
    rows_to_use = town_rows if has_precinct_registration and town_rows else ([(current_town, last_data_row)] if last_data_row is not None else [])
    
    for precinct_name, data in rows_to_use:
        base = make_base(precinct_name if has_precinct_registration else current_town)
        reg1 = clean_num(data.get('Registered1', 0))

        for party, col in registration_parties:
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

    # === Emit turnout-by-party records (EVENT_TYPE_TURNOUT) ===
    rows_to_use = town_rows if has_precinct_turnout and town_rows else ([(current_town, last_data_row)] if last_data_row is not None else [])
    
    for precinct_name, data in rows_to_use:
        base = make_base(precinct_name if has_precinct_turnout else current_town)
        cast = clean_num(data.get('Total2', 0))

        for party, col in turnout_parties:
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

    # === Emit overall statistics (EVENT_TYPE_STATS) ===
    # Use precinct rows if available; otherwise fall back to town-level row
    if town_rows:
        rows = town_rows
        use_precinct = True
    elif last_data_row is not None:
        rows = [(current_town, last_data_row)]
        use_precinct = False
    else:
        rows = []

    for precinct_name, data in rows:
        base = make_base(precinct_name if use_precinct else current_town) 
        reg3 = clean_num(data.get('Registered3', 0))
        turnout3 = clean_num(data.get('Turnout3', 0))

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

    cell = re.sub(r'[…]+|\.+|"|\'|\' \'\' \, \'\'|,', ' ', raw).strip()
    lower = cell.lower()

    if index <= start_line:
        continue

    if 'break' in lower:
        break

    # 1. County
    if 'county' in lower and not any(k in lower for k in junk_keywords):
        m = county_pattern.findall(raw)
        new_county = to_title(m[-1].strip() if m else "Unknown") + " County"
        if new_county == current_county:
            continue
        flush_town()
        current_county = new_county
        print(f"County → {current_county}")
        continue

    # 2. Junk
    if any(k in lower for k in junk_keywords) or raw.startswith('*'):
        continue

    # # New: Check if other columns are all empty/NaN (header-like ward line)
    # other_cols = row.drop(labels='Precinct')
    # if other_cols.isna().all():
    #     # Attempt to detect and set ward prefix (e.g., "Wd. 1")
    #     if re.search(r'\bwd\.?\b', lower):
    #         ward_m = re.search(r'\bwd\.?\s*([A-Z0-9]+)', lower, re.I)
    #         if ward_m:
    #             current_prefix = f"Ward {ward_m.group(1).upper()} Precinct "
    #             print(f"    Set ward prefix from header line: {current_prefix}")
    #     # If no ward match, ignore this empty row (as before)
    #     continue


# ────────────────────────────────────────────────
#  Main logic (replace your current block)
# ────────────────────────────────────────────────
    s_precinct_like = (
        'wd'      in lower or
        'pct'     in lower or
        'ward'    in lower or
        'precinct'in lower or
        re.search(r'^\s*[A-Z0-9]{1,3}\s*$', cell) or
        re.search(r'^\s*[A-Z0-9]{1,3}\s+[A-Z0-9]{1,4}\s*$', cell, re.IGNORECASE)
    )

    if current_town and s_precinct_like:
        precinct_name = current_town

        ward_num, pct_num = extract_ward_and_precinct(cell)

        if ward_num:
            current_prefix = f"Ward {ward_num} Precinct "
            if pct_num:
                precinct_name = current_prefix + pct_num
            elif current_prefix and re.search(r'\b[A-Z0-9]+\b', cell):
                # fallback: single number after prefix already set
                m = re.search(r'\b([A-Z0-9]+)\b', cell)
                if m:
                    precinct_name = current_prefix + m.group(1).upper()
        elif current_prefix:
            cleaned = re.sub(r'(?i)\b(pct\.?|precinct)[\.\s]*', '', cell).strip()
            m = re.search(r'\b([A-Z0-9]+)\b', cleaned or cell)
            if m:
                precinct_name = f"{current_prefix} {m.group(1).upper()}"
            else:
                precinct_name = f"{current_prefix} {cleaned or cell.strip()}"

        else:
            # No ward found → treat as plain precinct number
            cleaned = re.sub(r'(?i)\b(pct\.?|precinct)[\.\s]*', '', cell).strip()
            m = re.search(r'\b([A-Z0-9]+)\b', cleaned or cell)
            if m:
                precinct_name = f"{m.group(1).upper()}"
            else:
                precinct_name = cleaned or cell.strip()

        precinct_name = re.sub(r'\s+', ' ', precinct_name).strip()
        town_rows.append((precinct_name, row.to_dict()))
        continue

    # else:
    #     print("got passed the precinct line: %s", cell)

    # 4. New town detected
    if re.search(r'[A-Za-z]', cell):
        flush_town()                                   # ← saves previous town (including single-precinct)
        current_town = to_title(cell)
        current_prefix = ""
        town_rows = []
        last_data_row = row.to_dict()                  # ← SAVE THIS ROW 
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

