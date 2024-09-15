import datetime

from ascents import _utils
from ascents._models import Route, Ascent


def test_make_ascents_table() -> None:
    ascents = [
        Ascent(Route("Some Route", "5.7", "Some Crag"), datetime.date(2024, 9, 9)),
        Ascent(Route("Another Route", "5.8", "Some Crag"), datetime.date(2024, 9, 10)),
    ]

    expected = "\n".join(
        [
            "Some Route 5.7 at Some Crag on 2024-09-09",
            "Another Route 5.8 at Some Crag on 2024-09-10",
        ],
    )

    actual = _utils.make_ascents_table(ascents)

    assert actual == expected
