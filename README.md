# ascents :climbing_man:

## Overview

My personal log of rock climbing ascents, powered by a [module](ascent.py) defining `Ascent` and `AscentLog` classes and a [`log_ascent`](log_ascent) command for logging ascents. Ascents are logged in a [CSV file](ascents.csv) with the following fields:

1. `route`: Name of the route.
2. `grade`: Grade of the route in terms of the Yosemite Decimal System (YDS).
3. `crag`: Name of the crag, or general climbing area, where the route is located.
4. `date`: Date of my first recorded ascent.

An ascent is defined as a redpoint ascent (i.e., successfully leading the route with no falls or takes).

## Setup Instructions

```shell
# Clone the repo
git clone https://github.com/matt-saenz/ascents.git

# Move into local clone
cd ascents/

# Make commands executable
chmod u+x log_ascent drop_ascent analyze_log

# Add ascents/ directory to $PATH
vim ~/.bash_profile
source ~/.bash_profile

# Verify that things have been set up correctly
which log_ascent
log_ascent --help
```
