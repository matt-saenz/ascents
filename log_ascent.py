"""Script for logging an ascent."""


import argparse
import datetime
import sys
from pathlib import Path

import utils
from ascent import (
    Ascent,
    AscentError,
    AscentDB,
    AscentDBError,
    Route,
    RouteError,
)


parser = argparse.ArgumentParser()
parser.add_argument("database", type=Path)
args = parser.parse_args()


# Create AscentDB object

try:
    db = AscentDB(args.database)
except AscentDBError as e:
    sys.exit(f"Error: {e}")


# Gather info

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
        utils.fail("date must be a valid date in YYYY-MM-DD format")


# Create Ascent object

try:
    ascent = Ascent(Route(name, grade, crag), date)
except (AscentError, RouteError) as e:
    utils.fail(e)


# Check if known crag

with db:
    known_crags = db.crags()

if known_crags and ascent.route.crag not in known_crags:
    print(f"Warning: '{ascent.route.crag}' is not a known crag")

    print("Known crags currently include:", "\n".join(known_crags), sep="\n")

    cont = utils.get_y_n("Continue logging the above ascent (y/n)? ")

    if cont == "n":
        utils.abort()


# Log the ascent

print(f"Ascent to be logged: {ascent}")

log_ascent = utils.get_y_n(f"Log the above ascent in {args.database} (y/n)? ")

if log_ascent == "n":
    utils.abort()

try:
    with db:
        db.log_ascent(ascent)
except AscentDBError as e:
    utils.fail(e)

print("Successfully logged the above ascent")
