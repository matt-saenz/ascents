"""Module with helpers."""


import csv
import os


# Open CSV files with the following args, as recommended:
# https://docs.python.org/3/library/csv.html#csv.reader
# https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files

def open_csvfile(csvfile, mode="r"):
    return open(csvfile, mode, encoding="utf-8", newline="")


# Set dialect to unix when reading/writing CSV files
# https://docs.python.org/3/library/csv.html#csv.unix_dialect

def csv_reader(csvfile):
    return csv.reader(csvfile, dialect="unix")

def csv_writer(csvfile):
    return csv.writer(csvfile, dialect="unix")


# Get route info

def get_route_info():
    route = input("Enter the name of the route: ")
    grade = input("Enter the grade of the route: ")
    crag = input("Enter the name of the crag where the route is located: ")

    return route, grade, crag


# Allow user to provide input again

def oops_try_again():
    return input("Oops! Valid inputs are 'y' or 'n'. Please try again: ")


# Read/update known crags

def open_known_crags(csvfile, mode="r"):
    known_crags_file = os.path.join(os.path.dirname(csvfile), ".known_crags")
    return open(known_crags_file, mode, encoding="utf-8")

def known_crags(csvfile):
    try:
        f = open_known_crags(csvfile)
    except FileNotFoundError:
        known_crags = []
    else:
        with f:
            known_crags = f.read().strip().splitlines()

    return known_crags

def update_known_crags(csvfile):
    with open_csvfile(csvfile) as f:
        reader = csv_reader(f)
        next(reader)  # Skip header row
        known_crags = {row[2] for row in reader}

    with open_known_crags(csvfile, "w") as f:
        f.write("\n".join(sorted(known_crags)) + "\n")
