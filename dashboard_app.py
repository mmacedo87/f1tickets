"""
Dashboard Agent (interface).
Pequeno servidor FastAPI que expoe:
  - "/"            pagina HTML com o estado atual (auto-atualiza)
  - "/api/status"  o mesmo estado em JSON, consumido pelo JavaScript da pagina
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request

from state_store import load_state

app = FastAPI(title="F1 Ticket Watcher")
templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/api/status")
async def status():
    return load_state()
