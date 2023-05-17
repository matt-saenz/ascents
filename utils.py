"""Utilities for log_ascent script."""


import sys


def abort():
    print("Aborted logging the above ascent")
    sys.exit(0)


def fail(why):
    sys.exit(f"Failed to log the above ascent: {why}")


def get_y_n(message):
    resp = input(message)

    while True:
        if resp in {"y", "n"}:
            break

        resp = input("Oops! Valid inputs are 'y' or 'n'. Please try again: ")

    return resp
