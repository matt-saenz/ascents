from ascents._models import Ascent


def make_ascents_table(
    ascents: list[Ascent],
) -> str:
    return "\n".join([str(ascent) for ascent in ascents])
