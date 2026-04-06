# Pipeline Troubleshooting Assistant (MVP)

Small rule-based troubleshooting assistant that parses pipeline logs and configs to surface likely failure points, recommended next steps, and evidence. Built as a demo portfolio project for Solutions Engineering roles.

## Why I built this
To demonstrate a deterministic, explainable troubleshooting tool that a Solutions or Implementation Engineer could use to rapidly diagnose common pipeline failures.

## Who it's for
- Implementers, support engineers, or recruiters reviewing a technical portfolio.

## Core features
- Paste or upload logs and configs (JSON/YAML).
- Deterministic rule engine (no LLM) that identifies categories like missing params, missing files, permission errors, schema mismatches, missing dependencies, timeouts.
- Returns probable root causes, next steps, severity, confidence, and matched evidence.
- Stores recent analysis runs in a local SQLite database.

## Architecture
- FastAPI backend serving a small Jinja2-rendered frontend.
- Deterministic `RuleEngine` that loads JSON rule definitions from `app/rules/rules.json`.
- Simple SQLite JSON store under `data/runs.db`.

## Rule engine design
- Rules are defined in JSON and support types: `substring`, `regex`, `missing_field`, `invalid_value`, `path_missing`.
- The engine applies rules to logs, failed output, and parsed config, returning structured matches ranked by severity and confidence.

## Demo flow — quick for recruiters
This section is designed so a recruiter or hiring manager can try the app in < 2 minutes.

With Docker (recommended):

```bash
docker-compose up --build
# open http://localhost:8000 in your browser
```

Without Docker (local dev):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
# open http://127.0.0.1:8000
```

How to demo (recommended):
1. Open the web UI at `/`.
2. Use the sample picker to load a sample log (e.g. `sample1.log`).
3. Click `Analyze` — the results card shows the top issue, severity, confidence, evidence, and recommended next steps.
4. Visit `Recent Runs` to view saved runs and open a run detail page to see the full JSON and evidence snippets.

This flow is intentionally short and deterministic so a non-technical reviewer can reproduce the classification quickly.

## API
- `GET /health` — health check
- `POST /analyze` — form: `logs`, `config_file`, `failed_output`
- `GET /runs` — list recent runs
- `GET /runs/{run_id}` — get run
- `GET /api/rules` — list rule definitions
- `GET /api/sample-cases` — return sample logs

## Sample data
See `app/sample_data` for five example logs and a sample config.

## Tests
Run tests with:

```bash
pytest -q
```

## Future improvements (first 5)
1. Add a formal config schema validator (e.g., JSON Schema) and schema-driven rules.
2. Improve UI: paginated runs, run details page, copyable actionable steps.
3. Add role-based access and exportable run reports (PDF/JSON).
4. Add richer evidence extraction with context windows and line numbers.
5. Add rule editor in UI for on-the-fly rule creation and testing.

## Why this matters for Solutions Engineering
Deterministic, transparent diagnostics reduce onboarding time for customers and enable reproducible steps for remediation — core outcomes for Solutions and Implementation Engineers.

## Screenshots
Placeholders: add screenshots to `/screenshots` showing the UI and results.
