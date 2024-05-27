import datetime

import pytest

from ascents import __main__
from ascents._models import Route, Ascent, AscentDB, AscentDBError


@pytest.fixture
def confirmed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(__main__, "confirm", lambda p: None)


class TestGetDate:
    @pytest.mark.parametrize(
        "user_input,expected",
        [
            ("t", datetime.date.today()),
            ("y", datetime.date.today() - datetime.timedelta(days=1)),
            ("2024-05-26", datetime.date(2024, 5, 26)),
        ],
    )
    def test_valid(
        self,
        user_input: str,
        expected: datetime.date,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr("builtins.input", lambda p: user_input)
        actual = __main__.get_date()

        assert actual == expected

    @pytest.mark.parametrize(
        "user_input",
        ["tt", "yy", "May 26 2024", "05/26/2024", "2024-05"],
    )
    def test_invalid(
        self,
        user_input: str,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr("builtins.input", lambda p: user_input)

        with pytest.raises(__main__.InvalidDateError):
            __main__.get_date()


def test_log(
    confirmed: None,
    db: AscentDB,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    latest_send = Ascent(
        Route("Super New Route", "5.12a", "Usual Crag"),
        datetime.date(2024, 5, 26),
    )

    monkeypatch.setattr(__main__, "get_ascent", lambda: latest_send)

    __main__.log(db._database)

    with pytest.raises(
        AscentDBError,
        match=r"^That ascent was already logged with a date of 2024-05-26$",
    ):
        __main__.log(db._database)


def test_drop(
    confirmed: None,
    db: AscentDB,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    previous_send = Route("Some Route", "5.7", "Some Crag")

    monkeypatch.setattr(__main__, "get_route", lambda: previous_send)

    __main__.drop(db._database)

    with pytest.raises(
        AscentDBError,
        match=r"^No ascent found matching provided route$",
    ):
        __main__.drop(db._database)
