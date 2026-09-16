"""
Orchestrator -- o "agent loop" principal.
Coordena o Monitor Agent e o Alert Agent num ciclo continuo, e corre em
paralelo o servidor do dashboard (dashboard_app.py) para poderes acompanhar
tudo num browser em http://localhost:8000

Como correr:
    pip install -r requirements.txt
    python orchestrator.py
"""
import asyncio

import uvicorn

from config import WATCH_TARGETS, POLL_INTERVAL_SECONDS
from monitor_agent import check_all
from alert_agent import raise_alert
from state_store import log_event
from dashboard_app import app


async def agent_loop():
    log_event("Orchestrator iniciado. A monitorizar os alvos configurados...")
    while True:
        results = await check_all(WATCH_TARGETS)
        for result in results:
            if result["changed"]:
                await raise_alert(result["name"], result["url"])
        await asyncio.sleep(POLL_INTERVAL_SECONDS)


async def run_dashboard():
    server_config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_level="warning")
    server = uvicorn.Server(server_config)
    await server.serve()


async def main():
    await asyncio.gather(agent_loop(), run_dashboard())


if __name__ == "__main__":
    asyncio.run(main())
