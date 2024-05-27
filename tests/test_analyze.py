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
