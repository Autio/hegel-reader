@echo off
REM Quick health check for the local LLM server
curl -s http://localhost:8080/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] llama-server is running on port 8080
) else (
    echo [DOWN] llama-server not responding
    exit /b 1
)
