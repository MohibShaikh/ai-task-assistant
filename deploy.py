#!/usr/bin/env python3
"""
Deployment helper script for AI Task Assistant
"""

import os
import subprocess
import sys

def check_requirements():
    """Check if all required files exist."""
    required_files = [
        'web_app.py',
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        'templates/index.html',
        'static/css/style.css',
        'static/js/app.js'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def check_env_vars():
    """Check if required environment variables are set."""
    required_vars = [
        'PINECONE_API_KEY',
        'PINECONE_ENVIRONMENT',
        'PINECONE_INDEX_NAME'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nSet these in your cloud platform's environment variables section")
        return False
    
    print("✅ All required environment variables found")
    return True

def create_env_sample():
    """Create a sample .env file."""
    env_content = """# AI Task Assistant Environment Variables

# Pinecone Configuration
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=ai-task-assistant

# Flask Configuration
SECRET_KEY=your_secret_key_here
FLASK_DEBUG=False

# Optional: Google OAuth (if using)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=https://your-app-url.com/api/auth/google/callback
"""
    
    with open('.env.sample', 'w') as f:
        f.write(env_content)
    
    print("✅ Created .env.sample file")

def main():
    print("🚀 AI Task Assistant - Deployment Check")
    print("=" * 50)
    
    # Check files
    if not check_requirements():
        sys.exit(1)
    
    # Check environment variables
    check_env_vars()
    
    # Create sample env file
    create_env_sample()
    
    print("\n" + "=" * 50)
    print("📋 Next Steps:")
    print("1. Get your Pinecone API key from https://pinecone.io")
    print("2. Choose a deployment platform:")
    print("   - Railway: https://railway.app (Recommended)")
    print("   - Render: https://render.com")
    print("   - Heroku: https://heroku.com")
    print("3. Set environment variables in your platform")
    print("4. Deploy!")
    print("\n📖 See DEPLOYMENT_GUIDE.md for detailed instructions")

if __name__ == '__main__':
    main() 