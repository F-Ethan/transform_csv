
# This code is set up to proccess single page csv files that are grouped first by the 
# Precinct and secondly by the Contests. 



import csv

input_file = 'Bexar County -  November 5, 2024 Official Precinct Report.csv'  # Replace with your input file name
output_file = 'output.csv'  # Replace with your desired output file name

with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
    reader = csv.reader(infile)  # If tab-separated, add: delimiter='\t'
    writer = csv.writer(outfile)

    # Write the output header
    header = [
        'Precinct Name',
        'Number of Winners',
        'Contest Title',
        'Candidate Name',
        'Candidate Total Votes',
        'VOTE %',
        'Election Day',
        'Absentee',
        'Early Voting',
        'Total Votes Cast',
        'Total Election Day',
        'Total Absentee',
        'Total Early Voting'
    ]
    writer.writerow(header)

    current_stats = {
        'Registered Voters - Total': 0,
        'Ballots Cast - Total': 0,
        'Ballots Cast - Blank': 0,
        'Voter Turnout - Total': 0,
        'Total Votes Cast': 0,
        'Total Election Day': 0,
        'Total Absentee': 0,
        'Total Early Voting': 0
    }

    current_precinct = None
    current_vote_for = None
    current_contest = None
    in_contest = False

    for row in reader:
        # Pad short rows to at least 9 columns
        if len(row) < 9:
            row += [''] * (9 - len(row))

        # Check if row is empty (all cells are empty or whitespace)
        if not any(cell.strip() for cell in row):
            continue

        # Strip whitespace from all cells
        row = [cell.strip() for cell in row]

        # Detect precinct (in column A, others mostly empty)
        if row[0] and not any(row[1:4]):
            current_precinct = row[0]
            continue

        # Detect statistics section
        if row[3] == 'Statistics':
            print('Statistics')
            current_contest = 'Statistics'
            in_contest = False
            continue


        # Detect start of a contest (Vote For X in column B, contest title in column D)
        if row[1]:
            print('Voting start')
            current_vote_for = row[1]
            current_contest = row[3]
            in_contest = True
            continue

        # Parse statistics section
        if current_contest == 'Statistics':
            if row[2] in current_stats:
                current_stats[row[2]] = row[4] if row[4] else '0'
            continue

        # Capture candidate rows (candidate in column C, votes in D-H)
        if in_contest and row[2]:  # Ensure candidate name exists
            candidate = row[2]
            total_votes = row[4]
            vote_pct = row[5]
            eday = row[6]
            absentee = row[7]
            early = row[8]

            if current_precinct and current_contest and current_vote_for:
                out_row = [
                    current_precinct,
                    current_vote_for,
                    current_contest,
                    candidate,
                    total_votes,
                    vote_pct,
                    eday,
                    absentee,
                    early,
                    current_stats['Ballots Cast - Total'],
                    current_stats['Total Election Day'],
                    current_stats['Total Absentee'],
                    current_stats['Total Early Voting']
                ]
                writer.writerow(out_row)

    print(f"Transformation complete. Output written to {output_file}")