#!/usr/bin/env bash
set -e

black --check --diff *.py analyze_ascents init_ascent_db log_ascent
mypy *.py
pytest --quiet test_ascent.py
