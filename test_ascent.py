"""Testing for the ascent module."""


from datetime import date
import unittest

from ascent import Ascent, AscentLog, AscentLogError


class TestAscentLogMethods(unittest.TestCase):
    def setUp(self):
        self.log = AscentLog()
        self.log.add(Ascent("Over Easy", "5.9", "Barton Creek Greenbelt", date.today()))
        self.ascent = Ascent("Slither", "5.7", "Reimers Ranch", date.today())
        self.log.add(self.ascent)

    def test_add(self):
        self.assertIn(self.ascent.row, self.log)

        with self.assertRaises(AscentLogError):
            self.log.add(self.ascent)

    def test_find(self):
        found = self.log.find(*self.ascent.row[:3])
        self.assertEqual(found.row, self.ascent.row)

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
