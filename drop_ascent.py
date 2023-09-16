"""Script for dropping an ascent."""


import utils
from ascent import (
    AscentDB,
    AscentDBError,
    Route,
)


def drop_ascent(route: Route, db: AscentDB) -> None:
    try:
        with db:
            ascent = db.find_ascent(route)
    except AscentDBError as e:
        utils.fail("drop", e)

    print(f"Ascent to be dropped: {ascent}")

    drop = utils.confirm(f"Drop the above ascent from {db.name}")

    if not drop:
        utils.abort("dropping")

    with db:
        db.drop_ascent(route)

    print("Successfully dropped the above ascent")


def main() -> None:
    args = utils.get_args()
    db = utils.get_ascent_db(args.database)
    route = utils.get_route()
    drop_ascent(route, db)


if __name__ == "__main__":
    main()
