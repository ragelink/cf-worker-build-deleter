# Cloudflare Pages Deployment Deleter

A utility to delete all deployments from a Cloudflare Pages project.

> **Note:** This tool was created because the [official Cloudflare solution](https://developers.cloudflare.com/pages/platform/known-issues/#delete-a-project-with-a-high-number-of-deployments) for deleting projects with a high number of deployments doesn't work reliably. Our tool provides a more robust approach with additional features like dry run mode, progress tracking, and force deletion options.

## Project Organization

This project is organized as follows:

- The root directory contains a wrapper script (`delete_deployments.py`) that calls the implementation in the `deleter` directory
- The `deleter` directory contains the actual implementation, including:
  - `src/` - Core Python files and requirements
  - `scripts/` - Shell scripts for easier execution
  - `docker/` - Docker configuration files
  - `config/` - Configuration templates
- Configuration files (envfile) can be placed in either the root directory or the `deleter` directory

## Installation

There are several ways to install and use this tool:

### Option 1: Use the project directly

1. Clone the repository or download the script
2. Set up a virtual environment and install requirements:

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
pip install -r deleter/src/requirements.txt
```

3. Make the script executable:

```bash
chmod +x delete_deployments.py
```

### Option 2: Install as a package

You can install this tool as a Python package, which will make the `cf-pages-deleter` command available in your environment:

```bash
pip install .
```

Then you can use the tool with:

```bash
cf-pages-deleter --help
```

### Option 3: Use Docker (see Docker Usage section below)

## Usage

First, make the script executable:

```bash
chmod +x delete_deployments.py
```

### Using a Configuration File (envfile)

The script can automatically load configuration from an `envfile` with the following format:

```
CF_API_TOKEN=your_api_token
CF_ACCOUNT_ID=your_account_id
CF_PAGES_PROJECT_NAME=your_project_name
```

With your envfile configured, simply run:

```bash
./delete_deployments.py
```

By default, the script looks for an envfile in the current directory. You can specify a different location:

```bash
./delete_deployments.py --env-file /path/to/your/envfile
```

### Basic Usage with Command Line Arguments

```bash
./delete_deployments.py --account-id YOUR_ACCOUNT_ID --project-name YOUR_PROJECT_NAME --email YOUR_EMAIL --api-key YOUR_API_KEY
```

### Using an API Token (Recommended)

```bash
./delete_deployments.py --account-id YOUR_ACCOUNT_ID --project-name YOUR_PROJECT_NAME --api-token YOUR_API_TOKEN
```

### Using Environment Variables

You can set the following environment variables instead of passing them as arguments:

- `CF_API_TOKEN` or `CLOUDFLARE_API_TOKEN`
- `CF_EMAIL` or `CLOUDFLARE_EMAIL`
- `CF_API_KEY` or `CLOUDFLARE_API_KEY`
- `CF_ACCOUNT_ID`
- `CF_PAGES_PROJECT_NAME`

```bash
export CF_API_TOKEN=your_token
export CF_ACCOUNT_ID=your_account_id
export CF_PAGES_PROJECT_NAME=your_project_name
./delete_deployments.py
```

### Docker Usage

You can also run the tool using Docker:

```bash
cd deleter/docker
docker-compose run --rm deleter
```

Or build and run the Docker image directly:

```bash
cd deleter
docker build -t cf-pages-deleter -f docker/Dockerfile .
docker run --rm -it cf-pages-deleter --env-file /path/to/envfile
```

### Filter by Environment

Only delete deployments from a specific environment:

```bash
./delete_deployments.py --env production
```

Options for `--env` are:
- `production`
- `preview`

### Dry Run

Test the deletion process without actually deleting anything:

```bash
./delete_deployments.py --dry-run
```

### Force Deletion of Aliased Deployments

If you need to delete aliased deployments (typically the production deployment), use the force flag:

```bash
./delete_deployments.py --force
```

### Verbose Mode

For debugging or to see more details about API requests:

```bash
./delete_deployments.py --verbose
```

## Notes

- You need appropriate Cloudflare API permissions to perform these operations
- The script includes a delay between deletions to avoid rate limiting
- For security, it's recommended to use API tokens with limited scope instead of global API keys
- When using `--force`, be careful as this can delete your active production deployment

## Why This Tool Exists

Cloudflare's official documentation acknowledges an [issue with deleting projects that have many deployments](https://developers.cloudflare.com/pages/platform/known-issues/#delete-a-project-with-a-high-number-of-deployments). Their recommended solution is a Node.js script that has several limitations:

1. It doesn't provide progress tracking for large numbers of deployments
2. It lacks a dry-run mode to preview deletions before executing them
3. It doesn't handle rate limiting dynamically
4. It has minimal error handling
5. It doesn't offer environment-specific filtering

This tool addresses all these limitations and provides additional features:

- **Progress Tracking**: Shows completion percentage and counts of successful/failed deletions
- **Dry Run Mode**: Preview which deployments would be deleted without making changes
- **Dynamic Rate Limiting**: Adjusts request timing based on API response
- **Comprehensive Error Handling**: Detects and reports specific error conditions
- **Multiple Authentication Methods**: Supports both API tokens and email+key authentication
- **Environment Filtering**: Can target specific environments (production/preview)
- **Docker Support**: Can be run in a containerized environment
- **Installable Package**: Can be installed as a Python package with command-line entry point

The tool was developed for real-world use cases where projects can have hundreds or thousands of deployments that need to be systematically cleaned up.

## Development

### Testing

This project uses pytest for testing. To run the tests:

```bash
# Using the test script
./run_tests.sh

# Or using Make
make test
```

To run with verbose output:

```bash
make test-verbose
```

### Code Quality

We use flake8 for code linting:

```bash
make lint
```

### CI/CD

This project uses GitHub Actions for continuous integration. The CI pipeline:

1. Runs on multiple Python versions (3.8 - 3.13)
2. Performs code linting
3. Runs tests with coverage reporting
4. Builds and validates the Python package

The CI configuration can be found in `.github/workflows/ci.yml`.

### Common Development Tasks

A Makefile is provided with common development tasks:

```bash
# Install development dependencies
make install

# Run tests
make test

# Run linting
make lint

# Build the package
make build

# Clean up build artifacts
make clean

# Do everything (install, test, lint, build)
make all
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

All PRs will be automatically tested by the CI pipeline. 