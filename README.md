# Application Desk

A privacy-first Streamlit workspace for organizing job applications. This clean
rewrite deliberately does **not** scrape websites, call an AI model, automate a
browser, or submit applications. It provides a dependable base before those
features are introduced behind an explicit review step.

## Features

- validated local candidate profile
- validated, duplicate-free Greenhouse job bookmarks
- review workflow (`saved`, `reviewing`, `ready`, `applied`, `rejected`)
- notes and application history persisted in SQLite
- no API key required and no personal data sent to third parties

## Local development

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Data is stored in `app/data/applications.db` by default and ignored by Git. Set
`APPLICATION_DB` to choose another location.

## Docker

```bash
docker build -t application-desk .
docker run --rm -p 8501:8501 -v application-data:/data application-desk
```

Open <http://localhost:8501>. The named volume preserves data across container
restarts.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Roadmap

1. Resume metadata and safe file storage.
2. A Greenhouse adapter that extracts application questions.
3. Optional, structured AI answer suggestions with source attribution.
4. User approval before any browser-assisted form filling.

Automatic submission is intentionally out of scope.
