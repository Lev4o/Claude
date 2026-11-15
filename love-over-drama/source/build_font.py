"""Build LoveOverDrama-Gothic.ttf/.otf from glyphs.py."""
import sys
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from shapely.geometry.polygon import orient
from shapely import affinity
import glyphs

FAMILY = "Love Over Drama Gothic"
PS = "LoveOverDramaGothic-Regular"
SB = 18           # side bearing
SMALLCAP = 0.80   # lowercase = small capitals


def polys(g):
    return list(g.geoms) if hasattr(g, 'geoms') else [g]


def contours(g, sign):
    out = []
    for p in polys(g.simplify(0.6)):
        if p.geom_type != 'Polygon' or p.area < 20:
            continue
        p = orient(p, sign=sign)
        for ring in [p.exterior, *p.interiors]:
            pts = []
            for x, y in list(ring.coords)[:-1]:
                q = (round(x), round(y))
                if not pts or pts[-1] != q:
                    pts.append(q)
            if len(pts) > 1 and pts[0] == pts[-1]:
                pts.pop()
            if len(pts) >= 3:
                out.append(pts)
    return out


def all_shapes():
    shapes = {}
    for ch, fn in glyphs.L.items():
        shapes[ch] = fn().shape()
    for ch in list(shapes):
        shapes[ch.lower()] = affinity.scale(shapes[ch], SMALLCAP, SMALLCAP, origin=(0, 0))
    for ch, fn in glyphs.EXTRA.items():
        shapes[ch] = fn().shape()
    return shapes


NAMES = {' ': 'space', '.': 'period', ',': 'comma', '-': 'hyphen', "'": 'quotesingle',
         '!': 'exclam', '*': 'asterisk', '⚜': 'uni269C'}


def build(outdir):
    shapes = all_shapes()
    order = ['.notdef', 'space']
    cmap = {32: 'space'}
    metrics = {'.notdef': (500, 0), 'space': (300, 0)}
    placed = {}
    for ch, g in shapes.items():
        name = NAMES.get(ch, ch)
        minx, _, maxx, _ = g.bounds
        g = affinity.translate(g, SB - minx, 0)
        adv = round(maxx - minx + 2*SB)
        placed[name] = g
        metrics[name] = (adv, SB)
        order.append(name)
        cmap[ord(ch)] = name

    for flavor in ('ttf', 'otf'):
        fb = FontBuilder(1000, isTTF=(flavor == 'ttf'))
        fb.setupGlyphOrder(order)
        fb.setupCharacterMap(cmap)
        if flavor == 'ttf':
            gl = {}
            for n in order:
                pen = TTGlyphPen(None)
                if n in placed:
                    for c in contours(placed[n], -1.0):   # TrueType: outer clockwise
                        pen.moveTo(c[0]); [pen.lineTo(q) for q in c[1:]]; pen.closePath()
                gl[n] = pen.glyph()
            fb.setupGlyf(gl)
        else:
            cs = {}
            for n in order:
                pen = T2CharStringPen(metrics[n][0], None)
                if n in placed:
                    for c in contours(placed[n], 1.0):    # CFF: outer counter-clockwise
                        pen.moveTo(c[0]); [pen.lineTo(q) for q in c[1:]]; pen.closePath()
                cs[n] = pen.getCharString()
            fb.setupCFF(PS, {"FullName": FAMILY}, cs, {})
        fb.setupHorizontalMetrics(metrics)
        fb.setupHorizontalHeader(ascent=1000, descent=-200)
        fb.setupNameTable({"familyName": FAMILY, "styleName": "Regular",
                           "uniqueFontIdentifier": PS + "-1.0", "fullName": FAMILY,
                           "psName": PS, "version": "Version 1.000"})
        fb.setupOS2(sTypoAscender=1000, sTypoDescender=-200, usWinAscent=1050,
                    usWinDescent=200, sCapHeight=glyphs.H, sxHeight=round(glyphs.H*SMALLCAP))
        fb.setupPost()
        if flavor == 'ttf':
            fb.setupDummyDSIG = None
        fb.save(f"{outdir}/LoveOverDramaGothic-Regular.{flavor}")
    return placed, metrics


if __name__ == '__main__':
    build(sys.argv[1])
