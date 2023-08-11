#!/usr/bin/env bash
set -e

black --check --diff *.py
mypy --strict ascent.py utils.py
pytest --quiet test_ascent.py
