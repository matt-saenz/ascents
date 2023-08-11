"""Utilities for log_ascent.py script."""


import sys
from typing import Any


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
