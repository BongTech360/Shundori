FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (no database client needed for MongoDB)
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create exports directory
RUN mkdir -p exports

# Run the bot (database initialization happens in bot.py post_init)
CMD ["python", "bot.py"]

