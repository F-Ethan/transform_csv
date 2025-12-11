import os
import csv
import re
from collections import Counter

folder = "files"
output_file = "output/unique_results.csv"
		
# columns = ["District Name", "District Type", "Office"]
# columns = ["Contest Title", "District", "District Type"]
columns = ['CandidateParty']
# columns = ['OfficeName', 'DistrictName']

unique_counts = Counter()

for filename in os.listdir(folder):
    if not filename.endswith('.csv'):
        continue
    filepath = os.path.join(folder, filename)
    with open(filepath, 'r', newline='') as csvfile:
        print(f'reading file {csvfile}')
        reader = csv.DictReader(csvfile)
        for row in reader:
            key = tuple(row.get(col, '') for col in columns)
            unique_counts[key] += 1

# Separate those containing "proposition"
proposition_list = {}
cc_list = {}
for key, count in unique_counts.items():
    combined = ' '.join(key)
    if re.search(r'proposition', combined, re.IGNORECASE):
        proposition_list[key] = count
    else:
        cc_list[key] = count

# Output all uniques with counts
print("All unique strings and their counts:")
for key, count in sorted(cc_list.items(), key=lambda x: x[1], reverse=True):
    print(f"{' '.join(key)}: {count}")

# Output separate list for "proposition"
print("\nUnique strings containing 'proposition' and their counts:")
for key, count in sorted(proposition_list.items(), key=lambda x: x[1], reverse=True):
    print(f"{' '.join(key)}: {count}")

# Write to output file
if not os.path.exists(output_file):
    with open(output_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Type', 'OfficeName', 'DistrictName', 'DistrictType', 'BallotQuestionType', 'BallotQuestionText', 'Count'])

with open(output_file, 'a', newline='') as csvfile:
    writer = csv.writer(csvfile)
    
    # Write propositions
    for key, count in sorted(proposition_list.items(), key=lambda x: x[1], reverse=True):
        # writer.writerow(['Proposition'] + list(key) + [count])
        writer.writerow(list(key))
    
    # Write CC
    for key, count in sorted(cc_list.items(), key=lambda x: x[1], reverse=True):
        # writer.writerow(['CC'] + list(key) + [count])
        writer.writerow(list(key))
    
    # Write summary as a separate row
    writer.writerow(['Summary', f'There are {len(cc_list)} CC, and {len(proposition_list)} Propositions', '', '', '', '', ''])

print("- - - - - - - - - ")
print("- - - - - - - - - ") 
print("- - - - - - - - - ")
print("- - - - - - - - - ")
print(f'There are {len(cc_list)} CC, and {len(proposition_list)} Propositions')
print("- - - - - - - - - ")
print("- - - - - - - - - ")
print("- - - - - - - - - ")
print("- - - - - - - - - ")