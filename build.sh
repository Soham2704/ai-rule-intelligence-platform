#!/usr/bin/env bash
# Build script for AI Rule Intelligence Platform
# This script runs during the Render build process

echo "Starting build process for AI Rule Intelligence Platform..."

# Upgrade pip to the latest version
pip install --upgrade pip

# Install setuptools and wheel first (required for some packages)
pip install setuptools==68.2.2 wheel==0.41.2

# Install all project dependencies
echo "Installing project dependencies..."
pip install --only-binary=:all: -r requirements.txt

# Create and initialize the database
echo "Initializing database..."
python database_setup.py

# Populate the database with Mumbai rules
echo "Populating database with Mumbai rules..."
python populate_comprehensive_rules.py

echo "Build process completed successfully!"