@echo off

set VENV_FOLDER=venv

if exist %VENV_FOLDER% (
    echo Virtual environment exists 
) else (
    echo Creating virtual environment...
    python -m venv %VENV_FOLDER%
    if %errorlevel% neq 0 (
        echo ERROR: Failed to create virtual environment
        goto :EOF
    )
)

echo Activating virtual environment...
call %VENV_FOLDER%\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    goto :EOF
)
echo Activated

if exist requirements.txt (
    echo Installing from requirements...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install requirements
        goto :EOF
    )
) else (
    echo No requirements.txt in the folder; you have to do a manual install.
)
