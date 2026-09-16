# F1 Ticket Watcher — GP Portugal 2027

Sistema multi-agente em Python que monitoriza as páginas oficiais de
bilhética do GP de Portugal 2027 (Portimão, 18–20 junho) e avisa-te
assim que os bilhetes ficarem disponíveis, com um dashboard HTML ao
vivo para acompanhares tudo.

## Arquitetura

- **`monitor_agent.py`** — verifica periodicamente as páginas oficiais
  configuradas em `config.py`, à procura de palavras-chave que indicam
  mudança de "lista de espera" para "à venda".
- **`alert_agent.py`** — envia uma mensagem Telegram assim que uma
  mudança é detetada, e (opcional) abre a página automaticamente no
  browser.
- **`state_store.py`** — guarda o estado partilhado (`state.json`) lido
  por todos os agentes e pelo dashboard.
- **`dashboard_app.py`** + **`templates/index.html`** — servidor
  FastAPI que serve o dashboard em `http://localhost:8000`, mostrando
  o estado de cada alvo e o registo de eventos em tempo real.
- **`orchestrator.py`** — o "agent loop" principal: corre o monitor em
  ciclo contínuo e o dashboard em paralelo (`asyncio`).

## Ritmo de verificação

O intervalo entre verificações não é fixo — aproxima-se de `SALE_DATE`
(21 de setembro de 2026, em `config.py`, hora de Lisboa) através de
`get_poll_interval_seconds()`:

| Quando | Ritmo |
|---|---|
| Até à véspera de `SALE_DATE` (exclusive) | 2x por dia |
| Nesse dia (véspera), 00h–18h | 1x por hora |
| Nesse dia, 18h–23h | 4x por hora (a cada 15 min) |
| Nesse dia, a partir das 23h (e dias seguintes) | a cada 5 segundos |

Cada vez que o ritmo muda, fica registado no dashboard (secção de
eventos). Para ajustar as datas/horas ou os próprios intervalos, edita
as constantes em `config.py`.

## Instalação

```bash
cd f1-ticket-watcher
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Configurar o alerta Telegram

1. Fala com **@BotFather** no Telegram e cria um bot novo (`/newbot`).
   Vais receber um **token**.
2. Envia qualquer mensagem ao teu bot novo.
3. Visita `https://api.telegram.org/bot<TOKEN>/getUpdates` no browser
   para obteres o teu `chat_id`.
4. Copia `.env.example` para `.env` e preenche `TELEGRAM_BOT_TOKEN` e
   `TELEGRAM_CHAT_ID` com os valores reais. O ficheiro `.env` nunca é
   commitado (está no `.gitignore`).

Se não configurares o Telegram, os alertas continuam a aparecer no
dashboard e nos logs — só não recebes a notificação push.

## Correr

```bash
python orchestrator.py
```

Abre `http://localhost:8000` para veres o dashboard ao vivo.

Para deixar a correr 24/7 antes do dia 21 de setembro, o mais simples
é meter isto numa VPS pequena (ou num Raspberry Pi em casa) com
`systemd` ou `tmux`/`screen`, ou usar `nohup python orchestrator.py &`.

## Avisos importantes

- **Isto não compra bilhetes automaticamente.** O clique final de
  "Confirmar Compra" fica sempre contigo. A maior parte dos sites de
  bilhética (incluindo os da F1) proíbe bots de compra automática nos
  Termos de Serviço, e usa CAPTCHA/rate-limiting para o impedir —
  contornar isso pode violar os ToS e, nalguns países, legislação
  específica anti-bot de bilhética.
- **Regista-te já na waitlist oficial** em paralelo (
  `ticketing.formula1.com` e `f1.autodromodoalgarve.com`) — é o passo
  que mais aumenta as tuas hipóteses reais, porque os registados
  costumam ser avisados primeiro ou ter acesso a pré-venda.
- **O ritmo de verificação acelera sozinho perto da data de venda**
  (ver secção "Ritmo de verificação" acima) — ajusta com bom senso,
  pedidos demasiado frequentes (como o de 5 em 5 segundos, já perto da
  hora) podem levar a que o teu IP seja bloqueado.
- As palavras-chave em `config.py` são um ponto de partida — inspeciona
  o HTML real das páginas (`Ctrl+U` ou DevTools) mais perto da data e
  ajusta conforme o texto que a página realmente mostra quando os
  bilhetes abrem.
