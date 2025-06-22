@echo off
echo 🚀 Setting up AI Task Assistant Flutter App...

REM Check if Flutter is installed
flutter --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Flutter is not installed. Please install Flutter first:
    echo    https://flutter.dev/docs/get-started/install
    pause
    exit /b 1
)

REM Check Flutter version
echo 📱 Checking Flutter version...
flutter --version

REM Get dependencies
echo 📦 Installing dependencies...
flutter pub get

REM Generate Hive models
echo 🔧 Generating Hive models...
flutter packages pub run build_runner build --delete-conflicting-outputs

REM Check if Android emulator is running
echo 📱 Checking for Android emulator...
adb devices | findstr "emulator" >nul
if errorlevel 1 (
    echo ⚠️  No Android emulator detected.
    echo    Please start an Android emulator or connect a physical device.
    echo    You can start an emulator with: flutter emulators --launch ^<emulator_id^>
)

REM Check if backend is running
echo 🔍 Checking backend connection...
curl -s http://10.0.2.2:8080/api/tasks >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Backend is not accessible at http://10.0.2.2:8080
    echo    Make sure your Flask backend is running on port 8080
    echo    You can start it with: python web_app.py
) else (
    echo ✅ Backend is running and accessible
)

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Make sure your Flask backend is running: python web_app.py
echo 2. Start an Android emulator or connect a physical device
echo 3. Run the app: flutter run
echo.
echo 📱 App will be available on your device/emulator
echo 🌐 Web interface: http://localhost:8080
echo.
echo For more information, see README.md
pause 