#!/bin/bash
set -e

echo "==============================================="
echo "  CloudFlare Pages Deployment Bulk Deleter"
echo "  Optimized for 600+ deployments"
echo "==============================================="

# Directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if the bash script exists, if so use it
if [ -f "$SCRIPT_DIR/cf-pages-deleter.sh" ]; then
    echo "Using shell wrapper..."
    chmod +x "$SCRIPT_DIR/cf-pages-deleter.sh"
    "$SCRIPT_DIR/cf-pages-deleter.sh" --force --limit 25 "$@"
else
    # Otherwise use Docker directly
    echo "Using Docker directly..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        echo "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Build the image if needed
    if ! docker image inspect cf-pages-deleter &> /dev/null; then
        echo "Building Docker image..."
        docker build -t cf-pages-deleter "$SCRIPT_DIR"
    fi
    
    # Find the envfile
    if [ -f "$SCRIPT_DIR/envfile" ]; then
        ENVFILE_PATH="$SCRIPT_DIR/envfile"
    elif [ -f "./envfile" ]; then
        ENVFILE_PATH="./envfile"
    else
        echo "No envfile found. Please create an envfile first."
        if [ -f "$SCRIPT_DIR/envfile.sample" ]; then
            cp "$SCRIPT_DIR/envfile.sample" "$SCRIPT_DIR/envfile"
            echo "Created $SCRIPT_DIR/envfile from sample. Please edit it with your credentials."
        fi
        exit 1
    fi
    
    # Run with optimal settings for large deployments
    echo "Running with envfile: $ENVFILE_PATH"
    docker run --rm -v "$ENVFILE_PATH:/app/envfile:ro" cf-pages-deleter --env-file /app/envfile --force --limit 25 "$@"
fi

echo "==============================================="
echo "  Deletion process complete"
echo "===============================================" 