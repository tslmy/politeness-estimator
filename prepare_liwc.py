## Convert LIWC Dictionary from its original `.dic` format to "long-form" `CSV`
try:
    raw_lines = open("LIWC2015_Dictionary.dic", "r").readlines()[1:]
except FileNotFoundError:
    print("Kindly put `LIWC2015_Dictionary.dic` here, please.")
    import sys

    sys.exit()

import re

whitespace_pattern = re.compile("\t+")
leftAligned_lines = [line.strip() for line in raw_lines]
whitespace_lines = [whitespace_pattern.sub("\t", line) for line in leftAligned_lines]
# find boundary:
for i, line in enumerate(whitespace_lines):
    if line is "%":
        break
# Split lines:
label_lines = whitespace_lines[:i]
dict_lines = whitespace_lines[i + 1 :]
# Make mapping:
labels = {}
for line in label_lines:
    parts = line.split("\t")
    if len(parts) < 2:
        print(f'This line is not long enough: "{line}"')
        continue
    ID, label = parts[:2]
    if not ID.isnumeric():
        print(f'What is "{line}"?')
        continue
    labels[ID] = label[: label.find(" ")].title()
# Write CSV -- no need for `pandas`:
tokens = ["term,category\n"]
for line in dict_lines:
    parts = line.split("\t")
    token = parts[0]
    IDs = parts[1:]
    for ID in IDs:
        tokens.append(token + "," + labels[ID] + "\n")
# Write to file:
open("liwc15.csv", "w").writelines(tokens)
