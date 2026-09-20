# Verificação de legitimidade — Site oficial (primary)

**Alvo:** `https://portugalf1gp.com/pt` (marcado `primary: True` em [config.py](config.py))
**Data da verificação:** 2026-09-20
**Método:** Playwright (via Chrome do sistema) + `openssl s_client` + `whois` + `dig`

## Resultado: ✅ Site parece legítimo

## Certificado TLS
- Emitido por **Google Trust Services (WE1)**, TLS 1.3
- Válido de 23 jul a 21 out 2026 (renovação automática de 90 dias, típico de sites atrás da Cloudflare)
- Confirmado tanto pelo Chrome como por `openssl s_client` — sem avisos de certificado inválido ou auto-assinado

## Infraestrutura
- DNS resolve para `104.18.1.239` (gama Cloudflare); header `server: cloudflare` — consistente com o emissor do certificado
- Sem redirecionamentos suspeitos: `https://portugalf1gp.com/pt` responde diretamente com HTTP 200

## Conteúdo da página
- Contador para "Abertura de bilhetes" em **21 de setembro de 2026 às 10:30 GMT+1** — coincide exatamente com `SALE_DATE = date(2026, 9, 21)` já configurado neste projeto
- Rodapé: *"© 2026 Autódromo Internacional do Algarve... marcas registadas da Formula One Licensing BV, uma empresa da Formula 1"* — entidade correta (circuito real de Portimão, promotor oficial do GP)
- Formulário de waitlist (nome, apelido, email, telefone com prefixo +351) — consistente com os `waitlist_keywords` já definidos em [config.py](config.py)

## Domínios contactados pela página
Só subdomínios próprios e serviços de terceiros conhecidos/esperados — nenhum domínio de phishing, encurtador ou tracker desconhecido:
- `api.portugalf1gp.com`, `assets.portugalf1gp.com`, `geolocation.portugalf1gp.com`
- Google Analytics / Tag Manager, reCAPTCHA, Cloudflare Insights
- Armazenamento de assets: Cloudflare R2, AWS S3

## Ponto de atenção
- Domínio registado na GoDaddy em **2025-10-02** (pouco menos de 1 ano). Não é alarmante para um microsite dedicado a um evento futuro, mas é mais recente do que seria de esperar para um site "há muito estabelecido". Combinado com o resto (branding, certificado, rodapé legal, data de venda coincidente), não há indícios de phishing/spoofing.

## Notas técnicas
- Os binários próprios do Playwright (Chromium/WebKit) não são compatíveis com este macOS 12.7.6 — a verificação reutilizou o Google Chrome já instalado via `channel="chrome"`.
- `playwright` foi instalado no `.venv` do projeto apenas para esta verificação pontual; não foi adicionado ao `requirements.txt`.
