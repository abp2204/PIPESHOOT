from fastapi import APIRouter, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from pydantic import BaseModel
import json, yaml, io, os, datetime
from app.services.storage import DB

router = APIRouter()


def _parse_config_upload(upload: UploadFile | None):
    if not upload:
        return {}
    content = upload.file.read()
    try:
        if upload.filename.lower().endswith(('.yml', '.yaml')):
            return yaml.safe_load(content)
        else:
            return json.loads(content)
    except Exception:
        raise HTTPException(status_code=400, detail="Config file must be valid JSON or YAML")


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.post("/analyze")
async def analyze(request: Request, logs: str = Form(""), config_file: UploadFile | None = File(None), failed_output: UploadFile | None = File(None)):
    engine = request.app.state.rule_engine
    config = _parse_config_upload(config_file)
    failed_text = None
    if failed_output:
        try:
            failed_text = failed_output.file.read().decode('utf-8', errors='ignore')
        except Exception:
            failed_text = None

    result = engine.analyze(logs or "", config or {}, failed_text or "")

    # store run
    db = DB()
    run_record = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "input_summary": {
            "logs_len": len(logs or ""),
            "config_keys": list(config.keys())
        },
        "result": result
    }
    run_id = db.save_run(run_record)
    return JSONResponse({"run_id": run_id, "result": result})


@router.get("/runs")
async def list_runs(request: Request):
    db = DB()
    runs = db.list_runs()
    # Render a simple UI for recent runs
    templates = request.app.state.templates
    return templates.TemplateResponse("runs.html", {"request": request, "runs": runs})


@router.get("/runs/{run_id}")
async def get_run(run_id: int):
    db = DB()
    run = db.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found")
    # Render details page
    templates = Request.app.state.templates if False else None
    templates = None
    try:
        templates = request.app.state.templates
    except Exception:
        pass
    if templates:
        return templates.TemplateResponse("run_detail.html", {"request": request, "run": run})
    return JSONResponse(run)


@router.get('/api/rules')
async def get_rules(request: Request):
    engine = request.app.state.rule_engine
    return JSONResponse(engine.rules)


@router.get('/api/sample-cases')
async def sample_cases():
    base = os.path.join(os.path.dirname(__file__), '..', 'sample_data')
    base = os.path.normpath(base)
    samples = {}
    samples_dir = os.path.join(os.path.dirname(__file__), '..', 'sample_data')
    samples_dir = os.path.normpath(samples_dir)
    if os.path.isdir(samples_dir):
        for name in os.listdir(samples_dir):
            if name.endswith('.log') or name.endswith('.txt'):
                path = os.path.join(samples_dir, name)
                with open(path, 'r', encoding='utf8') as f:
                    samples[name] = f.read()
    return JSONResponse(samples)
