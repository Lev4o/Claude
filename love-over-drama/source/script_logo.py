"""'Love Over Drama' script logo with flourishes."""
from shapely.ops import unary_union
from shapely import affinity
import script_glyphs as S
from ld_mark import save

HI = {c for c, sp in S.GLYPHS.items() if sp.get('hi')}


def set_words(text, x=0):
    prev, parts, marks = None, [], {}
    for i, c in enumerate(text):
        if c == ' ':
            x += 300; prev = None; continue
        sp = S.GLYPHS[c]
        g = S.build(sp, entry_hi=(prev in HI and c.islower()))
        parts.append(affinity.translate(g, x, 0))
        marks[i] = x
        x += sp['adv']
        prev = c
    return unary_union(parts), marks, x


def flourish(pts, shade=30):
    return S.slant(S.pen(pts, shade=shade))


def logo(swashes=True):
    word, m, end = set_words("Love Over Drama")
    parts = [word]
    if swashes:
        xL, xD = m[0], m[10]
        # entry loop: rises from the left, arcs over "ove" and rolls back in
        parts.append(flourish([(xL - 300, 150), (xL - 160, 420), (xL + 120, 700),
                               (xL + 560, 860), (xL + 1100, 850), (xL + 1380, 760),
                               (xL + 1390, 660), (xL + 1220, 610), (xL + 1020, 660)], shade=34))
        # hairline crown over "rama", answering the D
        parts.append(flourish([(xD + 300, 770), (xD + 720, 860), (xD + 1250, 830),
                               (xD + 1520, 730), (xD + 1510, 640), (xD + 1340, 610),
                               (xD + 1180, 670)], shade=30))
        # long underline swash returning from the final "a"
        parts.append(flourish([(end, 80), (end + 140, 60), (end + 170, -60), (end - 60, -210),
                               (end - 700, -270), (end - 1500, -240), (end - 2300, -150),
                               (end - 2700, -60), (end - 2850, 20)], shade=34))
    return unary_union(parts)


if __name__ == "__main__":
    out = "../script/logo"
    save("love-over-drama-script-flourished", [(logo(True), "#000000")], out)
    save("love-over-drama-script-clean", [(logo(False), "#000000")], out)
