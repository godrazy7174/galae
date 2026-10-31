# -*- coding: utf-8 -*-
"""갈래 링크 미리보기 이미지(og.png, r/<노선>-<유형>.png)를 새 디자인으로 다시 그린다.

사용법: python3 tools/make_og.py
필요한 것: Pillow, node(게임 데이터 읽기), 글꼴 BlackHanSans-Regular.ttf와
GothicA1-{Medium,Bold,ExtraBold}.ttf (~/.local/share/fonts, google/fonts 저장소)
"""
import json
import os
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_DIR = os.path.expanduser("~/.local/share/fonts")
W, H = 1200, 630

WALL = (236, 238, 240)
PANEL = (255, 255, 255)
INK = (18, 24, 32)
INK2 = (76, 86, 97)
INK3 = (119, 129, 139)
SIGN = (23, 33, 44)
LED = (255, 178, 30)
TACTILE = (242, 194, 0)
TACTILE_DOT = (90, 66, 0, 72)
L1 = (0, 82, 164)
L3 = (239, 124, 28)
LINE_RGB = {1: (0, 82, 164), 2: (0, 168, 77), 3: (239, 124, 28), 4: (0, 165, 222), 5: (153, 108, 172),
            6: (205, 124, 47), 7: (116, 127, 0), 8: (230, 24, 108), 9: (187, 131, 54)}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def display(size):
    return font("BlackHanSans-Regular.ttf", size)


def gothic(weight, size):
    return font(f"GothicA1-{weight}.ttf", size)


def hexrgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def load_lines():
    js = r"""
const fs = require('fs');
const s = fs.readFileSync(process.argv[1], 'utf8');
const a = s.indexOf('const LINES = [');
let i = s.indexOf('[', a), d = 0, j = i;
for (; j < s.length; j++) { const c = s[j]; if (c === '[') d++; else if (c === ']') { d--; if (d === 0) break; } }
const L = eval(s.slice(i, j + 1));
process.stdout.write(JSON.stringify(L.map(l => ({ id: l.id, no: l.no, name: l.name, hex: l.hex, onHex: l.onHex, L: l.L, R: l.R, tiers: l.tiers }))));
"""
    out = subprocess.run(["node", "-e", js, os.path.join(ROOT, "index.html")], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


def tactile(im, y, h=16):
    d = ImageDraw.Draw(im, "RGBA")
    d.rectangle((0, y, W, y + h), fill=TACTILE)
    for x in range(7, W, 12):
        for yy in range(y + 4, y + h - 2, 8):
            d.ellipse((x - 2, yy - 2, x + 2, yy + 2), fill=TACTILE_DOT)


def panel(im, box, radius=16):
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((x0, y0 + 6, x1, y1 + 10), radius, fill=(18, 24, 32, 46))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    ImageDraw.Draw(im).rounded_rectangle(box, radius, fill=PANEL)


def pill(d, right, cy, text, f, fg=LED, bg=SIGN, pad=(14, 7), anchor_right=True):
    w = d.textlength(text, font=f)
    x1 = right if anchor_right else right + w + pad[0] * 2
    x0 = x1 - w - pad[0] * 2
    asc, desc = f.getmetrics()
    h = asc + desc
    d.rounded_rectangle((x0, cy - h / 2 - pad[1], x1, cy + h / 2 + pad[1]), 6, fill=bg)
    d.text(((x0 + x1) / 2, cy), text, font=f, fill=fg, anchor="mm")
    return x0, x1


def fit(d, text, maker, start, min_size, max_w):
    size = start
    f = maker(size)
    while d.textlength(text, font=f) > max_w and size > min_size:
        size -= 4
        f = maker(size)
    return f


def badge(d, cx, cy, r, line):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=hexrgb(line["hex"]))
    d.text((cx, cy + 1), str(line["no"]), font=gothic("ExtraBold", int(r * 1.05)), fill=hexrgb(line["onHex"]), anchor="mm")


def sign_band(im, y, h, cta):
    d = ImageDraw.Draw(im)
    d.rectangle((0, y, W, y + h), fill=SIGN)
    cy = y + h / 2
    f = display(46)
    d.text((48, cy + 2), "갈래", font=f, fill=(255, 255, 255), anchor="lm")
    w = d.textlength("갈래", font=f)
    d.text((48 + w + 14, cy + 4), "Gallae", font=gothic("Bold", 22), fill=(178, 188, 198), anchor="lm")
    d.text((W - 48, cy + 2), cta, font=gothic("ExtraBold", 30), fill=LED, anchor="rm")


def result_card(line, k, tier):
    color = LINE_RGB.get(line["no"], hexrgb(line["hex"]))
    im = Image.new("RGBA", (W, H), WALL + (255,))
    box = (40, 30, W - 40, 476)
    panel(im, box)
    # the enamel sign, with the line-colour band along its top edge
    sign = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), PANEL + (255,))
    ImageDraw.Draw(sign).rectangle((0, 0, sign.width, 14), fill=color)
    mask = Image.new("L", sign.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sign.width, sign.height), 16, fill=255)
    im.paste(sign, (box[0], box[1]), mask)
    d = ImageDraw.Draw(im, "RGBA")
    # header: badge + line name, arrival tag
    badge(d, 118, 98, 28, line)
    d.text((160, 98), f"{line['no']}호선 {line['name']}", font=gothic("ExtraBold", 34), fill=INK, anchor="lm")
    pill(d, W - 88, 98, "도착역", gothic("ExtraBold", 24))
    # the station you got off at
    name = tier[0]
    f = fit(d, name, display, 136, 84, W - 176)
    d.text((88, 256), name, font=f, fill=INK, anchor="ls")
    # one line of description
    desc = tier[1].split(". ")[0].rstrip(".") + "."
    fd = fit(d, desc, lambda s: gothic("Medium", s), 30, 22, W - 176)
    if d.textlength(desc, font=fd) > W - 176:
        while d.textlength(desc + "…", font=fd) > W - 176:
            desc = desc[:-1]
        desc += "…"
    d.text((88, 310), desc, font=fd, fill=INK2, anchor="ls")
    # the line's five result stations, you-are-here marked
    fl = gothic("ExtraBold", 26)
    ltxt, rtxt = f"← {line['L']}", f"{line['R']} →"
    wl, wr = d.textlength(ltxt, font=fl), d.textlength(rtxt, font=fl)
    y = 410
    x0, x1 = 88 + wl + 26, W - 88 - wr - 26
    d.text((88, y), ltxt, font=fl, fill=INK, anchor="lm")
    d.text((W - 88, y), rtxt, font=fl, fill=INK, anchor="rm")
    d.rounded_rectangle((x0, y - 6, x1, y + 6), 6, fill=color)
    for i in range(5):
        cx = x0 + (x1 - x0) * i / 4
        if i == k:
            continue
        d.ellipse((cx - 13, y - 13, cx + 13, y + 13), fill=PANEL, outline=color, width=6)
    cx = x0 + (x1 - x0) * k / 4
    d.ellipse((cx - 19, y - 19, cx + 19, y + 19), fill=PANEL)
    d.ellipse((cx - 15, y - 15, cx + 15, y + 15), fill=INK)
    tag = "현위치"
    ft = gothic("ExtraBold", 20)
    tw = d.textlength(tag, font=ft)
    tx0 = min(max(cx - tw / 2 - 10, 88), W - 88 - tw - 20)
    d.rounded_rectangle((tx0, y - 64, tx0 + tw + 20, y - 34), 5, fill=SIGN)
    d.text((tx0 + 10 + tw / 2, y - 49), tag, font=ft, fill=LED, anchor="mm")
    # platform edge and the sign band
    tactile(im, 494)
    sign_band(im, 510, H - 510, "같은 10문제로 나랑 비교해 볼래?")
    return im


def site_card():
    im = Image.new("RGBA", (W, H), WALL + (255,))
    box = (40, 30, W - 40, 470)
    panel(im, box)
    sign = Image.new("RGBA", (box[2] - box[0], box[3] - box[1]), (255, 255, 255, 255))
    sd = ImageDraw.Draw(sign)
    sw, sh = sign.size
    for i in range(9):
        cx, cy = 34 + i * 34, 34
        line = {"no": i + 1, "hex": "#%02X%02X%02X" % LINE_RGB[i + 1], "onHex": "#111418" if i + 1 in (2, 3, 4, 6, 9) else "#FFFFFF"}
        badge(sd, cx, cy, 13, line)
    sd.text((sw / 2, 196), "갈래", font=display(212), fill=INK, anchor="mm")
    sd.text((sw / 2, 300), "G a l l a e", font=gothic("Bold", 26), fill=INK3, anchor="mm")
    by = sh - 96
    sd.rectangle((0, by, sw / 2, sh), fill=L1)
    sd.rectangle((sw / 2, by, sw, sh), fill=L3)
    sd.text((34, by + 48), "← 이쪽", font=gothic("ExtraBold", 36), fill=(255, 255, 255), anchor="lm")
    sd.text((sw - 34, by + 48), "저쪽 →", font=gothic("ExtraBold", 36), fill=(255, 255, 255), anchor="rm")
    mask = Image.new("L", sign.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, sw, sh), 16, fill=255)
    im.paste(sign, (box[0], box[1]), mask)
    tactile(im, 486)
    sign_band(im, 502, H - 502, "둘 중 하나, 어느 쪽으로 갈래?")
    return im


def save(im, rel):
    path = os.path.join(ROOT, rel)
    im.convert("RGB").save(path, "PNG", optimize=True)
    return path


def main():
    lines = load_lines()
    save(site_card(), "og.png")
    n = 1
    for line in lines:
        for k, tier in enumerate(line["tiers"]):
            save(result_card(line, k, tier), os.path.join("r", f"{line['id']}-{k}.png"))
            n += 1
    print(f"drew {n} preview images")


if __name__ == "__main__":
    main()
