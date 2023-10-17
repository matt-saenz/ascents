#!/usr/bin/env bash
set -e

black --check --diff *.py
isort --check --diff --force-grid-wrap 2 --profile black *.py
mypy --strict *.py
flake8 --extend-ignore E501 *.py
pytest --quiet test_ascent.py
