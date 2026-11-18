# Dra. Jeanine Carneiro: site novo

Site da Dra. Jeanine Carneiro (autismo, TDAH e neurodesenvolvimento), com atendimento presencial no Tatuapé (SP) e online. CRM-SP 234310.

Planejamento: [briefing](../02%20-%20Briefing%20do%20site.md) · [estrutura](../03%20-%20Estrutura%20do%20site.md)

> **Regra de comunicação:** o paciente pode ser a criança, mas quem lê, decide e paga é **a mãe**. O "você" dos textos é sempre ela.
> **CFM:** ela não tem RQE publicado, então o site nunca usa "especialista", "psiquiatra", "neuropediatra" ou "pediatra" como título.

## Status (17/11/2026, v2)

| URL | Status |
|---|---|
| `/avaliacao-autismo-infantil/` | ✅ v2: enxuta e interativa (ICP A, recebe os anúncios) |
| `/` home | ✅ v1: escolha "meu filho / mim" |
| `/sinais-de-autismo/` · `/como-funciona/` (Protocolo) · `/avaliacao-diagnostica/` · `/dra-jeanine/` · `/consultorio/` · `/consulta-online/` · `/valores-e-duvidas/` | ✅ 7 páginas de sitelink (18/11: Protocolo oficial + Avaliação Médica Diagnóstica; nenhum valor no site) |
| `/autismo-tdah-adulto/` · `/programa-de-cuidado/` | ⏳ (enquanto isso, `ADULTO_PRONTO = False` manda o "É sobre mim" para o WhatsApp) |
| `/politica-de-privacidade/` | ⏳ (o aviso de cookies já aponta para ela) |

Os sitelinks prontos para o Google Ads estão no fim de [03 - Estrutura do site](../03%20-%20Estrutura%20do%20site.md).

**Regra de texto:** a página de anúncio só tem frases curtas. O que precisar de parágrafo vai para a página de sitelink correspondente.

**Testado** em 320, 375, 768, 1100, 1280 e 1440px, nas 8 páginas,, sem transbordo horizontal e sem erro no console.

## Estrutura

```
public/              o site publicado: HTML estático, sem build
  assets/            style.css, app.js, imagens WebP, fontes (assets/fonts)
build.py             gera as páginas, sitemap e robots (edite o conteúdo AQUI)
gerar_imagens.py     gera WebP, ícones e imagens de compartilhamento (Pillow)
_originais/          fotos e logo em resolução cheia (não sobem)
vercel.json          deploy na Vercel (mesmo padrão do site do Thales)
```

## Editar

```bash
python3 build.py
```

Trocou uma foto? Coloque-a em `_originais/` e rode antes `python3 gerar_imagens.py`.

## Pendências da cliente

Estão marcadas no próprio HTML como `<mark class="pendente">` (aparecem em amarelo) e são criadas com `P("…")` no `build.py`. Antes de publicar:

```bash
grep -c pendente public/*/index.html
```

O resultado precisa ser **0** em todas as páginas.

## Medição

- GTM `GTM-NK58M5DS` (o mesmo do site atual) com Consent Mode v2. **Tudo fica negado até a pessoa clicar em "Aceitar"**, porque é site de saúde. Anúncio personalizado fica sempre negado.
- Com "Aceitar", o GTM recebe o evento `consent_accept`. Clarity e Pixel/CAPI da Meta devem disparar nesse gatilho, **configurar no GTM**.
- Eventos na camada de dados (sem nenhum dado de saúde):
  - `whatsapp_click` com `{pagina, posicao, publico}`
  - `maps_click`
  - `faq_open`
  - `scroll_protocolo`
- **Origem no WhatsApp:** se a pessoa chega com `utm_campaign` (ou `utm_source`, `gclid`, `fbclid`), a mensagem do WhatsApp ganha `[ref: campanha]` no fim, para a equipe registrar de onde veio. Isso funciona mesmo com cookies recusados.
  - Use nos anúncios: `?utm_source=meta&utm_campaign=presencial-sinais`

## Design (resumo)

- **Cores:** verde da marca `#17393b` e dourado `#b99865`, amostradas do site atual.
  - O dourado **não serve como texto** em fundo claro (2,5:1). Para texto, use `--gold-ink #7d5f2c` (5,4:1).
- **Tipografia:** Playfair Display **500** nos títulos (pedido de 17/11: letras mais delicadas; o texto usa peso 400) (combina com o monograma JC) e **Atkinson Hyperlegible Next** no texto.
  - A Atkinson foi desenhada para máxima legibilidade, o que conversa com o público.
  - Ela corta o zero (Ø) de propósito, para não confundir com a letra O.
- **Movimento:** só a entrada suave das seções, desligada com `prefers-reduced-motion`.
  - Sem carrossel, sem pop-up e sem autoplay.
- **Celular:** o título e o botão aparecem na primeira tela.
- **Botão flutuante de WhatsApp** no canto inferior direito, em todas as páginas e tamanhos de tela. No celular ele é um círculo; no computador mostra "Agendar pelo WhatsApp". Sobe enquanto o aviso de cookies está aberto.
- **Fim de todas as páginas:** CTA + bloco de contato (endereço, WhatsApp, Instagram, horário e "Ver rota no Maps") com o mapa ao lado, como no site do Thales.
  - O mapa do Google só carrega com o clique em "Mostrar mapa" ou depois de a pessoa aceitar os cookies (LGPD: o iframe grava cookies do Google).
  - O horário (seg–sex 8h–16h) foi tirado do Perfil da Empresa no Google em 17/11/2026; está em `HORARIOS` no `build.py`.

## Prévia local

O servidor de prévia não lê a pasta Documents (permissão do macOS). Então a prévia usa uma cópia no scratchpad da sessão (`site-jeanine-scratch` no `.claude/launch.json` da pasta de clientes).

## Publicação

- **No ar (provisório):** https://dra-jeanine.vercel.app (Vercel, projeto `dra-jeanine`, conta israelino02-6552). Existe só esse projeto: um duplicado criado sem querer (`dra-jeanine-u6uq`) foi apagado em 17/11.
- **Repositório:** https://github.com/israelino02/Dra-Jeanine (público, branch `main`)
- **Atualizar:** `python3 build.py` → commit → `git push origin main`. A Vercel publica sozinha em segundos.
- **Fora do Google** enquanto estiver no endereço provisório: `INDEXAR = False` no `build.py` gera `noindex` e `robots.txt` com `Disallow`.
- **Para ir para o domínio:**
  1. Adicionar `drajeaninecarneiro.com.br` no projeto da Vercel (Settings → Domains).
  2. Trocar o DNS. Hoje ele aponta para o site antigo, hospedado pelo ChatGPT atrás da Cloudflare.
  3. Mudar para `INDEXAR = True`, rodar o build e fazer push.
  4. Só fazer isso depois de zerar as pendências em amarelo.
