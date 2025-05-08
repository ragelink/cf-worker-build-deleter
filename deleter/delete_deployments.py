#!/usr/bin/env python3
import argparse
import json
import os
import requests
import sys
import time
from typing import Dict, List, Optional, Union


def load_env_file(file_path):
    """Load environment variables from a file."""
    if not os.path.exists(file_path):
        return {}
    
    env_vars = {}
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value.strip()
            
    return env_vars


class CloudflareDeploymentDeleter:
    """Delete all deployments from a Cloudflare Pages project."""
    
    BASE_URL = "https://api.cloudflare.com/client/v4"
    
    def __init__(
        self,
        account_id: str,
        project_name: str,
        email: Optional[str] = None,
        api_key: Optional[str] = None,
        api_token: Optional[str] = None,
        env: Optional[str] = None,
        dry_run: bool = False,
        verbose: bool = False,
        force: bool = False,
        limit: int = 50,
    ):
        self.account_id = account_id
        self.project_name = project_name
        self.email = email
        self.api_key = api_key
        self.api_token = api_token
        self.env = env
        self.dry_run = dry_run
        self.verbose = verbose
        self.force = force
        self.limit = limit
        
        # Validate auth
        if api_token:
            self.headers = {"Authorization": f"Bearer {api_token}"}
            if self.verbose:
                print(f"Using API token authentication")
                # Don't print the full token for security reasons
                print(f"Token: {api_token[:5]}...{api_token[-5:] if len(api_token) > 10 else ''}")
        elif email and api_key:
            self.headers = {
                "X-Auth-Email": email,
                "X-Auth-Key": api_key
            }
            if self.verbose:
                print(f"Using Email+API key authentication")
                print(f"Email: {email}")
                # Don't print the full API key for security reasons
                print(f"API Key: {api_key[:5]}...{api_key[-5:] if len(api_key) > 10 else ''}")
        else:
            raise ValueError("Either API token or Email+API key must be provided")
    
    def get_deployments_paginated(self) -> List[Dict]:
        """Get all deployments for the project with pagination."""
        url = f"{self.BASE_URL}/accounts/{self.account_id}/pages/projects/{self.project_name}/deployments"
        
        all_deployments = []
        page = 1
        
        while True:
            params = {
                "page": page,
                "per_page": min(self.limit, 25)  # Cloudflare API limit is 25 per page for this endpoint
            }
            
            if self.env:
                params["env"] = self.env
            
            if self.verbose:
                print(f"Making GET request to: {url} (page {page})")
                print(f"Request headers: {json.dumps({k: '***' if k.lower() in ['authorization', 'x-auth-key'] else v for k, v in self.headers.items()})}")
                print(f"Request params: {json.dumps(params)}")
            
            try:
                response = requests.get(url, headers=self.headers, params=params)
                
                if self.verbose:
                    print(f"Response status: {response.status_code}")
                
                if response.status_code != 200:
                    print(f"Error getting deployments: {response.status_code}")
                    print(response.text)
                    self._handle_error_response(response)
                    sys.exit(1)
                    
                data = response.json()
                
                if not data["success"]:
                    print(f"API returned unsuccessful response: {data}")
                    sys.exit(1)
                
                deployments = data["result"]
                all_deployments.extend(deployments)
                
                # Check if we have more pages
                if "result_info" in data and data["result_info"].get("total_pages", 1) > page:
                    page += 1
                    print(f"Fetching page {page} of {data['result_info'].get('total_pages', 'unknown')}...")
                    # Short delay to avoid rate limiting
                    time.sleep(0.3)
                else:
                    break
                
            except requests.exceptions.RequestException as e:
                print(f"Network error when contacting Cloudflare API: {e}")
                sys.exit(1)
            except json.JSONDecodeError:
                print("Error decoding API response - received invalid JSON")
                print(f"Raw response: {response.text}")
                sys.exit(1)
        
        return all_deployments
    
    def _handle_error_response(self, response):
        """Handle common error responses with helpful messages."""
        try:
            if response.status_code == 400:
                data = response.json()
                if "errors" in data and len(data["errors"]) > 0:
                    for error in data["errors"]:
                        if error.get("code") == 10001 and "authenticate" in error.get("message", "").lower():
                            print("\nAuthentication Error: Your API token or key may be invalid or expired.")
                            print("Please check that:")
                            print("1. Your API token is correct and has not expired")
                            print("2. The token has the necessary permissions (Pages:Read and Pages:Edit)")
                            print("3. There are no extra spaces or characters in your token")
                            print("4. Your account ID is correct\n")
            
            elif response.status_code == 403:
                print("\nPermission Error: Your API token does not have permission to access this resource.")
                print("Please ensure your token has the Pages:Read and Pages:Edit permissions.\n")
            
            elif response.status_code == 404:
                print(f"\nNot Found Error: The project '{self.project_name}' was not found in account '{self.account_id}'.")
                print("Please check that both the project name and account ID are correct.\n")
            
            elif response.status_code == 429:
                print("\nRate Limit Error: You've exceeded Cloudflare's API rate limits.")
                print("Please wait a few minutes before trying again or reduce the frequency of requests.\n")
        
        except (json.JSONDecodeError, KeyError):
            pass
    
    def delete_deployment(self, deployment_id: str) -> bool:
        """Delete a specific deployment."""
        base_url = f"{self.BASE_URL}/accounts/{self.account_id}/pages/projects/{self.project_name}/deployments/{deployment_id}"
        
        # Add force parameter if required
        url = f"{base_url}?force=true" if self.force else base_url
        
        if self.dry_run:
            print(f"[DRY RUN] Would delete deployment: {deployment_id}" + (" (forced)" if self.force else ""))
            return True
        
        if self.verbose:
            print(f"Making DELETE request to: {url}")
            
        try:
            response = requests.delete(url, headers=self.headers)
            
            if response.status_code not in (200, 204):
                print(f"Error deleting deployment {deployment_id}: {response.status_code}")
                print(response.text)
                
                # Check if it's an aliased deployment error
                try:
                    data = response.json()
                    if not data.get("success", True) and data.get("errors"):
                        for error in data["errors"]:
                            if error.get("code") == 8000035 and "aliased deployment" in error.get("message", "").lower():
                                if not self.force:
                                    print("\nThis is an aliased deployment (likely the production deployment).")
                                    print("To delete it, rerun with the --force flag.\n")
                                else:
                                    print("\nFailed to delete even with force flag. This might be the active production deployment.")
                                    print("You may need to make another deployment the production deployment first.\n")
                except (json.JSONDecodeError, KeyError):
                    pass
                
                return False
                
            data = response.json()
            return data.get("success", False)
        
        except requests.exceptions.RequestException as e:
            print(f"Network error when contacting Cloudflare API: {e}")
            return False
        except json.JSONDecodeError:
            print("Error decoding API response - received invalid JSON")
            print(f"Raw response: {response.text}")
            return False
    
    def run(self):
        """Run the deletion process."""
        print(f"Getting deployments for project: {self.project_name}")
        
        deployments = self.get_deployments_paginated()
        print(f"Found {len(deployments)} deployments")
        
        if not deployments:
            print("No deployments to delete")
            return
            
        if self.dry_run:
            print("DRY RUN mode enabled - no actual deletions will occur")

        if self.force:
            print("FORCE mode enabled - will attempt to delete aliased deployments")
        
        deleted_count = 0
        failed_count = 0
        total_count = len(deployments)
        
        print(f"\nStarting deletion of {total_count} deployments...")
        
        for idx, deployment in enumerate(deployments, 1):
            deployment_id = deployment["id"]
            progress_pct = (idx / total_count) * 100
            
            print(f"[{idx}/{total_count}] ({progress_pct:.1f}%) Deleting deployment: {deployment_id}")
            success = self.delete_deployment(deployment_id)
            
            if success:
                print(f"✓ Successfully deleted deployment: {deployment_id}")
                deleted_count += 1
            else:
                print(f"✗ Failed to delete deployment: {deployment_id}")
                failed_count += 1
            
            # Avoid rate limiting, but use a shorter delay for efficiency with large deployments
            # We'll dynamically adjust the delay based on whether we've had any failures
            if failed_count > 0:
                # If we've had failures, be more cautious
                time.sleep(1.0) 
            else:
                # If all is going well, use a shorter delay
                time.sleep(0.5)
        
        print(f"Completed deletion: {deleted_count} deleted, {failed_count} failed")


def main():
    parser = argparse.ArgumentParser(description="Delete all deployments from a Cloudflare Pages project")
    
    parser.add_argument("--account-id", help="Cloudflare account ID")
    parser.add_argument("--project-name", help="Pages project name")
    
    # Auth options
    auth_group = parser.add_argument_group("Authentication (use either token or email+key)")
    auth_group.add_argument("--api-token", help="Cloudflare API token")
    auth_group.add_argument("--email", help="Cloudflare account email")
    auth_group.add_argument("--api-key", help="Cloudflare API key")
    
    # Optional filters and settings
    parser.add_argument("--env", choices=["production", "preview"], 
                        help="Filter deployments by environment")
    parser.add_argument("--dry-run", action="store_true", 
                        help="Show what would be deleted without actually deleting")
    parser.add_argument("--env-file", default="../envfile",
                        help="Path to environment file (default: ../envfile)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Enable verbose debug output")
    parser.add_argument("--force", "-f", action="store_true",
                        help="Force deletion of aliased deployments (production)")
    parser.add_argument("--limit", type=int, default=25,
                        help="Maximum number of deployments to fetch per page (default: 25, max: 25)")
    
    args = parser.parse_args()
    
    # Try to load from env file if it exists
    env_vars = {}
    if os.path.exists(args.env_file):
        print(f"Loading configuration from {args.env_file}")
        env_vars = load_env_file(args.env_file)
        
        if args.verbose:
            # Print env vars but mask sensitive values
            masked_vars = {k: (v[:5] + "..." + v[-5:] if k.upper().endswith(("TOKEN", "KEY")) and len(v) > 15 else v) 
                          for k, v in env_vars.items()}
            print(f"Loaded environment variables: {json.dumps(masked_vars, indent=2)}")
    
    # Get values from arguments, env file, or environment variables
    account_id = args.account_id or env_vars.get('CF_ACCOUNT_ID') or os.environ.get('CF_ACCOUNT_ID')
    project_name = args.project_name or env_vars.get('CF_PAGES_PROJECT_NAME') or os.environ.get('CF_PAGES_PROJECT_NAME')
    api_token = args.api_token or env_vars.get('CF_API_TOKEN') or os.environ.get('CF_API_TOKEN') or os.environ.get('CLOUDFLARE_API_TOKEN')
    email = args.email or env_vars.get('CF_EMAIL') or os.environ.get('CF_EMAIL') or os.environ.get('CLOUDFLARE_EMAIL')
    api_key = args.api_key or env_vars.get('CF_API_KEY') or os.environ.get('CF_API_KEY') or os.environ.get('CLOUDFLARE_API_KEY')
    
    # Validate required parameters
    if not account_id:
        parser.error("Account ID is required. Provide it via --account-id or CF_ACCOUNT_ID in env file/variables")
    
    if not project_name:
        parser.error("Project name is required. Provide it via --project-name or CF_PAGES_PROJECT_NAME in env file/variables")
    
    # Validate auth inputs
    if not (api_token or (email and api_key)):
        parser.error("Authentication required. Provide API token or Email+API key via arguments or environment variables")
    
    if args.verbose:
        print("\nConfiguration:")
        print(f"Account ID: {account_id}")
        print(f"Project Name: {project_name}")
        print(f"Environment: {args.env or 'all'}")
        print(f"Dry Run: {args.dry_run}")
        print(f"Force: {args.force}")
        print(f"Page limit: {args.limit}")
        print()
    
    deleter = CloudflareDeploymentDeleter(
        account_id=account_id,
        project_name=project_name,
        email=email,
        api_key=api_key,
        api_token=api_token,
        env=args.env,
        dry_run=args.dry_run,
        verbose=args.verbose,
        force=args.force,
        limit=args.limit
    )
    
    deleter.run()


if __name__ == "__main__":
    main() 