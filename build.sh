#!/bin/bash

# This script runs the Python-based conversion process to build the blog from markdown source.

echo "Starting blog conversion..."

# Run the Python script
python3 scripts/convert_writeups.py

echo "Conversion complete."
