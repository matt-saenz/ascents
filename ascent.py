"""Module defining the Ascent and AscentLog classes."""


import csv
import datetime
import re


FIELDS = ["route", "grade", "crag", "date"]


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
        """Row representation of the ascent (used for logging)."""
        return [self.route, self.grade, self.crag, self.date.isoformat()]

    def __repr__(self):
        repr_string = (
            f"{self.__class__.__qualname__}"
            f'("{self.route}", "{self.grade}", "{self.crag}", {repr(self.date)})'
        )

        return repr_string

    def __str__(self):
        return f"{self.route} {self.grade} at {self.crag} on {self.date.isoformat()}"


class AscentLog:
    """
    Log of rock climbing ascents.

    Note that ascents are only logged once.
    """

    def __init__(self, csvfile: str | None = None):
        """
        Create a new AscentLog object.

        csvfile: Path to existing log CSV file (optional).

        If a csvfile is given, an existing log is loaded from the CSV file.
        If left None (default), an empty log is created. Log CSV files are
        created via the AscentLog.write() method.
        """

        if csvfile is None:
            self.rows = []
        else:
            with _open_csvfile(csvfile) as f:
                reader = _csv_reader(f)

                try:
                    header = next(reader)
                except StopIteration as e:
                    raise AscentLogError(f"{csvfile} found but empty") from e

                if header != FIELDS:
                    raise AscentLogError(f"{csvfile} missing proper header row")

                self.rows = [row for row in reader]

    @property
    def crags(self):
        """Crags in the log."""
        return sorted({row[2] for row in self.rows})

    def add(self, ascent):
        """Add an ascent to the log after confirming it doesn't already exist."""

        for row in self.rows:
            if ascent.row[:3] == row[:3]:
                raise AscentLogError(
                    f"That ascent was already logged with a date of {row[3]}"
                )

        self.rows.append(ascent.row)

    def find(self, route, grade, crag):
        """
        Find an ascent in the log using the provided info and return it as an
        Ascent object.

        Note that since ascents are unique on route, grade, and crag, date is
        not needed.
        """

        route_info = [route, grade, crag]

        try:
            i = [row[:3] for row in self.rows].index(route_info)
        except ValueError as e:
            raise AscentLogError(f"No ascent found matching {route_info}") from e

        date = self.rows[i][3]

        ascent = Ascent(*route_info, datetime.date.fromisoformat(date))

        return ascent

    def drop(self, ascent):
        """Drop an ascent from the log."""

        try:
            self.rows.remove(ascent.row)
        except ValueError as e:
            raise AscentLogError("That ascent does not exist") from e

    def write(self, csvfile):
        """Write the log to a CSV file."""

        with _open_csvfile(csvfile, "w") as f:
            writer = _csv_writer(f)
            writer.writerow(FIELDS)
            writer.writerows(self.rows)

    def __len__(self):
        return len(self.rows)

    def __str__(self):
        return f"Log containing {len(self)} ascents"


class AscentError(Exception):
    """Raise if something goes wrong with an Ascent object."""


class AscentLogError(Exception):
    """Raise if something goes wrong with an AscentLog object."""


# Open CSV files with the following args, as recommended:
# https://docs.python.org/3/library/csv.html#csv.reader
# https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files


def _open_csvfile(csvfile, mode="r"):
    return open(csvfile, mode, encoding="utf-8", newline="")


# Set dialect to unix when reading/writing CSV files
# https://docs.python.org/3/library/csv.html#csv.unix_dialect


def _csv_reader(csvfile):
    return csv.reader(csvfile, dialect="unix")


def _csv_writer(csvfile):
    return csv.writer(csvfile, dialect="unix")
