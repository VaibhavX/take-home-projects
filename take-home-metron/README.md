# take-home-metron

Simple Flask application that reads a sample meter data CSV, normalizes
volume units to litres and renders a preview table + line chart on the
home page.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
pip install -r requirements.txt
```

## Run

```bash
python main_process.py
```

Open http://127.0.0.1:5000/ in your browser. Data and templates live in
`data/` and `templates/` respectively.
