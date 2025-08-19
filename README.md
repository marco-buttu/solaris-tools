# Solaris Tools

Tools for telescope pointing analysis and solar observation support.

---

## Installation (for users)

### Requirements
- Python ≥ 3.11
- [Poetry](https://python-poetry.org/docs/#installation) installed

### Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/marco-buttu/solaris-tools.git
   cd solaris-tools
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   poetry install
   ```

3. (Optional) Activate the shell environment:
   ```bash
   poetry shell
   ```

Now you can run the command-line tools such as:

```bash
poetry run check-errors-over-time \
    --start-time "2025-12-21T00:00:00" \
    --end-time "2025-12-21T03:00:00" \
    --frequency "30min" --show-max-error \
    --plot --save-plot result.png
```

---

## Development Setup

### Install development dependencies
```bash
poetry install --with dev
```

### Run all tests, coverage and linter

To run only the linter:

```bash
tox -e lint
```

To apply formatting locally (modifies files):

```bash
tox -e format
```

To run tests on other Python versions if available:

```bash
tox -e py310,py311
```

Finally, without arguments it runs lint + format-check + tests (py313):

```bash
tox
```
