# Cloudflare Pages Deployment Deleter

A utility to delete all deployments from a Cloudflare Pages project.

## Installation

1. Clone the repository or download the script
2. Set up a virtual environment and install requirements:

```bash
cd deleter
python -m venv venv
source venv/bin/activate  # On Windows, use venv\Scripts\activate
pip install -r requirements.txt
```

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

By default, the script looks for an envfile in the parent directory. You can specify a different location:

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