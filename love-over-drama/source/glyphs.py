"""Ornate Gothic display letters inspired by a carved-iron capital A.

Every letter is built from a small vocabulary of parts:
  - fluted strokes  (thick/thin contrast + two carved grooves)
  - gothic heads    (flared caps with curled horns on stem tops)
  - claw feet       (flared base with curled hooks + a centre point)
  - side spurs      (curls sprouting from the outer side of stems)
  - fleur-de-lis    (crowning finial / hanging pendant)
"""
import math
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box
from shapely.ops import unary_union
from shapely import affinity
from shapely.validation import make_valid

H = 740          # cap height
T = 138          # thick stroke
t = 50           # thin stroke
ORN = 1.28
GROOVE = 7       # carved groove width


# ---------------------------------------------------------------- geometry
def bez(p0, p1, p2, p3, n=40):
    s = np.linspace(0, 1, n)[:, None]
    p0, p1, p2, p3 = map(np.array, (p0, p1, p2, p3))
    return (1-s)**3*p0 + 3*(1-s)**2*s*p1 + 3*(1-s)*s**2*p2 + s**3*p3


def line(p0, p1, n=12):
    s = np.linspace(0, 1, n)[:, None]
    return (1-s)*np.array(p0) + s*np.array(p1)


def path(*segs):
    out = [segs[0]]
    for sgm in segs[1:]:
        out.append(sgm[1:])
    return np.vstack(out)


def normals(p):
    d = np.gradient(p, axis=0)
    d /= np.linalg.norm(d, axis=1)[:, None] + 1e-9
    return np.stack([-d[:, 1], d[:, 0]], axis=1), d


def poly_clean(g):
    g = make_valid(g)
    if g.geom_type == 'GeometryCollection':
        g = unary_union([x for x in g.geoms if x.area > 0])
    return g.buffer(0)


def vstroke(p, w):
    """Variable-width stroke along centreline p with width array w."""
    w = np.broadcast_to(np.asarray(w, float), (len(p),))
    n, _ = normals(p)
    left = p + n * (w/2)[:, None]
    right = p - n * (w/2)[:, None]
    ring = np.vstack([left, right[::-1]])
    g = Polygon(ring)
    if not g.is_valid:
        # union of quads is robust for tight curls
        quads = [Polygon([left[i], left[i+1], right[i+1], right[i]]).buffer(0.01)
                 for i in range(len(p)-1)]
        g = unary_union(quads)
    return poly_clean(g)


def auto_width(p, thick=T, thin=t, power=1.6):
    _, d = normals(p)
    return thin + (thick-thin) * np.abs(d[:, 1])**power


def grooves(p, w, trim=40, minw=90, k=0.27):
    """Two carved flutes running along a stroke wherever it is thick."""
    w = np.broadcast_to(np.asarray(w, float), (len(p),))
    n, _ = normals(p)
    seg = np.r_[0, np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))]
    ok = (w >= minw) & (seg > trim) & (seg < seg[-1]-trim)
    lines = []
    for sgn in (-1, 1):
        q = p + n * (sgn*k*w)[:, None]
        run = []
        for i, flag in enumerate(ok):
            if flag:
                run.append(q[i])
            elif len(run) > 1:
                lines.append(LineString(run)); run = []
            else:
                run = []
        if len(run) > 1:
            lines.append(LineString(run))
    if not lines:
        return Polygon()
    return unary_union([l.buffer(GROOVE/2, cap_style=1) for l in lines])


def thorn(p, w0, w1=2.0):
    w = np.linspace(w0, w1, len(p))
    return vstroke(p, w)


def mirror_x(g, x):
    return affinity.scale(g, -1, 1, origin=(x, 0))


# --------------------------------------------------------------- ornaments
def head(x, y, w=T, left=True, right=True, crown=True):
    """Flared gothic cap on top of a stem whose top is at y."""
    hw = w/2
    parts = [Polygon([(x-hw, y-70), (x+hw, y-70), (x+hw+18, y+6),
                      (x-hw-18, y+6)])]
    sides = []
    if left:
        sides.append(-1)
    if right:
        sides.append(1)
    for s in sides:
        parts.append(thorn(bez((x+s*(hw-6), y-4), (x+s*(hw+30), y+4),
                               (x+s*(hw+52), y+26), (x+s*(hw+40), y+58)), 30))
        parts.append(thorn(bez((x+s*(hw+2), y-40), (x+s*(hw+26), y-46),
                               (x+s*(hw+30), y-66), (x+s*(hw+12), y-84), 20), 18))
    if crown:
        parts.append(Polygon([(x-20, y), (x, y+44), (x+20, y)]))
        parts.append(Point(x, y+50).buffer(9))
    return affinity.scale(unary_union(parts), ORN, ORN, origin=(x, y-40))


def foot(x, y=0, w=T, left=True, right=True):
    """Clawed foot at the bottom of a stem."""
    hw = w/2
    parts = [Polygon([(x-hw-26, y), (x+hw+26, y), (x+hw, y+80), (x-hw, y+80)])]
    sides = []
    if left:
        sides.append(-1)
    if right:
        sides.append(1)
    for s in sides:
        # outer hook: sweeps out along the baseline then curls upward
        parts.append(thorn(bez((x+s*(hw-4), y+26), (x+s*(hw+60), y-6),
                               (x+s*(hw+104), y+18), (x+s*(hw+96), y+70)), 46))
        # small inner barb pointing up
        parts.append(thorn(bez((x+s*(hw+30), y+40), (x+s*(hw+40), y+60),
                               (x+s*(hw+38), y+80), (x+s*(hw+26), y+96), 16), 18))
    parts.append(Polygon([(x-22, y+2), (x, y-40), (x+22, y+2)]))
    return affinity.scale(unary_union(parts), ORN, ORN, origin=(x, y))


def spur(x, y, side):
    """A curl sprouting outward from the edge of a stem at (x, y)."""
    s = side
    a = thorn(bez((x-s*4, y-30), (x+s*40, y-20), (x+s*70, y+10), (x+s*66, y+56), 30), 40)
    b = thorn(bez((x+s*66, y+56), (x+s*62, y+82), (x+s*36, y+86), (x+s*30, y+64), 16), 18, 3)
    c = thorn(bez((x-s*2, y-50), (x+s*22, y-58), (x+s*36, y-80), (x+s*30, y-104), 16), 22)
    return affinity.scale(unary_union([a, b, c]), ORN, ORN, origin=(x-s*10, y))


def fleur(x, y, s=1.0, down=False):
    """Fleur-de-lis standing on (x, y); down=True hangs it below (x, y)."""
    P = lambda dx, dy: (x + dx*s, y + dy*s)
    parts = []
    # central petal (lens)
    cp = line(P(0, 18), P(0, 150), 30)
    wv = np.array([20, 44, 58, 62, 60, 54, 44, 30, 14, 2]) * s
    wv = np.interp(np.linspace(0, 1, len(cp)), np.linspace(0, 1, len(wv)), wv)
    parts.append(vstroke(cp, wv))
    for sd in (-1, 1):
        parts.append(thorn(bez(P(sd*14, 28), P(sd*70, 40), P(sd*96, 92),
                               P(sd*72, 116), 30), 40*s))
        parts.append(thorn(bez(P(sd*72, 116), P(sd*58, 128), P(sd*44, 112),
                               P(sd*52, 100), 12), 16*s, 2))
        parts.append(thorn(bez(P(sd*10, -8), P(sd*40, -14), P(sd*56, -34),
                               P(sd*46, -54), 20), 22*s))
    parts.append(box(*P(-50, 18), *P(50, 40)))
    parts.append(Polygon([P(-16, 20), P(16, 20), P(10, -30), P(-10, -30)]))
    g = unary_union(parts)
    if down:
        g = affinity.scale(g, 1, -1, origin=(x, y))
    return g


def diamond(x, y, r=26):
    return Polygon([(x, y-r*1.4), (x+r, y), (x, y+r*1.4), (x-r, y)])


def band(x, y, w=T):
    hw = w/2 + 16
    return unary_union([box(x-hw, y-14, x+hw, y+14), diamond(x-hw, y, 12),
                        diamond(x+hw, y, 12)])


def barb(x, y, dirx, diry, size=1.0):
    """Arm terminal: a beak that hooks vertically (diry) at an arm end."""
    s = size
    a = thorn(bez((x-dirx*26, y), (x+dirx*8, y), (x+dirx*16, y+diry*40*s),
                  (x+dirx*4, y+diry*84*s)), 46*s)
    b = thorn(bez((x-dirx*10, y-diry*10), (x+dirx*14, y-diry*16), (x+dirx*24, y-diry*30),
                  (x+dirx*20, y-diry*46), 12), 18*s)
    return unary_union([a, b])


# --------------------------------------------------------------- strokes
class Glyph:
    def __init__(self):
        self.body, self.cuts, self.orn = [], [], []

    def stroke(self, p, w, flute=True):
        p = np.asarray(p, float)
        self.body.append(vstroke(p, w))
        if flute:
            self.cuts.append(grooves(p, w))
        return self

    def curve(self, p, thick=T, thin=t, flute=True):
        w = auto_width(p, thick, thin)
        return self.stroke(p, w, flute)

    def add(self, g):
        self.orn.append(g)
        return self

    def shape(self):
        body = unary_union(self.body)
        if self.cuts:
            body = body.difference(unary_union(self.cuts))
        return poly_clean(unary_union([body] + self.orn))


def stem(g, x, y0, y1, w=T, flute=True):
    return g.stroke(line((x, y0), (x, y1)), w, flute)


def diag(g, p0, p1, w=T, flute=True):
    return g.stroke(line(p0, p1, 20), w, flute)


def bar(g, x0, x1, y, w=44):
    return g.stroke(line((x0, y), (x1, y)), w, flute=False)


# ------------------------------------------------------------------ letters
L = {}


def letter(ch):
    def deco(fn):
        L[ch] = fn
        return fn
    return deco


@letter('A')
def _A():
    g = Glyph()
    diag(g, (90, 0), (300, H-50))
    diag(g, (550, 0), (340, H-50))
    # apex shield
    g.add(Polygon([(214, H+18), (426, H+18), (392, H-96), (248, H-96)]))
    g.add(thorn(bez((220, H+14), (196, H+26), (180, H+44), (192, H+70)), 24))
    g.add(thorn(bez((420, H+14), (444, H+26), (460, H+44), (448, H+70)), 24))
    g.add(diamond(320, H-36, 22).difference(diamond(320, H-36, 12)))
    g.add(fleur(320, H+18, 0.82))
    # crossbar + hanging pendant
    yb = 300
    xl = 90 + 210*yb/(H-50); xr = 550 - 210*yb/(H-50)
    bar(g, xl, xr, yb, 46)
    g.add(fleur(320, yb-10, 0.62, down=True))
    # side curls
    ys = 400
    g.add(spur(90 + 210*ys/(H-50) - T/2 + 6, ys, -1))
    g.add(spur(550 - 210*ys/(H-50) + T/2 - 6, ys, 1))
    g.add(foot(90)).add(foot(550))
    return g


@letter('B')
def _B():
    g = Glyph()
    stem(g, 110, 0, H)
    g.curve(path(line((120, H-18), (250, H-18), 6),
                 bez((250, H-18), (360, H-18), (420, H-70), (420, 570)),
                 bez((420, 570), (420, 470), (350, 410), (200, 410)),
                 line((200, 410), (130, 410), 5)))
    g.curve(path(line((130, 410), (270, 410), 6),
                 bez((270, 410), (400, 410), (470, 330), (470, 210)),
                 bez((470, 210), (470, 80), (380, 18), (260, 18)),
                 line((260, 18), (120, 18), 6)))
    g.add(head(110, H, right=False)).add(foot(110, right=False))
    g.add(diamond(160, 410, 20))
    return g


@letter('C')
def _C():
    g = Glyph()
    g.curve(path(bez((490, 600), (460, H-6), (380, H-18), (300, H-18)),
                 bez((300, H-18), (150, H-18), (70, 560), (70, 370)),
                 bez((70, 370), (70, 170), (150, 18), (300, 18)),
                 bez((300, 18), (390, 18), (460, 60), (500, 150))))
    g.add(barb(478, H-40, 1, -1, 1.1))
    g.add(thorn(bez((490, 140), (520, 170), (536, 210), (530, 250)), 34))
    g.add(spur(28, 370, -1))
    return g


@letter('D')
def _D():
    g = Glyph()
    stem(g, 110, 0, H)
    g.curve(path(line((120, H-18), (280, H-18), 6),
                 bez((280, H-18), (440, H-18), (530, 560), (530, 370)),
                 bez((530, 370), (530, 180), (440, 18), (280, 18)),
                 line((280, 18), (120, 18), 6)))
    g.add(head(110, H, right=False)).add(foot(110, right=False))
    g.add(spur(578, 370, 1))
    return g


def _E_like(bottom=True, mid_len=340):
    g = Glyph()
    stem(g, 120, 0, H)
    bar(g, 120, 440, H-22, 48)
    g.add(barb(440, H-22, 1, -1))
    bar(g, 120, mid_len, 390, 44)
    g.add(barb(mid_len, 390, 1, -1, 0.55)).add(barb(mid_len, 390, 1, 1, 0.55))
    g.add(fleur(mid_len-80, 372, 0.45, down=True))
    g.add(head(120, H, right=False))
    if bottom:
        bar(g, 120, 470, 22, 48)
        g.add(barb(470, 22, 1, 1))
        g.add(foot(120, right=False))
    else:
        g.add(foot(120))
    return g


letter('E')(lambda: _E_like(True))
letter('F')(lambda: _E_like(False))


@letter('G')
def _G():
    g = Glyph()
    g.curve(path(bez((490, 600), (460, H-6), (380, H-18), (300, H-18)),
                 bez((300, H-18), (150, H-18), (70, 560), (70, 370)),
                 bez((70, 370), (70, 170), (150, 18), (300, 18)),
                 bez((300, 18), (400, 18), (470, 60), (470, 180))))
    stem(g, 470, 40, 330, T)
    bar(g, 330, 560, 330, 44)
    g.add(barb(478, H-40, 1, -1, 1.1))
    g.add(diamond(560, 330, 22))
    g.add(spur(28, 370, -1))
    return g


@letter('H')
def _H():
    g = Glyph()
    stem(g, 120, 0, H)
    stem(g, 500, 0, H)
    bar(g, 120, 500, 390, 46)
    g.add(fleur(310, 380, 0.6, down=True))
    g.add(head(120, H)).add(head(500, H))
    g.add(foot(120)).add(foot(500))
    g.add(spur(120-T/2+6, 470, -1)).add(spur(500+T/2-6, 470, 1))
    return g


@letter('I')
def _I():
    g = Glyph()
    stem(g, 150, 0, H)
    g.add(head(150, H)).add(foot(150)).add(band(150, 380))
    return g


@letter('J')
def _J():
    g = Glyph()
    g.stroke(path(line((330, H), (330, 230), 20),
                  bez((330, 230), (330, 60), (250, 0), (160, 10))),
             np.r_[np.full(20, T), np.linspace(T, 40, 39)])
    g.add(thorn(bez((166, 10), (100, 18), (70, 70), (96, 120)), 40))
    g.add(head(330, H)).add(band(330, 430))
    return g


@letter('K')
def _K():
    g = Glyph()
    stem(g, 120, 0, H)
    diag(g, (150, 330), (470, H-30), 50, flute=False)
    diag(g, (230, 430), (500, 0), T)
    g.add(barb(470, H-30, 1, -1, 0.9))
    g.add(head(120, H)).add(foot(120)).add(foot(500, left=False))
    g.add(diamond(200, 400, 24))
    return g


@letter('L')
def _L():
    g = Glyph()
    stem(g, 120, 0, H)
    bar(g, 120, 470, 22, 50)
    g.add(barb(470, 22, 1, 1, 1.1))
    g.add(head(120, H)).add(foot(120, right=False))
    g.add(spur(120-T/2+6, 470, -1))
    return g


@letter('M')
def _M():
    g = Glyph()
    stem(g, 120, 0, H)
    stem(g, 700, 0, H)
    diag(g, (130, H-10), (410, 160), 58, flute=False)
    diag(g, (410, 160), (690, H-10), T)
    g.add(fleur(410, 150, 0.6, down=True))
    g.add(head(120, H)).add(head(700, H))
    g.add(foot(120)).add(foot(700))
    g.add(spur(120-T/2+6, 470, -1)).add(spur(700+T/2-6, 470, 1))
    return g


@letter('N')
def _N():
    g = Glyph()
    stem(g, 110, 0, H, 52, flute=False)
    diag(g, (110, H), (500, 0), T)
    stem(g, 500, 0, H, 52, flute=False)
    g.add(head(110, H, w=52)).add(head(500, H, w=52))
    g.add(foot(110, w=52)).add(foot(500, w=52))
    g.add(spur(110-26+4, 470, -1)).add(spur(500+26-4, 300, 1))
    return g


@letter('O')
def _O():
    g = Glyph()
    cx, cy, rx, ry = 320, 370, 250, 352
    k = 0.5523
    g.curve(path(bez((cx, cy+ry), (cx-k*rx, cy+ry), (cx-rx, cy+k*ry), (cx-rx, cy)),
                 bez((cx-rx, cy), (cx-rx, cy-k*ry), (cx-k*rx, cy-ry), (cx, cy-ry)),
                 bez((cx, cy-ry), (cx+k*rx, cy-ry), (cx+rx, cy-k*ry), (cx+rx, cy)),
                 bez((cx+rx, cy), (cx+rx, cy+k*ry), (cx+k*rx, cy+ry), (cx, cy+ry))))
    g.add(diamond(cx, cy+ry+20, 20)).add(diamond(cx, cy-ry-20, 20))
    g.add(spur(cx-rx-T/2+4, cy, -1)).add(spur(cx+rx+T/2-4, cy, 1))
    return g


def _P_like(bowl_bottom, leg=False):
    g = Glyph()
    stem(g, 110, 0, H)
    mid = (H + bowl_bottom)/2
    g.curve(path(line((120, H-18), (270, H-18), 6),
                 bez((270, H-18), (420, H-18), (480, H-80), (480, mid)),
                 bez((480, mid), (480, bowl_bottom+60), (400, bowl_bottom), (260, bowl_bottom)),
                 line((260, bowl_bottom), (120, bowl_bottom), 6)))
    g.add(head(110, H, right=False))
    if leg:
        diag(g, (330, bowl_bottom), (550, 0), T)
        g.add(foot(110, right=False)).add(foot(555, left=False))
    else:
        g.add(foot(110))
    g.add(diamond(165, bowl_bottom, 20))
    return g


letter('P')(lambda: _P_like(330))
letter('R')(lambda: _P_like(380, leg=True))


@letter('Q')
def _Q():
    g = L['O']()
    g.add(thorn(bez((300, 60), (380, -10), (470, -40), (580, -110)), 70))
    return g


@letter('S')
def _S():
    g = Glyph()
    g.curve(path(bez((450, 610), (420, H-6), (350, H-18), (280, H-18)),
                 bez((280, H-18), (160, H-18), (90, 660), (90, 560)),
                 bez((90, 560), (90, 440), (200, 410), (280, 385)),
                 bez((280, 385), (380, 355), (480, 310), (480, 190)),
                 bez((480, 190), (480, 70), (390, 18), (280, 18)),
                 bez((280, 18), (190, 18), (110, 60), (80, 130))), thick=T+6)
    g.add(barb(440, H-40, 1, -1, 1.0))
    g.add(barb(90, 120, -1, 1, 1.0))
    return g


@letter('T')
def _T():
    g = Glyph()
    bar(g, 40, 600, H-24, 52)
    stem(g, 320, 0, H-24)
    g.add(barb(40, H-24, -1, -1)).add(barb(600, H-24, 1, -1))
    g.add(fleur(320, H, 0.75))
    g.add(foot(320))
    return g


@letter('U')
def _U():
    g = Glyph()
    p = path(line((120, H), (120, 230), 20),
             bez((120, 230), (120, 60), (210, 18), (310, 18)),
             bez((310, 18), (410, 18), (500, 60), (500, 230)),
             line((500, 230), (500, H), 20))
    g.curve(p, thick=T, thin=t)
    g.add(head(120, H)).add(head(500, H))
    g.add(spur(120-T/2+6, 470, -1)).add(spur(500+T/2-6, 470, 1))
    return g


@letter('V')
def _V():
    g = Glyph()
    diag(g, (110, H), (320, 40), T)
    diag(g, (530, H), (320, 40), 52, flute=False)
    g.add(Polygon([(260, 60), (380, 60), (320, -30)]))
    g.add(head(110, H)).add(head(530, H, w=52))
    return g


@letter('W')
def _W():
    g = Glyph()
    diag(g, (90, H), (250, 40), T)
    diag(g, (250, 40), (420, H-80), 52, flute=False)
    diag(g, (420, H-80), (590, 40), T)
    diag(g, (590, 40), (740, H), 52, flute=False)
    for x in (250, 590):
        g.add(Polygon([(x-56, 60), (x+56, 60), (x, -30)]))
    g.add(diamond(420, H-70, 24))
    g.add(head(90, H)).add(head(740, H, w=52))
    return g


@letter('X')
def _X():
    g = Glyph()
    diag(g, (110, H), (520, 0), T)
    diag(g, (520, H), (110, 0), 52, flute=False)
    g.add(diamond(315, 370, 30))
    g.add(head(110, H)).add(head(520, H, w=52))
    g.add(foot(110, w=52)).add(foot(520))
    return g


@letter('Y')
def _Y():
    g = Glyph()
    diag(g, (110, H), (320, 380), T)
    diag(g, (530, H), (320, 380), 52, flute=False)
    stem(g, 320, 0, 400)
    g.add(head(110, H)).add(head(530, H, w=52))
    g.add(band(320, 330)).add(foot(320))
    return g


@letter('Z')
def _Z():
    g = Glyph()
    bar(g, 90, 500, H-24, 50)
    diag(g, (480, H-40), (110, 40), T+8)
    bar(g, 90, 530, 24, 50)
    g.add(barb(90, H-24, -1, -1)).add(barb(530, 24, 1, 1))
    g.add(band(300, 380, 0).intersection(box(0, 0, 1000, 1000)))
    return g


# --------------------------------------------------------------- extras
def _period():
    g = Glyph(); g.add(diamond(110, 50, 34)); return g


def _comma():
    g = Glyph(); g.add(diamond(110, 60, 30))
    g.add(thorn(bez((120, 40), (130, 0), (110, -50), (70, -90)), 36)); return g


def _hyphen():
    g = Glyph(); bar(g, 60, 300, 330, 44)
    g.add(diamond(60, 330, 18)).add(diamond(300, 330, 18)); return g


def _apos():
    g = Glyph(); g.add(diamond(110, H-40, 28))
    g.add(thorn(bez((120, H-60), (130, H-100), (110, H-140), (70, H-170)), 32)); return g


def _excl():
    g = Glyph()
    g.stroke(line((130, H), (130, 200), 12), np.linspace(T, 30, 12), flute=False)
    g.add(head(130, H, crown=False)).add(diamond(130, 50, 34)); return g


def _fleuron():
    g = Glyph(); g.add(fleur(300, 120, 2.2)); return g


EXTRA = {'.': _period, ',': _comma, '-': _hyphen, "'": _apos, '!': _excl,
         '*': _fleuron, '⚜': _fleuron}
