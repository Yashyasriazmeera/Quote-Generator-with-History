# Quote-Generator-with-History

Random quote generator built with Python Flask and external API integration.

## Features
- Fetches random quotes from an external API
- Stores every fetched quote in SQLite quote history
- Provides a responsive UI with a **New Quote** action
- Exposes backend API endpoints for quote generation and history retrieval

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open `http://127.0.0.1:5000` in your browser.

## Run tests
```bash
python -m unittest discover -s tests -q
```
