"""Testing for the ascent module."""


from datetime import date, timedelta
import unittest

from ascent import Ascent, AscentError, AscentLog, AscentLogError


class TestAscent(unittest.TestCase):
    def setUp(self):
        self.ascent = Ascent("Some Route", "5.7", "Some Crag", date(2022, 10, 18))

    def test_row(self):
        self.assertEqual(
            self.ascent.row,
            dict(route="Some Route", grade="5.7", crag="Some Crag", date="2022-10-18"),
        )

    def test_grade(self):
        bad_grades = ["5.9+", "5.10", "5.11a/b", "5.12-"]

        for bad_grade in bad_grades:
            with self.assertRaises(AscentError):
                self.ascent.grade = bad_grade

    def test_date(self):
        bad_dates = ["2022-10-18", date.today() + timedelta(days=1)]

        for bad_date in bad_dates:
            with self.assertRaises(AscentError):
                self.ascent.date = bad_date


class TestAscentLog(unittest.TestCase):
    def setUp(self):
        self.log = AscentLog()
        self.log.add(Ascent("Over Easy", "5.9", "Barton Creek Greenbelt", date.today()))
        self.ascent = Ascent("Slither", "5.7", "Reimers Ranch", date.today())
        self.log.add(self.ascent)

    def test_add(self):
        self.assertIn(self.ascent, self.log)

        with self.assertRaises(AscentLogError):
            self.log.add(self.ascent)

    def test_len(self):
        self.assertEqual(len(self.log), 2)

    def test_crags(self):
        self.log.add(
            Ascent("Some Route", "5.7", "Barton Creek Greenbelt", date.today())
        )

        self.assertEqual(self.log.crags, ["Barton Creek Greenbelt", "Reimers Ranch"])

    def test_find(self):
        row = self.ascent.row
        found = self.log.find(row["route"], row["grade"], row["crag"])
        self.assertEqual(found, self.ascent)

        with self.assertRaises(AscentLogError):
            self.log.find("Over Easy", "5.9", "Austin Greenbelt")

    def test_drop(self):
        self.log.drop(self.ascent)
        self.assertNotIn(self.ascent, self.log)

        with self.assertRaises(AscentLogError):
            self.log.drop(self.ascent)

    def test_read_write(self):
        self.log.write("test_log.csv")
        test_log = AscentLog("test_log.csv")
        self.assertEqual(test_log, self.log)


if __name__ == "__main__":
    unittest.main()
