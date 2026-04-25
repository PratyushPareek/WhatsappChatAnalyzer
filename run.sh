#!/usr/bin/env bash
set -e

echo "============================================"
echo " WAChatAnalysis — Setup & Run"
echo "============================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed."
    echo "Install it via: brew install python3 (macOS) or sudo apt install python3 python3-venv (Linux)"
    exit 1
fi

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Install dependencies
echo "Installing dependencies..."
venv/bin/python -m pip install --quiet --upgrade pip
venv/bin/python -m pip install --quiet -r requirements.txt

# Create folders
mkdir -p chats output

# Check for chat files
if ! ls chats/*.txt 1> /dev/null 2>&1; then
    echo ""
    echo "No chat files found in chats/ folder."
    echo "Export a WhatsApp chat as .txt and place it in the chats/ folder."
    echo "Then run this script again."
    exit 0
fi

# Run analysis
echo ""
echo "Running analysis..."
venv/bin/python -m src.main

echo ""
echo "Done! Reports are in the output/ folder."
