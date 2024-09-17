import datetime
from pathlib import Path

import pytest

from ascents import _init
from ascents._models import Route, Ascent, AscentDB

Ascents = list[Ascent]

DATE_2022 = datetime.date(2022, 12, 1)
DATE_2023 = datetime.date(2023, 1, 1)


@pytest.fixture
def ascents() -> Ascents:
    ascents = [
        Ascent(Route("Classic Route", "5.12a", "Some Crag"), DATE_2023),
        Ascent(Route("Some Other Route", "5.9", "Some Crag"), DATE_2022),
        Ascent(Route("New Route", "5.10d", "New Crag"), DATE_2022),
        Ascent(Route("Another Route", "5.10a", "Another Crag"), DATE_2023),
        Ascent(Route("Some Route", "5.7", "Some Crag"), DATE_2023),
        Ascent(Route("Old Route", "5.11a", "Old Crag"), DATE_2022),
        Ascent(Route("Cool Route", "5.10a", "Some Crag"), DATE_2022),
        Ascent(Route("Last Route", "5.7", "Old Crag"), DATE_2023),
    ]

    return ascents


@pytest.fixture
def db(ascents: Ascents) -> AscentDB:
    database = Path("test.db")

    database.unlink(missing_ok=True)
    _init.init_ascent_db(database)

    with AscentDB(database) as db:
        for ascent in ascents:
            db.log_ascent(ascent)

    return db


@pytest.fixture
def empty_db() -> AscentDB:
    database = Path("empty.db")

    database.unlink(missing_ok=True)
    _init.init_ascent_db(database)
    empty_db = AscentDB(database)

    return empty_db
