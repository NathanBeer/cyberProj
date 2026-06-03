@echo off
echo ========================================
echo   CyberDetect - Attack Detection Agent
echo ========================================
echo.

echo [1/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)
echo.

if not exist "data\csic_database.csv" (
    echo [2/3] Generating training data...
    python generate_data.py
    if errorlevel 1 (
        echo ERROR: Failed to generate data.
        pause
        exit /b 1
    )
) else (
    echo [2/3] Training data already exists, skipping generation.
)
echo.

if not exist "models\classifier.joblib" (
    echo [3/3] Training the classifier...
    python train.py --data-dir data/
    if errorlevel 1 (
        echo ERROR: Training failed.
        pause
        exit /b 1
    )
) else (
    echo [3/3] Trained model already exists, skipping training.
)
echo.

echo ========================================
echo   Starting app at http://localhost:5000
echo ========================================
echo   Press Ctrl+C to stop the server.
echo.
python run.py
pause
