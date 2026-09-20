# Fluxo de login — Site oficial (Acesso para Subscritores)

**Alvo:** `https://portugalf1gp.com/pt`
**Data da inspeção:** 2026-09-20
**Método:** Playwright (via Chrome do sistema)

## Descoberta importante

O login **não usa password**. É um fluxo de **código de acesso enviado por email (OTP)**:

1. Utilizador clica em **"ACESSO PARA SUBSCRITORES"** (canto superior direito)
2. Abre um modal **"BEM-VINDO À GRELHA"** com um único campo de email
3. Utilizador submete o email e clica **"Enviar código"**
4. O site envia um código de acesso para esse email
5. (presumido, ainda não testado) O utilizador introduz o código recebido para completar o login

Isto significa que uma automação completa de login precisa de acesso a uma caixa de correio (via IMAP, webhook, ou colagem manual do código) para ler o OTP — não chega só de Playwright.

## Passos para reproduzir com Playwright (até ao envio do código)

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)  # binarios proprios do
    page = browser.new_page()                                     # Playwright nao correm
    page.goto("https://portugalf1gp.com/pt", wait_until="load")   # neste macOS 12.7.6

    # 1. Dispensar banner de cookies (bloqueia cliques se nao for fechado)
    page.get_by_text("Aceitar tudo", exact=False).first.click(timeout=5000)

    # 2. Abrir o modal de login
    page.get_by_text("Acesso para Subscritores", exact=False).first.click()

    # 3. Preencher o email e pedir o codigo
    # (campo de email dentro do modal "BEM-VINDO A GRELHA")
    modal_email = page.locator("text=BEM-VINDO À GRELHA").locator("..").locator("input[type=email]")
    modal_email.fill("<EMAIL_AQUI>")
    page.get_by_text("Enviar código", exact=False).click()

    # 4. A partir daqui, falta capturar o campo/form que aparece para
    #    introduzir o codigo recebido por email (nao verificado ainda)
```

## Elementos identificados na página

**Botão que abre o modal:**
- Texto: `Acesso para Subscritores`
- Localização: canto superior direito da página

**Modal de login ("BEM-VINDO À GRELHA"):**
- Um único campo: `input[type=email]`
- Botão de submissão: `Enviar código`
- Botão de fecho: `×` (canto superior direito do modal)

**Outros formulários na página (waitlist geral, não é o login):**
- `first_name`, `last_name`, `email`, `country_code`, `mobile` — formulário "Seja o primeiro a saber mais"
- Checkboxes de consentimento (hospitalidade, política de privacidade)
- Botão: `Notifique-me`

Ambos os `<form>` da página têm `action="https://portugalf1gp.com/pt"` e `method="get"` — sugere que a submissão real é feita via JavaScript/fetch para uma API (`api.portugalf1gp.com`, identificado na [verificação de legitimidade](VERIFICACAO_SITE.md)), não via submit HTML tradicional. Para automação robusta convém capturar os pedidos de rede (`page.on("request"/"response")`) em vez de confiar só nos formulários HTML.

## Por completar

- [ ] Confirmar com o utilizador qual email usar para o teste real (isto envia um email real e um código de acesso genuíno)
- [ ] Capturar o ecrã/campo de introdução do código OTP após o envio
- [ ] Decidir como o código OTP será obtido para a automação: colagem manual, leitura de inbox via IMAP, ou webhook de email
- [ ] Capturar o pedido de rede exato (endpoint, payload, headers) feito pelo botão "Enviar código", para eventualmente substituir a navegação por chamadas diretas à API
- [ ] Repetir esta inspeção quando os bilhetes abrirem (21 set 2026, 10:30 GMT+1) — o fluxo pode mudar nessa altura (ex: passar a exigir login antes da compra)
