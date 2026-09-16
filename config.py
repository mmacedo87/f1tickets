"""
Configuracao do F1 Ticket Watcher.
Ajusta os valores abaixo antes de correr o sistema.
"""
import os

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

# Intervalo entre verificacoes (segundos). Nao uses um valor demasiado baixo
# -- respeita o servidor e evita ser bloqueado por excesso de pedidos.
POLL_INTERVAL_SECONDS = 45

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
