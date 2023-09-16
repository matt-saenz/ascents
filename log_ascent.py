"""Script for logging an ascent."""


import datetime

import utils
from ascent import (
    Ascent,
    AscentDB,
    AscentDBError,
    AscentError,
)


def get_ascent() -> Ascent:
    route = utils.get_route()

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
            utils.fail("log", "date must be a valid date in YYYY-MM-DD format")

    try:
        ascent = Ascent(route, date)
    except AscentError as e:
        utils.fail("log", e)

    return ascent


def check_if_known_crag(ascent: Ascent, db: AscentDB) -> None:
    with db:
        known_crags = db.crags()

    if known_crags and ascent.route.crag not in known_crags:
        print(f"Warning: '{ascent.route.crag}' is not a known crag")

        print("Known crags currently include:", "\n".join(known_crags), sep="\n")

        cont = utils.confirm("Continue logging the above ascent")

        if not cont:
            utils.abort("logging")


def log_ascent(ascent: Ascent, db: AscentDB) -> None:
    print(f"Ascent to be logged: {ascent}")

    log = utils.confirm(f"Log the above ascent in {db.name}")

    if not log:
        utils.abort("logging")

    try:
        with db:
            db.log_ascent(ascent)
    except AscentDBError as e:
        utils.fail("log", e)

    print("Successfully logged the above ascent")


def main() -> None:
    args = utils.get_args()
    db = utils.get_ascent_db(args.database)
    ascent = get_ascent()
    check_if_known_crag(ascent, db)
    log_ascent(ascent, db)


if __name__ == "__main__":
    main()
