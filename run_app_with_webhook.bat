@echo off
echo Starting Voice Notes API with Telegram webhook setup...
echo.

REM Change to project root directory
cd /d "C:\Users\bruce\Desktop\Voice-Notes-Python"
echo Changed to project directory: %CD%

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found at .venv\Scripts\activate.bat
    echo Please create a virtual environment first with: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

REM Start uvicorn in a new command window
echo Starting uvicorn server in new window...
start "Voice Notes API" cmd /k ".venv\Scripts\python.exe -m uvicorn app.main:app --reload"

REM Wait for uvicorn to start
echo Waiting for uvicorn to start (5 seconds)...
timeout /t 5 /nobreak >nul

REM Health check for FastAPI server
echo Checking FastAPI server health...
for /f "delims=" %%i in ('curl -s http://127.0.0.1:8000/health 2^>nul') do set HEALTH_RESPONSE=%%i

if "%HEALTH_RESPONSE%"=="{"status":"ok"}" (
    echo FastAPI server is running.
) else (
    echo FastAPI server may not have started yet.
)

REM Start ngrok in a new command window
echo Starting ngrok tunnel in new window...
start "Ngrok Tunnel" cmd /k "ngrok http 8000"

REM Wait for ngrok to establish tunnel
echo Waiting for ngrok to establish tunnel (5 seconds)...
timeout /t 5 /nobreak >nul

REM Get ngrok public URL using PowerShell
echo Getting ngrok public URL...
for /f "delims=" %%i in ('powershell -Command "(Invoke-RestMethod http://127.0.0.1:4040/api/tunnels).tunnels[0].public_url"') do set PUBLIC_URL=%%i

if "%PUBLIC_URL%"=="" (
    echo Error: Could not get ngrok public URL. Make sure ngrok is running.
    pause
    exit /b 1
)

echo Public URL: %PUBLIC_URL%

REM Read TELEGRAM_BOT_TOKEN from .env file
echo Reading TELEGRAM_BOT_TOKEN from .env file...
set TELEGRAM_BOT_TOKEN=

if exist ".env" (
    for /f "tokens=2 delims==" %%a in ('findstr /b "TELEGRAM_BOT_TOKEN=" .env') do set TELEGRAM_BOT_TOKEN=%%a
)

if "%TELEGRAM_BOT_TOKEN%"=="" (
    echo.
    echo ERROR: TELEGRAM_BOT_TOKEN not found in .env file!
    echo Please edit the .env file and add:
    echo TELEGRAM_BOT_TOKEN=your_bot_token_here
    echo.
    echo Then run this script again.
    pause
    exit /b 1
)

echo Found TELEGRAM_BOT_TOKEN: %TELEGRAM_BOT_TOKEN%

REM Set Telegram webhook
echo Setting Telegram webhook...
set WEBHOOK_URL=%PUBLIC_URL%/telegram/%TELEGRAM_BOT_TOKEN%
echo Webhook URL: %WEBHOOK_URL%

curl -X POST "https://api.telegram.org/bot%TELEGRAM_BOT_TOKEN%/setWebhook" -d "url=%WEBHOOK_URL%"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo SUCCESS! Webhook setup complete.
    echo ========================================
    echo Public URL: %PUBLIC_URL%
    echo Webhook URL: %WEBHOOK_URL%
    echo.
    echo Your Telegram bot is now ready!
    echo Test it by sending /start to your bot.
    echo.
) else (
    echo.
    echo ERROR: Failed to set webhook. Check your TELEGRAM_BOT_TOKEN.
    echo.
)

echo Press any key to close this window...
pause >nul
