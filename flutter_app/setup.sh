#!/bin/bash

# AI Task Assistant Flutter App Setup Script
echo "🚀 Setting up AI Task Assistant Flutter App..."

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter is not installed. Please install Flutter first:"
    echo "   https://flutter.dev/docs/get-started/install"
    exit 1
fi

# Check Flutter version
echo "📱 Checking Flutter version..."
flutter --version

# Get dependencies
echo "📦 Installing dependencies..."
flutter pub get

# Generate Hive models
echo "🔧 Generating Hive models..."
flutter packages pub run build_runner build --delete-conflicting-outputs

# Check if Android emulator is running
echo "📱 Checking for Android emulator..."
if ! adb devices | grep -q "emulator"; then
    echo "⚠️  No Android emulator detected."
    echo "   Please start an Android emulator or connect a physical device."
    echo "   You can start an emulator with: flutter emulators --launch <emulator_id>"
fi

# Check if backend is running
echo "🔍 Checking backend connection..."
if curl -s http://10.0.2.2:8080/api/tasks > /dev/null 2>&1; then
    echo "✅ Backend is running and accessible"
else
    echo "⚠️  Backend is not accessible at http://10.0.2.2:8080"
    echo "   Make sure your Flask backend is running on port 8080"
    echo "   You can start it with: python web_app.py"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "1. Make sure your Flask backend is running: python web_app.py"
echo "2. Start an Android emulator or connect a physical device"
echo "3. Run the app: flutter run"
echo ""
echo "📱 App will be available on your device/emulator"
echo "🌐 Web interface: http://localhost:8080"
echo ""
echo "For more information, see README.md" 