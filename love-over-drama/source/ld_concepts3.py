"""LD concepts, round 4."""
import numpy as np
from shapely.geometry import Point, box, Polygon
from shapely.ops import unary_union
from shapely import affinity
import glyphs
import logo as wm
from ld_mark import save, soften
from ld_concepts2 import sans_L, sans_D

BLACK = "#000000"


def gothic_pair(scale, cx, cy, gap=40):
    Lg = affinity.scale(wm.SH['L'], scale, scale, origin=(0, 0))
    Dg = affinity.scale(wm.SH['D'], scale, scale, origin=(0, 0))
    lw = Lg.bounds[2]-Lg.bounds[0]; dw = Dg.bounds[2]-Dg.bounds[0]
    tot = lw + gap + dw
    Lg = affinity.translate(Lg, cx - tot/2 - Lg.bounds[0], cy)
    Dg = affinity.translate(Dg, cx - tot/2 + lw + gap - Dg.bounds[0], cy)
    return unary_union([Lg, Dg])


def heart_shape(s=350):
    sq = affinity.rotate(box(-s, -s, s, s), 45, origin=(0, 0))
    k = s*0.7071
    return unary_union([sq, Point(-k, k).buffer(s, 128), Point(k, k).buffer(s, 128)])


def gothic_heart():
    h = heart_shape()
    frame = h.difference(h.buffer(-46)).union(h.buffer(-74).difference(h.buffer(-84)))
    return [(unary_union([frame, gothic_pair(0.38, 0, -40)]), BLACK)]


def reflection():
    """LD standing on a line, its reflection below dissolving into stripes."""
    s, hgt = 120, 600
    top = unary_union([sans_L(0, 40, hgt, 380, s), sans_D(440, 40, hgt, 470, s)])
    mirror = affinity.scale(top, 1, -1, origin=(0, 0))
    stripes, y, th = [], -40, 46
    while y > -700 and th > 4:
        stripes.append(box(-100, y - th, 1100, y)); y -= th + 18; th *= 0.78
    refl = mirror.intersection(unary_union(stripes))
    base = box(-60, 8, 970, 18)
    return [(unary_union([top, refl, base]), BLACK)]


def banner():
    """Gothic LD above a forked ribbon carrying the full name."""
    top = gothic_pair(0.8, 0, 120, gap=50)
    y0, y1, drop = -250, -40, 60
    band = box(-760, y0, 760, y1)
    parts = [band]
    for s_ in (-1, 1):
        tail = Polygon([(s_*690, y0 - drop), (s_*980, y0 - drop), (s_*900, (y0 + y1)/2 - drop),
                        (s_*980, y1 - drop), (s_*690, y1 - drop)])
        parts.append(tail.difference(box(s_*760 - 9, -2000, s_*760 + 9, 2000)))
    ribbon = unary_union(parts)
    words = wm.centred(wm.set_text("LOVE OVER DRAMA", 0.12, 40), 0, (y0 + y1)/2 - 52)
    return [(unary_union([top, ribbon.difference(words.buffer(3))]), BLACK)]


def diamond():
    d = affinity.rotate(box(-560, -560, 560, 560), 45, origin=(0, 0))
    frame = d.difference(d.buffer(-40, join_style=2)).union(
        d.buffer(-68, join_style=2).difference(d.buffer(-80, join_style=2)))
    top = d.bounds[3]
    crown = glyphs.fleur(0, top - 10, 1.2)
    foot = glyphs.fleur(0, -top + 10, 0.8, down=True)
    return [(unary_union([frame, crown, foot, gothic_pair(0.5, 0, -200)]), BLACK)]


def arch():
    """Pointed gothic window split by a mullion: L in one light, D in the other."""
    W, spring = 460, 640
    r = 2*W
    th = np.linspace(0, 1, 120)
    # right arc centred at (-W, spring), left arc centred at (W, spring)
    apex_y = spring + np.sqrt(r**2 - W**2)
    a_end = np.arcsin(np.sqrt(r**2 - W**2)/r)
    right = [(-W + r*np.cos(a), spring + r*np.sin(a)) for a in np.linspace(0, a_end, 120)]
    left = [(-x, y) for x, y in right[::-1]]
    outer = Polygon([(-W, 0), (W, 0)] + right + left[1:])
    frame = outer.difference(outer.buffer(-48)).union(
        outer.buffer(-74).difference(outer.buffer(-84)))
    mull = box(-12, 0, 12, spring + 160)
    rose_c = (0, spring + 330)
    rose = Point(*rose_c).buffer(120, 128).difference(Point(*rose_c).buffer(96, 128))
    petals = unary_union([Point(rose_c[0] + 48*np.cos(a), rose_c[1] + 48*np.sin(a)).buffer(30, 64)
                          for a in np.linspace(0, 2*np.pi, 4, endpoint=False)+np.pi/4])
    Lg = affinity.scale(wm.SH['L'], 0.42, 0.42, origin=(0, 0))
    Dg = affinity.scale(wm.SH['D'], 0.42, 0.42, origin=(0, 0))
    Lg = wm.centred(Lg, -W/2 + 20, 160)
    Dg = wm.centred(Dg, W/2 - 20, 160)
    base = box(-W - 40, -40, W + 40, 0)
    return [(unary_union([frame, mull, rose, petals, Lg, Dg, base]), BLACK)]


if __name__ == "__main__":
    out = "../ld-mark-v4"
    for name, fn in (("option-9-gothic-heart", gothic_heart), ("option-10-banner", banner),
                     ("option-11-diamond", diamond), ("option-12-cathedral-window", arch)):
        save(name, fn(), out)
