# Cloudflare Pages Deployment Deleter

A utility to delete all deployments from a Cloudflare Pages project. This tool can handle large numbers of deployments through pagination and provides options for forcing deletion of aliased deployments.

## Handling Large Deployment Sets

This tool is specifically designed to handle very large numbers of deployments (hundreds or even thousands) by:

1. Using automatic pagination to retrieve all deployments in batches
2. Implementing proper rate limiting to avoid API throttling
3. Providing clear progress indicators during the deletion process
4. Supporting resumable operations (through filtering)

## Installation

### Option 1: Regular Python Installation

1. Clone the repository or download the script
2. Set up a virtual environment and install requirements:

```bash
cd deleter
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
pip install -r requirements.txt
```

3. Make the script executable:

```bash
chmod +x delete_deployments.py
```

### Option 2: Docker Installation (Recommended)

1. Clone the repository or download the files
2. Build and run with Docker:

```bash
cd deleter
docker build -t cf-pages-deleter .
```

## Usage

### Using Docker (Recommended)

You can use the Docker container in several ways:

#### Using docker-compose with an envfile

1. Copy `envfile.sample` to `envfile` and fill in your values:
```bash
cp envfile.sample envfile
# Edit envfile with your values
```

2. Run using docker-compose:
```bash
docker-compose up
```

#### Using Docker directly with an envfile

```bash
docker run -v $(pwd)/envfile:/app/envfile cf-pages-deleter --env-file /app/envfile
```

#### Using Docker with environment variables

```bash
docker run -e CF_API_TOKEN=your_token -e CF_ACCOUNT_ID=your_account_id -e CF_PAGES_PROJECT_NAME=your_project cf-pages-deleter
```

### Using Python Directly

#### Configuration File (envfile)

The script can automatically load configuration from an `envfile` with the following format:

```
CF_API_TOKEN=your_api_token
CF_ACCOUNT_ID=your_account_id
CF_PAGES_PROJECT_NAME=your_project_name
```

With your envfile configured, simply run:

```bash
./delete_deployments.py --env-file envfile
```

#### Command Line Arguments

```bash
./delete_deployments.py --account-id YOUR_ACCOUNT_ID --project-name YOUR_PROJECT_NAME --api-token YOUR_API_TOKEN
```

#### Environment Variables

You can set environment variables instead of passing them as arguments:

```bash
export CF_API_TOKEN=your_token
export CF_ACCOUNT_ID=your_account_id
export CF_PAGES_PROJECT_NAME=your_project_name
./delete_deployments.py
```

## Advanced Options

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

### Pagination Limit

Set the maximum number of items to retrieve per page (default: 50, maximum: 100):

```bash
./delete_deployments.py --limit 100
```

For projects with hundreds of deployments, using the maximum limit of 100 is recommended for efficiency.

## Docker Usage Examples

### Delete all deployments with dry run

```bash
docker run -v $(pwd)/envfile:/app/envfile cf-pages-deleter --env-file /app/envfile --dry-run
```

### Force delete all deployments including production

```bash
docker run -v $(pwd)/envfile:/app/envfile cf-pages-deleter --env-file /app/envfile --force
```

### Delete all deployments with maximum efficiency (for 600+ deployments)

```bash
docker run -v $(pwd)/envfile:/app/envfile cf-pages-deleter --env-file /app/envfile --force --limit 100
```

### Only delete preview deployments

```bash
docker run -v $(pwd)/envfile:/app/envfile cf-pages-deleter --env-file /app/envfile --env preview
```

## Notes

- You need appropriate Cloudflare API permissions to perform these operations (Pages:Read and Pages:Edit)
- The script automatically handles pagination for large numbers of deployments
- For very large projects (600+ deployments), the process may take 10-15 minutes due to API rate limits
- The script includes a delay between deletions to avoid rate limiting
- For security, it's recommended to use API tokens with limited scope instead of global API keys
- When using `--force`, be careful as this can delete your active production deployment 