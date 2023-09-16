"""Utils for scripts."""


import argparse
import sys
from pathlib import Path

from ascent import (
    AscentDB,
    AscentDBError,
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


def get_route() -> Route:
    name = input("Enter the name of the route: ")
    grade = input("Enter the grade of the route: ")
    crag = input("Enter the name of the crag where the route is located: ")

    try:
        route = Route(name, grade, crag)
    except RouteError as e:
        sys.exit(f"Error: {e}")

    return route


def abort(what: str) -> None:
    print(f"Aborted {what} the above ascent")
    sys.exit(0)


def fail(what: str, why: str | Exception) -> None:
    sys.exit(f"Failed to {what} the above ascent: {why}")


def confirm(message: str) -> bool:
    resp = input(message + " (y/n)? ")

    while True:
        if resp in {"y", "n"}:
            break

        resp = input("Oops! Valid inputs are 'y' or 'n'. Please try again: ")

    return resp == "y"
