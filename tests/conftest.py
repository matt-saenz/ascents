import datetime
from pathlib import Path

import pytest

from ascents import _init
from ascents._models import Route, Ascent, AscentDB

Ascents = list[Ascent]


@pytest.fixture
def ascents() -> Ascents:
    date_2022 = datetime.date(2022, 12, 1)
    date_2023 = datetime.date(2023, 1, 1)

    ascents = [
        Ascent(Route("Classic Route", "5.12a", "Some Crag"), date_2023),
        Ascent(Route("Some Other Route", "5.9", "Some Crag"), date_2022),
        Ascent(Route("New Route", "5.10d", "New Crag"), date_2022),
        Ascent(Route("Another Route", "5.10a", "Another Crag"), date_2023),
        Ascent(Route("Some Route", "5.7", "Some Crag"), date_2023),
        Ascent(Route("Old Route", "5.11a", "Old Crag"), date_2022),
        Ascent(Route("Cool Route", "5.10a", "Some Crag"), date_2022),
        Ascent(Route("Last Route", "5.7", "Old Crag"), date_2023),
    ]

    return ascents


@pytest.fixture
def db(ascents: Ascents) -> AscentDB:
    test_db = Path("test.db")

    test_db.unlink(missing_ok=True)
    _init.init_ascent_db(test_db)

    with AscentDB(test_db) as db:
        for ascent in ascents:
            db.log_ascent(ascent)

    return db
