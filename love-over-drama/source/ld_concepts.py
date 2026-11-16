"""Four new LD concepts (no oval)."""
import numpy as np
from shapely.geometry import Point, box, Polygon, LineString
from shapely.ops import unary_union
from shapely import affinity
import glyphs
import logo as wm
from ld_mark import save, soften

BLACK, GREY, WHITE = "#000000", "#7A7F84", "#FFFFFF"


def heart():
    """Heart = L + D. The L (turned 45 deg) forms the left lobe and runs along the
    heart's lower-right edge as its foot; the D rests on that foot: love holds drama."""
    w, arm, gap = 420, 620, 30
    f = 0.30 * w
    right_arm = box(0, 0, arm, w).union(Point(arm, w/2).buffer(w/2, 128))
    stem = box(0, 0, w, arm).union(Point(w/2, arm).buffer(w/2, 128))
    L = stem.union(right_arm.intersection(box(-1, -1, 2000, f)))
    D = right_arm.intersection(box(w + gap, f + gap, 2000, 2000))
    counter = box(w + gap + 78, f + gap + 64, 640, w - 64).union(
        Point(640, (f + gap + w)/2 + 4).buffer(((w - 64) - (f + gap + 64))/2, 128))
    D = D.difference(counter)
    g = affinity.rotate(unary_union([soften(L, 8), soften(D, 8)]), 45, origin=(0, 0))
    return [(g, BLACK)]


def l_over_d():
    """A tall gothic L holding a smaller D in its crook: love over drama."""
    Lg = affinity.scale(wm.SH['L'], 1.45, 1.45, origin=(0, 0))
    Dg = affinity.scale(wm.SH['D'], 0.62, 0.62, origin=(0, 0))
    Dg = affinity.translate(Dg, 300 - Dg.bounds[0], 78)
    # thin white halo where the D meets the L so the two letters stay distinct
    Lg = Lg.difference(Dg.buffer(18))
    frame_r = 800
    cx = (unary_union([Lg, Dg]).bounds[0] + unary_union([Lg, Dg]).bounds[2]) / 2
    cy = 430
    ring = Point(cx, cy).buffer(frame_r, 256).difference(Point(cx, cy).buffer(frame_r - 16, 256))
    ring2 = Point(cx, cy).buffer(frame_r - 40, 256).difference(Point(cx, cy).buffer(frame_r - 46, 256))
    return [(unary_union([Lg, Dg, ring, ring2]), BLACK)]


def crest():
    """Gothic shield split down the middle; L and D carved out of each half."""
    top, side, pt = 520, -120, -640
    t = np.linspace(0, 1, 60)
    right = [(450*(1-t_)**1.0 * (1 - 0.0) , side + (pt - side)*t_) for t_ in t]
    curve = [(450*np.cos(a), side + (pt-side)*np.sin(a)) for a in np.linspace(0, np.pi/2, 60)]
    outline = [(-450, top), (-150, top), (0, top + 60), (150, top), (450, top)] + curve + \
              [(-x, y) for x, y in curve[::-1]]
    shield = soften(Polygon(outline).buffer(0), 14)
    split = box(-17, -2000, 17, 2000)
    inner = shield.buffer(-38).difference(shield.buffer(-50))
    body = shield.difference(split).difference(inner.difference(split.buffer(22)))
    Lg = affinity.scale(wm.SH['L'], 0.5, 0.5, origin=(0, 0))
    Dg = affinity.scale(wm.SH['D'], 0.5, 0.5, origin=(0, 0))
    Lg = wm.centred(Lg, -205, -20)
    Dg = wm.centred(Dg, 195, -20)
    body = body.difference(Lg).difference(Dg)
    crown = glyphs.fleur(0, top + 70, 1.5)
    return [(unary_union([body, crown]), BLACK)]


def monoline():
    """One continuous line draws the L, runs along the base and becomes the D."""
    r = 300
    arc = [(330 + r*np.sin(a), r - r*np.cos(a)) for a in np.linspace(0, np.pi, 80)]
    pts = [(0, 860), (0, 0)] + arc + [(190, 2*r), (190, 110)]
    g = LineString(pts).buffer(26, cap_style=1, join_style=1, quad_segs=32)
    dot = Point(190 + 0, 860).buffer(30, 64)          # small heart-dot for the "over"
    return [(unary_union([g]), BLACK)]


if __name__ == "__main__":
    out = "../ld-mark-v2"
    for name, fn in (("option-1-heart", heart), ("option-2-L-over-D", l_over_d),
                     ("option-3-crest", crest), ("option-4-single-line", monoline)):
        save(name, fn(), out)
