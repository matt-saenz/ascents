import datetime
import sqlite3

import pytest

from tests.conftest import Ascents
from ascents._models import (
    Ascent,
    AscentError,
    AscentDB,
    AscentDBError,
    Route,
    RouteError,
)


@pytest.fixture
def route() -> Route:
    return Route("Some Route", "5.7", "Some Crag")


class TestRoute:
    @pytest.mark.parametrize(
        "bad_grade",
        [
            "5.9+",
            "5.10",
            "5.11a/b",
            "5.12-",
        ],
    )
    def test_grade(
        self,
        route: Route,
        bad_grade: str,
    ) -> None:
        with pytest.raises(RouteError):
            route.grade = bad_grade

    @pytest.mark.parametrize(
        "other,expected",
        [
            (Route("Some Route", "5.7", "Some Crag"), True),
            (Route("Some Route", "5.7", "Other Crag"), False),
        ],
    )
    def test_equal(
        self,
        route: Route,
        other: Route,
        expected: bool,
    ) -> None:
        actual = route == other
        assert actual is expected

    def test_str(self, route: Route) -> None:
        assert str(route) == "Some Route 5.7 at Some Crag"

    def test_repr(self, route: Route) -> None:
        assert repr(route) == "Route('Some Route', '5.7', 'Some Crag')"


@pytest.fixture
def ascent(route: Route) -> Ascent:
    return Ascent(route, datetime.date(2023, 1, 1))


class TestAscent:
    def test_date(self, ascent: Ascent) -> None:
        with pytest.raises(AscentError):
            ascent.date = datetime.date.today() + datetime.timedelta(days=1)

    @pytest.mark.parametrize(
        "other,expected",
        [
            (
                Ascent(
                    Route("Some Route", "5.7", "Some Crag"),
                    datetime.date(2023, 1, 1),
                ),
                True,
            ),
            (
                Ascent(
                    Route("Some Route", "5.7", "Some Crag"),
                    datetime.date(2023, 1, 2),
                ),
                False,
            ),
        ],
    )
    def test_equal(
        self,
        ascent: Ascent,
        other: Ascent,
        expected: bool,
    ) -> None:
        actual = ascent == other
        assert actual is expected

    def test_str(self, ascent: Ascent) -> None:
        assert str(ascent) == "Some Route 5.7 at Some Crag on 2023-01-01"

    def test_repr(self, ascent: Ascent) -> None:
        assert (
            repr(ascent)
            == "Ascent(Route('Some Route', '5.7', 'Some Crag'), datetime.date(2023, 1, 1))"
        )


class TestAscentDB:
    def test_no_connection(self, db: AscentDB) -> None:
        new_db = AscentDB(db._database)

        # Context has never been entered, so connection/
        # cursor have never been created
        # Attempting to operate out of context raises
        # attribute error
        with pytest.raises(AttributeError):
            new_db.crags()

    def test_connection_closed(self, db: AscentDB) -> None:
        # Context has been entered (and exited), so connection
        # has been created (and closed)
        # Attempting to operate out of context raises closed
        # connection error
        with pytest.raises(sqlite3.ProgrammingError):
            db.crags()

    def test_name(self, db: AscentDB) -> None:
        assert db.name == db._database.name

    def test_crags(self, db: AscentDB) -> None:
        with db:
            crags = db.crags()

        assert crags == [
            "Another Crag",
            "New Crag",
            "Old Crag",
            "Some Crag",
        ]

    def test_log_ascent(
        self,
        db: AscentDB,
        ascents: Ascents,
    ) -> None:
        with db:
            for ascent in ascents:
                with pytest.raises(
                    AscentDBError,
                    match=rf"^That ascent was already logged with a date of {ascent.date}$",
                ):
                    db.log_ascent(ascent)

    def test_find_ascent_found(
        self,
        db: AscentDB,
        ascents: Ascents,
    ) -> None:
        with db:
            for ascent in ascents:
                found = db.find_ascent(ascent.route)
                assert found == ascent

    def test_find_ascent_not_found(
        self,
        db: AscentDB,
    ) -> None:
        with db:
            with pytest.raises(
                AscentDBError,
                match=r"^No ascent found matching provided route$",
            ):
                db.find_ascent(Route("Does Not Exist", "5.7", "Some Crag"))

    def test_drop_ascent(
        self,
        db: AscentDB,
        ascents: Ascents,
    ) -> None:
        with db:
            for ascent in ascents:
                db.drop_ascent(ascent.route)

                with pytest.raises(
                    AscentDBError,
                    match=r"^No ascent found matching provided route$",
                ):
                    db.drop_ascent(ascent.route)

        # DB connection has at this point been closed
        # Confirm that changes were actually committed
        with db:
            total_count = db.total_count()

        assert total_count == 0

    def test_total_count(self, db: AscentDB) -> None:
        with db:
            total_count = db.total_count()

        assert total_count == 8

    def test_year_counts(self, db: AscentDB) -> None:
        with db:
            year_counts = db.year_counts()

        assert year_counts == [
            (2022, 4),
            (2023, 4),
        ]

    def test_crag_counts(self, db: AscentDB) -> None:
        with db:
            crag_counts = db.crag_counts()

        assert crag_counts == [
            ("Another Crag", 1),
            ("New Crag", 1),
            ("Old Crag", 2),
            ("Some Crag", 4),
        ]

    def test_grade_counts(self, db: AscentDB) -> None:
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
