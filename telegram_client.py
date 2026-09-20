"""
Telegram Client.
Envio e receção de mensagens via Telegram Bot API. Usado pelo alert_agent
(so envio) e pelo purchase_agent (envio + espera por uma resposta, ex.:
o codigo de acesso enviado por email, que o utilizador cola no Telegram).
"""
import time

import httpx

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
from state_store import log_event

API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


async def send_message(text: str) -> None:
    if "COLOCA_AQUI" in TELEGRAM_BOT_TOKEN:
        log_event("Telegram nao configurado -- mensagem apenas registada localmente.", "warn")
        return
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                f"{API_BASE}/sendMessage",
                json={"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"},
                timeout=10,
            )
        except httpx.HTTPError as exc:
            log_event(f"Falha ao enviar Telegram: {exc}", "error")


async def wait_for_reply(timeout_seconds: int) -> str | None:
    """Espera por uma mensagem nova do utilizador no chat configurado.

    Faz long-polling ao getUpdates ate `timeout_seconds` passarem. Devolve
    o texto da primeira mensagem recebida nesse intervalo, ou None se
    ninguem responder a tempo. So considera mensagens vindas do
    TELEGRAM_CHAT_ID configurado -- ignora tudo o resto (ex.: o bot a
    ser usado noutra conversa)."""
    if "COLOCA_AQUI" in TELEGRAM_BOT_TOKEN or "COLOCA_AQUI" in TELEGRAM_CHAT_ID:
        log_event("Telegram nao configurado -- nao e possivel esperar por resposta.", "error")
        return None

    deadline = time.monotonic() + timeout_seconds
    offset = None

    async with httpx.AsyncClient() as client:
        # marca as mensagens ja existentes como lidas, para so reagir a
        # respostas novas a partir de agora
        try:
            resp = await client.get(f"{API_BASE}/getUpdates", params={"timeout": 0}, timeout=10)
            updates = resp.json().get("result", [])
            if updates:
                offset = updates[-1]["update_id"] + 1
        except httpx.HTTPError:
            pass

        while time.monotonic() < deadline:
            remaining = max(1, int(deadline - time.monotonic()))
            poll_timeout = min(25, remaining)
            try:
                resp = await client.get(
                    f"{API_BASE}/getUpdates",
                    params={"timeout": poll_timeout, "offset": offset},
                    timeout=poll_timeout + 10,
                )
                updates = resp.json().get("result", [])
            except httpx.HTTPError as exc:
                log_event(f"Erro a consultar Telegram: {exc}", "error")
                continue

            for update in updates:
                offset = update["update_id"] + 1
                message = update.get("message") or {}
                chat_id = str(message.get("chat", {}).get("id", ""))
                text = message.get("text")
                if text and chat_id == str(TELEGRAM_CHAT_ID):
                    return text.strip()

    return None
