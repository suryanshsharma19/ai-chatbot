#!/bin/bash

python -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

python -m spacy download en_core_web_sm

echo "Setup completed! You can now run:"
echo "1. ./start_backend.sh (in one terminal)"
echo "2. ./start_gui.sh (in another terminal)" 