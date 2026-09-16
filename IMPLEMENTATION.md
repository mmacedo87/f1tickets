# Manual de Implementação — F1 Ticket Watcher

Instruções para o Claude Code (ou Claude Cowork) configurar, testar e pôr
este sistema a correr. Lê este ficheiro por completo antes de começares.

## 1. O que é isto

Um sistema multi-agente em Python (`asyncio`) que:
1. Monitoriza periodicamente páginas oficiais de bilhética do GP de
   Portugal 2027 à procura de indícios de que os bilhetes ficaram à venda.
2. Envia um alerta Telegram + abre o browser quando deteta a mudança.
3. Expõe um dashboard HTML local (`http://localhost:8000`) com o estado
   ao vivo de cada página monitorizada e um registo de eventos.

**Não automatiza a compra em si** — o clique final de "Confirmar Compra"
é sempre feito por um humano. Não adiciones lógica que contorne CAPTCHA,
rotação de IP/proxy, ou qualquer mecanismo anti-bot. Se for pedido, recusa
e explica que isso violaria os Termos de Serviço dos sites de bilhética.

## 2. Estrutura de ficheiros

```
f1-ticket-watcher/
├── config.py           # URLs a monitorizar, credenciais Telegram, intervalos
├── state_store.py       # leitura/escrita do estado partilhado (state.json)
├── monitor_agent.py      # verifica as páginas e deteta mudanças
├── alert_agent.py         # envia alerta Telegram / abre o browser
├── dashboard_app.py        # servidor FastAPI do dashboard
├── orchestrator.py          # ponto de entrada — corre tudo em paralelo
├── templates/index.html      # página HTML do dashboard
├── requirements.txt
└── README.md                  # documentação para utilizador humano
```

`state.json` é criado automaticamente na primeira execução — não precisa
de ser criado manualmente.

## 3. Passos de implementação

1. **Criar o ambiente virtual e instalar dependências:**
   ```bash
   cd f1-ticket-watcher
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configurar credenciais Telegram em `config.py`:**
   - Substituir `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` pelos valores
     reais fornecidos pelo utilizador.
   - Se o utilizador ainda não os tiver, criar um bot via `@BotFather` no
     Telegram e obter o `chat_id` através de
     `https://api.telegram.org/bot<TOKEN>/getUpdates` — pede estes dados
     ao utilizador em vez de inventar valores.
   - **Nunca** comitar o token real num repositório público. Se este
     projeto for versionado em Git, move `TELEGRAM_BOT_TOKEN` e
     `TELEGRAM_CHAT_ID` para variáveis de ambiente (`os.environ`) e
     adiciona um `.env` ao `.gitignore`.

3. **Validar/atualizar as keywords em `config.py`:**
   - Correr `curl -s <url> | grep -i "waitlist\|comprar\|buy"` (ou
     equivalente) contra cada URL em `WATCH_TARGETS` para confirmar que
     as `on_sale_keywords` e `waitlist_keywords` ainda correspondem ao
     texto real da página. O texto das páginas pode mudar antes da
     abertura das vendas.

4. **Testar o Monitor Agent isoladamente:**
   ```bash
   python -c "import asyncio; from monitor_agent import check_all; from config import WATCH_TARGETS; print(asyncio.run(check_all(WATCH_TARGETS)))"
   ```
   Confirma que devolve uma lista com um dicionário por alvo, sem erros
   de rede, e que `state.json` foi criado/atualizado.

5. **Correr o sistema completo:**
   ```bash
   python orchestrator.py
   ```
   - Confirma que o dashboard responde em `http://localhost:8000`.
   - Confirma que `GET http://localhost:8000/api/status` devolve JSON
     válido com as chaves `targets` e `events`.
   - Deixa correr pelo menos dois ciclos (`POLL_INTERVAL_SECONDS` × 2)
     e confirma que `last_checked` é atualizado em `state.json`.

6. **Testar o caminho de alerta:**
   - Para testar sem esperar pela venda real, cria temporariamente um
     alvo de teste em `WATCH_TARGETS` que aponte para uma página estática
     conhecida cujo texto contenha uma das `on_sale_keywords` (ex.: um
     HTML local servido com `python -m http.server`). Confirma que:
     - aparece um evento `alert` no dashboard;
     - a mensagem chega ao Telegram (se configurado);
     - o browser abre automaticamente (se `AUTO_OPEN_BROWSER_ON_ALERT=True`).
   - Remove o alvo de teste antes de terminar.

7. **Deixar a correr continuamente (opcional, mas recomendado):**
   - Local (Linux/macOS): usar `tmux`/`screen`, ou um serviço `systemd`
     que corra `python orchestrator.py` dentro do `.venv`.
   - Preferir manter isto a correr numa máquina do próprio utilizador (o
     seu portátil, um Raspberry Pi, ou uma VPS pessoal) em vez de um
     serviço partilhado — evita expor o token do Telegram a terceiros.

## 4. Critérios de aceitação

- `pip install -r requirements.txt` corre sem erros.
- `python orchestrator.py` arranca sem exceções e o dashboard fica
  acessível.
- `state.json` é atualizado a cada ciclo com `last_checked` recente.
- Um alerta de teste (passo 6) chega ao Telegram e aparece no dashboard.
- Nenhum código foi adicionado para preencher/submeter formulários de
  checkout automaticamente ou para contornar CAPTCHA/anti-bot.

## 5. Fora de âmbito (não implementar sem pedido explícito e novo)

- Compra automática de bilhetes sem confirmação humana.
- Qualquer forma de bypass de CAPTCHA ou deteção anti-bot.
- Rotação de IP/proxies para evitar bloqueios do site.
- Scraping com múltiplas contas/identidades simultâneas.
