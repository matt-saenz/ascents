"""Script for logging an ascent."""


import argparse
import datetime
import sys
from pathlib import Path
from typing import Any

from ascent import (
    Ascent,
    AscentDB,
    AscentDBError,
    AscentError,
    Route,
    RouteError,
)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("database", type=Path)
    args = parser.parse_args()
    return args


def get_ascent_db(database: Path) -> AscentDB:
    try:
        db = AscentDB(database)
    except AscentDBError as e:
        sys.exit(f"Error: {e}")

    return db


def get_ascent() -> Ascent:
    name = input("Enter the name of the route: ")
    grade = input("Enter the grade of the route: ")
    crag = input("Enter the name of the crag where the route is located: ")

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
        except ValueError:
            fail("date must be a valid date in YYYY-MM-DD format")

    try:
        ascent = Ascent(Route(name, grade, crag), date)
    except (AscentError, RouteError) as e:
        fail(e)

    return ascent


def check_if_known_crag(ascent: Ascent, db: AscentDB) -> None:
    with db:
        known_crags = db.crags()

    if known_crags and ascent.route.crag not in known_crags:
        print(f"Warning: '{ascent.route.crag}' is not a known crag")

        print("Known crags currently include:", "\n".join(known_crags), sep="\n")

        cont = confirm("Continue logging the above ascent")

        if not cont:
            abort()


def log_ascent(ascent: Ascent, db: AscentDB) -> None:
    print(f"Ascent to be logged: {ascent}")

    log = confirm(f"Log the above ascent in {db.name}")

    if not log:
        abort()

    try:
        with db:
            db.log_ascent(ascent)
    except AscentDBError as e:
        fail(e)

    print("Successfully logged the above ascent")


def abort() -> None:
    print("Aborted logging the above ascent")
    sys.exit(0)


def fail(why: Any) -> None:
    sys.exit(f"Failed to log the above ascent: {why}")


def confirm(message: str) -> bool:
    resp = input(message + " (y/n)? ")

    while True:
        if resp in {"y", "n"}:
            break

        resp = input("Oops! Valid inputs are 'y' or 'n'. Please try again: ")

    return resp == "y"


def main() -> None:
    args = get_args()
    db = get_ascent_db(args.database)
    ascent = get_ascent()
    check_if_known_crag(ascent, db)
    log_ascent(ascent, db)


if __name__ == "__main__":
    main()
