"""Original stippled 5-point star (spray-dot texture)."""
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 2000, 2200
CX, CY = 1000, 1120
rng = np.random.default_rng(7)


def bez(p0, p1, p2, n=30):
    t = np.linspace(0, 1, n)[:, None]
    return (1-t)**2*p0 + 2*(1-t)*t*p1 + t**2*p2


def star_outline():
    # five uneven, slightly swirling arms
    tips = [(-96, 930), (-20, 780), (58, 880), (128, 720), (200, 820)]   # (angle deg, radius)
    inner_r = 215
    pts = []
    for i, (a, r) in enumerate(tips):
        a0 = np.radians(a - 36 + 6)       # inner vertex before the tip
        a1 = np.radians(a + 36 + 6)       # inner vertex after the tip
        tip = np.array([CX + r*np.cos(np.radians(a)), CY - r*np.sin(np.radians(a))])
        v0 = np.array([CX + inner_r*np.cos(a0), CY - inner_r*np.sin(a0)])
        v1 = np.array([CX + inner_r*np.cos(a1), CY - inner_r*np.sin(a1)])
        # curved edges give the pinwheel twist: concave in, convex out
        mid0 = (v0 + tip)/2 + 0.10*np.array([-(tip-v0)[1], (tip-v0)[0]])
        mid1 = (tip + v1)/2 + 0.04*np.array([-(v1-tip)[1], (v1-tip)[0]])
        pts += list(bez(v0, mid0, tip)) + list(bez(tip, mid1, v1))[1:]
    return [tuple(p) for p in pts]


def density():
    m = Image.new("L", (W, H), 0)
    ImageDraw.Draw(m).polygon(star_outline(), fill=255)
    core = np.asarray(m.filter(ImageFilter.GaussianBlur(26)), float)/255
    halo = np.asarray(m.filter(ImageFilter.GaussianBlur(90)), float)/255
    f = 0.7*core**1.6 + 0.4*halo**2.0
    # fade: the lower-right side thins out into scattered dust
    yy, xx = np.mgrid[0:H, 0:W]
    u = ((xx - CX)*0.8 + (yy - CY)*0.6)/700
    fade = np.clip(1 - 0.9*np.clip(u - 0.05, 0, 1)**1.0, 0.08, 1)
    # gentle large-scale clumping, like spray paint
    noise = Image.fromarray((rng.random((H//40, W//40))*255).astype(np.uint8)).resize((W, H), Image.BICUBIC)
    n = np.asarray(noise.filter(ImageFilter.GaussianBlur(20)), float)/255
    return np.clip(f*fade*(0.75 + 0.5*n), 0, 1)


def dots():
    f = density()
    N = 420000
    x = rng.uniform(0, W, N); y = rng.uniform(0, H, N)
    p = f[y.astype(int), x.astype(int)]
    keep = rng.random(N) < p**1.6 * 0.33
    x, y, p = x[keep], y[keep], p[keep]
    r = np.clip(rng.lognormal(np.log(3.0), 0.40, len(x)) * (0.7 + 0.5*p), 1.4, 9)
    return x, y, r


def render(color, path, transparent=False, ss=2):
    x, y, r = dots_cache
    im = Image.new("RGBA", (W*ss, H*ss), (255, 255, 255, 0 if transparent else 255))
    d = ImageDraw.Draw(im)
    c = tuple(int(color[i:i+2], 16) for i in (1, 3, 5)) + (255,)
    for xi, yi, ri in zip(x*ss, y*ss, r*ss):
        d.ellipse((xi-ri, yi-ri, xi+ri, yi+ri), fill=c)
    im.resize((W, H), Image.LANCZOS).save(path)


def svg(color, path):
    x, y, r = dots_cache
    body = "".join(f'<circle cx="{a:.1f}" cy="{b:.1f}" r="{c:.1f}"/>' for a, b, c in zip(x, y, r))
    open(path, "w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
                          f'width="{W}" height="{H}"><title>Star</title><g fill="{color}">{body}</g></svg>')


if __name__ == "__main__":
    import sys
    out = sys.argv[1]
    dots_cache = dots()
    print("dots:", len(dots_cache[0]))
    for name, col in (("magenta", "#D4145A"), ("black", "#000000")):
        render(col, f"{out}/star-{name}.png")
        render(col, f"{out}/star-{name}-transparent.png", transparent=True)
        svg(col, f"{out}/star-{name}.svg")
