"""Build LoveOverDramaScript-Regular.otf/.ttf with joining alternates (calt)."""
import sys, math
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
import script_glyphs as S
from build_font import contours

FAMILY, PS = "Love Over Drama Script", "LoveOverDramaScript-Regular"
HI_EXIT = [c for c, sp in S.GLYPHS.items() if sp.get('hi')]


def shapes():
    out = {}
    for c, sp in S.GLYPHS.items():
        out[c] = (S.build(sp), sp['adv'])
        if c.islower():
            out[c + '.hi'] = (S.build(sp, entry_hi=True), sp['adv'])
    return out


def build(outdir):
    sh = shapes()
    order = ['.notdef', 'space'] + list(sh)
    cmap = {32: 'space'}
    for n in sh:
        if len(n) == 1:
            cmap[ord(n)] = n
    metrics = {'.notdef': (500, 0), 'space': (280, 0)}
    for n, (g, adv) in sh.items():
        metrics[n] = (adv, max(0, round(g.bounds[0])))
    lc = [c for c in sh if len(c) == 1 and c.islower()]
    fea = f"""
    @lc = [{' '.join(lc)}];
    @lc_hi = [{' '.join(c + '.hi' for c in lc)}];
    @hi_exit = [{' '.join(HI_EXIT + [c + '.hi' for c in HI_EXIT if c.islower()])}];
    feature calt {{ sub @hi_exit @lc' by @lc_hi; }} calt;
    """
    for flavor in ('otf', 'ttf'):
        fb = FontBuilder(1000, isTTF=(flavor == 'ttf'))
        fb.setupGlyphOrder(order)
        fb.setupCharacterMap(cmap)
        if flavor == 'ttf':
            gl = {}
            for n in order:
                pen = TTGlyphPen(None)
                if n in sh:
                    for c in contours(sh[n][0], -1.0):
                        pen.moveTo(c[0]); [pen.lineTo(q) for q in c[1:]]; pen.closePath()
                gl[n] = pen.glyph()
            fb.setupGlyf(gl)
        else:
            cs = {}
            for n in order:
                pen = T2CharStringPen(metrics[n][0], None)
                if n in sh:
                    for c in contours(sh[n][0], 1.0):
                        pen.moveTo(c[0]); [pen.lineTo(q) for q in c[1:]]; pen.closePath()
                cs[n] = pen.getCharString()
            fb.setupCFF(PS, {"FullName": FAMILY}, cs, {})
        fb.setupHorizontalMetrics(metrics)
        fb.setupHorizontalHeader(ascent=950, descent=-460)
        fb.setupNameTable({"familyName": FAMILY, "styleName": "Regular",
                           "uniqueFontIdentifier": PS + "-1.0", "fullName": FAMILY,
                           "psName": PS, "version": "Version 1.000"})
        fb.setupOS2(sTypoAscender=950, sTypoDescender=-460, usWinAscent=1000,
                    usWinDescent=470, sCapHeight=720, sxHeight=300)
        fb.setupPost()
        addOpenTypeFeaturesFromString(fb.font, fea)
        fb.save(f"{outdir}/{PS}.{flavor}")


if __name__ == '__main__':
    build(sys.argv[1])
