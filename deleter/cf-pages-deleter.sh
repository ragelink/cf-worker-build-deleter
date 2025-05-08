#!/bin/bash
set -e

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker first."
    exit 1
fi

# Directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if the image exists, build if it doesn't
if ! docker image inspect cf-pages-deleter &> /dev/null; then
    echo "Building Docker image..."
    docker build -t cf-pages-deleter "$SCRIPT_DIR"
fi

# Check if envfile exists
if [ ! -f "$SCRIPT_DIR/envfile" ] && [ ! -f "./envfile" ]; then
    echo "No envfile found. Creating a sample one..."
    if [ -f "$SCRIPT_DIR/envfile.sample" ]; then
        cp "$SCRIPT_DIR/envfile.sample" "$SCRIPT_DIR/envfile"
        echo "Created $SCRIPT_DIR/envfile from sample. Please edit it with your credentials."
        exit 1
    else
        echo "Could not find envfile.sample. Please create an envfile manually."
        exit 1
    fi
fi

# Determine which envfile to use
if [ -f "./envfile" ]; then
    ENVFILE_PATH="./envfile"
else
    ENVFILE_PATH="$SCRIPT_DIR/envfile"
fi

# Run the container with the provided arguments
echo "Running with envfile: $ENVFILE_PATH"
docker run --rm -v "$ENVFILE_PATH:/app/envfile:ro" cf-pages-deleter --env-file /app/envfile "$@" 