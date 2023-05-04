#! /bin/env python


def examine_file(lines):
    data = {}
    for i, line in enumerate(lines):
        if "quick room shielding test" in line.lower():
            data['filename'] = line.split()[0]
        if "Shield material" in line:
            data['material'] = line.split(':')[1].strip()
        elif "Shield thickness" in line:
            data['thickness'] = float(line.split(':')[1].split()[0])
        elif 'passed the 10 statistical checks' in line: 
            data['stats_failed'] = 0
        elif 'of 10 tfc bin checks' in line:
            data['stats_failed'] = int(line.split()[0].strip())
        elif '1tally fluctuation charts' in line:
            tally_line = i
            break
    for i, line in enumerate(lines[tally_line+4:]):
        if line.strip() == '':
            val_line = lines[tally_line + 4 + i - 1]
            vals = val_line.split()
            data['dose'], data['relerr'] = float(vals[1]), float(vals[2])
            break
    return data

from glob import glob
oufiles = glob('*ou')
dataset = []
for oufile in sorted(oufiles):
    lines = open(oufile).readlines()
    dataset.append(examine_file(lines))

import csv
with open('data.csv', 'w') as f:
    cols = dataset[0].keys()
    writer = csv.DictWriter(f, cols)
    writer.writeheader()
    for row in dataset:
        writer.writerow(row)

