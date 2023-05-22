"""Testing for the ascent module."""


import datetime
import sqlite3
from pathlib import Path

import pytest

from ascent import (
    Ascent,
    AscentError,
    AscentDB,
    AscentDBError,
    Route,
    RouteError,
)


@pytest.fixture
def route():
    return Route("Some Route", "5.7", "Some Crag")


class TestRoute:
    @pytest.mark.parametrize("bad_grade", ["5.9+", "5.10", "5.11a/b", "5.12-"])
    def test_grade(self, route, bad_grade):
        with pytest.raises(RouteError):
            route.grade = bad_grade

    def test_str(self, route):
        assert str(route) == "Some Route 5.7 at Some Crag"


@pytest.fixture
def ascent(route):
    return Ascent(route, datetime.date(2023, 1, 1))


class TestAscent:
    @pytest.mark.parametrize(
        "bad_date",
        ["2022-10-18", datetime.date.today() + datetime.timedelta(days=1)],
    )
    def test_date(self, ascent, bad_date):
        with pytest.raises(AscentError):
            ascent.date = bad_date

    def test_str(self, ascent):
        assert str(ascent) == "Some Route 5.7 at Some Crag on 2023-01-01"


@pytest.fixture(scope="module")
def ascent_data():
    date_2022 = datetime.date(2022, 12, 1)
    date_2023 = datetime.date(2023, 1, 1)

    return [
        ("Classic Route", "5.12a", "Some Crag", date_2023),
        ("Some Other Route", "5.9", "Some Crag", date_2022),
        ("New Route", "5.10d", "New Crag", date_2022),
        ("Another Route", "5.10a", "Another Crag", date_2023),
        ("Some Route", "5.7", "Some Crag", date_2023),
        ("Old Route", "5.11a", "Old Crag", date_2022),
        ("Cool Route", "5.10a", "Some Crag", date_2022),
        ("Last Route", "5.7", "Old Crag", date_2023),
    ]


@pytest.fixture(scope="module")
def db(ascent_data):
    test_db = Path("test.db")

    if not test_db.exists():
        raise FileNotFoundError("test.db must be initialized to test")

    connection = sqlite3.connect(test_db)

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM ascents")
        connection.commit()
    finally:
        connection.close()

    with AscentDB(test_db) as db:
        for name, grade, crag, date in ascent_data:
            db.log_ascent(Ascent(Route(name, grade, crag), date))

    return db


class TestAscentDB:
    def test_crags(self, db):
        with db:
            crags = db.crags()

        assert crags == [
            "Another Crag",
            "New Crag",
            "Old Crag",
            "Some Crag",
        ]

    def test_log_ascent(self, db, ascent_data):
        with db:
            for name, grade, crag, date in ascent_data:
                with pytest.raises(AscentDBError):
                    db.log_ascent(Ascent(Route(name, grade, crag), date))

    def test_total_count(self, db):
        with db:
            total_count = db.total_count()

        assert total_count == 8

    def test_year_counts(self, db):
        with db:
            year_counts = db.year_counts()

        assert year_counts == [
            (2022, 4),
            (2023, 4),
        ]

    def test_crag_counts(self, db):
        with db:
            crag_counts = db.crag_counts()

        assert crag_counts == [
            ("Another Crag", 1),
            ("New Crag", 1),
            ("Old Crag", 2),
            ("Some Crag", 4),
        ]

    def test_grade_counts(self, db):
        with db:
            grade_counts = db.grade_counts()

        assert grade_counts == [
            ("5.7", 2),
            ("5.9", 1),
            ("5.10a", 2),
            ("5.10d", 1),
            ("5.11a", 1),
            ("5.12a", 1),
        ]
