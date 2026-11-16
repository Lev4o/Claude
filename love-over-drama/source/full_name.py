"""Logo lockups with the full brand name, round 5."""
import numpy as np
from shapely.geometry import Point, box
from shapely.ops import unary_union
from shapely import affinity
import glyphs
import logo as wm
from ld_mark import save
from ld_concepts import heart as ld_heart
from ld_concepts2 import heart_cutout
from ld_concepts3 import arch

BLACK = "#000000"


def bounds_w(g):
    return g.bounds[2] - g.bounds[0]


def strike():
    """LOVE / over / DRAMA, with drama crossed out: love wins."""
    love = wm.centred(wm.set_text("LOVE", 1.0, 50), 0, 1560)
    over = wm.centred(wm.set_text("over", 0.5, 40), 0, 1010)
    drama = wm.centred(wm.set_text("DRAMA", 1.0, 50), 0, 0)
    W = bounds_w(drama)
    ow = bounds_w(over)/2
    rules = [box(-W/2 + 120, 1194, -ow - 70, 1206), box(ow + 70, 1194, W/2 - 120, 1206),
             glyphs.diamond(-ow - 50, 1200, 16), glyphs.diamond(ow + 50, 1200, 16)]
    slash = box(-W/2 - 60, 330, W/2 + 60, 390)
    drama = drama.difference(box(-W/2 - 80, 310, W/2 + 80, 410))
    return [(unary_union([love, over, *rules, drama, slash]), BLACK)]


def arc_text(text, size, rad, centre_deg=90, bottom=False):
    widths = [(260 if c == ' ' else bounds_w(wm.SH[c]) + 40)*size for c in text]
    total = sum(widths)/rad
    out = []
    if not bottom:
        a = np.radians(centre_deg) + total/2
        for c, w in zip(text, widths):
            ang = a - (w/2)/rad
            if c != ' ':
                g = wm.centred(affinity.scale(wm.SH[c], size, size, origin=(0, 0)), 0, rad)
                out.append(affinity.rotate(g, np.degrees(ang) - 90, origin=(0, 0)))
            a -= w/rad
    else:
        a = np.radians(centre_deg) - total/2
        for c, w in zip(text, widths):
            ang = a + (w/2)/rad
            if c != ' ':
                g = wm.centred(affinity.scale(wm.SH[c], size, size, origin=(0, 0)), 0, -rad - 760*size)
                out.append(affinity.rotate(g, np.degrees(ang) + 90, origin=(0, 0)))
            a += w/rad
    return unary_union(out)


def ring_badge():
    R = 1000
    ring = Point(0, 0).buffer(R, 256).difference(Point(0, 0).buffer(R - 30, 256))
    ring2 = Point(0, 0).buffer(R - 52, 256).difference(Point(0, 0).buffer(R - 60, 256))
    inner = Point(0, 0).buffer(560, 256).difference(Point(0, 0).buffer(552, 256))
    top = arc_text("LOVE OVER", 0.27, 660, 90)
    bot = arc_text("DRAMA", 0.27, 660, 270, bottom=True)
    dots = [glyphs.diamond(s*770, 0, 22) for s in (-1, 1)]
    (h, _), = heart_cutout()
    h = affinity.scale(h, 0.62, 0.62, origin=(0, 0))
    h = affinity.translate(h, 0, -(h.bounds[1] + h.bounds[3])/2)
    return [(unary_union([ring, ring2, inner, top, bot, *dots, h]), BLACK)]


def window_lockup():
    (a, _), = arch()
    word = wm.set_text("LOVE OVER DRAMA", 0.22, 40)
    word = wm.centred(word, 0, a.bounds[1] - 270)
    return [(unary_union([a, word]), BLACK)]


def side_by_side():
    (h, _), = ld_heart()
    h = affinity.scale(h, 0.95, 0.95, origin=(0, 0))
    h = affinity.translate(h, -h.bounds[2], -h.bounds[1])
    hh = h.bounds[3] - h.bounds[1]
    lines = ["LOVE", "OVER", "DRAMA"]
    size = (hh / 3.25) / 900
    words = []
    for i, t in enumerate(lines):
        g = wm.set_text(t, size, 40)
        g = affinity.translate(g, 230 - g.bounds[0], hh - (i + 1)*hh/3 + 40*size)
        words.append(g)
    divider = box(100, 0, 112, hh)
    return [(unary_union([h, divider, *words]), BLACK)]


if __name__ == "__main__":
    out = "../full-name"
    for name, fn in (("option-13-love-wins", strike), ("option-14-ring-badge", ring_badge),
                     ("option-15-window-lockup", window_lockup), ("option-16-side-by-side", side_by_side)):
        save(name, fn(), out)
