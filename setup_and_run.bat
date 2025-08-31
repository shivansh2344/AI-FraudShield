@echo off
REM Go to project folder
cd /d "%~dp0fraud_detection_skeleton"

REM Create venv if not exists
if not exist venv (
    python -m venv venv
)

REM Activate venv
call venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install dependencies
pip install -r requirements.txt

REM Run Streamlit app
streamlit run app/app.py
