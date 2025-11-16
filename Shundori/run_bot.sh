#!/bin/bash

# Script to run the bot (direct Python method)

cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Run ./setup_direct.sh first"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "   Run ./setup_direct.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the bot
echo "🚀 Starting Telegram Attendance Bot..."
echo ""
python bot.py

