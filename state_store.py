"""
Armazenamento de estado partilhado entre o Monitor Agent, o Alert Agent
e o Dashboard. Usa um ficheiro JSON simples com um lock para evitar
condicoes de corrida entre escrita (orchestrator) e leitura (dashboard).
"""
import json
import threading
from datetime import datetime, timezone
from pathlib import Path

from config import STATE_FILE

_lock = threading.Lock()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def load_state() -> dict:
    path = Path(STATE_FILE)
    if not path.exists():
        return {"targets": {}, "events": []}
    with _lock:
        return json.loads(path.read_text(encoding="utf-8"))


def save_state(state: dict) -> None:
    with _lock:
        Path(STATE_FILE).write_text(
            json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
        )


def update_target(name: str, **fields) -> dict:
    state = load_state()
    target = state["targets"].get(name, {})
    target.update(fields)
    target["last_checked"] = _now()
    state["targets"][name] = target
    save_state(state)
    return state


def log_event(message: str, level: str = "info") -> None:
    state = load_state()
    state["events"].append({"time": _now(), "level": level, "message": message})
    # mantem so os ultimos 200 eventos para o ficheiro nao crescer sem limite
    state["events"] = state["events"][-200:]
    save_state(state)
