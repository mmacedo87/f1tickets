"""
Alert Agent.
Envia uma notificacao assim que o Monitor Agent deteta que os bilhetes
ficaram disponiveis. Usa a API do Telegram (simples e instantanea via
push no telemovel) e opcionalmente abre logo a pagina no browser.
"""
import webbrowser

from config import AUTO_OPEN_BROWSER_ON_ALERT
from state_store import log_event
from telegram_client import send_message


async def raise_alert(name: str, url: str) -> None:
    message = f"F1 TICKET WATCHER: {name} parece estar A VENDA! {url}"
    log_event(message, "alert")
    await send_message(message)
    if AUTO_OPEN_BROWSER_ON_ALERT:
        webbrowser.open(url)
