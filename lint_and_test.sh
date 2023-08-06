#!/usr/bin/env bash
set -e

black --check --diff *.py
mypy ascent.py utils.py test_ascent.py
pytest --quiet test_ascent.py
