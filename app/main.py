from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from app.api.routes import router as api_router
from app.core.rule_engine import RuleEngine
import os

def create_app():
    app = FastAPI(title="Pipeline Troubleshooting Assistant")
    app.mount("/static", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "static")), name="static")
    templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))

    # Load rules and create engine once
    rules_path = os.path.join(os.path.dirname(__file__), "rules", "rules.json")
    engine = RuleEngine(rules_path)

    app.state.rule_engine = engine
    app.state.templates = templates

    app.include_router(api_router)
    return app

app = create_app()

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return app.state.templates.TemplateResponse("index.html", {"request": request})
