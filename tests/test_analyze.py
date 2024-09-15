from ascents import _analyze


def test_make_counts_table() -> None:
    counts = [
        ("5.7", 9),
        ("5.8", 11),
    ]

    expected = "\n".join(
        [
            "   9  5.7",
            "  11  5.8",
        ],
    )

    actual = _analyze.make_counts_table(counts)

    assert actual == expected


def test_make_max_grade_by_year_table() -> None:
    max_grade_by_year = [
        (2022, "5.11a"),
        (2023, "5.12a"),
    ]

    expected = "\n".join(
        [
            "2022  5.11a",
            "2023  5.12a",
        ],
    )

    actual = _analyze.make_max_grade_by_year_table(max_grade_by_year)

    assert actual == expected
