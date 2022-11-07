"""Module defining the Ascent and AscentLog classes."""


import copy
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
        valid_yds = re.search(r"^5\.([0-9]|1[0-5][a-d])$", value)

        if not valid_yds:
            raise AscentError(
                "grade must be in YDS with no pluses, minuses, or slashes "
                "(translate as needed)"
            )

        self._grade = value

    @property
    def row(self) -> dict:
        """Row representation of the ascent."""

        row = dict(
            route=self.route,
            grade=self.grade,
            crag=self.crag,
            date=self.date.isoformat(),
        )

        return row

    def __repr__(self):
        repr_string = (
            f"{self.__class__.__qualname__}"
            f'("{self.route}", "{self.grade}", "{self.crag}", {repr(self.date)})'
        )

        return repr_string

    def __str__(self):
        return f"{self.route} {self.grade} at {self.crag} on {self.date.isoformat()}"

    def __eq__(self, other):
        if not isinstance(other, Ascent):
            return NotImplemented

        return self.row == other.row


class AscentLog:
    """
    Log of rock climbing ascents.

    An ascent of a given route may only appear in a log once. Therefore,
    ascents in a log are unique on route, grade, and crag (referred to
    collectively as route info).
    """

    FIELDNAMES = ["route", "grade", "crag", "date"]

    def __init__(self, csvfile: str | None = None):
        """
        Create a new AscentLog object.

        csvfile: Path to existing log CSV file (optional).

        If a CSV file is given, an existing log is loaded from the CSV file.
        If csvfile is left None (default), an empty log is created. Log CSV
        files are created via the AscentLog.write() method.
        """

        if csvfile is None:
            self._rows = []
        else:
            with _open_csvfile(csvfile) as f:
                reader = _csv_reader(f)

                if reader.fieldnames != self.FIELDNAMES:
                    raise AscentLogError(f"{csvfile} missing proper header row")

                self._rows = [row for row in reader]

    @property
    def rows(self) -> list[dict]:
        """
        Rows in the log.

        This returns a deep copy of rows in the log since rows should not be
        manipulated directly (only through dedicated methods). The purpose of
        this property is to provide an easy and safe way to access log rows
        for viewing and analysis.
        """
        return copy.deepcopy(self._rows)

    @property
    def crags(self) -> list:
        """Crags in the log."""
        return sorted({row["crag"] for row in self._rows})

    def add(self, ascent: Ascent) -> None:
        """Add an ascent to the log."""

        route_info = _get_route_info(ascent.row)

        for row in self._rows:
            if _get_route_info(row) == route_info:
                raise AscentLogError(
                    f"That ascent was already logged with a date of {row['date']}"
                )

        self._rows.append(ascent.row)

    def find(self, route: str, grade: str, crag: str) -> Ascent:
        """
        Find an ascent in the log using the provided route info and return it
        as an Ascent object.
        """

        route_info = dict(route=route, grade=grade, crag=crag)

        for row in self._rows:
            if _get_route_info(row) == route_info:
                break
        else:
            # https://docs.python.org/3/tutorial/controlflow.html#break-and-continue-statements-and-else-clauses-on-loops
            raise AscentLogError("No ascent found matching provided route info")

        return Ascent(route, grade, crag, datetime.date.fromisoformat(row["date"]))

    def drop(self, ascent: Ascent) -> None:
        """Drop an ascent from the log."""

        try:
            self._rows.remove(ascent.row)
        except ValueError as e:
            raise AscentLogError("That ascent does not exist") from e

    def write(self, csvfile: str) -> None:
        """Write the log to a CSV file."""

        with _open_csvfile(csvfile, "w") as f:
            writer = _csv_writer(f, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            writer.writerows(self._rows)

    def __len__(self):
        return len(self._rows)

    def __str__(self):
        return f"Log containing {len(self)} ascents"

    def __contains__(self, item):
        if isinstance(item, Ascent):
            return item.row in self._rows

        return item in self._rows

    def __eq__(self, other):
        if not isinstance(other, AscentLog):
            return NotImplemented

        return self._rows == other._rows


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
    return csv.DictReader(csvfile, dialect="unix")


def _csv_writer(csvfile, fieldnames):
    return csv.DictWriter(csvfile, fieldnames=fieldnames, dialect="unix")


def _get_route_info(row):
    return {key: row[key] for key in ["route", "grade", "crag"]}
