# NetLogo Models Static Site

`I created this code with GitHub Copilot (GPT 5.2-Codex)`

Generates a fully static website that lists all NetLogo .nlogox models and provides a detail page for each model with the Info tab rendered as HTML.

## What it does
- Builds a folder-tree index of all models under models
- Generates one HTML page per model with screenshot and Info tab content
- Adds a Run on NetLogoWeb button for each model

## Requirements
- Python 3.10+
- Dependencies listed in requirements.txt

## Setup
Create and activate a virtual environment (macOS/Linux):
- `python3 -m venv .venv`
- `source .venv/bin/activate`

Install dependencies using the venv:
- `.venv/bin/pip install -r requirements.txt`

## Build
Generate the site:
- `.venv/bin/python build_static.py`

The output is written to the `public` folder. You can deploy the site folder as-is.

## Assets
- Model icon is stored in `public/assets/model.png`.
- Model images are stored alongside the html files in the `public/models` folder.

## Notes
- Screenshots are resolved from the models folder and must be .png files with matching names.
