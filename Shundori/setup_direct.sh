#!/bin/bash

# Direct Python setup script (without Docker)

echo "🐍 Telegram Attendance Bot - Direct Python Setup"
echo "================================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $PYTHON_VERSION"

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "📝 Setting up .env file..."
    echo ""
    
    # Get BOT_TOKEN
    echo "1️⃣  Get your BOT_TOKEN:"
    echo "   - Open Telegram and message @BotFather"
    echo "   - Send /newbot and follow instructions"
    echo "   - Copy the token you receive"
    echo ""
    read -p "   Enter your BOT_TOKEN: " BOT_TOKEN
    
    # Get ADMIN_ID
    echo ""
    echo "2️⃣  Get your ADMIN_ID:"
    echo "   - Open Telegram and message @userinfobot"
    echo "   - It will reply with your user ID"
    echo "   - Copy the ID number"
    echo ""
    read -p "   Enter your ADMIN_ID: " ADMIN_ID
    
    # Create .env file
    cat > .env << EOF
# Telegram Bot Configuration
BOT_TOKEN=${BOT_TOKEN}
ADMIN_ID=${ADMIN_ID}

# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/attendance_bot

# Timezone
TZ=Asia/Phnom_Penh

# Fine Configuration (default)
DEFAULT_FINE_AMOUNT=20

# Attendance Window (default)
ATTENDANCE_WINDOW_START=09:00
ATTENDANCE_WINDOW_END=10:00

# Report Time
REPORT_TIME=10:05
EOF
    
    echo ""
    echo "✅ .env file created!"
    echo ""
else
    echo "✅ .env file found"
    source .env
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "✅ Dependencies installed!"
echo ""

# Check PostgreSQL
echo "🔍 Checking PostgreSQL..."
if command -v psql &> /dev/null; then
    echo "✅ PostgreSQL found"
    
    # Try to create database (will fail if exists, that's okay)
    createdb attendance_bot 2>/dev/null || echo "   Database may already exist"
else
    echo "⚠️  PostgreSQL not found in PATH"
    echo ""
    echo "📋 To install PostgreSQL:"
    echo "   brew install postgresql@15"
    echo "   brew services start postgresql@15"
    echo ""
    echo "   Or download from: https://www.postgresql.org/download/macosx/"
    echo ""
    read -p "Press Enter to continue anyway (you'll need to set up PostgreSQL manually)..."
fi

# Initialize database
echo ""
echo "🗄️  Initializing database..."
python migrations/init_db.py

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Make sure PostgreSQL is running"
echo "   2. Add your bot to your Telegram group"
echo "   3. Run the bot:"
echo "      source venv/bin/activate"
echo "      python bot.py"
echo ""
echo "   Or use the run script:"
echo "      ./run_bot.sh"
echo ""

