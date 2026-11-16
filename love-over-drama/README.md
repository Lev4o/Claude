# Love over drama: Gothic display font and logo

Ornate Gothic capitals based on a carved-iron letter "A": fluted strokes, flared crowned heads,
clawed feet, side curls and fleur-de-lis ornaments.

- `font/LoveOverDramaGothic-Regular.otf` / `.ttf`: installable font. A–Z capitals; lowercase
  keys type smaller capitals. Also includes `. , - ' !` and a fleur-de-lis on `*` and U+269C.
- `logo/`: stacked and horizontal lockups as SVG (vector), PNG on white, and transparent PNG.
- `source/`: Python that generates everything (`pip install shapely fonttools pillow`):
  `python3 build_font.py ../font && python3 logo.py`

## LD monogram (`ld-mark/`)
Clean geometric redraws of the hand-drawn LD oval mark (`python3 source/ld_mark.py`):
1. Pure (solid oval) · 2. Circle badge · 3. Outline · 4. Shadow mark + gothic wordmark.
Each comes as SVG, PNG on white, and transparent PNG; `ld-mark-options.png` compares all four.

## LD concepts, round 2 (`ld-mark-v2/`)
Four new directions without the oval (`python3 source/ld_concepts.py`):
1. Heart: an L and a D turned 45° form a heart; the D rests on the L's foot.
2. L over D: a tall gothic L holding a small D, in a thin double ring.
3. Crest: split gothic shield with L and D carved out, fleur-de-lis on top.
4. Single line: one continuous line draws the L, runs along the base and becomes the D.

## LD concepts, round 3 (`ld-mark-v3/`)
`python3 source/ld_concepts2.py`
5. L over D: gothic L above a rule, D below, a literal "L over D".
6. Overlap: bold geometric L and D overlapping, the shared corner knocked out in white.
7. Heart cut-out: solid heart with a clean LD cut out of it.
8. Wax seal: scalloped seal, gothic LD centre, LOVE OVER DRAMA around the edge.

## LD concepts, round 4 (`ld-mark-v4/`)
`python3 source/ld_concepts3.py`
9. Gothic heart: double-line heart frame with the gothic LD inside.
10. Banner: gothic LD above a forked ribbon reading LOVE OVER DRAMA.
11. Diamond: double-line diamond frame, fleur-de-lis at top and bottom points.
12. Cathedral window: pointed gothic arch split by a mullion, rose window above, L and D in each light.
