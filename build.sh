#!/bin/bash

set -e

echo "Building portfolio website..."

# Run markdown → HTML
python scripts/convert_writeups.py

# ✅ ADD THIS BLOCK (IMPORTANT)
echo "Copying static assets..."

rm -rf docs/assets/videos
mkdir -p docs/assets/videos
cp -r blog-src/assets/videos/* docs/assets/videos/

echo "Build completed successfully!"
