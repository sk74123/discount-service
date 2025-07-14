# Code Coverage for Discount Service

To measure code coverage for your tests, use `pytest-cov`.


## Running Tests with Coverage

To run all tests and see a coverage report in the terminal:

```sh
pytest --cov=discount_service --cov-report=term --cov-report=html
```

- The `--cov=discount_service` flag measures coverage for your main code.
- The `--cov-report=html` flag generates a detailed HTML report in the `htmlcov/` directory.

Open `htmlcov/index.html` in your browser to view the coverage report.
