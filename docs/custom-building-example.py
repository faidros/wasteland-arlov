"""Example custom building: a church with a steep roof and two towers with copper spires.

Copy to cities/<slug>/custom/<building id>.py (find the id with `python3 wasteland.py buildings
<slug> --name "kyrka"`), adapt, then `python3 wasteland.py rebuild <slug>` and
`python3 wasteland.py render <slug> --near "<name>"`. Coordinates are metres: x east, y north.

Available: ctx (footprint, b, geo, mat), Geo, math, citylib (frame, local, square, facade,
gable_roof, spire). Material roles: 'upper', 'ground', 'blank', 'roof', 'flat' or library names.
"""
ring = ctx.footprint['outer']
cx, cy, a, L, W = citylib.frame(ring)
nave = 15.0                                   # eaves height of the nave, metres

# Walls follow the real footprint. One texture row over the whole wall height stretches each
# window bay into a tall church window.
citylib.facade(ctx.geo, ring, -0.3, nave, 'upper', bay=5.0, storey=nave)
citylib.gable_roof(ctx.geo, cx, cy, a, L, W, nave, rise=min(W * 0.5, 9.0), mat='roof', gable='blank')

# Two towers at the western end (swap the sign of `end` for the eastern end).
end = -1 if math.cos(a) > 0 else 1
side = min(7.0, W * 0.45)
for across in (-1, 1):
    tx, ty = citylib.local(cx, cy, a, end * (L / 2 - side / 2), across * (W / 2 - side / 2))
    tower = citylib.square(tx, ty, side, a)
    top = nave * 2.3
    citylib.facade(ctx.geo, tower, -0.3, top, 'blank', bay=3.4, storey=3.0)
    ctx.geo.polygon(citylib.ccw(tower), top, 'flat')
    citylib.spire(ctx.geo, tx, ty, side + 0.6, top, side * 2.6, a, 'M_Roof_Metal_copper')
