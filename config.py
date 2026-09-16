"""
Configuracao do F1 Ticket Watcher.
Ajusta os valores abaixo antes de correr o sistema.
"""
import os
from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

load_dotenv()

# URLs oficiais a monitorizar (adiciona/remove conforme necessario)
WATCH_TARGETS = [
    {
        "name": "F1 Ticketing - Portugal Waitlist",
        "url": "https://ticketing.formula1.com/tickets/en/portugal/general-admission-f1-portimao-waitlist",
        # Palavras que indicam que os bilhetes JA estao a venda
        "on_sale_keywords": ["buy tickets", "add to cart", "select seats", "comprar bilhete"],
        # Palavras que indicam que ainda estamos em lista de espera
        "waitlist_keywords": ["waitlist", "join the waitlist", "notify me"],
    },
    {
        "name": "Autodromo do Algarve - Subscricao",
        "url": "https://f1.autodromodoalgarve.com/pt-pt/",
        "on_sale_keywords": ["comprar bilhetes", "comprar ja", "adicionar ao carrinho"],
        "waitlist_keywords": ["registar", "subscrever", "nao existem bilhetes a venda"],
    },
]

# Fuso horario usado para decidir o ritmo de verificacao abaixo.
TIMEZONE = ZoneInfo("Europe/Lisbon")

# Dia em que se espera que os bilhetes fiquem a venda.
SALE_DATE = date(2026, 9, 21)

# Ritmo de verificacao, consoante a proximidade do dia de abertura da
# bilheteira (SALE_DATE). Ajusta com bom senso -- pedidos demasiado
# frequentes podem levar a que o IP seja bloqueado.
#   - Ate ao dia anterior a SALE_DATE (exclusive): 2x/dia
#   - Nesse dia, das 00h as 18h: 1x/hora
#   - Nesse dia, das 18h as 23h: 4x/hora (a cada 15 min)
#   - Nesse dia, a partir das 23h (e dai em diante): a cada 5 segundos
TWICE_A_DAY_SECONDS = 12 * 3600
HOURLY_SECONDS = 3600
FOUR_TIMES_AN_HOUR_SECONDS = 15 * 60
RAPID_SECONDS = 5


def get_poll_interval_seconds(now: datetime | None = None) -> int:
    """Devolve o intervalo (em segundos) ate a proxima verificacao."""
    now = now or datetime.now(TIMEZONE)
    eve_of_sale = SALE_DATE - timedelta(days=1)

    if now.date() < eve_of_sale:
        return TWICE_A_DAY_SECONDS
    if now.date() == eve_of_sale:
        if now.time() < time(18, 0):
            return HOURLY_SECONDS
        if now.time() < time(23, 0):
            return FOUR_TIMES_AN_HOUR_SECONDS
        return RAPID_SECONDS
    # a partir do dia da venda, mantem o ritmo mais agressivo
    return RAPID_SECONDS

# --- Telegram (agente de alerta) ---
# Cria um bot com o @BotFather no Telegram e obtem o token.
# Para obter o teu chat_id, envia uma mensagem ao bot e visita:
# https://api.telegram.org/bot<TOKEN>/getUpdates
# Os valores reais NUNCA vao para o codigo -- define-os num ficheiro
# ".env" (ver ".env.example") que fica fora do controlo de versao.
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "COLOCA_AQUI_O_TEU_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "COLOCA_AQUI_O_TEU_CHAT_ID")

# Ficheiro onde o estado partilhado e guardado (lido pelo dashboard)
STATE_FILE = "state.json"

# Se True, abre automaticamente o browser na pagina assim que deteta a mudanca
AUTO_OPEN_BROWSER_ON_ALERT = True
