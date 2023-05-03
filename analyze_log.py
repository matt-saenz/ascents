"""Script for running a basic log analysis."""


import collections
from datetime import datetime
import re
import sys

from ascent import AscentLog


script = sys.argv[0]
args = sys.argv[1:]

if not args:
    sys.exit(f"Usage: {script} csvfile")

csvfile = args[0]


# Load log rows

rows = AscentLog(csvfile).rows

if not rows:
    sys.exit("Error: Cannot generate analysis for empty log")


# Begin analysis

ts = datetime.now().strftime("%a %b %d %Y %I:%M:%S %p")

print(f"Analysis of {csvfile}\nGenerated on {ts}\n")

print(f"Total number of ascents: {len(rows)}\n")


def count(values, sort_key=None):
    value_counts = sorted(collections.Counter(values).items(), key=sort_key)
    table = "\n".join([f"{count:>4}  {value}" for value, count in value_counts])
    return table


# Counts by year
years = [int(row["date"][:4]) for row in rows]
print(f"Count of ascents by year:\n{count(years)}\n")

# Counts by crag
crags = [row["crag"] for row in rows]
print(f"Count of ascents by crag:\n{count(crags)}\n")


# Count by grade
def grade_key(grade):
    match = re.search(r"(?<=5\.)([0-9]+)([a-d]*)", grade)
    return int(match[1]), match[2]


grades = [row["grade"] for row in rows]

print(
    "Count of ascents by grade:",
    count(grades, sort_key=lambda item: grade_key(item[0])),
    sep="\n",
)
