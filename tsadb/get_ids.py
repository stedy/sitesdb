import csv
ids = []
reader = csv.reader(open("test_ids.csv"))
for line in reader:
    ids.append(line[0])
print ids
