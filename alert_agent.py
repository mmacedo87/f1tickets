"""
Alert Agent.
Envia uma notificacao assim que o Monitor Agent deteta que os bilhetes
ficaram disponiveis. Usa a API do Telegram (simples e instantanea via
push no telemovel) e opcionalmente abre logo a pagina no browser.
"""
import webbrowser

import httpx

from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, AUTO_OPEN_BROWSER_ON_ALERT
from state_store import log_event


async def send_telegram_message(text: str) -> None:
    if "COLOCA_AQUI" in TELEGRAM_BOT_TOKEN:
        log_event("Telegram nao configurado -- alerta apenas registado localmente.", "warn")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json=payload, timeout=10)
        except httpx.HTTPError as exc:
            log_event(f"Falha ao enviar Telegram: {exc}", "error")


async def raise_alert(name: str, url: str) -> None:
    message = f"F1 TICKET WATCHER: {name} parece estar A VENDA! {url}"
    log_event(message, "alert")
    await send_telegram_message(message)
    if AUTO_OPEN_BROWSER_ON_ALERT:
        webbrowser.open(url)
