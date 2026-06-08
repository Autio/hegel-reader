@echo off
REM Hegel Reader - Local LLM Server (CUDA)
REM Qwen 2.5 72B IQ3_XXS on RTX 5090
REM 55/80 layers GPU, 24K context

set SERVER=%LOCALAPPDATA%\Programs\llama.cpp-cuda\llama-server.exe
set MODEL=%LOCALAPPDATA%\hermes\models\Qwen2.5-72B-Instruct-IQ3_XXS.gguf
set PORT=8081

echo ========================================
echo Hegel Reader Local LLM Server [CUDA]
echo Model: Qwen 2.5 72B IQ3_XXS
echo GPU: RTX 5090 - 55/80 layers
echo Context: 24,576 | Port: %PORT%
echo ========================================

if not exist "%MODEL%" (
    echo ERROR: Model not found at %MODEL%
    pause
    exit /b 1
)

echo Starting server with CUDA...
"%SERVER%" ^
    --model "%MODEL%" ^
    --port %PORT% ^
    --n-gpu-layers 55 ^
    --ctx-size 24576 ^
    --batch-size 512 ^
    --flash-attn on ^
    --host 127.0.0.1 ^
    -fit off

pause
