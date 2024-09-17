from datetime import datetime
from typing import Any

from ascents._models import AscentDB, Search
from ascents._utils import make_ascents_table


def make_counts_table(
    counts: list[tuple[Any, int]],
) -> str:
    return "\n".join([f"{count:>4}  {value}" for value, count in counts])


def make_max_grade_by_year_table(
    max_grade_by_year: list[tuple[int, str]],
) -> str:
    return "\n".join([f"{year}  {grade}" for year, grade in max_grade_by_year])


def analyze_ascent_db(db: AscentDB) -> str:
    timestamp = datetime.now().strftime("%a %b %d %Y %I:%M:%S %p")

    with db:
        total_count = db.total_count()
        year_counts = db.year_counts()
        crag_counts = db.crag_counts()
        grade_counts = db.grade_counts()

        max_grade = db.max_grade()
        max_grade_by_year = db.max_grade_by_year()
        hardest_ascents = db.ascents(Search(grade=max_grade))

        latest_date = db.latest_date()
        latest_ascents = db.ascents(Search(date=latest_date))

    analysis = "\n".join(
        [
            f"Analysis of ascents in {db.name}",
            f"Generated on {timestamp}",
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
            "",
            f"Max grade ascended: {max_grade}",
            "",
            "Max grade ascended by year:",
            make_max_grade_by_year_table(max_grade_by_year),
            "",
            "Hardest ascent(s):",
            make_ascents_table(hardest_ascents),
            "",
            f"Latest date of an ascent: {latest_date}",
            "",
            "Latest ascent(s):",
            make_ascents_table(latest_ascents),
        ]
    )

    return analysis
