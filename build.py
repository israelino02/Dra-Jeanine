#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gerador do site da Dra. Jeanine Carneiro.

Edite o conteúdo aqui e rode:   python3 build.py
Saída em public/, que é a pasta que sobe para o servidor.

v2 (17/11/2026): página de anúncio enxuta e interativa + 5 páginas curtas
próprias para os SITELINKS do Google Ads (cada uma com URL e conteúdo únicos).

REGRAS
- Quem lê, decide e paga é a MÃE. O "você" dos textos é sempre ela.
- Pouco texto: frase curta, bloco curto. Se precisa de parágrafo, vai para
  a página de sitelink correspondente, não para a página de anúncio.
- CFM: sem RQE publicado. Nunca "especialista", "psiquiatra",
  "neuropediatra" ou "pediatra" como título. Só "pós-graduada em…".
- Pendências da cliente: P("texto") → <mark class="pendente"> (amarelo).
  Antes de publicar: grep -c pendente public/*/index.html  → tem que dar 0.
"""
import hashlib
import json
import os
import re
from urllib.parse import quote

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "public")
SITE = "https://www.drajeaninecarneiro.com.br"   # ⚠️ confirmar domínio final
WA = "5511982696783"
GTM = "GTM-WFXXFQ7R"                              # conta suporte.israellino@gmail.com (19/11/2026). GA4 G-9NZJXQ03RK, Pixel 2244092109453222
TEL = "(11) 98269-6783"
ENDERECO = "Rua Vilela, 665 · 8º andar"
BAIRRO = "Tatuapé · São Paulo/SP"
CEP = "03314-000"
CRM = "CRM-SP 234310"
INSTAGRAM = "https://www.instagram.com/drajeanine/"
GOOGLE = "https://www.google.com/maps/search/?api=1&query=Dra.+Jeanine+Carneiro+Autismo+e+Neurodesenvolvimento+Tatuap%C3%A9"
MAPS = "https://www.google.com/maps/search/?api=1&query=Rua+Vilela+665+Tatuap%C3%A9+S%C3%A3o+Paulo"
NOTA, AVALIACOES = "4,8", "136"
INSTA_USER = "@drajeanine"
# horário do Perfil da Empresa no Google (17/11/2026): seg a sex, 8h às 16h
HORARIOS = [("Segunda a sexta", "8h às 16h"), ("Sábado e domingo", "Fechado")]
MAP_EMBED = "https://www.google.com/maps?q=" + "R.+Vilela,+665+-+Tatuap%C3%A9,+S%C3%A3o+Paulo+-+SP,+03314-000" + "&z=16&output=embed"
ATUALIZADO = "2026-11-19"
ATUALIZADO_EXTENSO = "19 de novembro de 2026"

# Enquanto o site está só no endereço provisório da Vercel (com pendências em
# amarelo), ele fica FORA do Google. Ao apontar o domínio: INDEXAR = True.
# 19/11/2026: domínio www.drajeaninecarneiro.com.br no ar → site liberado para o Google.
INDEXAR = True

# página principal (de anúncio) enquanto a home não existe
PRINCIPAL = "avaliacao-autismo-infantil/"

# páginas de sitelink: (slug, rótulo do menu)
SITELINKS = [
    ("sinais-de-autismo/", "Sinais"),
    ("como-funciona/", "Protocolo"),
    ("avaliacao-diagnostica/", "Avaliação"),
    ("dra-jeanine/", "A médica"),
    ("consultorio/", "Consultório"),
    ("valores-e-duvidas/", "Valores e dúvidas"),
]

# a página de adultos ainda não existe: enquanto False, o caminho "É sobre mim"
# leva ao WhatsApp com mensagem de adulto em vez de um link quebrado
ADULTO_PRONTO = False
WA_ADULTO = "Olá! Vim pelo site e quero agendar uma consulta para mim (adulto) com a Dra. Jeanine."
WA_GERAL = "Olá! Vim pelo site e gostaria de agendar uma consulta com a Dra. Jeanine."

WA_INFANTIL = "Olá! Vim pelo site e quero agendar a avaliação do meu filho(a) com a Dra. Jeanine."
WA_AVALIACAO = "Olá! Vim pelo site e gostaria de informações sobre o agendamento da Avaliação Médica Diagnóstica com a Dra. Jeanine Carneiro."

# links do rodapé: o menu + páginas que não cabem no menu
EXTRA_RODAPE = [("consulta-online/", "Consulta online")]


def P(txt):
    """Marca uma pendência da cliente (fica amarela na revisão)."""
    return '<mark class="pendente" title="Pendente: confirmar com a Dra. Jeanine">%s</mark>' % txt


def wa(texto):
    """WhatsApp com mensagem pré-preenchida. O app.js acrescenta a campanha (utm)."""
    return "https://wa.me/%s?text=%s" % (WA, quote(texto, safe=""))


def versao(arquivo):
    with open(os.path.join(OUT, "assets", arquivo), "rb") as f:
        return hashlib.md5(f.read()).hexdigest()[:8]


def foto(p, nome, alt, sizes, prioridade=False, w=800, h=1000, cls=""):
    srcset = ", ".join("%sassets/%s-%d.webp %dw" % (p, nome, x, x) for x in (480, 800))
    carga = 'fetchpriority="high"' if prioridade else 'loading="lazy" decoding="async"'
    c = ' class="%s"' % cls if cls else ""
    return ('<img%s src="%sassets/%s-800.webp" srcset="%s" sizes="%s" alt="%s" '
            'width="%d" height="%d" %s>' % (c, p, nome, srcset, sizes, alt, w, h, carga))


# ---------------------------------------------------------------- ícones ----
def _s(i, d):
    return '<symbol id="i-%s" viewBox="0 0 24 24"><g fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">%s</g></symbol>' % (i, d)


SPRITE = ('<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">'
          '<symbol id="i-wa" viewBox="0 0 24 24"><path fill="currentColor" d="M12.04 2C6.58 2 2.13 6.45 2.13 11.91c0 1.75.46 3.46 1.32 4.96L2 22l5.25-1.38c1.45.79 3.08 1.21 4.79 1.21 5.46 0 9.91-4.45 9.91-9.91S17.5 2 12.04 2m0 1.67c4.55 0 8.24 3.7 8.24 8.24s-3.69 8.25-8.24 8.25c-1.5 0-2.96-.4-4.24-1.16l-.3-.18-3.12.82.83-3.04-.19-.32a8.19 8.19 0 0 1-1.25-4.37c0-4.54 3.7-8.24 8.27-8.24m-3.7 4.1c-.18 0-.46.07-.7.33-.25.25-.94.92-.94 2.23 0 1.32.96 2.59 1.09 2.77.14.18 1.87 2.98 4.6 4.06 2.27.9 2.73.72 3.22.67.5-.04 1.6-.65 1.82-1.29.23-.63.23-1.18.16-1.29-.07-.11-.25-.18-.53-.32-.27-.14-1.6-.79-1.85-.88-.25-.09-.43-.14-.61.14-.18.27-.7.89-.86 1.07-.16.18-.32.2-.59.07-.27-.14-1.17-.43-2.23-1.38-.82-.73-1.38-1.63-1.54-1.9-.16-.28-.02-.43.11-.57.12-.13.32-.34.48-.52.16-.18.21-.3.32-.48.11-.18.05-.34-.02-.48-.07-.14-.6-1.47-.83-2-.18-.43-.37-.44-.53-.45h-.36Z"/></symbol>'
          '<symbol id="i-star" viewBox="0 0 24 24"><path fill="currentColor" d="M12 2.3l2.9 5.9 6.5.95-4.7 4.6 1.1 6.5-5.8-3.05-5.8 3.05 1.1-6.5-4.7-4.6 6.5-.95L12 2.3Z"/></symbol>'
          + _s("pin", '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>')
          + _s("check", '<circle cx="12" cy="12" r="9.2"/><path d="m8.2 12.3 2.6 2.6 5-5.4"/>')
          + _s("tick", '<path d="m5 12.5 4.5 4.5L19 7.5" stroke-width="3"/>')
          + _s("menu", '<path d="M4 7h16M4 12h16M4 17h16"/>')
          + _s("arrow", '<path d="M5 12h14M13 6l6 6-6 6"/>')
          + _s("compass", '<circle cx="12" cy="12" r="9.2"/><path d="m15.5 8.5-2 5-5 2 2-5 5-2Z"/>')
          + _s("doc", '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8l-5-5Z"/><path d="M14 3v5h5M9 13h6M9 17h4"/>')
          + _s("school", '<path d="m2 9 10-5 10 5-10 5L2 9Z"/><path d="M6 11v5c0 1.5 2.7 3 6 3s6-1.5 6-3v-5"/>')
          + _s("home", '<path d="M3 11 12 4l9 7"/><path d="M5 10v10h14V10"/><path d="M10 20v-5h4v5"/>')
          + _s("clock", '<circle cx="12" cy="12" r="9.2"/><path d="M12 7v5l3 2"/>')
          + _s("chat", '<path d="M21 12a8 8 0 0 1-11.6 7.1L4 20.5l1.4-4.9A8 8 0 1 1 21 12Z"/>')
          + _s("eye", '<path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12Z"/><circle cx="12" cy="12" r="3"/>')
          + _s("refresh", '<path d="M20 11a8 8 0 0 0-14.3-4.9L4 8"/><path d="M4 4v4h4"/><path d="M4 13a8 8 0 0 0 14.3 4.9L20 16"/><path d="M20 20v-4h-4"/>')
          + _s("heart", '<path d="M12 20s-7.5-4.6-9.2-9.3C1.6 7.3 4 4 7.3 4c2 0 3.6 1.1 4.7 2.7C13.1 5.1 14.7 4 16.7 4 20 4 22.4 7.3 21.2 10.7 19.5 15.4 12 20 12 20Z"/>')
          + _s("bag", '<path d="M5 8h14l-1 12H6L5 8Z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/>')
          + _s("car", '<path d="M5 16V11l2-5h10l2 5v5"/><path d="M3 16h18v3H3zM7 19v1M17 19v1"/><circle cx="7.5" cy="13.5" r=".8"/><circle cx="16.5" cy="13.5" r=".8"/>')
          + _s("insta", '<rect x="3" y="3" width="18" height="18" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r=".6" fill="currentColor"/>')
          + _s("book", '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2V5Z"/><path d="M4 21a2 2 0 0 1 2-2h13M8 7h7M8 11h5"/>')
          + _s("video", '<rect x="3" y="6" width="13" height="12" rx="2"/><path d="m16 10 5-3v10l-5-3"/>')
          + '</svg>')


def ic(nome):
    return '<svg aria-hidden="true" focusable="false"><use href="#i-%s"/></svg>' % nome


def more(href, txt):
    return '<a class="more" href="%s">%s%s</a>' % (href, txt, ic("arrow"))


def btn_wa(pos, txt="Agendar a avaliação do meu filho", msg=WA_INFANTIL, pub="infantil"):
    return '<a class="btn btn-1" href="%s" data-wa="%s" data-publico="%s">%s%s</a>' % (wa(msg), pos, pub, ic("wa"), txt)


def stars():
    return '<div class="stars" aria-hidden="true">%s</div>' % (ic("star") * 5)


# ------------------------------------------------------- partes comuns ------
def head(p, title, desc, canon, og_img, extra=""):
    ROBOTS = "index,follow,max-image-preview:large" if INDEXAR else "noindex,nofollow"
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="{ROBOTS}">
<meta name="geo.region" content="BR-SP">
<meta name="geo.placename" content="Tatuapé, São Paulo">
<meta property="og:type" content="website">
<meta property="og:locale" content="pt_BR">
<meta property="og:site_name" content="Dra. Jeanine Carneiro">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/{og_img}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#17393b">
<meta name="format-detection" content="telephone=no">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" href="{p}assets/icon-192.png" type="image/png" sizes="192x192">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preload" as="font" type="font/woff2" href="{p}assets/fonts/atkinson-latin.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="{p}assets/fonts/playfair-latin.woff2" crossorigin>
<link rel="stylesheet" href="{p}assets/style.css?v={versao('style.css')}">
<script>
document.documentElement.classList.add('js');
// Consentimento (Google Consent Mode v2) antes do GTM.
// Site de saúde: TUDO negado até a pessoa aceitar. Anúncio personalizado sempre negado.
// Com "Aceitar", o GTM recebe consent_accept: é nele que dispara o Pixel da Meta.
window.dataLayer=window.dataLayer||[];
function gtag(){{dataLayer.push(arguments);}}
(function(){{
  var c=null;try{{c=localStorage.getItem('jc_consent')}}catch(e){{}}
  var g=c==='aceito'?'granted':'denied';
  gtag('consent','default',{{ad_storage:g,analytics_storage:g,ad_user_data:g,ad_personalization:'denied',wait_for_update:500}});
  gtag('set','ads_data_redaction',true);
  gtag('set','url_passthrough',true);
  if(c==='aceito')dataLayer.push({{event:'consent_accept'}});
}})();
</script>
<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':new Date().getTime(),event:'gtm.js'}});
var f=d.getElementsByTagName(s)[0],j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;
j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);}})
(window,document,'script','dataLayer','{GTM}');</script>
{extra}
</head>
"""


def header(p, atual, msg=WA_INFANTIL, pub="infantil"):
    links = []
    for slug, rotulo in SITELINKS:
        cur = ' aria-current="page"' if slug == atual else ""
        links.append('<a href="%s%s"%s>%s</a>' % (p, slug, cur, rotulo))
    links = "\n      ".join(links)
    return f"""<body>
<noscript><iframe src="https://www.googletagmanager.com/ns.html?id={GTM}" height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
{SPRITE}
<a class="skip" href="#conteudo">Pular para o conteúdo</a>
<header class="site-header">
  <div class="wrap head-in">
    <a class="brand" href="{p}" aria-label="Dra. Jeanine Carneiro, página inicial">
      <img src="{p}assets/logo-96.webp" alt="" width="44" height="44">
      <span><b>Dra. Jeanine Carneiro</b><small>Autismo · TDAH · Neurodesenvolvimento</small></span>
    </a>
    <button class="menu-btn" type="button" aria-expanded="false" aria-controls="nav" aria-label="Abrir menu">{ic("menu")}</button>
    <nav class="nav" id="nav" aria-label="Principal">
      {links}
      {btn_wa("cabecalho", "Agendar", msg, pub)}
    </nav>
  </div>
</header>
<main id="conteudo">
"""


def proof():
    return f"""
<section class="proof" aria-label="Credenciais">
  <ul class="wrap">
    <li><a href="{GOOGLE}" target="_blank" rel="noopener" data-maps="prova">{ic("star")}<b>{NOTA}</b>&nbsp;· {AVALIACOES} avaliações no Google</a></li>
    <li><b>+3 mil</b>&nbsp;famílias atendidas</li>
    <li>{CRM}</li>
    <li>Tatuapé · Online</li>
  </ul>
</section>
"""


def stats():
    itens = "".join('<li class="reveal"><b>%s</b><span>%s</span></li>' % (n, t) for n, t in (
        ("+3 mil", "famílias atendidas"),
        ("%s★" % NOTA, "%s avaliações no Google" % AVALIACOES),
        ("1 hora", "de consulta, sem pressa"),
        ("Brasil", "presencial ou online"),
    ))
    return f"""
<section class="dark stats-band" aria-label="Números">
  <div class="wrap stats-track">
    <ul class="stats">{itens}</ul>
    <ul class="stats stats-dup" aria-hidden="true">{itens}</ul>
  </div>
</section>
"""


def page_hero(p, crumb, eyebrow, h1, lede, img=None):
    lado = ""
    if img:
        lado = foto(p, img, "Dra. Jeanine Carneiro", "(max-width: 800px) 280px, 360px", True, 800, 1200)
    return f"""
<section class="page-hero">
  <div class="wrap {'ph-grid' if img else 'narrow'}">
    <div>
      <p class="crumbs"><a href="{p}{PRINCIPAL}">Avaliação infantil</a> / {crumb}</p>
      <p class="eyebrow">{eyebrow}</p>
      <h1>{h1}</h1>
      <p class="lede">{lede}</p>
      <div class="cta-row">{btn_wa("hero")}</div>
    </div>
    {lado}
  </div>
</section>
"""


def closing(titulo="O primeiro passo pode ser hoje.",
            texto="Fale com a equipe da Dra. Jeanine e escolha o melhor horário para você e seu filho.",
            botao="Agendar a avaliação do meu filho", msg=WA_INFANTIL, pub="infantil"):
    horas = "".join("<li><span>%s</span><b>%s</b></li>" % h for h in HORARIOS)
    return f"""
<section class="sec dark closing" id="agendar">
  <div class="wrap">
    <h2>{titulo}</h2>
    <p class="lede">{texto}</p>
    <div class="cta-row">{btn_wa("final", botao, msg, pub)}</div>
    <p class="cta-note">Atendimento particular · presencial no Tatuapé ou online</p>

    <div class="visit" id="contato">
      <div>
        <p class="eyebrow">Como chegar</p>
        <h2>Consultório no Tatuapé</h2>
        <ul class="contact">
          <li><span class="ci">{ic("pin")}</span><span><small>Endereço</small><a href="{MAPS}" target="_blank" rel="noopener" data-maps="contato">{ENDERECO}<br>{BAIRRO} · {CEP}</a></span></li>
          <li><span class="ci">{ic("wa")}</span><span><small>Agendamento</small><a href="{wa(msg)}" data-wa="contato" data-publico="{pub}">WhatsApp {TEL}</a></span></li>
          <li><span class="ci">{ic("insta")}</span><span><small>Instagram</small><a href="{INSTAGRAM}" target="_blank" rel="noopener">{INSTA_USER}</a></span></li>
        </ul>
        <div class="hours">
          <h3>{ic("clock")}Horário de atendimento</h3>
          <ul>{horas}</ul>
          <p>Somente com agendamento. Consulta online em horário combinado.</p>
        </div>
        <div class="cta-row">
          <a class="btn btn-2" href="{MAPS}" target="_blank" rel="noopener" data-maps="rota">{ic("pin")}Ver rota no Maps</a>
        </div>
      </div>
      <div class="map" data-map="{MAP_EMBED}">
        <div class="map-cover">
          <div>
            <svg class="pinbig" aria-hidden="true" focusable="false"><use href="#i-pin"/></svg>
            <p>{ENDERECO} · Tatuapé</p>
            <button type="button" class="btn btn-1" data-map-load>Mostrar mapa</button>
            <small>O mapa é do Google e carrega só com o seu clique ou consentimento.</small>
          </div>
        </div>
      </div>
    </div>
  </div>
</section>
"""


def footer(p, msg=WA_INFANTIL, pub="infantil"):
    links = "\n          ".join('<li><a href="%s%s">%s</a></li>' % (p, s, r) for s, r in SITELINKS + EXTRA_RODAPE)
    return f"""</main>

<footer class="site-footer dark">
  <div class="wrap">
    <div class="foot-grid">
      <div class="foot-brand">
        <img src="{p}assets/logo-96.webp" alt="" width="52" height="52" loading="lazy">
        <p>Médica, autista e mãe atípica. Autismo, TDAH e neurodesenvolvimento para crianças, adolescentes e adultos.</p>
      </div>
      <nav aria-label="Páginas">
        <h2 class="foot-h">Avaliação infantil</h2>
        <ul>
          <li><a href="{p}">Página inicial</a></li>
          <li><a href="{p}{PRINCIPAL}">Avaliação infantil</a></li>
          {links}
        </ul>
      </nav>
      <div>
        <h2 class="foot-h">Contato</h2>
        <ul>
          <li><a href="{wa(msg)}" data-wa="rodape" data-publico="{pub}">WhatsApp {TEL}</a></li>
          <li><a href="{INSTAGRAM}" target="_blank" rel="noopener">Instagram @drajeanine</a></li>
          <li><a href="{GOOGLE}" target="_blank" rel="noopener" data-maps="rodape">Perfil no Google</a></li>
          <li><a href="{MAPS}" target="_blank" rel="noopener" data-maps="rodape">{ENDERECO}<br>{BAIRRO}</a></li>
        </ul>
      </div>
    </div>
    <div class="foot-legal">
      <p>Dra. Jeanine Carneiro · Médica · {CRM}</p>
      <p>Conteúdo educativo, que não substitui a consulta médica. Os canais de mensagem não atendem urgências: em caso de emergência, procure o pronto-socorro ou ligue 192.</p>
      <p class="foot-links"><a href="{p}politica-de-privacidade/">Política de privacidade</a><button type="button" class="link-btn" data-cookie-prefs>Preferências de privacidade</button><span>© 2026 Dra. Jeanine Carneiro</span></p>
    </div>
  </div>
</footer>

<a class="wa-fab" href="{wa(msg)}" data-wa="flutuante" data-publico="{pub}" aria-label="Agendar pelo WhatsApp">{ic("wa")}<span>Agendar pelo WhatsApp</span></a>

<div class="cookie" id="cookie" role="region" aria-label="Aviso de privacidade" hidden>
  <p>Com a sua permissão, medimos as visitas com ferramentas do Google e da Meta. Nenhuma informação de saúde é coletada. <a href="{p}politica-de-privacidade/">Saiba mais</a></p>
  <div class="cta-row">
    <button type="button" class="btn btn-1" data-consent="aceito">Aceitar</button>
    <button type="button" class="btn btn-2" data-consent="recusado">Recusar</button>
  </div>
</div>

<script src="{p}assets/app.js?v={versao('app.js')}" defer></script>
</body>
</html>
"""


# ------------------------------------------------------------- schema -------
def schema_medico():
    return '<script type="application/ld+json">%s</script>' % json.dumps({
        "@context": "https://schema.org",
        "@type": ["Physician", "MedicalClinic"],
        "name": "Dra. Jeanine Carneiro | Autismo e Neurodesenvolvimento",
        "url": SITE + "/" + PRINCIPAL,
        "image": SITE + "/assets/hero-800.webp",
        "logo": SITE + "/assets/icon-192.png",
        "telephone": "+55 11 98269-6783",
        "address": {"@type": "PostalAddress", "streetAddress": "Rua Vilela, 665, 8º andar",
                    "addressLocality": "São Paulo", "addressRegion": "SP",
                    "postalCode": CEP, "addressCountry": "BR"},
        "areaServed": ["Tatuapé", "Zona Leste de São Paulo", "Brasil (online)"],
        "sameAs": [INSTAGRAM],
        "aggregateRating": {"@type": "AggregateRating", "ratingValue": "4.8", "reviewCount": AVALIACOES},
    }, ensure_ascii=False)


def schema_faq(itens):
    limpa = lambda s: re.sub(r"<[^>]+>", "", s)
    return '<script type="application/ld+json">%s</script>' % json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q,
                        "acceptedAnswer": {"@type": "Answer", "text": limpa(a)}} for q, a in itens],
    }, ensure_ascii=False)


def schema_crumb(nome, slug):
    return '<script type="application/ld+json">%s</script>' % json.dumps({
        "@context": "https://schema.org", "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Avaliação infantil", "item": SITE + "/" + PRINCIPAL},
            {"@type": "ListItem", "position": 2, "name": nome, "item": SITE + "/" + slug}],
    }, ensure_ascii=False)


# ------------------------------------------------------------ conteúdo ------
CHIPS = [
    "A escola chamou para conversar",
    "Ele não atende quando chamo pelo nome",
    "As crises parecem birra, mas são diferentes",
    "Cada profissional fala uma coisa",
    "Me pediram um laudo e não sei por onde começar",
    "Já tem diagnóstico, mas não sei o que fazer depois",
]

IDADES = [  # (id, rótulo, faixa, sinais curtos, sinais extras para a página completa)
    ("bebes", "1 a 2 anos", "bebês",
     ["Pouco contato visual", "Não atende pelo nome", "Não aponta para mostrar", "Atraso ou perda da fala"],
     ["Pouco sorriso de volta", "Movimentos repetitivos com as mãos"]),
    ("pequenos", "3 a 5 anos", "primeira infância",
     ["Fala pouco ou repete frases", "Não brinca com outras crianças", "Crises quando a rotina muda", "Seletividade alimentar forte"],
     ["Incômodo com sons, roupas e texturas", "Anda na ponta dos pés"]),
    ("escolar", "6 a 10 anos", "idade escolar",
     ["Desatenção ou agitação na escola", "Dificuldade em fazer amizades", "Interesses muito intensos", "Exaustão e crises depois da aula"],
     ["Queixas frequentes da escola", "Dificuldade de aprendizagem"]),
    ("adolescentes", "11 a 17 anos", "adolescentes",
     ["Isolamento e dificuldade com amigos", "Desorganização com estudos e prazos", "Cansaço extremo depois de socializar", "Queda no rendimento escolar"],
     ["Ansiedade em situações sociais", "Sensibilidade a barulho e multidão"]),
]

PASSOS = [  # Protocolo Dra. Jeanine Carneiro (oficial): (ícone, quando, título, curto, completo)
    ("doc", "Antes", "Entrada essencial", "Formulário breve e documentos antes da consulta.",
     "Formulário breve e documentos anteriores organizam as informações antes da consulta."),
    ("clock", "1 hora", "Avaliação médica", "História, desenvolvimento e vida diária.",
     "História, desenvolvimento, saúde e impacto das dificuldades na vida diária, em cerca de 1 hora."),
    ("compass", "Na consulta", "Definição de rota", "O que já dá para concluir e como seguir.",
     "Clareza sobre o que pode ser concluído, o que permanece em investigação e como seguir."),
    ("heart", "Plano", "Plano individualizado", "Prioridades, encaminhamentos e medicação quando indicada.",
     "Prioridades, orientações, encaminhamentos e medicação quando indicada."),
    ("book", "Por escrito", "Documentos orientadores", "Materiais para retomar o que foi combinado.",
     "Materiais personalizados para consultar os acordos e aplicar as orientações em casa, na escola e nas terapias."),
    ("refresh", "Retorno", "Retorno e evolução", "Comparação, ajustes e Mapa de Evolução.",
     "Comparação dos resultados, ajustes no plano e Mapa de Evolução após o retorno."),
]

LEVA = [  # materiais do protocolo (conteúdo individualizado conforme o caso)
    ("book", "Orientação inicial", "PDF Cuidado Inicial", "Prioridades e pontos a trabalhar na rotina, de acordo com os combinados da consulta."),
    ("compass", "Direção do cuidado", "Mapa de Direção Pós-Consulta", "Compreensão médica, diagnóstico ou hipótese, condutas, metas e próximos passos. Em geral, enviado em 2 a 3 dias."),
    ("doc", "Quando há medicação", "Diário Medicamentoso", "Registro do uso prescrito, benefícios, efeitos e dúvidas para o retorno. Não autoriza ajustes por conta própria."),
    ("school", "No primeiro diagnóstico", "E-book Inicial", "Material educativo sobre a condição identificada, para entender o diagnóstico e o cuidado."),
]

AVALIACAO_ETAPAS = [  # Avaliação Médica Diagnóstica (oficial)
    ("chat", "Consulta", "Consulta inicial e anamnese", "Motivo da avaliação, história do desenvolvimento e de saúde e como as dificuldades afetam a rotina. Relatórios que você já tem entram desde aqui."),
    ("doc", "Depois", "Escalas e questionários", "A Dra. envia os instrumentos escolhidos para a idade e as hipóteses do caso. Família, pessoas próximas ou a escola podem contribuir."),
    ("clock", "Até 45 dias", "Você preenche e devolve", "Questionários e documentos são devolvidos em até 45 dias."),
    ("eye", "Análise", "Análise médica integrada", "A consulta, as respostas e os documentos são cruzados para ver se os sinais atendem aos critérios clínicos e se há outras explicações ou condições associadas."),
    ("refresh", "Se necessário", "Encontro complementar", "Só quando necessário: para esclarecer uma dúvida, aprofundar a história ou aplicar uma escala específica."),
    ("check", "Retorno", "Devolutiva e laudos", "A Dra. explica os resultados e os próximos passos. Você recebe o laudo da avaliação médica e, quando há diagnóstico, o laudo correspondente."),
]

FAQ = [
    ("Sai o diagnóstico já na primeira consulta?",
     "Quando existem informações suficientes, uma conclusão pode ser possível. Outros casos precisam de novos encontros, documentos ou avaliações, e o motivo é sempre explicado. O protocolo não promete diagnóstico, laudo ou medicação na primeira consulta."),
    ("Com que idade dá para avaliar?",
     "Sinais podem aparecer já no primeiro ano de vida. Crianças menores de 7 anos começam pela consulta do Protocolo. A Avaliação Médica Diagnóstica completa, com escalas e laudo, é a partir de 7 anos."),
    ("Preciso ter um diagnóstico para agendar?",
     "Não. O protocolo também atende quem está em investigação de autismo, TDAH ou outras dificuldades do neurodesenvolvimento."),
    ("Aceita convênio?",
     "Não, o atendimento é particular: é o que permite 1 hora de consulta, sem pressa. Os valores são informados pelo WhatsApp. " + P("Confirmar se emite documento para reembolso.")),
    ("A consulta online funciona?",
     "Sim, para pacientes de todo o Brasil. Quando é necessário exame ou avaliação presencial, essa necessidade é explicada. O presencial acontece no Tatuapé, em São Paulo."),
    ("Quais documentos eu recebo?",
     "Na consulta do Protocolo, documentos orientadores conforme o caso, como o Mapa de Direção Pós-Consulta. Na Avaliação Médica Diagnóstica, o laudo da avaliação médica e, quando há diagnóstico, o laudo correspondente."),
    ("Meu filho precisa ir junto?",
     P("Confirmar:") + " sim, ele participa no tempo dele. Uma parte da conversa pode ser só com você."),
    ("Quem responde no WhatsApp?",
     "A equipe da Dra. Jeanine. " + P("Confirmar: humano ou automação, horário e tempo de resposta.")),
]

FAQ_PROTOCOLO = [
    ("Preciso ter um diagnóstico para agendar?",
     "Não. O protocolo também atende quem está em investigação de autismo, TDAH ou outras dificuldades do neurodesenvolvimento."),
    ("O diagnóstico é concluído na primeira consulta?",
     "Quando existem informações suficientes, uma conclusão pode ser possível. Outros casos precisam de novos encontros, documentos ou avaliações. O que falta e o motivo das solicitações são explicados."),
    ("Todos recebem os mesmos materiais?",
     "Não. O conteúdo é individualizado: a seleção de materiais, relatórios e reuniões depende da avaliação e do momento do cuidado."),
    ("O atendimento pode ser online?",
     "Sim, para pacientes de todo o Brasil. Quando é necessário exame ou avaliação presencial, essa necessidade é explicada. O presencial acontece no Tatuapé, em São Paulo."),
    ("Como funciona o retorno?",
     "A evolução é comparada com o plano anterior e as prioridades são ajustadas. Depois do retorno, você recebe o Mapa de Evolução Pós-Consulta. O prazo é definido na consulta."),
]

FAQ_AVALIACAO = [
    ("A partir de que idade é a avaliação?",
     "A partir de 7 anos: crianças, adolescentes e adultos. Para crianças menores, a investigação começa pela consulta do Protocolo."),
    ("Já tenho avaliação psicológica, relatório escolar ou laudo anterior. Posso levar?",
     "Sim. Esses documentos ajudam a entender a história e a interpretar os achados atuais."),
    ("Todo paciente precisa de um encontro antes da devolutiva?",
     "Não. O encontro complementar é agendado quando existe uma dúvida clínica a esclarecer ou quando é preciso aplicar um instrumento específico."),
    ("Quais documentos vou receber?",
     "O laudo da avaliação médica. Quando a avaliação estabelece um diagnóstico, também o laudo médico correspondente."),
    ("Quanto custa?",
     "Os valores e as formas de pagamento são informados pelo WhatsApp. Se você já fez a consulta inicial e decidir seguir com a avaliação, o valor pago pela consulta é abatido."),
]


# ---------------------------------------------------------- componentes -----
def sec_chips(eyebrow="Toque no que você tem vivido", titulo="Alguma dessas frases é sua?"):
    chips = "\n".join('<button type="button" class="chip" aria-pressed="false"><i>%s</i>%s</button>' % (ic("tick"), c) for c in CHIPS)
    return f"""
<section class="sec" id="voce">
  <div class="wrap">
    <div class="head center">
      <p class="eyebrow">{eyebrow}</p>
      <h2>{titulo}</h2>
    </div>
    <div class="chips" data-chips role="group" aria-label="Situações">
      {chips}
    </div>
    <div class="chips-out" data-chips-out data-n="0">
      <p aria-live="polite" data-chips-msg>Toque nas frases que fazem parte da sua rotina.</p>
      {btn_wa("frases", "Quero conversar com a Dra.")}
    </div>
  </div>
</section>
"""


def sec_idades(completo=False):
    ids = IDADES if completo else IDADES[:3]
    tabs = "\n".join('<button type="button" role="tab" class="tab" id="tab-%s" aria-controls="painel-%s" aria-selected="%s">%s<small>%s</small></button>'
                     % (i, i, "true" if n == 0 else "false", r, f) for n, (i, r, f, _, _) in enumerate(ids))
    paineis = []
    for i, r, f, curtos, extras in ids:
        sinais = curtos + (extras if completo else [])
        lis = "".join("<li>%s%s</li>" % (ic("eye"), s) for s in sinais)
        paineis.append('<div class="tabpanel" role="tabpanel" id="painel-%s" aria-labelledby="tab-%s"><h3>%s</h3><ul class="signs">%s</ul></div>' % (i, i, r, lis))
    paineis = "\n".join(paineis)
    mais = "" if completo else '<div class="more-row">%s</div>' % more("/sinais-de-autismo/", "Ver todos os sinais, até a adolescência")
    return f"""
<section class="sec sec-alt" id="sinais">
  <div class="wrap center">
    <div class="head">
      <p class="eyebrow">Sinais de atenção</p>
      <h2>Escolha a idade do seu filho</h2>
    </div>
    <div class="tabs" data-tabs>
      <div class="tablist {'t4' if completo else ''}" role="tablist" aria-label="Faixa de idade">{tabs}</div>
      {paineis}
    </div>
    <p class="note">Sinais são motivo para avaliar, não um diagnóstico.</p>
    {mais}
  </div>
</section>
"""


def sec_passos(completo=False, dark=False):
    cards = "\n".join('<li class="card reveal"><div class="ico">%s</div><span class="when">%s</span><h3>%s</h3><p>%s</p></li>'
                      % (ic(i), q, t, (longo if completo else curto)) for i, q, t, curto, longo in PASSOS)
    mais = "" if completo else '<div class="more-row">%s</div>' % more("/como-funciona/", "Conhecer o protocolo completo")
    return f"""
<section class="sec{' dark' if dark else ''}" id="como-funciona">
  <div class="wrap">
    <div class="head">
      <p class="eyebrow">Protocolo Dra. Jeanine Carneiro</p>
      <h2>Uma trilha. <em>Seis etapas de cuidado.</em></h2>
      <p class="lede">Da dúvida diagnóstica ao plano de cuidado, com orientações que você pode retomar depois da consulta.</p>
    </div>
    <ol class="cards c6" data-track="protocolo">
      {cards}
    </ol>
    {mais}
  </div>
</section>
"""


def sec_protocolo(completo=False, materiais=True, wa_msg=WA_INFANTIL, pub="infantil"):
    """Protocolo em destaque: seção escura, título de marca e trilha de 6 etapas
    ligadas por uma linha dourada (horizontal no computador, vertical no celular)."""
    passos = "\n".join(
        '<li class="trail-step reveal"><span class="trail-dot">%d</span><div><span class="when">%s</span><h3>%s</h3><p>%s</p></div></li>'
        % (n + 1, q, t, (longo if completo else curto)) for n, (i, q, t, curto, longo) in enumerate(PASSOS))
    selos = ""
    if materiais:
        selos = """
    <div class="proto-docs reveal">
      <p>Você sai com orientações por escrito:</p>
      <ul>
        <li>%sPDF Cuidado Inicial</li>
        <li>%sMapa de Direção Pós-Consulta</li>
        <li>%sDiário Medicamentoso <small>quando há medicação</small></li>
        <li>%sE-book Inicial <small>no primeiro diagnóstico</small></li>
        <li>%sMapa de Evolução <small>após o retorno</small></li>
      </ul>
    </div>""" % (ic("book"), ic("compass"), ic("doc"), ic("school"), ic("refresh"))
    botoes = "" if completo else '<div class="cta-row proto-cta">%s<a class="btn btn-ghost" href="/como-funciona/">Conhecer o protocolo completo%s</a></div>' % (
        btn_wa("protocolo", "Quero começar pelo protocolo", wa_msg, pub), ic("arrow"))
    return f"""
<section class="sec dark protocol" id="protocolo">
  <div class="wrap">
    <div class="proto-head">
      <p class="proto-badge">{ic("star")}Método próprio da Dra. Jeanine</p>
      <h2>{"Uma trilha. <em>Seis etapas de cuidado.</em>" if completo else "Protocolo <em>Dra. Jeanine Carneiro</em>"}</h2>
      <p class="lede">Da dúvida diagnóstica ao plano de cuidado. Uma trilha em seis etapas, com orientações que você pode retomar depois da consulta.</p>
    </div>
    <ol class="trail" data-track="protocolo">
      {passos}
    </ol>
    {selos}
    <p class="proto-note">A condução é individualizada: o protocolo não promete diagnóstico, laudo ou medicação para todos na primeira consulta.</p>
    {botoes}
  </div>
</section>
"""


def sec_avaliacao_teaser(fundo="dark"):
    cls = {"dark": "sec dark", "claro": "sec", "alt": "sec sec-alt"}[fundo]
    return f"""
<section class="{cls}">
  <div class="wrap program{' light' if fundo != 'dark' else ''}">
    <div>
      <p class="eyebrow">A partir de 7 anos</p>
      <h2>Avaliação Médica <em>Diagnóstica</em></h2>
      <p class="lede">Investigação completa de autismo, TDAH e neurodesenvolvimento: consulta, escalas, análise integrada e devolutiva com laudo.</p>
    </div>
    <ul class="ticks">
      <li>{ic("check")}<span>Mesma médica do início à devolutiva</span></li>
      <li>{ic("check")}<span>Escalas e questionários para cada caso</span></li>
      <li>{ic("check")}<span>Relatórios que você já tem são aproveitados</span></li>
      <li>{ic("check")}<span>Laudo entregue na devolutiva</span></li>
    </ul>
    <p class="note-dark">Seu filho tem menos de 7 anos? A investigação começa pela consulta do Protocolo.</p>
    <div class="cta-row"><a class="btn btn-1" href="/avaliacao-diagnostica/">Conhecer a avaliação{ic("arrow")}</a></div>
  </div>
</section>
"""


def sec_leva():
    cards = "\n".join('<li class="card reveal"><div class="ico">%s</div><span class="when">%s</span><h3>%s</h3><p>%s</p></li>' % (ic(i), q, t, d) for i, q, t, d in LEVA)
    return f"""
<section class="sec dark">
  <div class="wrap">
    <div class="head">
      <p class="eyebrow">Seu cuidado, também por escrito</p>
      <h2>Orientações que continuam <em>depois da consulta</em></h2>
      <p class="lede">Cada material tem uma finalidade, e o conteúdo é escolhido conforme o caso. Depois do retorno, você recebe o Mapa de Evolução.</p>
    </div>
    <ul class="cards no-num">{cards}</ul>
    <p class="note-dark">Os documentos ajudam a retomar os combinados, sem depender só da memória. Medidas urgentes não esperam o envio dos PDFs.</p>
  </div>
</section>
"""


def sec_frase(p):
    return f"""
<section class="sec dark quote-band">
  <div class="wrap">
    <p class="big-quote reveal"><span class="l1">Você não está exagerando.</span> <span>Você está prestando atenção.</span></p>
    <p class="lede">A Dra. Jeanine é médica, autista, tem TDAH e é mãe de um menino autista. Ela já esteve do seu lado da mesa.</p>
    <div class="sign">
      <img src="{p}assets/sobre-480.webp" alt="" width="54" height="54" loading="lazy">
      <span><b>Dra. Jeanine Carneiro</b>Médica · {CRM}</span>
    </div>
  </div>
</section>
"""


def sec_medica(p, titulo="Quem é a Dra. Jeanine Carneiro"):
    return f"""
<section class="sec sec-alt" id="a-medica">
  <div class="wrap doc-grid">
    <div class="doc-photo reveal">{foto(p, "sobre", "Dra. Jeanine Carneiro de terno branco", "(max-width: 860px) 340px, 420px", False, 800, 1200)}</div>
    <div>
      <p class="eyebrow">Sobre a médica</p>
      <h2>{titulo}</h2>
      <p class="lede">Médica, autista, com TDAH e mãe do Miguel, um menino autista. Ela conhece o autismo e o TDAH dos dois lados da mesa, e é isso que muda a consulta.</p>
      <ul class="creds">
        <li>{ic("check")}<span>+3 mil famílias neurodivergentes atendidas</span></li>
        <li>{ic("check")}<span>Pós-graduada em Psiquiatria, Pediatria e Medicina de Família</span></li>
        <li>{ic("check")}<span>Certificação em autismo (formação Dr. Thiago Castro)</span></li>
        <li>{ic("check")}<span>Formação em neurodesenvolvimento e funções executivas (CBI of Miami)</span></li>
        <li>{ic("check")}<span>Criadora do Protocolo Dra. Jeanine Carneiro</span></li>
      </ul>
      <p class="crm">Médica · {CRM}</p>
      <div class="cta-row" style="margin-top:1.4rem">{more("/dra-jeanine/", "Conhecer a história da Dra. Jeanine")}</div>
    </div>
  </div>
</section>
"""


def sec_avaliacoes():
    return f"""
<section class="sec">
  <div class="wrap center">
    <div class="head">
      <p class="eyebrow">O que as famílias dizem</p>
      <h2>Nota máxima em acolhimento</h2>
    </div>
    <div class="rating">
      <span class="score">{NOTA}</span>
      <div style="text-align:left">{stars()}<p>{AVALIACOES} avaliações no Google</p></div>
    </div>
    <ul class="themes" aria-label="Temas mais citados">
      <li>Acolhimento</li><li>Escuta sem pressa</li><li>Clareza no diagnóstico</li><li>Humanidade</li>
    </ul>
    <div class="more-row"><a class="more" href="{GOOGLE}" target="_blank" rel="noopener" data-maps="avaliacoes">Ler as avaliações no Google{ic("arrow")}</a></div>
  </div>
</section>
"""


def sec_valor(completo=False):
    mais = "" if completo else more("/valores-e-duvidas/", "Valores e dúvidas")
    extra = f"<p>{P('Reembolso do plano de saúde: confirmar.')}</p>" if completo else ""
    return f"""
<section class="sec sec-alt" id="valor">
  <div class="wrap">
    <div class="invest">
      <div>
        <p class="eyebrow">Investimento</p>
        <p class="price">Atendimento particular</p>
        <ul class="ticks">
          <li>{ic("check")}<span><b>Consulta do Protocolo:</b> formulário prévio, cerca de 1 hora de consulta e documentos orientadores conforme o caso</span></li>
          <li>{ic("check")}<span><b>Avaliação Médica Diagnóstica</b> (a partir de 7 anos): consulta inicial, escalas, análise integrada, encontro complementar quando necessário e devolutiva com laudo</span></li>
          <li>{ic("check")}<span>Se você fizer a consulta inicial e seguir para a avaliação, o valor da consulta é abatido</span></li>
        </ul>
      </div>
      <aside>
        <h3>Valores e formas de pagamento</h3>
        <p>A equipe da Dra. Jeanine informa os valores e as condições pelo WhatsApp.</p>
        {extra}
        <div class="cta-row">{btn_wa("valor", "Consultar valores")}</div>
        <p style="margin:1rem 0 0">{mais}</p>
      </aside>
    </div>
  </div>
</section>
"""


def sec_faq(itens, mais=True):
    det = "\n".join('<details><summary>%s</summary><div class="ans"><p>%s</p></div></details>' % (q, a) for q, a in itens)
    link = '<div class="more-row">%s</div>' % more("/valores-e-duvidas/", "Todas as dúvidas") if mais else ""
    return f"""
<section class="sec" id="duvidas">
  <div class="wrap narrow">
    <div class="head">
      <p class="eyebrow">Dúvidas das mães</p>
      <h2>Antes de agendar</h2>
    </div>
    <div class="faq">{det}</div>
    {link}
  </div>
</section>
"""


def sec_consultorio(completo=False):
    extra = ""
    if completo:
        extra = f"""
<section class="sec sec-alt">
  <div class="wrap">
    <div class="head"><p class="eyebrow">No dia da consulta</p><h2>O que levar</h2></div>
    <ul class="cards c3 no-num">
      <li class="card reveal"><div class="ico">{ic("doc")}</div><h3>Documentos</h3><p>Relatórios da escola, das terapias e exames que você já tem.</p></li>
      <li class="card reveal"><div class="ico">{ic("heart")}</div><h3>Objeto de conforto</h3><p>Um brinquedo ou algo que acalme seu filho. {P("confirmar")}</p></li>
      <li class="card reveal"><div class="ico">{ic("bag")}</div><h3>Lanche e água</h3><p>Para a criança ficar tranquila durante a hora de consulta. {P("confirmar")}</p></li>
    </ul>
  </div>
</section>
<section class="sec">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Como chegar</p><h2>No coração do Tatuapé</h2></div>
    <ul class="cards c3 no-num">
      <li class="card reveal"><div class="ico">{ic("pin")}</div><h3>Endereço</h3><p>{ENDERECO}<br>{BAIRRO} · {CEP}</p></li>
      <li class="card reveal"><div class="ico">{ic("compass")}</div><h3>Metrô</h3><p>{P("Confirmar estação mais próxima e distância a pé.")}</p></li>
      <li class="card reveal"><div class="ico">{ic("car")}</div><h3>Carro</h3><p>{P("Confirmar estacionamento / valet.")}</p></li>
    </ul>
    <div class="more-row"><a class="btn btn-2" href="{MAPS}" target="_blank" rel="noopener" data-maps="consultorio">{ic("pin")}Abrir no Google Maps</a></div>
  </div>
</section>
"""
    mais = "" if completo else '<p style="margin-top:1.6rem">%s</p>' % more("/consultorio/", "Ver o consultório e como chegar")
    return f"""
<section class="sec">
  <div class="wrap place-grid">
    <div class="photo-slots" aria-hidden="true">
      <div class="slot">{P("Foto: espaço infantil")}</div>
      <div class="slot">{P("Foto: Dra. com mãe e criança (autorizada)")}</div>
      <div class="slot">{P("Foto: sala de espera")}</div>
    </div>
    <div>
      <p class="eyebrow">O consultório</p>
      <h2>Feito para seu filho ficar <em>à vontade</em></h2>
      <ul class="ticks">
        <li>{ic("check")}<span>No tempo dele, sem pressa</span></li>
        <li>{ic("check")}<span>Espaço para a criança explorar {P("confirmar")}</span></li>
        <li>{ic("check")}<span>{ENDERECO} · Tatuapé</span></li>
      </ul>
      {mais}
    </div>
  </div>
</section>
{extra}
"""


def montar(slug, title, desc, og, corpo, extra_schema=""):
    p = "/"
    return (head(p, title, desc, SITE + "/" + slug, og, schema_medico() + extra_schema)
            + header(p, slug) + corpo + footer(p))


# ------------------------------------------------------------- páginas ------
def page_principal():
    p = "/"
    corpo = f"""
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <span class="tag"><i></i>Médica · Autista · TDAH · Mãe atípica</span>
      <h1>Mãe, você percebeu sinais no seu filho? <em>A clareza começa aqui.</em></h1>
      <p class="lede">Avaliação de autismo e TDAH em 1 hora, sem pressa. Você sai com um plano para casa, escola e terapias.</p>
      <div class="cta-row">{btn_wa("hero")}</div>
      <ul class="pills">
        <li>{ic("clock")}1h de consulta</li>
        <li>{ic("pin")}Tatuapé ou online</li>
        <li>{ic("heart")}Crianças e adolescentes</li>
      </ul>
    </div>
    <figure class="hero-photo">
      {foto(p, "hero", "Dra. Jeanine Carneiro, médica", "(max-width: 900px) min(460px, calc(100vw - 2rem)), 480px", True, 800, 926)}
      <div class="badge b1"><b>+3 mil</b><span>famílias atendidas</span></div>
    </figure>
  </div>
</section>
{sec_chips()}
{sec_protocolo()}
{sec_avaliacao_teaser("claro")}
{sec_idades()}
{sec_frase(p)}
{sec_medica(p)}
{sec_avaliacoes()}
{sec_valor()}
{sec_faq(FAQ[:4])}
{closing()}
"""
    return montar(PRINCIPAL,
                  "Avaliação de Autismo e TDAH Infantil no Tatuapé (SP) | Dra. Jeanine Carneiro",
                  "Percebeu sinais de autismo ou TDAH no seu filho? Avaliação médica de 1 hora, sem pressa, com plano para casa, escola e terapias. Tatuapé e online.",
                  "og-infantil.jpg", corpo, schema_faq(FAQ[:4]))


def page_sinais():
    p = "/"
    corpo = page_hero(p, "Sinais por idade", "Guia rápido para mães",
                      "Sinais de autismo e TDAH <em>por idade</em>",
                      "Escolha a idade do seu filho e veja o que observar, do bebê ao adolescente.")
    corpo += proof() + sec_idades(completo=True)
    corpo += f"""
<section class="sec">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Quando procurar</p><h2>Hora de avaliar</h2></div>
    <ul class="cards c3 no-num">
      <li class="card reveal"><div class="ico">{ic("school")}</div><h3>A escola chamou</h3><p>Queixas de comportamento, atenção ou aprendizagem que se repetem.</p></li>
      <li class="card reveal"><div class="ico">{ic("eye")}</div><h3>Os sinais continuam</h3><p>Você reconhece vários sinais e eles não passam com o tempo.</p></li>
      <li class="card reveal"><div class="ico">{ic("refresh")}</div><h3>Ele perdeu algo que fazia</h3><p>Perder palavras ou habilidades é motivo para procurar avaliação logo.</p></li>
    </ul>
  </div>
</section>
"""
    corpo += sec_chips("Agora, sobre você", "O que você tem vivido?") + closing()
    return montar("sinais-de-autismo/",
                  "Sinais de Autismo e TDAH por Idade: o que Observar | Dra. Jeanine Carneiro",
                  "Sinais de autismo e TDAH em bebês, crianças e adolescentes: o que observar em cada idade e quando procurar uma avaliação médica.",
                  "og-infantil.jpg", corpo, schema_crumb("Sinais por idade", "sinais-de-autismo/"))


def page_como_funciona():
    p = "/"
    corpo = page_hero(p, "Protocolo", "Da dúvida diagnóstica ao plano de cuidado",
                      "Protocolo <em>Dra. Jeanine Carneiro</em>",
                      "Entender o que está acontecendo é o começo. Saber quais passos seguir faz parte do cuidado.")
    corpo += proof()
    corpo += f"""
<section class="sec">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Para quem é</p><h2>Uma trilha individualizada</h2></div>
    <ul class="cards c3 no-num">
      <li class="card reveal"><div class="ico">{ic("eye")}</div><span class="when">01</span><h3>Investigar e compreender</h3><p>Para quem busca entender sinais de autismo, TDAH ou outras dificuldades do neurodesenvolvimento.</p></li>
      <li class="card reveal"><div class="ico">{ic("heart")}</div><span class="when">02</span><h3>Acolher um diagnóstico</h3><p>Para quem recebeu um primeiro diagnóstico e precisa entender as necessidades de suporte.</p></li>
      <li class="card reveal"><div class="ico">{ic("refresh")}</div><span class="when">03</span><h3>Reorganizar o cuidado</h3><p>Para quem busca segunda opinião, clareza sobre tratamentos ou alinhamento com escola e terapias.</p></li>
    </ul>
  </div>
</section>
"""
    corpo += sec_protocolo(completo=True, materiais=False)
    corpo += f"""
<section class="sec">
  <div class="wrap">
    <div class="head"><p class="eyebrow">O encontro · cerca de 1 hora</p><h2>Uma consulta que considera <em>a vida como ela acontece</em></h2></div>
    <ul class="cards c3 no-num">
      <li class="card reveal"><div class="ico">{ic("home")}</div><h3>Além dos sintomas</h3><p>Desenvolvimento, comunicação, atenção, sono, alimentação, saúde emocional e o dia a dia em casa, na escola ou no trabalho.</p></li>
      <li class="card reveal"><div class="ico">{ic("compass")}</div><h3>Clareza sobre a investigação</h3><p>A conclusão depende de informações suficientes. Quando faltam relatórios, encontros ou avaliações, o motivo é explicado.</p></li>
      <li class="card reveal"><div class="ico">{ic("chat")}</div><h3>Acordos antes de encerrar</h3><p>O que fazer primeiro, o que observar e quando retornar, com a comunicação adaptada a cada paciente.</p></li>
    </ul>
    <p class="note">O protocolo não promete diagnóstico, laudo ou medicação para todos na primeira consulta. A condução é individualizada.</p>
  </div>
</section>
"""
    corpo += sec_leva()
    corpo += f"""
<section class="sec">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Médica e terapias juntas</p><h2>Quem faz o quê</h2></div>
    <div class="vs">
      <div class="reveal"><h3>As terapias tratam</h3><p>Fono, TO, psicologia e ABA no dia a dia do seu filho.</p></div>
      <div class="reveal"><h3>A médica investiga e coordena</h3><p>Diagnóstico, prescrição quando preciso e o cuidado alinhado com escola e equipe.</p></div>
    </div>
  </div>
</section>
"""
    corpo += sec_avaliacao_teaser() + sec_faq(FAQ_PROTOCOLO, mais=True) + closing()
    return montar("como-funciona/",
                  "Protocolo Dra. Jeanine Carneiro: Como Funciona a Consulta | Autismo e TDAH",
                  "Protocolo Dra. Jeanine Carneiro: entrada essencial, avaliação médica de 1 hora, definição de rota, plano individualizado, documentos orientadores e retorno.",
                  "og-infantil.jpg", corpo, schema_faq(FAQ_PROTOCOLO) + schema_crumb("Protocolo", "como-funciona/"))


def page_avaliacao():
    p = "/"
    pub = "avaliacao"
    etapas = "\n".join('<li class="card reveal"><div class="ico">%s</div><span class="when">%s</span><h3>%s</h3><p>%s</p></li>' % (ic(i), n, t, d) for i, n, t, d in AVALIACAO_ETAPAS)
    corpo = f"""
<section class="page-hero">
  <div class="wrap narrow">
    <div>
      <p class="crumbs"><a href="/{PRINCIPAL}">Avaliação infantil</a> / Avaliação diagnóstica</p>
      <p class="eyebrow">Autismo e TDAH · a partir de 7 anos</p>
      <h1>Avaliação Médica <em>Diagnóstica</em></h1>
      <p class="lede">Entenda o que está por trás dos sinais e saiba quais são os próximos passos. Da primeira consulta à devolutiva com laudo.</p>
      <div class="cta-row">{btn_wa("hero", "Quero agendar a avaliação", WA_AVALIACAO, pub)}</div>
      <p class="cta-note">Online em todo o Brasil · Presencial no Tatuapé (SP)</p>
    </div>
  </div>
</section>
{proof()}
<section class="sec">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Para quem é</p><h2>Crianças a partir de 7 anos, <em>adolescentes e adultos</em></h2></div>
    <ul class="cards c3 no-num">
      <li class="card reveal"><div class="ico">{ic("eye")}</div><h3>Suspeita de autismo ou TDAH</h3><p>Para investigar autismo, TDAH ou outras questões do neurodesenvolvimento.</p></li>
      <li class="card reveal"><div class="ico">{ic("school")}</div><h3>Dificuldades na rotina</h3><p>Comunicação, interação, atenção, aprendizagem ou adaptação, em casa, na escola ou no trabalho.</p></li>
      <li class="card reveal"><div class="ico">{ic("doc")}</div><h3>Relatórios que não se conectam</h3><p>Para quem já passou por avaliações e quer entender o que esses achados significam juntos.</p></li>
    </ul>
    <p class="note">Também esclarece se os sinais podem estar ligados a outras condições, como ansiedade, depressão, TOC ou transtornos do humor, conforme o caso.</p>
  </div>
</section>
<section class="sec sec-alt">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Por que com a médica desde o início</p><h2>Uma só médica, <em>do começo ao laudo</em></h2></div>
    <ul class="cards c3 no-num">
      <li class="card reveal"><div class="ico">{ic("compass")}</div><h3>O diagnóstico é clínico</h3><p>Conta quando os sinais começaram, onde aparecem e como afetam a rotina. Escalas organizam, a história interpreta.</p></li>
      <li class="card reveal"><div class="ico">{ic("check")}</div><h3>Laudo no próprio processo</h3><p>A mesma médica investiga, interpreta e explica. Sem precisar de outra consulta só para levar os resultados.</p></li>
      <li class="card reveal"><div class="ico">{ic("book")}</div><h3>Seus relatórios contam</h3><p>Psicologia, fono, TO e escola trazem o que não aparece na consulta, e entram na análise.</p></li>
    </ul>
  </div>
</section>
<section class="sec" id="etapas">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Passo a passo</p><h2>Como funciona <em>a avaliação</em></h2></div>
    <ol class="cards c6" data-track="protocolo">{etapas}</ol>
    <div class="more-row">{btn_wa("etapas", "Quero agendar a avaliação", WA_AVALIACAO, pub)}</div>
  </div>
</section>
<section class="sec sec-alt">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Na devolutiva</p><h2>O que a avaliação <em>ajuda a esclarecer</em></h2></div>
    <ul class="cards no-num">
      <li class="card reveal"><div class="ico">{ic("eye")}</div><h3>O que os sinais têm em comum</h3><p>Dificuldades parecidas podem ter causas diferentes, ou coexistir.</p></li>
      <li class="card reveal"><div class="ico">{ic("home")}</div><h3>O impacto no dia a dia</h3><p>Em casa, na escola, no trabalho e nas relações.</p></li>
      <li class="card reveal"><div class="ico">{ic("doc")}</div><h3>Como se chegou à conclusão</h3><p>Você entende como as informações foram interpretadas e tira dúvidas.</p></li>
      <li class="card reveal"><div class="ico">{ic("compass")}</div><h3>As prioridades de cuidado</h3><p>Acompanhamento, encaminhamentos e apoios para a rotina.</p></li>
    </ul>
  </div>
</section>
<section class="sec dark">
  <div class="wrap program">
    <div>
      <p class="eyebrow">Faz parte do Protocolo</p>
      <h2>Da dúvida diagnóstica <em>ao plano de cuidado</em></h2>
      <p class="lede">A Avaliação Médica Diagnóstica integra o Protocolo Dra. Jeanine Carneiro: começa pela escuta, avança com instrumentos escolhidos para cada caso e chega à devolutiva com orientações para a próxima etapa.</p>
    </div>
    <ul class="ticks">
      <li>{ic("check")}<span>Consulta inicial e questionários</span></li>
      <li>{ic("check")}<span>Análise clínica dos materiais</span></li>
      <li>{ic("check")}<span>Encontro complementar quando necessário</span></li>
      <li>{ic("check")}<span>Devolutiva com os documentos</span></li>
    </ul>
    <div class="cta-row"><a class="btn btn-1" href="/como-funciona/">Conhecer o protocolo{ic("arrow")}</a></div>
  </div>
</section>
{sec_faq(FAQ_AVALIACAO, mais=False)}
"""
    corpo += closing("Quer entender melhor os sinais que você observa?",
                     "Agende a consulta inicial para conversar sobre a história e começar a investigação.",
                     "Quero agendar a avaliação", WA_AVALIACAO, pub)
    return montar("avaliacao-diagnostica/",
                  "Avaliação Médica Diagnóstica de Autismo e TDAH (a partir de 7 anos) | Dra. Jeanine Carneiro",
                  "Avaliação médica de autismo, TDAH e neurodesenvolvimento a partir de 7 anos: consulta, escalas, análise integrada e devolutiva com laudo. Tatuapé (SP) e online.",
                  "og-infantil.jpg", corpo, schema_faq(FAQ_AVALIACAO) + schema_crumb("Avaliação diagnóstica", "avaliacao-diagnostica/"))


def page_medica():
    p = "/"
    corpo = page_hero(p, "A médica", "Quem vai atender o seu filho",
                      "Médica. Autista. TDAH. <em>Mãe atípica.</em>",
                      "A Dra. Jeanine une ciência e vivência: ela conhece o autismo e o TDAH por dentro.", img="sobre")
    corpo += stats()
    corpo += f"""
<section class="sec">
  <div class="wrap">
    <div class="pillars">
      <div class="pillar reveal"><b>Vivência</b><p>É autista, tem TDAH e é mãe do Miguel, um menino autista. Sabe o que é estar do seu lado da mesa.</p></div>
      <div class="pillar reveal"><b>Método</b><p>Criou o Protocolo Dra. Jeanine Carneiro: da escuta à clareza, da clareza ao cuidado.</p></div>
      <div class="pillar reveal"><b>Experiência</b><p>Mais de 3 mil famílias neurodivergentes atendidas, no Tatuapé e online.</p></div>
    </div>
  </div>
</section>
<section class="sec sec-alt">
  <div class="wrap narrow">
    <div class="head"><p class="eyebrow">Formação</p><h2>Ciência por trás do cuidado</h2></div>
    <ul class="creds">
      <li>{ic("check")}<span>Pós-graduada em Psiquiatria</span></li>
      <li>{ic("check")}<span>Pós-graduada em Pediatria</span></li>
      <li>{ic("check")}<span>Pós-graduada em Medicina de Família e Comunidade</span></li>
      <li>{ic("check")}<span>Certificação em autismo pela formação do Dr. Thiago Castro</span></li>
      <li>{ic("check")}<span>Formação complementar em neurodesenvolvimento e funções executivas pelo CBI of Miami</span></li>
      <li>{ic("check")}<span>Idealizadora do Protocolo Dra. Jeanine Carneiro</span></li>
      <li>{ic("check")}<span>Criadora do Programa de Cuidado Personalizado (6 meses)</span></li>
    </ul>
    <p class="crm">Médica · {CRM}</p>
    <p>{P("Vídeo curto (30 a 60s) da Dra. se apresentando: aumenta muito a confiança. Pedir à cliente.")}</p>
    <p>{P("Livro da Dra.: título, capa e link de venda.")}</p>
  </div>
</section>
{sec_frase(p)}
{sec_avaliacoes()}
{closing()}
"""
    return montar("dra-jeanine/",
                  "Dra. Jeanine Carneiro: Médica, Autista, TDAH e Mãe Atípica | CRM-SP 234310",
                  "Conheça a Dra. Jeanine Carneiro: médica, autista, com TDAH e mãe atípica, com mais de 3 mil famílias atendidas. Presencial no Tatuapé e online.",
                  "og-home.jpg", corpo, schema_crumb("A médica", "dra-jeanine/"))


def page_consultorio():
    p = "/"
    corpo = page_hero(p, "Consultório", "Tatuapé · São Paulo",
                      "Um consultório pensado <em>para crianças</em>",
                      "Ambiente calmo, sem pressa, para o seu filho ficar à vontade.")
    corpo += proof() + sec_consultorio(completo=True) + closing("Venha conhecer o espaço.")
    return montar("consultorio/",
                  "Consultório no Tatuapé (SP): Como Chegar | Dra. Jeanine Carneiro",
                  "Consultório da Dra. Jeanine Carneiro na Rua Vilela, 665, Tatuapé, São Paulo. Como chegar, o que levar e como é o espaço para as crianças.",
                  "og-infantil.jpg", corpo, schema_crumb("Consultório", "consultorio/"))


def page_valores():
    p = "/"
    corpo = page_hero(p, "Valores e dúvidas", "Antes de agendar",
                      "Valores e <em>dúvidas</em>",
                      "Tudo o que as mães costumam perguntar antes da primeira consulta.")
    corpo += proof() + sec_valor(completo=True) + sec_faq(FAQ, mais=False) + closing()
    return montar("valores-e-duvidas/",
                  "Valor da Consulta e Dúvidas: Avaliação de Autismo | Dra. Jeanine Carneiro",
                  "Quanto custa, o que está incluso, convênio, laudo e consulta online: as dúvidas das mães antes da avaliação de autismo e TDAH.",
                  "og-infantil.jpg", corpo, schema_faq(FAQ) + schema_crumb("Valores e dúvidas", "valores-e-duvidas/"))


def page_online():
    p = "/"
    corpo = page_hero(p, "Consulta online", "Telemedicina para todo o Brasil",
                      "A mesma escuta, <em>de onde você estiver</em>",
                      "Consulta online com a Dra. Jeanine, sem deslocamento e com seu filho no ambiente que ele conhece.")
    corpo += proof()
    corpo += f"""
<section class="sec">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Por que online</p><h2>Menos estresse, <em>mesmo cuidado</em></h2></div>
    <ul class="cards c3 no-num">
      <li class="card reveal"><div class="ico">{ic("home")}</div><h3>Seu filho em casa</h3><p>Sem trânsito, sala de espera ou ambiente novo, para quem se sobrecarrega fácil.</p></li>
      <li class="card reveal"><div class="ico">{ic("pin")}</div><h3>Qualquer cidade</h3><p>Famílias de todo o Brasil, sem precisar viajar para São Paulo.</p></li>
      <li class="card reveal"><div class="ico">{ic("clock")}</div><h3>1 hora, igual</h3><p>Mesmo tempo, mesmo protocolo e o mesmo mapa pós-consulta.</p></li>
    </ul>
  </div>
</section>
<section class="sec sec-alt">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Passo a passo</p><h2>Como funciona a consulta online</h2></div>
    <ol class="cards">
      <li class="card reveal"><div class="ico">{ic("chat")}</div><span class="when">WhatsApp</span><h3>Você agenda</h3><p>Escolhe o horário com a equipe.</p></li>
      <li class="card reveal"><div class="ico">{ic("doc")}</div><span class="when">Antes</span><h3>Envia a história</h3><p>Formulário e documentos pelo celular.</p></li>
      <li class="card reveal"><div class="ico">{ic("video")}</div><span class="when">No dia</span><h3>Entra pelo link</h3><p>Chamada de vídeo pelo celular ou computador. {P("confirmar plataforma")}</p></li>
      <li class="card reveal"><div class="ico">{ic("compass")}</div><span class="when">Depois</span><h3>Recebe o plano</h3><p>O Mapa de Direção Pós-Consulta chega, em geral, em 2 a 3 dias.</p></li>
    </ol>
  </div>
</section>
<section class="sec">
  <div class="wrap narrow">
    <div class="vs">
      <div class="reveal"><h3>Online é ótimo para</h3><p>Conversar sobre a história, orientar a família, retornos e quem mora longe.</p></div>
      <div class="reveal"><h3>Presencial quando preciso</h3><p>Se for necessário um exame ou uma avaliação presencial, a Dra. explica o motivo. O presencial é no Tatuapé.</p></div>
    </div>
  </div>
</section>
"""
    corpo += closing("Agende a consulta online.", "De qualquer lugar do Brasil, com a mesma escuta sem pressa.")
    return montar("consulta-online/",
                  "Consulta Online de Autismo e TDAH para Todo o Brasil | Dra. Jeanine Carneiro",
                  "Consulta online com a Dra. Jeanine Carneiro para crianças com suspeita de autismo ou TDAH, em qualquer cidade do Brasil. 1 hora, sem pressa.",
                  "og-infantil.jpg", corpo, schema_crumb("Consulta online", "consulta-online/"))


def page_home():
    p = "/"
    if ADULTO_PRONTO:
        mim = '<a class="route" href="/autismo-tdah-adulto/"><span><b>É sobre mim</b><small>Autismo e TDAH na vida adulta</small></span>%s</a>' % ic("arrow")
        mim_btn = '<a class="btn btn-2" href="/autismo-tdah-adulto/">Ver atendimento adulto</a>'
    else:
        mim = '<a class="route" href="%s" data-wa="home-rota-adulto" data-publico="adulto"><span><b>É sobre mim</b><small>Autismo e TDAH na vida adulta</small></span>%s</a>' % (wa(WA_ADULTO), ic("arrow"))
        mim_btn = btn_wa("home-card-adulto", "Agendar minha consulta", WA_ADULTO, "adulto")
    corpo = f"""
<section class="hero">
  <div class="wrap hero-grid">
    <div>
      <span class="tag"><i></i>Médica · Autista · TDAH · Mãe atípica</span>
      <h1>Autismo e TDAH com clareza. <em>Para o seu filho e pra você.</em></h1>
      <p class="lede">Avaliação de 1 hora, sem pressa, com um plano do que fazer depois. No Tatuapé ou online.</p>
      <p class="routes-q">Para quem é a consulta?</p>
      <div class="routes">
        <a class="route route-1" href="/{PRINCIPAL}"><span><b>É sobre o meu filho</b><small>Crianças e adolescentes</small></span>{ic("arrow")}</a>
        {mim}
      </div>
    </div>
    <figure class="hero-photo">
      {foto(p, "hero", "Dra. Jeanine Carneiro, médica", "(max-width: 900px) min(460px, calc(100vw - 2rem)), 480px", True, 800, 926)}
      <div class="badge b1"><b>+3 mil</b><span>famílias atendidas</span></div>
    </figure>
  </div>
</section>
{stats()}
<section class="sec">
  <div class="wrap">
    <div class="head center"><p class="eyebrow">Dois caminhos</p><h2>Cada história pede <em>um cuidado</em></h2></div>
    <div class="paths">
      <article class="path path-1 reveal">
        <p class="eyebrow">Para o seu filho</p>
        <h3>Sinais, escola, laudo e terapias</h3>
        <ul class="ticks">
          <li>{ic("check")}<span>Avaliação de autismo e TDAH</span></li>
          <li>{ic("check")}<span>Plano para casa, escola e terapias</span></li>
          <li>{ic("check")}<span>Do bebê ao adolescente</span></li>
        </ul>
        <div class="cta-row"><a class="btn btn-1" href="/{PRINCIPAL}">Ver avaliação infantil{ic("arrow")}</a></div>
      </article>
      <article class="path reveal">
        <p class="eyebrow">Para você</p>
        <h3>Diagnóstico na vida adulta</h3>
        <ul class="ticks">
          <li>{ic("check")}<span>TEA feminino e camuflagem</span></li>
          <li>{ic("check")}<span>TDAH adulto</span></li>
          <li>{ic("check")}<span>Online para todo o Brasil</span></li>
        </ul>
        <div class="cta-row">{mim_btn}</div>
      </article>
    </div>
  </div>
</section>
{sec_protocolo(wa_msg=WA_GERAL, pub="geral")}
{sec_avaliacao_teaser("claro")}
{sec_medica(p)}
{sec_frase(p)}
<section class="sec sec-alt">
  <div class="wrap">
    <div class="head"><p class="eyebrow">Médica e terapias juntas</p><h2>Quem faz o quê</h2></div>
    <div class="vs">
      <div class="reveal"><h3>As terapias tratam</h3><p>Fono, TO, psicologia e ABA no dia a dia.</p></div>
      <div class="reveal"><h3>A médica investiga e coordena</h3><p>Diagnóstico, prescrição quando preciso e o cuidado alinhado com escola e equipe.</p></div>
    </div>
  </div>
</section>
{sec_avaliacoes()}
<section class="sec dark">
  <div class="wrap program">
    <div>
      <p class="eyebrow">Depois do diagnóstico</p>
      <h2>Programa de Cuidado <em>de 6 meses</em></h2>
      <p class="lede">Para quem precisa de acompanhamento próximo: consultas mensais, escola e terapias alinhadas.</p>
    </div>
    <ul class="ticks">
      <li>{ic("check")}<span>Consultas mensais</span></li>
      <li>{ic("check")}<span>Reunião com escola e equipe</span></li>
      <li>{ic("check")}<span>App para acompanhar a evolução</span></li>
      <li>{ic("check")}<span>Dúvidas respondidas em até 24h</span></li>
    </ul>
    <div class="cta-row">{btn_wa("home-programa", "Quero saber do programa", "Olá! Vim pelo site e quero saber sobre o Programa de Cuidado de 6 meses da Dra. Jeanine.", "programa")}</div>
  </div>
</section>
{sec_faq(FAQ_HOME)}
{closing("O primeiro passo pode ser hoje.", "Fale com a equipe da Dra. Jeanine e escolha o melhor horário.", "Agendar pelo WhatsApp", WA_GERAL, "geral")}
"""
    html = (head(p, "Dra. Jeanine Carneiro | Autismo e TDAH · Tatuapé (SP) e Online",
                 "Médica, autista, com TDAH e mãe atípica. Avaliação de autismo e TDAH para crianças, adolescentes e adultos, presencial no Tatuapé (SP) e online para todo o Brasil.",
                 SITE + "/", "og-home.jpg", schema_medico() + schema_faq(FAQ_HOME))
            + header(p, "", WA_GERAL, "geral") + corpo + footer(p, WA_GERAL, "geral"))
    return html


FAQ_HOME = [
    ("Atende crianças e adultos?",
     "Sim. Crianças, adolescentes e adultos, com foco em autismo, TDAH e neurodesenvolvimento."),
    ("Aceita convênio?",
     "Não, o atendimento é particular: é o que permite 1 hora de consulta, sem pressa. Os valores são informados pelo WhatsApp. " + P("Confirmar reembolso.")),
    ("A consulta online funciona?",
     "Sim, para todo o Brasil, com o mesmo tempo e o mesmo protocolo da presencial."),
    ("Onde fica o consultório?",
     "Rua Vilela, 665, 8º andar, no Tatuapé, em São Paulo."),
]



CONTROLADORA = "Dra. Jeanine Carneiro Telemedicina LTDA, CNPJ 52.387.452/0001-71"

PRIVACIDADE = f"""
<h1>Política de privacidade</h1>
<p class="doc-meta">Última atualização: {ATUALIZADO_EXTENSO}</p>

<p>Esta política explica quais dados o site drajeaninecarneiro.com.br coleta, para que eles servem e como você pode recusar ou pedir a exclusão. Ela segue a Lei Geral de Proteção de Dados (Lei 13.709/2018, a LGPD).</p>

<h2>Quem é o responsável</h2>
<p>{CONTROLADORA}, com responsabilidade técnica da Dra. Jeanine Carneiro, médica, {CRM}. Consultório na {ENDERECO.replace(" · ", ", ")}, Tatuapé, São Paulo/SP, CEP {CEP}.</p>
<p>Para qualquer assunto sobre seus dados pessoais, fale conosco pelo WhatsApp <a href="{wa("Olá! Tenho uma solicitação sobre meus dados pessoais (LGPD).")}">{TEL}</a> ou por carta para o endereço acima.</p>

<h2>O que o site coleta</h2>
<p><strong>O site não tem formulário nem cadastro.</strong> Ele não pede nome, e-mail, telefone, CPF ou informações de saúde.</p>
<p><strong>Nada é medido antes da sua escolha.</strong> Ao entrar no site, aparece um aviso de privacidade. Enquanto você não clica em “Aceitar”, as ferramentas de medição não gravam cookies; o Google recebe apenas sinais técnicos sem identificador, que não permitem saber quem você é.</p>
<p><strong>Se você aceitar:</strong></p>
<ul>
  <li><strong>Google</strong> (Tag Manager, Analytics 4 e medição de conversões do Google Ads): páginas vistas, tempo na página, de onde você veio (por exemplo, uma busca ou um anúncio), tipo de aparelho e navegador, cidade aproximada e cliques nos botões do site, como WhatsApp, “Como chegar” e perguntas frequentes.</li>
  <li><strong>Meta</strong> (Pixel do Facebook e Instagram): a visita à página e o clique no botão de WhatsApp, para saber se os anúncios nessas redes trazem contatos.</li>
</ul>
<p><strong>Frases e abas interativas.</strong> As frases que você toca em “Alguma dessas frases é sua?” e as idades que você escolhe ficam só no seu navegador. Elas não são enviadas a ninguém.</p>
<p><strong>Contato pelo WhatsApp.</strong> Os botões de agendamento abrem o WhatsApp com uma mensagem já escrita. Se você chegou por um anúncio, a mensagem inclui um código curto da campanha (por exemplo, “[ref: …]”), para sabermos qual anúncio trouxe o contato. Nada é enviado se você não mandar a mensagem. Se mandar, o que você escrever é usado pela equipe da Dra. Jeanine para responder e agendar, e também passa pelo WhatsApp, que segue a política de privacidade da Meta.</p>
<p><strong>Conteúdo de terceiros.</strong> O mapa do consultório vem do Google Maps e só é carregado quando você clica em “Mostrar mapa” ou aceita o aviso. Ao carregar, o Google recebe o endereço IP e dados técnicos do navegador. As fontes de texto são do próprio site. A hospedagem (Vercel) registra o IP em seus registros de acesso.</p>

<h2>Para que usamos</h2>
<ul>
  <li>Saber quantas pessoas visitam o site e quais páginas são úteis.</li>
  <li>Saber se os anúncios no Google, no Facebook e no Instagram trazem pessoas que entram em contato, para decidir onde investir.</li>
  <li>Responder e agendar consultas pelo WhatsApp.</li>
</ul>
<p>Não usamos os dados para anúncios personalizados nem para remarketing: essa função fica sempre desligada, porque o site trata de saúde. Não vendemos dados.</p>

<h2>Bases legais</h2>
<ul>
  <li><strong>Medição de visitas e de anúncios (Google e Meta):</strong> consentimento (art. 7º, I), dado ao clicar em “Aceitar” e que pode ser revogado a qualquer momento.</li>
  <li><strong>Atendimento pelo WhatsApp:</strong> procedimentos preliminares a uma consulta, a seu pedido (art. 7º, V). Informações de saúde que você decidir contar na mensagem são tratadas para a tutela da saúde, por profissional de saúde (art. 11, II, f), sob sigilo médico.</li>
</ul>

<h2>Cookies e armazenamento no navegador</h2>
<div class="doc-table">
<table>
  <thead><tr><th>Nome</th><th>De quem</th><th>Para que</th><th>Duração</th></tr></thead>
  <tbody>
    <tr><td>_ga, _ga_*</td><td>Google Analytics (só com aceite)</td><td>Distinguir visitantes e sessões</td><td>até 2 anos</td></tr>
    <tr><td>_gcl_au, _gcl_aw</td><td>Google Ads (só com aceite)</td><td>Ligar um contato ao anúncio que o trouxe</td><td>90 dias</td></tr>
    <tr><td>_fbp</td><td>Meta (só com aceite)</td><td>Ligar um contato ao anúncio que o trouxe</td><td>90 dias</td></tr>
    <tr><td>jc_consent</td><td>Este site (armazenamento local)</td><td>Lembrar sua escolha no aviso de privacidade</td><td>até você limpar o navegador</td></tr>
    <tr><td>jc_origem</td><td>Este site (armazenamento da sessão)</td><td>Guardar o código da campanha para a mensagem do WhatsApp</td><td>até fechar a aba</td></tr>
  </tbody>
</table>
</div>
<p>Você pode mudar sua escolha quando quiser em <button type="button" class="link-btn" data-cookie-prefs>Preferências de privacidade</button>, que também está no rodapé de todas as páginas. Também é possível bloquear cookies nas configurações do navegador.</p>

<h2>Com quem os dados são compartilhados</h2>
<p>Com os fornecedores das ferramentas citadas: Google (Analytics, Ads, Tag Manager e Maps), Meta (Pixel e WhatsApp) e Vercel (hospedagem). Esses serviços guardam dados em servidores fora do Brasil, com as garantias contratuais previstas no art. 33 da LGPD.</p>

<h2>Por quanto tempo</h2>
<ul>
  <li>Google Analytics: dados detalhados de eventos por 2 meses. Os relatórios de totais, sem identificador, não expiram.</li>
  <li>Meta e Google Ads: conforme as políticas de cada empresa.</li>
  <li>Conversas no WhatsApp: pelo tempo necessário ao atendimento. Os dados da consulta, quando ela acontece, seguem as regras do prontuário médico.</li>
</ul>

<h2>Seus direitos</h2>
<p>Pela LGPD (art. 18), você pode pedir a confirmação de que tratamos seus dados, acesso, correção, anonimização ou eliminação, portabilidade, informação sobre com quem compartilhamos e a revogação do consentimento. Basta falar conosco pelo WhatsApp {TEL}; respondemos em até 15 dias. Você também pode reclamar à Autoridade Nacional de Proteção de Dados (ANPD).</p>

<h2>Crianças e adolescentes</h2>
<p>O site é informativo, é voltado a pais, mães e responsáveis e não coleta dados de cadastro. A Dra. Jeanine atende crianças, adolescentes e adultos; consultas de menores de 18 anos são agendadas e acompanhadas por um responsável. Dados de crianças e adolescentes contados no atendimento são tratados no melhor interesse deles (art. 14 da LGPD).</p>

<h2>Mudanças nesta política</h2>
<p>Se a forma de coletar dados mudar, esta página será atualizada e a data no topo mudará.</p>
"""


def page_privacidade():
    p = "/"
    corpo = f"""
<section class="doc-page">
  <div class="wrap narrow">
    <p class="crumbs"><a href="/">Início</a> / Política de privacidade</p>
    <article class="doc">
{PRIVACIDADE}
    </article>
  </div>
</section>
"""
    return (head(p, "Política de privacidade | Dra. Jeanine Carneiro",
                 "Quais dados o site da Dra. Jeanine Carneiro coleta, para que servem e como recusar ou pedir a exclusão, conforme a LGPD.",
                 SITE + "/politica-de-privacidade/", "og-home.jpg")
            + header(p, "politica-de-privacidade/", WA_GERAL, "geral") + corpo + footer(p, WA_GERAL, "geral"))


# ------------------------------------------------------------------ main ----
def escrever(caminho, conteudo):
    destino = os.path.join(OUT, caminho)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(conteudo)
    print("ok", caminho)


def main():
    paginas = {
        "": page_home(),
        PRINCIPAL: page_principal(),
        "sinais-de-autismo/": page_sinais(),
        "como-funciona/": page_como_funciona(),
        "avaliacao-diagnostica/": page_avaliacao(),
        "dra-jeanine/": page_medica(),
        "consultorio/": page_consultorio(),
        "consulta-online/": page_online(),
        "valores-e-duvidas/": page_valores(),
        "politica-de-privacidade/": page_privacidade(),
    }
    for slug, html in paginas.items():
        escrever(slug + "index.html", html)
    escrever("robots.txt", ("User-agent: *\nAllow: /\nSitemap: %s/sitemap.xml\n" % SITE) if INDEXAR else "User-agent: *\nDisallow: /\n")
    urls = "\n".join("  <url><loc>%s/%s</loc><lastmod>%s</lastmod></url>" % (SITE, s, ATUALIZADO) for s in paginas)
    escrever("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n'
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n%s\n</urlset>\n' % urls)


if __name__ == "__main__":
    main()
