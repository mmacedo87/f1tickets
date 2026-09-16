"""
Dashboard Agent (interface).
Pequeno servidor FastAPI que expoe:
  - "/"             pagina HTML com o estado atual (auto-atualiza)
  - "/api/status"   o mesmo estado em JSON, consumido pelo JavaScript da pagina
  - "/api/refresh"  forca uma verificacao imediata de todos os alvos
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from alert_agent import raise_alert
from config import WATCH_TARGETS
from monitor_agent import check_all
from state_store import load_state, log_event

app = FastAPI(title="F1 Ticket Watcher")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/status")
async def status():
    return load_state()


@app.post("/api/refresh")
async def refresh():
    log_event("Verificacao manual pedida a partir do dashboard.")
    results = await check_all(WATCH_TARGETS)
    for result in results:
        if result["changed"]:
            await raise_alert(result["name"], result["url"])
    return load_state()
