"""Module with helpers for scripts."""


import sys


def abort(what):
    print(f"Aborted {what} the above ascent")
    sys.exit(0)


def fail(what, why):
    sys.exit(f"Failed to {what} the above ascent: {why}")


def get_route_info():
    route = input("Enter the name of the route: ")
    grade = input("Enter the grade of the route: ")
    crag = input("Enter the name of the crag where the route is located: ")

    return route, grade, crag


def get_y_n(message):
    resp = input(message)

    while True:
        if resp in {"y", "n"}:
            break

        resp = input("Oops! Valid inputs are 'y' or 'n'. Please try again: ")

    return resp
