"""Script for analyzing ascents."""


import argparse
from datetime import datetime
from pathlib import Path

from ascent import AscentDB


parser = argparse.ArgumentParser()
parser.add_argument("database", type=Path)
args = parser.parse_args()


with AscentDB(args.database) as db:
    total_count = db.total_count()
    year_counts = db.year_counts()
    crag_counts = db.crag_counts()
    grade_counts = db.grade_counts()


def table(counts):
    return "\n".join([f"{count:>4}  {value}" for value, count in counts])


time_stamp = datetime.now().strftime("%a %b %d %Y %I:%M:%S %p")

analysis = f"""Analysis of ascents in {args.database}
Generated on {time_stamp}

Total number of ascents: {total_count}

Count of ascents by year:
{table(year_counts)}

Count of ascents by crag:
{table(crag_counts)}

Count of ascents by grade:
{table(grade_counts)}"""

print(analysis)
