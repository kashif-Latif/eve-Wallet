#!/bin/bash
set -e

echo "=== Vercel Python Build ==="

# Install dependencies (Vercel does this automatically, but just in case)
pip install -r requirements.txt 2>/dev/null || pip install -r ../requirements.txt 2>/dev/null || true

# Collect static files for WhiteNoise
cd ..
python manage.py collectstatic --noinput 2>/dev/null || true

echo "=== Build Complete ==="
