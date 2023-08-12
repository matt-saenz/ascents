"""Script for analyzing ascents."""


import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

from ascent import AscentDB


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()
    return args


def make_counts_table(counts: list[tuple[Any, int]]) -> str:
    return "\n".join([f"{count:>4}  {value}" for value, count in counts])


def analyze_ascents(database: Path) -> str:
    time_stamp = datetime.now().strftime("%a %b %d %Y %I:%M:%S %p")

    with AscentDB(database) as db:
        total_count = db.total_count()
        year_counts = db.year_counts()
        crag_counts = db.crag_counts()
        grade_counts = db.grade_counts()

    analysis = "\n".join(
        [
            f"Analysis of ascents in {database}",
            f"Generated on {time_stamp}",
            "",
            f"Total number of ascents: {total_count}",
            "",
            "Count of ascents by year:",
            make_counts_table(year_counts),
            "",
            "Count of ascents by crag:",
            make_counts_table(crag_counts),
            "",
            "Count of ascents by grade:",
            make_counts_table(grade_counts),
        ]
    )

    return analysis


def main() -> None:
    args = get_args()
    analysis = analyze_ascents(args.database)
    print(analysis)


if __name__ == "__main__":
    main()
