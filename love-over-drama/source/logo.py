"""Compose 'Love over drama' logo lockups as SVG + PNG."""
from shapely import affinity
from shapely.geometry import box
from shapely.ops import unary_union
from PIL import Image, ImageDraw
import glyphs
from build_font import all_shapes, polys

SH = all_shapes()


def set_text(text, size=1.0, track=40):
    x, parts = 0, []
    for ch in text:
        if ch == ' ':
            x += 260*size; continue
        g = SH[ch]
        minx, _, maxx, _ = g.bounds
        parts.append(affinity.scale(affinity.translate(g, x - minx, 0), size, size, origin=(x, 0)))
        x += (maxx - minx + track) * size
    return unary_union(parts)


def centred(g, cx, y):
    minx, _, maxx, _ = g.bounds
    return affinity.translate(g, cx - (minx+maxx)/2, y)


def rule(x0, x1, y, w=16):
    return unary_union([box(x0, y-w/2, x1, y+w/2),
                        glyphs.diamond(x0, y, 20), glyphs.diamond(x1, y, 20)])


def stacked():
    love = centred(set_text("LOVE", 1.0, 50), 0, 0)
    over = centred(set_text("over", 0.62, 40), 0, 0)
    drama = centred(set_text("DRAMA", 1.0, 50), 0, 0)
    W = max(love.bounds[2]-love.bounds[0], drama.bounds[2]-drama.bounds[0])
    y_drama = 0
    y_over = drama.bounds[3] + 150
    over = affinity.translate(over, 0, y_over)
    ow = (over.bounds[2]-over.bounds[0])/2
    ym = y_over + 230
    rules = [rule(-W/2+60, -ow-190, ym), rule(ow+190, W/2-60, ym),
             glyphs.fleur(-ow-120, ym-60, 0.55), glyphs.fleur(ow+120, ym-60, 0.55)]
    love = affinity.translate(love, 0, over.bounds[3] + 170)
    return unary_union([love, over, drama, *rules])


def horizontal():
    return set_text("Love over drama", 1.0, 34)


def to_svg(g, path, pad=60, color="#000000"):
    minx, miny, maxx, maxy = g.bounds
    w, h = maxx-minx+2*pad, maxy-miny+2*pad
    d = []
    for p in polys(g.simplify(0.4)):
        for ring in [p.exterior, *p.interiors]:
            pts = [(x-minx+pad, maxy-y+pad) for x, y in ring.coords]
            d.append("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts) + "Z")
    with open(path, "w") as f:
        f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
                f'width="{w:.0f}" height="{h:.0f}"><title>Love over drama</title>'
                f'<path fill="{color}" fill-rule="evenodd" d="{" ".join(d)}"/></svg>')


def to_png(g, path, width=3000, pad=0.06, transparent=False, ss=3):
    minx, miny, maxx, maxy = g.bounds
    gw, gh = maxx-minx, maxy-miny
    p = gw*pad
    sc = width*ss/(gw+2*p)
    W, Hh = int(width*ss), int((gh+2*p)*sc)
    m = Image.new("L", (W, Hh), 0); dr = ImageDraw.Draw(m)
    for poly in polys(g):
        dr.polygon([((x-minx+p)*sc, (maxy-y+p)*sc) for x, y in poly.exterior.coords], fill=255)
        for r in poly.interiors:
            dr.polygon([((x-minx+p)*sc, (maxy-y+p)*sc) for x, y in r.coords], fill=0)
    m = m.resize((W//ss, Hh//ss), Image.LANCZOS)
    if transparent:
        im = Image.new("RGBA", m.size, (0, 0, 0, 0)); im.putalpha(m)
        im = Image.composite(Image.new("RGBA", m.size, (0, 0, 0, 255)), im, m)
    else:
        im = Image.new("RGB", m.size, (255, 255, 255))
        im.paste((0, 0, 0), mask=m)
    im.save(path)


if __name__ == "__main__":
    out = "../logo"
    for name, g in (("stacked", stacked()), ("horizontal", horizontal())):
        to_svg(g, f"{out}/love-over-drama-{name}.svg")
        to_png(g, f"{out}/love-over-drama-{name}.png")
        to_png(g, f"{out}/love-over-drama-{name}-transparent.png", transparent=True)
