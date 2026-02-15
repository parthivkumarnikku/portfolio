#!/bin/bash

# Build script for portfolio website
# Converts markdown blog posts to HTML using Jinja2 templates

set -e

echo "Building portfolio website..."

# Run the Python script to convert markdown blog posts
python scripts/convert_writeups.py

echo "Build completed successfully!"
