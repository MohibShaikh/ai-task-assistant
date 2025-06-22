@echo off
echo 🚀 Deploying AI Task Assistant...

REM Check if virtual environment exists
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if not exist ".env" (
    echo ⚠️  Warning: .env file not found!
    echo 📝 Please create .env file with your configuration:
    echo    copy config_sample.env .env
    echo    # Then edit .env with your API keys
)

REM Run security tests
echo 🔒 Running security tests...
python tests\test_security.py

REM Start the application
echo 🌐 Starting AI Task Assistant...
echo 📱 Open your browser and go to: http://localhost:8080
echo 🚀 Press Ctrl+C to stop the server

python web_app.py 