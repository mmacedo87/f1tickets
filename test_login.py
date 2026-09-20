"""
Teste manual, isolado, do fluxo de login (email + codigo OTP por
Telegram). Nao toca no resto do sistema (orchestrator, monitor, etc.).

Corre com:
    python test_login.py
"""
import asyncio

from playwright.async_api import async_playwright

from config import BROWSER_CHANNEL, SITE_EMAIL
from purchase_agent import SITE_URL, _dismiss_cookie_banner, _login


async def main():
    if not SITE_EMAIL:
        print("SITE_EMAIL nao esta definido no .env -- para.")
        return

    print(f"A abrir {SITE_URL} com o browser '{BROWSER_CHANNEL}'...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel=BROWSER_CHANNEL, headless=False)
        page = await browser.new_page()
        await page.goto(SITE_URL, wait_until="load")

        await _dismiss_cookie_banner(page)

        print(f"A pedir codigo para {SITE_EMAIL} e a avisar por Telegram...")
        ok = await _login(page)
        print("LOGIN OK" if ok else "LOGIN FALHOU -- ve os eventos no dashboard ou a janela do browser")

        print("Janela do browser fica aberta 60s para poderes ver o resultado...")
        await asyncio.sleep(60)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
