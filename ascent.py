"""Module defining Route, Ascent, and AscentDB classes."""


import datetime
import re
import sqlite3
from pathlib import Path
from typing import Self


class Route:
    def __init__(self, name: str, grade: str, crag: str) -> None:
        self.name = name
        self.grade = grade
        self.crag = crag

    @property
    def grade(self) -> str:
        return self._grade

    @grade.setter
    def grade(self, value: str) -> None:
        valid_yds = re.search(r"^5\.([0-9]|1[0-5][a-d])$", value)

        if valid_yds is None:
            raise RouteError(
                "grade must be in YDS with no pluses, minuses, or slashes "
                "(translate as needed)"
            )

        self._grade = value

    def __str__(self) -> str:
        return f"{self.name} {self.grade} at {self.crag}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Route):
            return NotImplemented

        return (
            self.name == other.name
            and self.grade == other.grade
            and self.crag == other.crag
        )


class Ascent:
    def __init__(self, route: Route, date: datetime.date) -> None:
        self.route = route
        self.date = date

    @property
    def date(self) -> datetime.date:
        return self._date

    @date.setter
    def date(self, value: datetime.date) -> None:
        if value > datetime.date.today():
            raise AscentError("date cannot be in the future")

        self._date = value

    def __str__(self) -> str:
        return f"{self.route} on {self.date}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Ascent):
            return NotImplemented

        return self.route == other.route and self.date == other.date


class AscentDB:
    def __init__(self, database: Path) -> None:
        if not database.exists():
            raise AscentDBError(
                f"{database} not found, must be an already initialized ascent database"
            )

        self._database = database

    def __enter__(self) -> Self:
        self._connection = sqlite3.connect(self._database)
        self._cursor = self._connection.cursor()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:  # type: ignore
        self._connection.close()

    @property
    def name(self) -> str:
        return self._database.name

    def crags(self) -> list[str]:
        crags = []

        self._cursor.execute(
            """
            SELECT DISTINCT crag
            FROM ascents
            ORDER BY crag
            """
        )

        for row in self._cursor:
            crags.append(row[0])

        return crags

    def log_ascent(self, ascent: Ascent) -> None:
        self._cursor.execute(
            """
            SELECT date
            FROM ascents
            WHERE route = ? AND grade = ? AND crag = ?
            """,
            (ascent.route.name, ascent.route.grade, ascent.route.crag),
        )

        row = self._cursor.fetchone()

        if row is not None:
            raise AscentDBError(
                f"That ascent was already logged with a date of {row[0]}"
            )

        self._cursor.execute(
            """
            INSERT INTO ascents(route, grade, crag, date)
            VALUES(?, ?, ?, ?)
            """,
            (ascent.route.name, ascent.route.grade, ascent.route.crag, ascent.date),
        )

        self._connection.commit()

    def find_ascent(self, route: Route) -> Ascent:
        self._cursor.execute(
            """
            SELECT date
            FROM ascents
            WHERE route = ? AND grade = ? AND crag = ?
            """,
            (route.name, route.grade, route.crag),
        )

        row = self._cursor.fetchone()

        if row is None:
            raise AscentDBError("No ascent found matching provided route")

        date = datetime.date.fromisoformat(row[0])

        return Ascent(route, date)

    def drop_ascent(self, route: Route) -> None:
        self._cursor.execute(
            """
            SELECT 1
            FROM ascents
            WHERE route = ? AND grade = ? AND crag = ?
            """,
            (route.name, route.grade, route.crag),
        )

        row = self._cursor.fetchone()

        if row is None:
            raise AscentDBError("No ascent found matching provided route")

        self._cursor.execute(
            """
            DELETE FROM ascents
            WHERE route = ? AND grade = ? AND crag = ?
            """,
            (route.name, route.grade, route.crag),
        )

        self._connection.commit()

    def total_count(self) -> int:
        self._cursor.execute(
            """
            SELECT count(*)
            FROM ascents
            """
        )

        total_count: int = self._cursor.fetchone()[0]

        return total_count

    def year_counts(self) -> list[tuple[int, int]]:
        self._cursor.execute(
            """
            SELECT CAST(strftime('%Y', date) AS INTEGER) AS year, count(*)
            FROM ascents
            GROUP BY year
            ORDER BY year
            """
        )

        return self._cursor.fetchall()

    def crag_counts(self) -> list[tuple[str, int]]:
        self._cursor.execute(
            """
            SELECT crag, count(*)
            FROM ascents
            GROUP BY crag
            ORDER BY crag
            """
        )

        return self._cursor.fetchall()

    def grade_counts(self) -> list[tuple[str, int]]:
        self._cursor.execute(
            """
            SELECT grade_counts.grade, grade_counts.count
            FROM (
                SELECT grade, count(*) AS count
                FROM ascents
                GROUP BY grade
            ) AS grade_counts
            LEFT JOIN grade_info USING(grade)
            ORDER BY grade_info.grade_number, grade_info.grade_letter
            """
        )

        return self._cursor.fetchall()


class RouteError(Exception):
    """Raise if something goes wrong with a Route object."""


class AscentError(Exception):
    """Raise if something goes wrong with an Ascent object."""


class AscentDBError(Exception):
    """Raise if something goes wrong with an AscentDB object."""
