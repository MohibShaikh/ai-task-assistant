#!/bin/bash

echo "🚀 Deploying AI Task Assistant..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "📝 Please create .env file with your configuration:"
    echo "   cp config_sample.env .env"
    echo "   # Then edit .env with your API keys"
fi

# Run security tests
echo "🔒 Running security tests..."
python tests/test_security.py

# Start the application
echo "🌐 Starting AI Task Assistant..."
echo "📱 Open your browser and go to: http://localhost:8080"
echo "🚀 Press Ctrl+C to stop the server"

python web_app.py 