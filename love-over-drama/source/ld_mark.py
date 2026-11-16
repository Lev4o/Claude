"""Clean geometric versions of the LD oval monogram."""
from shapely.geometry import Point, box
from shapely.ops import unary_union
from shapely import affinity
import logo as wm   # wordmark + SVG/PNG writers

RX, RY, GAP = 600, 390, 46
ROT = lambda g: affinity.rotate(g, 180, origin=(0, 0))


def ellipse(cx, cy, rx, ry):
    return affinity.scale(Point(0, 0).buffer(1, 256), rx, ry).__class__(
        affinity.translate(affinity.scale(Point(0, 0).buffer(1, 256), rx, ry), cx, cy))


def soften(g, r=10):
    return g.buffer(-r, join_style=1).buffer(r, join_style=1)


def halves(counter, rx=RX, ry=RY):
    oval = ellipse(0, 0, rx, ry)
    left = oval.intersection(box(-rx-10, -ry-10, -GAP/2, ry+10)).difference(counter)
    right = ROT(left)
    return soften(left), soften(right)


def counter_round():
    # half-stadium notch opening onto the centre gap, upper half of the left side
    c = ellipse(-GAP/2, 125, 400, 112)
    return c


def counter_square():
    # squared notch so the left half reads as a crisp "L" and the right as a "D"
    return soften(box(-430, 20, 0, 232), 0).buffer(0).union(
        ellipse(-430+60, 126, 60, 106)).intersection(box(-500, 20, 0, 232))


def mark(kind):
    if kind == 'circle':
        l, r = halves(ellipse(-GAP/2, 150, 300, 118), 470, 470)
        return unary_union([l, r])
    c = counter_square() if kind == 'square' else counter_round()
    l, r = halves(c)
    return unary_union([l, r])


def outline(g, w=22):
    return unary_union([p.exterior.buffer(w/2, join_style=1) for p in wm.polys(g)])


def with_shadow(g, dx=-34, dy=-34):
    return affinity.translate(g, dx, dy).difference(g)


def save(name, layers, out="../ld-mark"):
    """layers: list of (geometry, colour), drawn in order."""
    allg = unary_union([g for g, _ in layers])
    minx, miny, maxx, maxy = allg.bounds
    pad = 0.12*(maxx-minx)
    w, h = maxx-minx+2*pad, maxy-miny+2*pad
    paths = []
    for g, col in layers:
        d = []
        for p in wm.polys(g.simplify(0.3)):
            for ring in [p.exterior, *p.interiors]:
                d.append("M" + " L".join(f"{x-minx+pad:.1f} {maxy-y+pad:.1f}" for x, y in ring.coords) + "Z")
        paths.append(f'<path fill="{col}" fill-rule="evenodd" d="{" ".join(d)}"/>')
    open(f"{out}/{name}.svg", "w").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" width="{w:.0f}" '
        f'height="{h:.0f}"><title>Love over drama LD mark</title>{"".join(paths)}</svg>')
    from PIL import Image, ImageDraw
    S = 2000/w*3
    W, Hh = int(w*S), int(h*S)
    for transparent in (False, True):
        im = Image.new("RGBA", (W, Hh), (255, 255, 255, 0 if transparent else 255))
        for g, col in layers:
            m = Image.new("L", (W, Hh), 0); dr = ImageDraw.Draw(m)
            for p in wm.polys(g):
                dr.polygon([((x-minx+pad)*S, (maxy-y+pad)*S) for x, y in p.exterior.coords], fill=255)
                for r in p.interiors:
                    dr.polygon([((x-minx+pad)*S, (maxy-y+pad)*S) for x, y in r.coords], fill=0)
            rgb = tuple(int(col[i:i+2], 16) for i in (1, 3, 5)) + (255,)
            im.paste(Image.new("RGBA", (W, Hh), rgb), mask=m)
        im = im.resize((W//3, Hh//3), Image.LANCZOS)
        im.save(f"{out}/{name}{'-transparent' if transparent else ''}.png")


if __name__ == "__main__":
    BLACK, GREY = "#000000", "#7A7F84"
    pure = mark('round')
    circ = mark('circle')
    save("option-1-pure", [(pure, BLACK)])
    save("option-2-circle-badge", [(circ, BLACK)])
    save("option-3-outline", [(outline(pure), BLACK)])
    # 4: refined shadow mark + gothic wordmark underneath
    word = wm.set_text("LOVE OVER DRAMA", 0.25, 40)
    word = wm.centred(word, 0, -RY - 330)
    save("option-4-shadow-lockup", [(with_shadow(pure), GREY), (pure, BLACK), (word, BLACK)])
