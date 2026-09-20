"""
Purchase Agent.
Fluxo semi-automatico de compra no site oficial (login por codigo OTP
enviado por email, depois selecao de bilhete ate ao carrinho). O
PAGAMENTO E SEMPRE CONFIRMADO POR UM HUMANO -- este agente para assim
que os bilhetes estao no carrinho e avisa por Telegram para o utilizador
terminar a compra manualmente.

Nunca tenta contornar CAPTCHA ou qualquer verificacao anti-bot. Se o
fluxo pedir isso a meio, para e avisa em vez de insistir.
"""
from playwright.async_api import async_playwright

from config import (
    BROWSER_CHANNEL,
    OTP_REPLY_TIMEOUT_SECONDS,
    SITE_EMAIL,
    TICKET_FALLBACK,
    TICKET_PREFERENCE,
    TICKET_QUANTITY,
)
from state_store import log_event
from telegram_client import send_message, wait_for_reply

SITE_URL = "https://portugalf1gp.com/pt"


async def _dismiss_cookie_banner(page) -> None:
    try:
        await page.get_by_text("Aceitar tudo", exact=False).first.click(timeout=5000)
    except Exception:
        pass  # banner pode nao aparecer (ex.: consentimento ja dado antes)


async def _submit_otp_code(page, code: str) -> bool:
    """Preenche o ecra "VERIFICAR E-MAIL" -- 4 caixas de um digito cada,
    mais o botao "Verificar" (fica desativado ate as 4 estarem cheias)."""
    digits = [c for c in code if c.isdigit()]
    if len(digits) != 4:
        log_event(f"purchase_agent: codigo recebido ('{code}') nao tem 4 digitos -- a ignorar.", "error")
        await send_message(f"⚠️ '{code}' não parece um código válido (preciso de 4 dígitos). Responde só com os 4 números.")
        return False

    code_inputs = page.locator("text=VERIFICAR E-MAIL").locator("..").locator("input")
    if await code_inputs.count() != 4:
        log_event("purchase_agent: nao encontrei as 4 caixas do codigo OTP na pagina.", "error")
        return False

    for i, digit in enumerate(digits):
        await code_inputs.nth(i).fill(digit)

    await page.get_by_text("Verificar", exact=True).click()
    log_event("purchase_agent: codigo OTP submetido.", "info")
    # NOTA: ainda nao confirmamos como e o ecra APOS um codigo correto
    # (fecha o modal? redireciona?) -- por agora assumimos sucesso se o
    # clique nao rebentou; a validar ao vivo.
    return True


async def _login(page) -> bool:
    """Pede o codigo de acesso por email e completa o login com o codigo
    que o utilizador colar no Telegram. Devolve True se o login terminou."""
    await page.get_by_text("Acesso para Subscritores", exact=False).first.click()
    modal_email = page.locator("text=BEM-VINDO À GRELHA").locator("..").locator("input[type=email]")
    await modal_email.fill(SITE_EMAIL)
    await page.get_by_text("Enviar código", exact=False).click()

    log_event(f"purchase_agent: codigo OTP pedido para {SITE_EMAIL}.", "info")
    await send_message(
        "🔑 O site oficial enviou um código de acesso para o teu email.\n"
        "Responde a esta mensagem com esse código (4 dígitos) para eu continuar o login."
    )
    code = await wait_for_reply(OTP_REPLY_TIMEOUT_SECONDS)
    if not code:
        log_event("purchase_agent: sem resposta ao codigo OTP a tempo -- fluxo parado.", "error")
        await send_message("⏱️ Não respondeste ao código a tempo. Login cancelado -- entra manualmente.")
        return False

    return await _submit_otp_code(page, code)


async def _select_ticket_to_cart(page) -> bool:
    """Procura TICKET_PREFERENCE na pagina; se nao existir, usa
    TICKET_FALLBACK. Seleciona a quantidade configurada e avanca ate ao
    carrinho -- nunca ate ao pagamento."""
    # TODO: a pagina de selecao de bilhetes so existe depois da venda abrir
    # -- esta funcao e escrita de forma adaptativa (procura por texto, nao
    # por seletores CSS fixos) mas precisa de validacao ao vivo nesse
    # momento. Ver README/IMPLEMENTATION para o plano de contingencia.
    log_event("purchase_agent: selecao de bilhetes ainda nao implementada.", "error")
    return False


async def run_purchase_flow() -> None:
    if not SITE_EMAIL:
        log_event("purchase_agent: SITE_EMAIL nao configurado em .env -- a parar antes de abrir o browser.", "error")
        return

    log_event("purchase_agent: a iniciar fluxo de compra no site oficial.", "alert")
    await send_message("🏁 Bilhetes à venda! A iniciar login automático no site oficial...")

    async with async_playwright() as p:
        browser = await p.chromium.launch(channel=BROWSER_CHANNEL, headless=False)
        page = await browser.new_page()
        await page.goto(SITE_URL, wait_until="load")

        await _dismiss_cookie_banner(page)

        if not await _login(page):
            await browser.close()
            return

        if not await _select_ticket_to_cart(page):
            await browser.close()
            return

        await send_message(
            f"🛒 {TICKET_QUANTITY}x bilhete no carrinho! Termina o pagamento agora "
            f"nesta janela do browser -- eu não confirmo a compra por ti."
        )
        log_event("purchase_agent: bilhetes no carrinho, a espera de confirmacao manual do pagamento.", "alert")
        # o browser fica aberto de propósito -- o humano confirma o pagamento
