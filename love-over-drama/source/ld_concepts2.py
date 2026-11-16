"""LD concepts, round 3."""
import numpy as np
from shapely.geometry import Point, box, Polygon
from shapely.ops import unary_union
from shapely import affinity
import glyphs
import logo as wm
from ld_mark import save, soften

BLACK = "#000000"


def sans_L(x, y, h, w, s):
    return box(x, y, x+s, y+h).union(box(x, y, x+w, y+s))


def sans_D(x, y, h, w, s):
    r = h/2
    outer = box(x, y, x+w-r, y+h).union(Point(x+w-r, y+r).buffer(r, 128)).intersection(box(x, y, x+w+1, y+h))
    return outer.difference(outer.buffer(-s, join_style=2))


def fraction():
    """L over D, literally: the letters stacked like a fraction."""
    Lg = wm.centred(wm.SH['L'], 0, 0)
    Dg = wm.centred(wm.SH['D'], 0, 0)
    Lg = affinity.translate(Lg, 0, 1150)
    rule = unary_union([box(-520, 960, 520, 978), glyphs.diamond(-520, 969, 22),
                        glyphs.diamond(520, 969, 22), glyphs.diamond(0, 969, 40)])
    return [(unary_union([Lg, rule, Dg]), BLACK)]


def overlap():
    """Bold L and D overlapping; where they meet becomes white: love meets drama."""
    s = 170
    L = sans_L(0, 0, 900, 600, s)
    D = sans_D(430, 0, 900, 820, s)
    g = L.symmetric_difference(D)
    return [(soften(g, 6), BLACK)]


def heart_cutout():
    """Solid heart with a clean LD cut out of it."""
    sq = affinity.rotate(box(-350, -350, 350, 350), 45, origin=(0, 0))
    c1 = Point(-247, 247).buffer(350, 128)
    c2 = Point(247, 247).buffer(350, 128)
    heart = unary_union([sq, c1, c2])
    s, h = 64, 330
    L = sans_L(-290, -60, h, 210, s)
    D = sans_D(-30, -60, h, 320, s)
    return [(heart.difference(L).difference(D), BLACK)]


def seal():
    """Scalloped wax-seal with a gothic LD and the name set around the edge."""
    th = np.linspace(0, 2*np.pi, 1200)
    R = 1000 + 26*np.sin(28*th)
    body = Polygon(np.c_[R*np.cos(th), R*np.sin(th)])
    ring_out = Point(0, 0).buffer(900, 256).difference(Point(0, 0).buffer(884, 256))
    ring_in = Point(0, 0).buffer(600, 256).difference(Point(0, 0).buffer(584, 256))
    Lg = affinity.scale(wm.SH['L'], 0.56, 0.56, origin=(0, 0))
    Dg = affinity.scale(wm.SH['D'], 0.56, 0.56, origin=(0, 0))
    Lg = wm.centred(Lg, -200, -235)
    Dg = wm.centred(Dg, 195, -235)
    # name around the top arc, letters standing on a circle of radius 650
    text = "LOVE OVER DRAMA"
    size = 0.25
    widths = [(260 if c == ' ' else (wm.SH[c].bounds[2]-wm.SH[c].bounds[0]) + 40)*size for c in text]
    rad = 655
    total = sum(widths)/rad
    a = np.pi/2 + total/2
    letters = []
    for c, wdt in zip(text, widths):
        ang = a - (wdt/2)/rad
        if c != ' ':
            g = affinity.scale(wm.SH[c], size, size, origin=(0, 0))
            g = wm.centred(g, 0, 0)
            g = affinity.translate(g, 0, rad)
            g = affinity.rotate(g, np.degrees(ang - np.pi/2), origin=(0, 0))
            letters.append(g)
        a -= wdt/rad
    stars = [glyphs.fleur(0, -760, 0.55, down=False)]
    cut = unary_union([ring_out, ring_in, Lg, Dg, *letters, *stars])
    return [(body.difference(cut), BLACK)]


if __name__ == "__main__":
    out = "../ld-mark-v3"
    for name, fn in (("option-5-fraction", fraction), ("option-6-overlap", overlap),
                     ("option-7-heart-cutout", heart_cutout), ("option-8-wax-seal", seal)):
        save(name, fn(), out)
