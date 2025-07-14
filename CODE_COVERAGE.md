# Code Coverage for Discount Service

To measure code coverage for your tests, use `pytest-cov`.

## Installation

First, install the development requirements:

```sh
pip install -r requirements.txt -r requirements-dev.txt
```

## Running Tests with Coverage

To run all tests and see a coverage report in the terminal:

```sh
pytest --cov=discount_service --cov-report=term --cov-report=html
```

- The `--cov=discount_service` flag measures coverage for your main code.
- The `--cov-report=html` flag generates a detailed HTML report in the `htmlcov/` directory.

Open `htmlcov/index.html` in your browser to view the coverage report.

## Tips
- Aim for high coverage, but focus on meaningful tests rather than just numbers.
- Review uncovered lines for missing tests or dead code.
