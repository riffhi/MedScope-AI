#!/bin/bash

# Set up environment (if using a virtual environment)
if [ -d "venv" ]; then
  source venv/bin/activate
elif [ -d ".venv" ]; then
  source .venv/bin/activate
fi

# Install dependencies if needed
pip install -r backend/requirements.txt

# Change to the backend directory
cd backend

# Start the Flask server
python run.py
