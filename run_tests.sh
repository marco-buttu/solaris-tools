#!/bin/bash
set -e

# Linter checks
echo "Linter checks by ruff:"
poetry run ruff check --select E --line-length 88
# poetry run ruff format --line-length 88
echo

# Set up coverage to run also in subprocesses (needed for full CLI coverage)
export COVERAGE_PROCESS_START=$(pwd)/.coveragerc
poetry run pytest --cov=pointing --cov-report=html

# Print full coverage report in the shell
poetry run coverage report
