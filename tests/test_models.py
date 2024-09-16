import datetime
import sqlite3

import pytest

from tests.conftest import Ascents, DATE_2022, DATE_2023
from ascents import _models
from ascents._models import (
    Route,
    RouteError,
    Ascent,
    AscentError,
    AscentDB,
    AscentDBError,
    Search,
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


def test_adapt_date() -> None:
    assert _models.adapt_date(datetime.date(2023, 1, 1)) == "2023-01-01"


def test_convert_date() -> None:
    assert _models.convert_date(b"2023-01-01") == datetime.date(2023, 1, 1)


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

    def test_latest_date(self, db: AscentDB) -> None:
        with db:
            assert db.latest_date() == datetime.date(2023, 1, 1)

    def test_latest_date_empty(self, empty_db: AscentDB) -> None:
        with empty_db:
            assert empty_db.latest_date() is None

    def test_max_grade(self, db: AscentDB) -> None:
        with db:
            assert db.max_grade() == "5.12a"

    def test_max_grade_empty(self, empty_db: AscentDB) -> None:
        with empty_db:
            assert empty_db.max_grade() is None

    def test_max_grade_by_year(self, db: AscentDB) -> None:
        with db:
            max_grade_by_year = db.max_grade_by_year()

        assert max_grade_by_year == [
            (2022, "5.11a"),
            (2023, "5.12a"),
        ]

    @pytest.mark.parametrize(
        "search,order,expected",
        [
            (
                None,
                "grade",
                [
                    Ascent(Route("Classic Route", "5.12a", "Some Crag"), DATE_2023),
                    Ascent(Route("Old Route", "5.11a", "Old Crag"), DATE_2022),
                    Ascent(Route("New Route", "5.10d", "New Crag"), DATE_2022),
                    Ascent(Route("Another Route", "5.10a", "Another Crag"), DATE_2023),
                    Ascent(Route("Cool Route", "5.10a", "Some Crag"), DATE_2022),
                    Ascent(Route("Some Other Route", "5.9", "Some Crag"), DATE_2022),
                    Ascent(Route("Last Route", "5.7", "Old Crag"), DATE_2023),
                    Ascent(Route("Some Route", "5.7", "Some Crag"), DATE_2023),
                ],
            ),
            (
                None,
                "date",
                [
                    Ascent(Route("Classic Route", "5.12a", "Some Crag"), DATE_2023),
                    Ascent(Route("Another Route", "5.10a", "Another Crag"), DATE_2023),
                    Ascent(Route("Last Route", "5.7", "Old Crag"), DATE_2023),
                    Ascent(Route("Some Route", "5.7", "Some Crag"), DATE_2023),
                    Ascent(Route("Old Route", "5.11a", "Old Crag"), DATE_2022),
                    Ascent(Route("New Route", "5.10d", "New Crag"), DATE_2022),
                    Ascent(Route("Cool Route", "5.10a", "Some Crag"), DATE_2022),
                    Ascent(Route("Some Other Route", "5.9", "Some Crag"), DATE_2022),
                ],
            ),
            (
                Search(grade="5.12a"),
                "grade",
                [
                    Ascent(Route("Classic Route", "5.12a", "Some Crag"), DATE_2023),
                ],
            ),
            (
                Search(grade="5.10a", date=DATE_2022),
                "grade",
                [
                    Ascent(Route("Cool Route", "5.10a", "Some Crag"), DATE_2022),
                ],
            ),
            (
                # Globbing not actually enabled, matches nothing
                Search(grade="5.10?"),
                "grade",
                [],
            ),
            (
                Search(grade="5.10?", glob=True),
                "grade",
                [
                    Ascent(Route("New Route", "5.10d", "New Crag"), DATE_2022),
                    Ascent(Route("Another Route", "5.10a", "Another Crag"), DATE_2023),
                    Ascent(Route("Cool Route", "5.10a", "Some Crag"), DATE_2022),
                ],
            ),
            (
                # Search is still case sensitive in glob mode
                Search(route="some route", glob=True),
                "grade",
                [],
            ),
        ],
    )
    def test_ascents(
        self,
        search: Search | None,
        order: str,
        expected: Ascents,
        db: AscentDB,
    ) -> None:
        with db:
            actual = db.ascents(search, order)

        assert actual == expected

    def test_ascents_invalid_order(self, db: AscentDB) -> None:
        with db:
            with pytest.raises(AscentDBError):
                db.ascents(order="invalid")
