import argparse
import datetime
import sys
from collections.abc import Callable
from importlib.metadata import version
from pathlib import Path

from ascents._analyze import analyze_ascent_db
from ascents._init import init_ascent_db, DatabaseAlreadyExistsError
from ascents._models import (
    Route,
    RouteError,
    Ascent,
    AscentError,
    AscentDB,
    AscentDBError,
    Search,
)
from ascents._utils import make_ascents_table


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=version("ascents"),
    )

    parser.add_argument(
        "command",
        choices=COMMANDS.keys(),
        help="Action to take",
    )

    parser.add_argument(
        "database",
        type=Path,
        help="Database to work on",
    )

    args = parser.parse_args()

    return args


def get_route() -> Route:
    name = input("Enter the name of the route: ")
    grade = input("Enter the grade of the route: ")
    crag = input("Enter the name of the crag where the route is located: ")

    return Route(name, grade, crag)


def get_date() -> datetime.date:
    date_in = input(
        "Enter the date of the ascent in YYYY-MM-DD format "
        "(or 't' for today or 'y' for yesterday): "
    )

    if date_in in {"t", "y"}:
        today = datetime.date.today()

        if date_in == "t":
            date = today
        else:
            date = today - datetime.timedelta(days=1)
    else:
        try:
            date = datetime.date.fromisoformat(date_in)
        except ValueError as e:
            raise InvalidDateError(e) from e

    return date


class InvalidDateError(Exception):
    """Raise if invalid date is passed."""


def get_ascent() -> Ascent:
    route = get_route()
    date = get_date()

    return Ascent(route, date)


def init(database: Path) -> None:
    print(f"Initializing ascent database: {database}")
    init_ascent_db(database)
    print("Successfully initialized database")


def confirm(prompt: str) -> None:
    resp = input(prompt + " (y/n)? ")

    while True:
        if resp == "y":
            break

        if resp == "n":
            sys.exit(0)

        resp = input("Oops! Valid inputs are 'y' or 'n'. Please try again: ")


def log(database: Path) -> None:
    db = AscentDB(database)
    ascent = get_ascent()

    with db:
        known_crags = db.crags()

    if known_crags and ascent.route.crag not in known_crags:
        print(f"Warning: '{ascent.route.crag}' is not a known crag")
        print("Known crags currently include:", "\n".join(known_crags), sep="\n")
        confirm("Continue logging the above ascent")

    print(f"Ascent to be logged: {ascent}")
    confirm(f"Log the above ascent in {db.name}")

    with db:
        db.log_ascent(ascent)

    print("Successfully logged the above ascent")


def drop(database: Path) -> None:
    db = AscentDB(database)
    route = get_route()

    with db:
        ascent = db.find_ascent(route)

    print(f"Ascent to be dropped: {ascent}")
    confirm(f"Drop the above ascent from {db.name}")

    with db:
        db.drop_ascent(route)

    print("Successfully dropped the above ascent")


def analyze(database: Path) -> None:
    db = AscentDB(database)
    analysis = analyze_ascent_db(db)
    print(analysis)


def search(database: Path) -> None:
    db = AscentDB(database)

    print(f"Searching {db.name}")
    print("Case-sensitive matching, globbing allowed")
    print("Empty field matches everything")

    def input_or_none(prompt: str) -> str | None:
        resp = input(f"{prompt}: ")
        return resp if resp else None

    search = Search(
        route=input_or_none("route"),
        grade=input_or_none("grade"),
        crag=input_or_none("crag"),
        date=input_or_none("date"),
        glob=True,
    )

    default = "date"
    order = input(f"Order by 'date' or 'grade' ({default=})? ")
    order = order if order else default

    with db:
        ascents = db.ascents(search, order)

    print("Result(s):")

    if ascents:
        print(make_ascents_table(ascents))
    else:
        print("No ascents found")


COMMANDS: dict[str, Callable[[Path], None]] = {
    "init": init,
    "log": log,
    "drop": drop,
    "analyze": analyze,
    "search": search,
}


def main() -> None:
    args = get_args()

    command = COMMANDS[args.command]

    try:
        command(args.database)
    except (
        # Errors that the app itself throws (as opposed to unexpected
        # internal errors) are printed nicely for the user
        RouteError,
        AscentError,
        AscentDBError,
        InvalidDateError,
        DatabaseAlreadyExistsError,
    ) as e:
        sys.exit(f"Error: {e}")


if __name__ == "__main__":
    main()
