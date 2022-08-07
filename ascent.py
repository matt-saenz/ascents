"""Module defining the Ascent class."""


import csv
import datetime
import re


class Ascent:
    """An Ascent object represents a rock climbing ascent."""

    def __init__(self, route: str, grade: str, crag: str, date: datetime.date):
        """
        Create a new Ascent object.

        route: Name of the route.
        grade: Grade of the route in YDS.
        crag: Name of the crag where the route is located.
        date: Date of the ascent.
        """

        self.route = route
        self.grade = grade
        self.crag = crag
        self.date = date

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        if not isinstance(value, datetime.date):
            raise AscentError("date must be a datetime.date object")

        if value > datetime.date.today():
            raise AscentError("date cannot be in the future")

        self._date = value

    @property
    def grade(self):
        return self._grade

    @grade.setter
    def grade(self, value):
        if not re.search("^5\.(([0-9])|(1[0-5][a-d]))$", value):
            raise AscentError(
                "grade must be in YDS with no pluses, minuses, or slashes "
                "(translate as needed)"
            )

        self._grade = value

    @property
    def row(self):
        return [self.route, self.grade, self.crag, self.date.isoformat()]

    def __repr__(self):
        repr_string = (
            f"{self.__class__.__qualname__}"
            f'("{self.route}", "{self.grade}", "{self.crag}", {repr(self.date)})'
        )

        return repr_string

    def __str__(self):
        return f"{self.route} {self.grade} at {self.crag} on {self.date.isoformat()}"

    def log(self, csvfile: str):
        """
        Log an ascent as a row in csvfile.

        The file specified by csvfile must be a CSV file with headers route,
        grade, crag, and date (in that exact order!) If the file specified by
        csvfile is not found, it is created. Otherwise, the row for the new
        ascent is appended to the file (after confirming the file has the
        proper structure and the ascent has not already been logged).
        """

        fields = ["route", "grade", "crag", "date"]

        # Open with the following args, as recommended:
        # https://docs.python.org/3/library/csv.html#csv.reader
        # https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files

        open_args = dict(encoding="utf-8", newline="")

        try:
            f = open(csvfile, "r+", **open_args)
        except FileNotFoundError:
            with open(csvfile, "w", **open_args) as f:
                writer = csv.writer(f)
                writer.writerows([fields, self.row])

            print(f"Created new file {csvfile}")
        else:
            with f:
                reader = csv.reader(f)

                try:
                    header = next(reader)
                except StopIteration as e:
                    raise AscentLoggingError(f"{csvfile} found but empty") from e

                if header != fields:
                    raise AscentLoggingError(f"{csvfile} missing proper header row")

                for row in reader:
                    if row[:3] == self.row[:3]:
                        raise AscentLoggingError(
                            f"That ascent was already logged with a date of {row[3]}"
                        )

                writer = csv.writer(f)
                writer.writerow(self.row)

        print(f"Successfully logged ascent: {self.row}")


class AscentError(Exception):
    """Raise if something goes wrong with an Ascent object."""


class AscentLoggingError(Exception):
    """Raise if something goes wrong when logging an Ascent object."""
