#!/bin/bash
echo "Starting build script..."
echo "Current directory: $(pwd)"
echo "Listing contents:"
ls -la

# Create bot directory if it doesn't exist
mkdir -p api/bot

# Copy src/bot contents to api/bot
cp -r src/bot/* api/bot/

echo "Build script completed" 