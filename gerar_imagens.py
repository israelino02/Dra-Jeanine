#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gera as imagens otimizadas do site a partir de _originais/.

    python3 gerar_imagens.py      (precisa de Pillow)

Saída em public/assets/: fotos WebP em 480 e 800 px, logo pequeno,
favicon, ícones e imagens de compartilhamento 1200x630.
"""
import os
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "_originais")
OUT = os.path.join(ROOT, "public", "assets")
DEEP = (23, 57, 59)


def webp(nome_src, nome_out, larguras=(480, 800), q=80):
    im = Image.open(os.path.join(SRC, nome_src)).convert("RGB")
    for w in larguras:
        h = round(im.height * w / im.width)
        im.resize((w, h), Image.LANCZOS).save(
            os.path.join(OUT, "%s-%d.webp" % (nome_out, w)), "WEBP", quality=q, method=6)
    print(nome_out, im.size)


def logo():
    im = Image.open(os.path.join(SRC, "logo.png")).convert("RGB")
    # recorte quadrado mais justo em volta do monograma
    w = im.width
    box = (int(w * .15), int(w * .15), int(w * .89), int(w * .89))
    m = im.crop(box)
    m.resize((96, 96), Image.LANCZOS).save(os.path.join(OUT, "logo-96.webp"), "WEBP", quality=88)
    m.resize((192, 192), Image.LANCZOS).save(os.path.join(OUT, "icon-192.png"))
    m.resize((180, 180), Image.LANCZOS).save(os.path.join(ROOT, "public", "apple-touch-icon.png"))
    m.resize((48, 48), Image.LANCZOS).save(os.path.join(ROOT, "public", "favicon.ico"), sizes=[(48, 48), (32, 32), (16, 16)])
    return m


def og(nome, titulo, foto="hero.png"):
    """Imagem de compartilhamento: verde da marca à esquerda, foto à direita."""
    W, H = 1200, 630
    base = Image.new("RGB", (W, H), DEEP)
    f = Image.open(os.path.join(SRC, foto)).convert("RGB")
    fw = 470
    fh = round(f.height * fw / f.width)
    f = f.resize((fw, fh), Image.LANCZOS).crop((0, 0, fw, H))
    base.paste(f, (W - fw, 0))
    d = ImageDraw.Draw(base)
    try:
        serif = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 56)
        small = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia.ttf", 28)
    except OSError:
        serif = small = ImageFont.load_default()
    y = 170
    for linha in titulo.split("\n"):
        d.text((70, y), linha, font=serif, fill=(248, 245, 239))
        y += 72
    d.text((70, y + 30), "Dra. Jeanine Carneiro · CRM-SP 234310", font=small, fill=(217, 191, 143))
    base.save(os.path.join(OUT, nome), "JPEG", quality=84, optimize=True)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    webp("hero.png", "hero")
    webp("sobre.png", "sobre")
    logo()
    og("og-infantil.jpg", "Avaliação de autismo\ne TDAH infantil\nno Tatuapé")
    og("og-home.jpg", "Médica, autista\ne mãe de autista")
    print("ok")
