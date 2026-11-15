from PIL import Image, ImageDraw
import glyphs
from shapely.geometry import Polygon, MultiPolygon

def polys(g):
    return list(g.geoms) if hasattr(g, 'geoms') else [g]

def draw_geom(dr, g, ox, oy, sc, fill=0, bgc=255):
    for p in polys(g):
        if p.geom_type != 'Polygon' or p.is_empty: continue
        dr.polygon([(ox+x*sc, oy-y*sc) for x, y in p.exterior.coords], fill=fill)
        for r in p.interiors:
            dr.polygon([(ox+x*sc, oy-y*sc) for x, y in r.coords], fill=bgc)

def specimen(out, chars, sc=0.25, per_row=7):
    shapes = [(c, (glyphs.L.get(c) or glyphs.EXTRA[c])().shape()) for c in chars]
    cw, ch = int(900*sc), int(1250*sc)
    rows = (len(shapes)+per_row-1)//per_row
    im = Image.new('L', (cw*per_row, ch*rows), 255)
    dr = ImageDraw.Draw(im)
    for i, (c, g) in enumerate(shapes):
        r, k = divmod(i, per_row)
        minx = g.bounds[0]; w = g.bounds[2]-g.bounds[0]
        ox = k*cw + (cw - w*sc)/2 - minx*sc
        oy = r*ch + 1000*sc
        draw_geom(dr, g, ox, oy, sc)
        dr.line([(k*cw, oy), (k*cw+cw, oy)], fill=200)
    im.save(out)

if __name__ == '__main__':
    import sys
    specimen(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else 0.25)
