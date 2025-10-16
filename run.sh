#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

PROJECT_ROOT=$(dirname "$(readlink -f "$0")")

echo "Building CWT Docker image..."
docker build -t cwt-tool "$PROJECT_ROOT"

echo "Running CWT Docker container..."
# Ensure .env file exists
if [ ! -f "$PROJECT_ROOT/.env" ]; then
    echo "Error: .env file not found in $PROJECT_ROOT."
    echo "Please create a .env file with CWT_MAIN_WITHDRAWAL_ADDRESS and other sensitive variables."
    exit 1
fi

docker run --rm -it --env-file "$PROJECT_ROOT/.env" cwt-tool "$@"
