"""Script for initializing ascent database."""


import sqlite3
import sys
from pathlib import Path

import utils

GradeInfoData = list[tuple[str, int, str | None]]


def generate_grade_info_data() -> GradeInfoData:
    grade_info_data: GradeInfoData = []

    for number in range(16):
        if number < 10:
            grade_info_data.append((f"5.{number}", number, None))
        else:
            for letter in "abcd":
                grade_info_data.append((f"5.{number}{letter}", number, letter))

    return grade_info_data


def init_ascent_db(database: Path) -> None:
    if database.exists():
        sys.exit(f"Error: {database} already exists")

    grade_info_data = generate_grade_info_data()

    connection = sqlite3.connect(database)

    try:
        cursor = connection.cursor()

        cursor.executescript(
            """
            CREATE TABLE ascents(
                route TEXT NOT NULL,
                grade TEXT NOT NULL,
                crag TEXT NOT NULL,
                date TEXT NOT NULL,
                PRIMARY KEY(route, grade, crag)
            );

            CREATE TABLE grade_info(
                grade TEXT PRIMARY KEY,
                grade_number INTEGER NOT NULL,
                grade_letter TEXT
            );
            """
        )

        cursor.executemany(
            """
            INSERT INTO grade_info
            VALUES(?, ?, ?)
            """,
            grade_info_data,
        )

        connection.commit()
    finally:
        connection.close()


def main() -> None:
    args = utils.get_args()
    init_ascent_db(args.database)


if __name__ == "__main__":
    main()
