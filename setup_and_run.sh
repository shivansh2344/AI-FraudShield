#!/bin/bash
cd "$(dirname "$0")/fraud_detection_skeleton"

# Create venv if not exists
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Run Streamlit app
streamlit run app/app.py
