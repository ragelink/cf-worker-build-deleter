# Cloudflare Pages Deployment Deleter - Tests

This directory contains tests for the Cloudflare Pages Deployment Deleter.

## Running Tests

You can run the tests using the provided `run_tests.sh` script from the project root:

```bash
./run_tests.sh
```

This will:
1. Install the package in development mode
2. Install test requirements
3. Run tests with coverage reporting
4. Generate HTML coverage reports

## Test Organization

- `test_deleter.py`: Unit tests for the `CloudflareDeploymentDeleter` class
- `test_main.py`: Tests for the main function
- `test_wrapper.py`: Tests for the wrapper script
- `test_integration.py`: Integration tests

## CI Setup

The project uses GitHub Actions for continuous integration. The CI workflow:

1. Runs on multiple Python versions (3.8 - 3.13)
2. Performs code linting with flake8
3. Runs tests with coverage reporting
4. Uploads coverage reports to Codecov
5. Builds and validates the Python package

The CI configuration is defined in `.github/workflows/ci.yml`.

## Coverage Requirements

We aim to maintain a minimum test coverage of 80% for the entire codebase. The CI will report coverage metrics but will not fail if coverage drops below this threshold.

## Adding New Tests

When adding new features or fixing bugs, please also add corresponding tests. Tests should follow these guidelines:

1. Use descriptive test names
2. Mock external dependencies (e.g. using `responses` for API calls)
3. Test both successful and error cases
4. Test edge cases and input validation 