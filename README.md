# ascents :climbing_man:

## Overview

[Script](log_ascent.py) for logging rock climbing ascents powered by a [module](ascent.py) defining `Ascent` and `AscentLog` classes. Ascents are logged in a CSV file with the following fields:

1. `route`: Name of the route.
2. `grade`: Grade of the route in terms of the Yosemite Decimal System (YDS).
3. `crag`: Name of the crag, or general climbing area, where the route is located.
4. `date`: Date of first recorded ascent.

## Example Usage

```
$ python log_ascent.py my_ascents.csv
Enter the name of the route: Slither
Enter the grade of the route: 5.7
Enter the name of the crag where the route is located: Reimers Ranch
Enter the date of the ascent in YYYY-MM-DD format (or 't' for today or 'y' for yesterday): t
Ascent to be logged: Slither 5.7 at Reimers Ranch on 2023-05-03
Log the above ascent in my_ascents.csv (y/n)? y
Successfully logged the above ascent
```

```
$ cat my_ascents.csv
"route","grade","crag","date"
"Lessa the Puramatic 6000 Kitty","5.5","Reimers Ranch","2023-05-03"
"Slither","5.7","Reimers Ranch","2023-05-03"
```
