#!/bin/bash

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Install spaCy model
python -m spacy download en_core_web_sm

echo "Setup completed! You can now run:"
echo "1. ./start_backend.sh (in one terminal)"
echo "2. ./start_gui.sh (in another terminal)" 