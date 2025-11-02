#!/usr/bin/env bash
# Build script for AI Rule Intelligence Platform
# This script runs during the Render build process

echo "Starting build process for AI Rule Intelligence Platform..."

# Print environment information
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Render environment: ${RENDER}"

# Upgrade pip to the latest version
echo "Upgrading pip..."
pip install --upgrade pip

# Install setuptools and wheel first (required for some packages)
echo "Installing setuptools and wheel..."
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

# Verify database was created
echo "Verifying database..."
if [ -f "rules_db/rules.db" ]; then
    echo "Database file exists"
else
    echo "Database file does not exist!"
fi

echo "Build process completed successfully!"