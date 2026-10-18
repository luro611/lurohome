"""Erzeugt die luro-Logos als SVG mit Buchstaben als Umrisse (keine Schrift nötig)."""
import sys
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FONTS = Path(sys.argv[1])
OUT = Path(sys.argv[2])
OUT.mkdir(parents=True, exist_ok=True)

REG = TTFont(FONTS / 'InstrumentSerif-Regular.ttf')
ITA = TTFont(FONTS / 'InstrumentSerif-Italic.ttf')
MONO = TTFont(FONTS / 'GeistMono-Variable.ttf')

HELL = dict(ink='#242321', accent='#c75d3b', muted='#77736c')
DUNKEL = dict(ink='#f6f0e8', accent='#e47a55', muted='#b8aea4')


def run(font, text, size, x0=0.0, spacing=0.0):
    """Text als Pfad ab (x0, Grundlinie 0). Gibt (d, neues x, bounds) zurück."""
    gs, cmap, upm = font.getGlyphSet(), font.getBestCmap(), font['head'].unitsPerEm
    s = size / upm
    pen, bpen = SVGPathPen(gs), BoundsPen(gs)
    x = x0
    for ch in text:
        g = cmap[ord(ch)]
        t = (s, 0, 0, -s, x, 0)
        gs[g].draw(TransformPen(pen, t))
        gs[g].draw(TransformPen(bpen, t))
        x += gs[g].width * s + spacing
    return pen.getCommands(), x - spacing, bpen.bounds


def line(parts, size):
    """parts: [(font, text, farbname, spacing)] → [(d, farbname)], Breite, Bounds (xmin, ymin, xmax, ymax)."""
    x, out, bb = 0.0, [], None
    for font, text, col, sp in parts:
        d, x, b = run(font, text, size, x, sp)
        out.append((d, col))
        if b:
            bb = b if bb is None else (min(bb[0], b[0]), min(bb[1], b[1]), max(bb[2], b[2]), max(bb[3], b[3]))
    return out, bb


def group(paths, colors, dx, dy):
    return ''.join(f'<path transform="translate({dx:.2f} {dy:.2f})" fill="{colors[c]}" d="{d}"/>' for d, c in paths)


def svg(w, h, body, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
            f'<title>{title}</title>{body}</svg>\n')


LURO = [(REG, 'lu', 'ink', 0), (ITA, 'ro', 'accent', 0)]

# 1) Wortmarke: lu aufrecht, ro kursiv in Terrakotta (lu-tz ro-the)
paths, (x0, y0, x1, y1) = line(LURO, 200)
pad = 24
W, H = round(x1 - x0 + 2 * pad), round(y1 - y0 + 2 * pad)
for name, c in (('hell', HELL), ('dunkel', DUNKEL)):
    (OUT / f'luro-wortmarke-{name}.svg').write_text(
        svg(W, H, group(paths, c, pad - x0, pad - y0), 'luro'))

# 2) Siegel: doppelter Ring, luro wie die Wortmarke, HOMELAB dicht darunter.
#    „kompakt“: gleiche Schrift, Ringe etwa 15 % kleiner.
for variante, S, r_aussen, r_innen in (('', 400, 188, 170), ('-kompakt', 340, 160, 144)):
    for name, c in (('hell', HELL), ('dunkel', DUNKEL)):
        p, (a0, b0, a1, b1) = line(LURO, 118)
        cx = S / 2 - (a0 + a1) / 2
        GAP = 34                                # Grundlinie HOMELAB liegt 34 px unter der von luro (dicht dran)
        base = S / 2 - (b0 + GAP) / 2           # beide Zeilen zusammen senkrecht mittig
        m, (m0, n0, m1, n1) = line([(MONO, 'HOMELAB', 'muted', 7)], 20)
        mx = S / 2 - (m0 + m1) / 2
        my = base + GAP
        h = S / 2
        rings = (f'<circle cx="{h}" cy="{h}" r="{r_aussen}" fill="none" stroke="{c["accent"]}" stroke-width="6"/>'
                 f'<circle cx="{h}" cy="{h}" r="{r_innen}" fill="none" stroke="{c["accent"]}" stroke-width="2.5"/>')
        (OUT / f'luro-siegel{variante}-{name}.svg').write_text(
            svg(S, S, rings + group(p, c, cx, base) + group(m, c, mx, my), 'luro · HOMELAB'))

# 3) Terminal: ~/luro_ auf dunkler Kachel (gleich in hell und dunkel)
p, (a0, b0, a1, b1) = line([(MONO, '~/', 'muted', 0), (MONO, 'luro', 'ink', 0), (MONO, '_', 'accent', 0)], 96)
TW, TH = 640, 280
body = (f'<rect width="{TW}" height="{TH}" rx="28" fill="#242321"/>'
        + group(p, dict(ink='#f6f0e8', accent='#e47a55', muted='#77736c'), TW / 2 - (a0 + a1) / 2, TH / 2 - (b0 + b1) / 2))
(OUT / 'luro-terminal.svg').write_text(svg(TW, TH, body, '~/luro_'))
print('fertig', sorted(f.name for f in OUT.iterdir()))
