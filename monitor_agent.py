"""
Monitor Agent.
Responsavel por verificar periodicamente cada URL em WATCH_TARGETS e
detetar quando o conteudo muda de "lista de espera" para "a venda".

Nota: usa apenas pedidos HTTP normais (httpx), tal como um browser faria
ao carregar a pagina -- os headers abaixo imitam um browser de desktop
comum para que o pedido seja tratado como qualquer visita normal (nada
de rotacao de IP, resolucao de CAPTCHA ou outro mecanismo de evasao).
Se um site bloquear o pedido mesmo assim, o agente regista o erro e
tenta novamente no proximo ciclo -- nunca insiste de forma agressiva.
"""
import hashlib

import httpx

from state_store import update_target, log_event

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
}


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def check_target(client: httpx.AsyncClient, target: dict) -> dict:
    """Verifica uma unica URL. Devolve um dicionario com o resultado."""
    name, url = target["name"], target["url"]
    try:
        resp = await client.get(url, headers=HEADERS, timeout=20, follow_redirects=True)
        body = resp.text.lower()
    except httpx.HTTPError as exc:
        log_event(f"[{name}] erro ao aceder a pagina: {exc}", level="error")
        update_target(name, status="erro", last_error=str(exc))
        return {"name": name, "url": url, "changed": False, "on_sale": False}

    content_hash = _hash(body)
    on_sale = any(kw.lower() in body for kw in target.get("on_sale_keywords", []))
    still_waitlist = any(kw.lower() in body for kw in target.get("waitlist_keywords", []))

    previous_state = update_target(name, status="a verificar")
    was_on_sale = previous_state["targets"].get(name, {}).get("on_sale", False)
    changed_state = on_sale and not was_on_sale

    update_target(
        name,
        content_hash=content_hash,
        on_sale=on_sale,
        still_waitlist=still_waitlist,
        status="A VENDA !!!" if on_sale else "em lista de espera",
        url=url,
    )

    if changed_state:
        log_event(f"[{name}] MUDANCA DETETADA -- parece estar a venda!", level="alert")

    return {"name": name, "url": url, "changed": changed_state, "on_sale": on_sale}


async def check_all(targets: list[dict]) -> list[dict]:
    async with httpx.AsyncClient() as client:
        results = []
        for target in targets:
            results.append(await check_target(client, target))
        return results
