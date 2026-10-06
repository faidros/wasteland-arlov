"""housekit: hand-model an ordinary town house from a short description (used by cities/<slug>/custom/*.py).

    import housekit
    housekit.build(ctx, levels=2, wall='M_Wall_Wood_petrol_Blank', roof={'shape': 'gabled', 'pitch': 40},
                   shop=True, awnings='M_Roof_Metal_red', dormers=[0.3, 0.7], chimneys=[(0.6, 0.5)])

What it draws, from the footprint (any ring; L- and T-shapes are cut into rectangles along the
building's main axis):
- walls with real window openings (reveals, glass, frames, glazing bars, sills), corner boards on
  timber houses, a plinth, a cornice; party walls next to other buildings stay blank;
- the ground floor towards the street as shop windows with a sign band, door and (striped) awnings
  when shop=True — the street sides are found from the city's roads;
- one roof per rectangle: gabled, hipped, mansard (brutet tak) or flat with a parapet; overhangs,
  fascias, gutters, gable windows, ridge caps;
- optional dormers, a cross gable (frontkvist) on the street side, chimneys, balconies, a veranda
  with a balcony on top, a sign with text.
Coordinates are metres, x east, y north (Blender z up). Materials are library names
(see citylib.MaterialLibrary), e.g. 'M_Wall_Wood_falu_Blank', 'M_Roof_Tiles_red'.
"""
import math
import random

import citylib

GLASS = 'M_Window_Pane'
GLASS_UV = [(0.2, 0.42), (0.8, 0.42), (0.8, 0.9), (0.2, 0.9)]
GUTTER = 'M_Fixture_Metal'


# ------------------------------------------------------------------------------------------ small geometry helpers
class Wall:
    """Vertical plane p→q; x along it, z up, d > 0 outwards (to the right of p→q on a CCW ring)."""
    def __init__(self, G, p, q):
        self.G, self.p, self.L = G, p, math.dist(p[:2], q[:2])
        self.t = ((q[0] - p[0]) / max(self.L, 1e-6), (q[1] - p[1]) / max(self.L, 1e-6))
        self.n = (self.t[1], -self.t[0])
        self.ang = math.atan2(self.t[1], self.t[0])

    def at(self, x, z, d=0.0):
        return (self.p[0] + self.t[0] * x + self.n[0] * d, self.p[1] + self.t[1] * x + self.n[1] * d, z)

    def poly(self, pts, mat, d=0.0, scale=3.0, uv=None):
        self.G.face([self.at(x, z, d) for x, z in pts], mat, uv or [(x / scale, z / scale) for x, z in pts])

    def rect(self, x0, x1, z0, z1, mat, d=0.0, scale=3.0, uv=None):
        if x1 - x0 > 1e-3 and z1 - z0 > 1e-3:
            self.poly([(x0, z0), (x1, z0), (x1, z1), (x0, z1)], mat, d, scale, uv)

    def ledge(self, x0, x1, z0, z1, mat, d1, ends=False):
        """A proud strip with its top (and optionally end) faces."""
        self.rect(x0, x1, z0, z1, mat, d1)
        self.G.face([self.at(x0, z1, d1), self.at(x1, z1, d1), self.at(x1, z1, 0), self.at(x0, z1, 0)], mat, uvscale=1.0)
        self.G.face([self.at(x0, z0, 0), self.at(x1, z0, 0), self.at(x1, z0, d1), self.at(x0, z0, d1)], mat, uvscale=1.0)
        if ends:
            self.G.face([self.at(x0, z0, 0), self.at(x0, z0, d1), self.at(x0, z1, d1), self.at(x0, z1, 0)], mat, uvscale=1.0)
            self.G.face([self.at(x1, z0, d1), self.at(x1, z0, 0), self.at(x1, z1, 0), self.at(x1, z1, d1)], mat, uvscale=1.0)

    def band(self, x0, x1, z0, z1, mat, holes, scale=3.0):
        """Wall area with rectangular holes [(a, b, za, zb)] cut out; holes may overlap in x at different heights."""
        xs = sorted({x0, x1, *[h[0] for h in holes], *[h[1] for h in holes]})
        xs = [x for x in xs if x0 <= x <= x1]
        for a, b in zip(xs, xs[1:]):
            if b - a < 1e-4:
                continue
            gaps = sorted((max(za, z0), min(zb, z1)) for ha, hb, za, zb in holes
                          if ha <= a + 1e-6 and hb >= b - 1e-6 and zb > z0 and za < z1)
            zc = z0
            for za, zb in gaps:
                if za > zc:
                    self.rect(a, b, zc, za, mat, scale=scale)
                zc = max(zc, zb)
            if z1 > zc:
                self.rect(a, b, zc, z1, mat, scale=scale)


def arch(xc, z0, w, h, n=8):
    r = w / 2
    zs = z0 + h - r
    return [(xc - r, z0), (xc + r, z0)] + [(xc + r * math.cos(math.pi * i / n), zs + r * math.sin(math.pi * i / n)) for i in range(n + 1)]


def inside(pt, ring):
    x, y, ok = pt[0], pt[1], False
    for (x1, y1), (x2, y2) in zip(ring, ring[1:] + ring[:1]):
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ok = not ok
    return ok


def seg_dist(p, a, b):
    ax, ay, bx, by = a[0], a[1], b[0], b[1]
    L2 = (bx - ax) ** 2 + (by - ay) ** 2 or 1e-9
    t = max(0.0, min(1.0, ((p[0] - ax) * (bx - ax) + (p[1] - ay) * (by - ay)) / L2))
    return math.dist(p, (ax + t * (bx - ax), ay + t * (by - ay)))


def housekit_glass():
    return GLASS


STREET_KINDS = {'primary', 'secondary', 'tertiary', 'residential', 'unclassified', 'living_street', 'pedestrian', 'service', 'trunk', 'footway'}


# ------------------------------------------------------------------------------------------ the builder
class House:
    def __init__(self, ctx, ring=None, levels=2, storey=3.0, ground=None, wall='M_Wall_Plaster_ivory_Blank',
                 trim='M_Wall_Plaster_white_Blank', frame=None, plinth='M_Concrete', door='M_Wall_Wood_brown_Blank',
                 timber=None, shop=False, street=None, party=None, lower=None):
        self.ctx, self.G = ctx, ctx.geo
        self.ring = citylib.ccw([tuple(p) for p in (ring or ctx.footprint['outer'])])
        self.levels, self.storey = levels, storey
        self.ground = ground or (3.8 if shop else 3.2)
        self.eave = self.ground + (levels - 1) * storey
        self.wall, self.trim, self.plinth, self.door = wall, trim, plinth, door
        self.lower = lower                        # a different wall material on the ground storey (two-tone houses)
        self.frame = frame or trim
        self.timber = ('Wood' in wall) if timber is None else timber
        self.shop = shop
        cx, cy, a, L, W = citylib.frame(self.ring)
        self.cx, self.cy, self.a, self.L, self.W = cx, cy, a, L, W
        self.walls = [Wall(self.G, p, q) for p, q in zip(self.ring, self.ring[1:] + self.ring[:1])]
        self.street = set(street) if street is not None else self._street_sides()
        self.party = set(party) if party is not None else self._party_walls()
        self.rng = random.Random(str(ctx.id))
        self.curtains = 0.4                       # share of windows with a light curtain/blind in the top
        self.surrounds = False                    # white window surrounds on rendered/brick houses

    # ---- frame helpers
    def P(self, u, w, z=0.0):
        c, s = math.cos(self.a), math.sin(self.a)
        return (self.cx + u * c - w * s, self.cy + u * s + w * c, z)

    def uw(self, p):
        dx, dy = p[0] - self.cx, p[1] - self.cy
        c, s = math.cos(self.a), math.sin(self.a)
        return dx * c + dy * s, -dx * s + dy * c

    def _street_sides(self):
        roads = [r for r in self.ctx.data.get('roads', []) if r.get('kind') in STREET_KINDS]
        out = set()
        for i, w in enumerate(self.walls):
            if w.L < 2.5:
                continue
            m = w.at(w.L / 2, 0, 3.0)
            best = min((seg_dist(m[:2], a, b) for r in roads for a, b in zip(r['p'], r['p'][1:])), default=99)
            back = w.at(w.L / 2, 0, -3.0)
            best_back = min((seg_dist(back[:2], a, b) for r in roads for a, b in zip(r['p'], r['p'][1:])), default=99)
            if best < 16 and best < best_back:
                out.add(i)
        return out

    def _party_walls(self):
        others = [b['footprint']['outer'] for b in self.ctx.data.get('buildings', [])
                  if b.get('id') != self.ctx.id and b.get('footprint')]
        out = set()
        for i, w in enumerate(self.walls):
            probe = w.at(w.L / 2, 0, 0.4)[:2]
            for ring in others:
                xs = [p[0] for p in ring]
                ys = [p[1] for p in ring]
                if min(xs) - 1 < probe[0] < max(xs) + 1 and min(ys) - 1 < probe[1] < max(ys) + 1 and inside(probe, [tuple(p) for p in ring]):
                    out.add(i)
                    break
        return out

    # ---- openings
    def window(self, w, xc, z0, width, height, kind='sash', reveal=None):
        G = self.G
        depth = reveal if reveal is not None else (0.12 if self.timber else 0.18)
        rv = self.trim if self.timber else self.wall
        d = -depth
        x0, x1, z1 = xc - width / 2, xc + width / 2, z0 + height
        if kind == 'arched':
            shape = arch(xc, z0, width, height)
            for p, q in zip(shape, shape[1:] + shape[:1]):
                G.face([w.at(*p, 0), w.at(*q, 0), w.at(*q, d), w.at(*p, d)][::-1], rv, uvscale=1.0)
            w.poly(shape, GLASS, d, uv=[(0.2 + 0.6 * (x - x0) / width, 0.42 + 0.48 * (z - z0) / height) for x, z in shape])
        else:
            G.face([w.at(x0, z0, 0), w.at(x0, z0, d), w.at(x0, z1, d), w.at(x0, z1, 0)], rv, uvscale=1.0)
            G.face([w.at(x1, z0, 0), w.at(x1, z1, 0), w.at(x1, z1, d), w.at(x1, z0, d)], rv, uvscale=1.0)
            G.face([w.at(x0, z0, 0), w.at(x1, z0, 0), w.at(x1, z0, d), w.at(x0, z0, d)], rv, uvscale=1.0)
            G.face([w.at(x0, z1, 0), w.at(x0, z1, d), w.at(x1, z1, d), w.at(x1, z1, 0)], rv, uvscale=1.0)
            w.rect(x0, x1, z0, z1, GLASS, d, uv=GLASS_UV)
        if kind in ('sash', 'modern') and self.rng.random() < self.curtains:
            drop = (z1 - z0) * self.rng.uniform(0.18, 0.45)
            w.rect(x0 + 0.04, x1 - 0.04, z1 - drop, z1 - 0.04, self.rng.choice(('M_Wall_Plaster_white_Blank', 'M_Wall_Plaster_ivory_Blank')), d + 0.01)
        f, fd = 0.07, d + 0.025
        top = z1 - (width / 2 if kind == 'arched' else 0)
        if kind != 'shop':
            w.rect(x0, x1, z0, z0 + f, self.frame, fd)
            w.rect(x0, x0 + f, z0, top, self.frame, fd)
            w.rect(x1 - f, x1, z0, top, self.frame, fd)
            if kind != 'arched':
                w.rect(x0, x1, z1 - f, z1, self.frame, fd)
            if kind in ('sash', 'arched') and width > 0.8:
                w.rect(xc - 0.035, xc + 0.035, z0, top, self.frame, fd)
            if kind == 'sash':
                for r in (0.62,) if height < 1.7 else (0.36, 0.68):
                    zr = z0 + (top - z0) * r
                    w.rect(x0, x1, zr - 0.03, zr + 0.03, self.frame, fd)
            w.ledge(x0 - 0.06, x1 + 0.06, z0 - 0.06, z0, self.trim if self.timber else 'M_Fixture_Metal', 0.08, ends=True)
            if self.timber or self.surrounds:
                tw = 0.1 if self.timber else 0.15
                w.rect(x0 - tw, x0, z0 - 0.06, z1 + tw, self.trim, 0.03)
                w.rect(x1, x1 + tw, z0 - 0.06, z1 + tw, self.trim, 0.03)
                w.rect(x0 - tw, x1 + tw, z1, z1 + tw, self.trim, 0.03)
        else:
            w.rect(x0, x1, z1 - 0.08, z1, self.frame, fd)
            w.rect(x0, x1, z0, z0 + 0.12, self.frame, fd)
            for k in (x0, x1 - 0.08):
                w.rect(k, k + 0.08, z0, z1, self.frame, fd)

    # ---- walls
    def facades(self, window=(1.2, 1.6), pitch=2.9, kind='sash', margin=0.9, shop_bays=3.4, door_at=0.5,
                sign=None, sign_mat='M_Roof_Metal_black', awnings=None, cornice=True, plinth_h=0.5,
                skip=None, upper_kind=None, upper_awnings=False, entrance=True, panels=None, downpipes=True,
                canopy='M_Roof_Metal_black'):
        """Walls with windows; street-side ground floors become shopfronts when shop=True. Houses get an
        entrance door (with a small canopy and steps) on their main wall, optional coloured panels under
        the windows (bröstningar) and downpipes at the corners of the street walls."""
        skip = skip or {}
        ww, wh = window
        cands = [i for i in sorted(self.street, key=lambda i: -self.walls[i].L) if i not in self.party]
        if not cands:
            cands = sorted((i for i in range(len(self.walls)) if i not in self.party), key=lambda i: -self.walls[i].L)
        door_wall = cands[0] if (entrance and cands and not (self.shop and cands[0] in self.street)) else None
        for i, w in enumerate(self.walls):
            if w.L < 0.05:
                continue
            if i in self.party:
                w.rect(0, w.L, -0.3, self.eave, self.wall)
                continue
            holes, opens = [], []
            usable = [(margin, w.L - margin)]
            for a, b in skip.get(i, []):
                usable = [(lo, hi) for lo, hi in sum(([(lo, min(hi, a - 0.3)), (max(lo, b + 0.3), hi)] for lo, hi in usable), []) if hi - lo > 0.5]
            for s in range(self.levels):
                z0 = 0.0 if s == 0 else self.ground + (s - 1) * self.storey
                z1 = self.ground if s == 0 else z0 + self.storey
                if s == 0 and self.shop and i in self.street:
                    n = max(1, round((w.L - 0.8) / shop_bays))
                    bw = (w.L - 0.8) / n
                    for k in range(n):
                        a = 0.4 + k * bw + 0.25
                        b = 0.4 + (k + 1) * bw - 0.25
                        top = z1 - 0.9
                        holes.append((a, b, 0.45 if abs((k + 0.5) / n - door_at) > 0.5 / n else 0.0, top))
                        opens.append(('shop' if holes[-1][2] > 0 else 'door', a, b, holes[-1][2], top))
                    continue
                if w.L < 1.8:
                    continue
                for lo, hi in usable:
                    room = hi - lo
                    n = int((room - ww) // pitch) + 1 if room >= ww else 0
                    if n <= 0:
                        continue
                    start = lo + (room - ((n - 1) * pitch + ww)) / 2
                    slots = [start + k * pitch + ww / 2 for k in range(n)]
                    door_x = None
                    if s == 0 and i == door_wall and slots and not any(o[0] == 'entry' for o in opens):
                        door_x = min(slots, key=lambda x: abs(x - w.L * door_at))
                    for xc in slots:
                        zs = z0 + (0.95 if s == 0 else 0.85)
                        h = min(wh, z1 - zs - 0.35)
                        if xc == door_x:
                            dh = min(2.25, z1 - 0.4)
                            holes.append((xc - 0.55, xc + 0.55, 0.0, dh))
                            opens.append(('entry', xc - 0.55, xc + 0.55, 0.0, dh))
                            continue
                        holes.append((xc - ww / 2, xc + ww / 2, zs, zs + h))
                        opens.append((upper_kind or kind if s > 0 else kind, xc - ww / 2, xc + ww / 2, zs, zs + h))
                        if panels:
                            prev_top = zs - (self.storey if s > 1 else (self.ground if s == 1 else 9)) + h
                            w.rect(xc - ww / 2, xc + ww / 2, max(prev_top + 0.12, plinth_h + 0.05), zs - 0.08, panels, 0.015)
            if self.lower:
                w.band(0, w.L, -0.3, self.ground, self.lower, holes)
                w.band(0, w.L, self.ground, self.eave, self.wall, holes)
            else:
                w.band(0, w.L, -0.3, self.eave, self.wall, holes)
            for o in opens:
                kd, a, b, za, zb = o
                if kd == 'shop':
                    self.window(w, (a + b) / 2, za, b - a, zb - za, 'shop', reveal=0.1)
                    w.rect(a - 0.05, b + 0.05, 0.0, za, self.plinth, 0.02)
                elif kd == 'door':
                    w.rect(a, b, 0.0, zb, GLASS, -0.12, uv=GLASS_UV)
                    m = (a + b) / 2
                    w.rect(m - 0.04, m + 0.04, 0.0, zb, self.frame, -0.08)
                    w.rect(a, b, zb - 0.1, zb, self.frame, -0.08)
                    for x in (a, b - 0.09):
                        w.rect(x, x + 0.09, 0.0, zb, self.frame, -0.08)
                    for x, s_ in ((a, 1), (b, -1)):
                        self.G.face([w.at(x, 0.0, 0), w.at(x, 0.0, -0.12), w.at(x, zb, -0.12), w.at(x, zb, 0)][::s_], self.wall, uvscale=1.0)
                elif kd == 'entry':
                    d = -0.15
                    for x, s_ in ((a, 1), (b, -1)):
                        self.G.face([w.at(x, 0.0, 0), w.at(x, 0.0, d), w.at(x, zb, d), w.at(x, zb, 0)][::s_], self.trim if self.timber else self.wall, uvscale=1.0)
                    self.G.face([w.at(a, zb, 0), w.at(a, zb, d), w.at(b, zb, d), w.at(b, zb, 0)], self.trim if self.timber else self.wall, uvscale=1.0)
                    w.rect(a, b, 0.0, zb, self.door, d, scale=1.0)
                    w.rect(a + 0.15, b - 0.15, zb - 0.75, zb - 0.2, GLASS, d + 0.02, uv=GLASS_UV)
                    w.rect(a + 0.12, b - 0.12, 0.25, zb - 0.95, self.door, d + 0.03, scale=1.0)
                    w.rect(a - 0.12, b + 0.12, zb, zb + 0.12, self.trim, 0.04)
                    c = w.at((a + b) / 2, zb + 0.35, 0.55)
                    self.G.box(c, (b - a + 0.8, 1.1, 0.1), canopy, w.ang, uvscale=1.0)
                    for k in range(2):
                        st = w.at((a + b) / 2, 0.0, 0.3 + 0.32 * (1 - k))
                        self.G.box((st[0], st[1], -0.05 + 0.16 * k), (b - a + 0.6, 0.35 + 0.64 * (1 - k), 0.16), 'M_Concrete', w.ang, uvscale=1.0)
                else:
                    self.window(w, (a + b) / 2, za, b - a, zb - za, kd)
            if downpipes and i in self.street and w.L > 5 and not self.timber:
                for x in (0.25, w.L - 0.25):
                    p = w.at(x, 0.0, 0.1)
                    self.G.cyl(p[0], p[1], 0.15, 0.05, self.eave - 0.4, GUTTER, seg=6, cap=False)
            if self.shop and i in self.street:
                w.ledge(0, w.L, self.ground - 0.75, self.ground - 0.15, sign_mat, 0.1)
                if awnings:
                    for o in opens:
                        if o[0] in ('shop', 'door') or upper_awnings:
                            self.awning(w, o[1], o[2], o[4] + 0.05, awnings, depth=1.0 if o[0] in ('shop', 'door') else 0.6,
                                        drop=0.7 if o[0] in ('shop', 'door') else 0.45)
            if plinth_h:
                w.ledge(0, w.L, -0.3, plinth_h, self.plinth, 0.04)
            if cornice:
                w.ledge(-0.05, w.L + 0.05, self.eave - 0.35, self.eave - 0.1, self.trim, 0.14)
            if self.timber:
                w.rect(0, 0.14, plinth_h, self.eave - 0.3, self.trim, 0.025)
                w.rect(w.L - 0.14, w.L, plinth_h, self.eave - 0.3, self.trim, 0.025)
                if self.levels > 1:
                    w.ledge(0, w.L, self.ground - 0.05, self.ground + 0.08, self.trim, 0.05)
        if sign:
            self.sign(*sign) if isinstance(sign, tuple) else self.sign(sign)

    def stair_bay(self, wall, x, width=3.0, depth=0.5, mat='M_Wall_Plaster_red_Blank', glazed=False):
        """A projecting stair-hall bay the full height of the wall, with its own narrow windows (or a glazed strip)."""
        w = self.walls[wall]
        a, b, top = x - width / 2, x + width / 2, self.eave + 0.3
        bay = Wall(self.G, w.at(a, 0, depth)[:2], w.at(b, 0, depth)[:2])
        bay.rect(0, width, -0.3, top, mat)
        for (p, q) in ((w.at(a, 0, 0), w.at(a, 0, depth)), (w.at(b, 0, depth), w.at(b, 0, 0))):
            Wall(self.G, p[:2], q[:2]).rect(0, depth, -0.3, top, mat)
        self.G.face([w.at(a, top, 0), w.at(b, top, 0), w.at(b, top, depth), w.at(a, top, depth)][::-1], 'M_Roof_Metal_black', uvscale=1.0)
        if glazed:
            bay.rect(0.35, width - 0.35, 0.6, top - 0.6, 'M_Wall_Glass_blue_Blank', 0.02)
        else:
            for s in range(self.levels):
                zc = (self.ground + (s - 1) * self.storey + self.storey * 0.55) if s else 2.6
                bay.rect(width / 2 - 0.35, width / 2 + 0.35, zc - 0.6, zc + 0.6, housekit_glass(), 0.03, uv=GLASS_UV)
                bay.rect(width / 2 - 0.42, width / 2 + 0.42, zc - 0.67, zc + 0.67, self.trim, 0.015)
            bay.rect(width / 2 - 0.6, width / 2 + 0.6, 0.0, 2.2, self.door, 0.02, scale=1.0)

    def garage(self, wall, x, width=2.6, height=2.3, mat='M_Wall_Wood_white_Blank'):
        """A garage or barn door (horizontal panels, recessed); pair with facades(skip={wall: [(x0, x1)]})."""
        w = self.walls[wall]
        a, b, d = x - width / 2, x + width / 2, -0.12
        for xx, s_ in ((a, 1), (b, -1)):
            self.G.face([w.at(xx, 0.0, 0), w.at(xx, 0.0, d), w.at(xx, height, d), w.at(xx, height, 0)][::s_], self.trim, uvscale=1.0)
        self.G.face([w.at(a, height, 0), w.at(a, height, d), w.at(b, height, d), w.at(b, height, 0)], self.trim, uvscale=1.0)
        w.rect(a, b, 0.0, height, mat, d, scale=1.0)
        for k in range(1, 5):
            z = height * k / 5
            w.rect(a + 0.05, b - 0.05, z - 0.025, z + 0.025, self.trim, d + 0.02)
        w.rect(a - 0.12, b + 0.12, height, height + 0.12, self.trim, 0.03)
        w.rect(a - 0.12, a, 0.0, height, self.trim, 0.03)
        w.rect(b, b + 0.12, 0.0, height, self.trim, 0.03)

    def awning(self, w, a, b, z, mats, depth=1.0, drop=0.7):
        mats = mats if isinstance(mats, (list, tuple)) else [mats]
        n = max(1, round((b - a) / 0.32))
        for k in range(n):
            x0 = a - 0.05 + (b - a + 0.1) * k / n
            x1 = a - 0.05 + (b - a + 0.1) * (k + 1) / n
            m = mats[k % len(mats)]
            self.G.face([w.at(x0, z - drop, depth), w.at(x1, z - drop, depth), w.at(x1, z, 0.03), w.at(x0, z, 0.03)], m, uvscale=1.0)
            self.G.face([w.at(x1, z - drop, depth), w.at(x0, z - drop, depth), w.at(x0, z - drop - 0.18, depth), w.at(x1, z - drop - 0.18, depth)], m, uvscale=1.0)
        for x, s in ((a - 0.05, 1), (b + 0.05, -1)):
            self.G.face([w.at(x, z, 0.03), w.at(x, z - drop, depth), w.at(x, z - drop, 0.03)][::s], mats[0], uvscale=1.0)

    def sign(self, text, wall=None, x=None, z=None, size=0.55, mat='M_Roof_Metal_black', board=None):
        """Raised letters on a street wall (default: the longest street side, centred on the sign band)."""
        import bpy
        if wall is None:
            cands = sorted(self.street, key=lambda i: -self.walls[i].L) or [max(range(len(self.walls)), key=lambda i: self.walls[i].L)]
            wall = cands[0]
        w = self.walls[wall]
        x = w.L / 2 if x is None else x
        z = (self.ground - 0.62 if self.shop else self.ground + 0.2) if z is None else z
        cu = bpy.data.curves.new('wb_sign', 'FONT')
        cu.body, cu.size, cu.align_x, cu.resolution_u, cu.extrude = text, size, 'CENTER', 2, 0.015
        for path in ('/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf',
                     '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
            try:
                cu.font = bpy.data.fonts.load(path, check_existing=True)
                break
            except (RuntimeError, OSError):
                continue
        ob = bpy.data.objects.new('wb_sign', cu)
        bpy.context.scene.collection.objects.link(ob)
        ev = ob.evaluated_get(bpy.context.evaluated_depsgraph_get())
        me = ev.to_mesh()
        xs = [v.co.x for v in me.vertices] or [0]
        if board:
            w.rect(x + min(xs) - 0.2, x + max(xs) + 0.2, z - 0.15, z + size * 0.9, board, 0.13)
        for poly in me.polygons:
            self.G.face([w.at(x + me.vertices[i].co.x, z + me.vertices[i].co.y, 0.15 + me.vertices[i].co.z) for i in poly.vertices], mat, uvscale=0.5)
        ev.to_mesh_clear()
        bpy.data.objects.remove(ob)
        bpy.data.curves.remove(cu)

    # ---- roofs
    def rects(self):
        """Cut the footprint into rectangles along the main axis (u slices merged when their spans match)."""
        loc = [self.uw(p) for p in self.ring]
        us = sorted(u for u, _ in loc)
        cuts = [us[0]]
        for u in us[1:]:
            if u - cuts[-1] > 0.6:
                cuts.append(u)
        cuts[-1] = us[-1]
        slices = []
        for u0, u1 in zip(cuts, cuts[1:]):
            um = (u0 + u1) / 2
            xs = []
            for (ua, wa), (ub, wb) in zip(loc, loc[1:] + loc[:1]):
                if (ua > um) != (ub > um):
                    xs.append(wa + (wb - wa) * (um - ua) / (ub - ua))
            xs.sort()
            for w0, w1 in zip(xs[0::2], xs[1::2]):
                slices.append([u0, u1, w0, w1])
        merged = []
        for s in slices:
            for m in merged:
                if abs(m[1] - s[0]) < 0.05 and abs(m[2] - s[2]) < 0.6 and abs(m[3] - s[3]) < 0.6:
                    m[1] = s[1]
                    m[2], m[3] = min(m[2], s[2]), max(m[3], s[3])
                    break
            else:
                merged.append(list(s))
        return [m for m in merged if m[1] - m[0] > 0.8 and m[3] - m[2] > 0.8]

    def roof(self, shape='gabled', pitch=35, mat='M_Roof_Tiles_red', overhang=0.45, gable_mat=None, gable_windows=True,
             mansard_break=None, parapet=0.5, ridge='long', fascia=None, max_rise=6.0):
        """One roof per rectangle; returns the list of (rect, z_of(u, w)) for dormers and chimneys."""
        G, fascia = self.G, fascia or self.trim
        gable_mat = gable_mat or self.wall
        loc_ring = [self.uw(p) for p in self.ring]
        self.roofs = []
        for u0, u1, w0, w1 in self.rects():
            if shape == 'flat':
                pts = [self.P(u0, w0, self.eave), self.P(u1, w0, self.eave), self.P(u1, w1, self.eave), self.P(u0, w1, self.eave)]
                G.face(pts, 'M_Roof_Flat_gravel', uvscale=4.0)
                self.roofs.append(((u0, u1, w0, w1), lambda u, w: self.eave))
                continue
            along_u = (u1 - u0 >= w1 - w0) if ridge == 'long' else (u1 - u0 < w1 - w0)
            # work in a rectangle-local frame: s along the ridge, t across it
            if along_u:
                S0, S1, T0, T1 = u0, u1, w0, w1
                Q = lambda s, t, z=0.0: self.P(s, t, z)
            else:
                S0, S1, T0, T1 = w0, w1, -u1, -u0
                Q = lambda s, t, z=0.0: self.P(-t, s, z)
            ext = lambda s, t: not inside(Q(s, t)[:2], self.ring)
            o_t0 = overhang if ext((S0 + S1) / 2, T0 - 0.3) else 0.0
            o_t1 = overhang if ext((S0 + S1) / 2, T1 + 0.3) else 0.0
            end0, end1 = ext(S0 - 0.3, (T0 + T1) / 2), ext(S1 + 0.3, (T0 + T1) / 2)
            o_s0, o_s1 = (overhang if end0 else 0.0), (overhang if end1 else 0.0)
            hw, tm = (T1 - T0) / 2, (T0 + T1) / 2
            k = math.tan(math.radians(pitch))
            rise = min(hw * k, max_rise)
            k = rise / hw
            ze = self.eave
            hip = shape == 'hipped'
            sr0 = S0 + (hw if hip and end0 else 0.0)
            sr1 = S1 - (hw if hip and end1 else 0.0)
            if sr1 < sr0:
                sr0 = sr1 = (S0 + S1) / 2
            top = ze + rise
            za, zb = ze - o_t0 * k, ze - o_t1 * k
            ta, tb = T0 - o_t0, T1 + o_t1
            se0, se1 = S0 - o_s0, S1 + o_s1
            if shape == 'mansard':
                br = mansard_break or 0.35 * hw
                zb_ = ze + br * 2.2
                kb = 0.45
                rtop = zb_ + (hw - br) * kb
                for side, (tt, zz) in ((0, (ta, za)), (1, (tb, zb))):
                    ti = T0 + br if side == 0 else T1 - br
                    pts = [Q(se0, tt, zz), Q(se1, tt, zz), Q(se1, ti, zb_), Q(se0, ti, zb_)]
                    G.face(pts if side == 0 else pts[::-1], mat, uvscale=2.0)
                    pts = [Q(se0, ti, zb_), Q(se1, ti, zb_), Q(se1, tm, rtop), Q(se0, tm, rtop)]
                    G.face(pts if side == 0 else pts[::-1], mat, uvscale=2.0)
                for s_, flip in ((se0, True), (se1, False)):
                    if (s_ == se0 and end0) or (s_ == se1 and end1):
                        pts = [Q(s_, T0, ze), Q(s_, T1, ze), Q(s_, T1 - br, zb_), Q(s_, tm, rtop), Q(s_, T0 + br, zb_)]
                        G.face(pts[::-1] if flip else pts, gable_mat, uvscale=3.0)
                top = rtop
                zf = lambda s, t: ze + min(abs(t - T0), abs(T1 - t), br) * 2.2 + max(0.0, min(abs(t - T0), abs(T1 - t)) - br) * kb
            else:
                G.face([Q(se0, ta, za), Q(se1, ta, za), Q(sr1, tm, top), Q(sr0, tm, top)], mat,
                       [(se0 / 2, 0), (se1 / 2, 0), (sr1 / 2, (tm - ta) / 2), (sr0 / 2, (tm - ta) / 2)])
                G.face([Q(se1, tb, zb), Q(se0, tb, zb), Q(sr0, tm, top), Q(sr1, tm, top)], mat,
                       [(se1 / 2, 0), (se0 / 2, 0), (sr0 / 2, (tb - tm) / 2), (sr1 / 2, (tb - tm) / 2)])
                for s_, e_, sr, sgn in ((se0, end0, sr0, -1), (se1, end1, sr1, 1)):
                    if not e_:
                        continue
                    if hip:
                        pts = [Q(s_, tb, zb), Q(s_, ta, za), Q(sr, tm, top)] if sgn < 0 else [Q(s_, ta, za), Q(s_, tb, zb), Q(sr, tm, top)]
                        G.face(pts, mat, uvscale=2.0)
                    else:
                        se = S0 if sgn < 0 else S1
                        pts = [Q(se, T1, ze), Q(se, T0, ze), Q(se, tm, top)] if sgn < 0 else [Q(se, T0, ze), Q(se, T1, ze), Q(se, tm, top)]
                        G.face(pts, gable_mat, uvscale=3.0)
                        for tx, zx in ((ta, za), (tb, zb)):                        # bargeboards
                            G.face([Q(s_, tx, zx - 0.22), Q(s_, tm, top - 0.22), Q(s_, tm, top + 0.03), Q(s_, tx, zx + 0.03)], fascia, uvscale=1.0)
                            G.face([Q(s_, tx, zx + 0.03), Q(s_, tm, top + 0.03), Q(s_, tm, top - 0.22), Q(s_, tx, zx - 0.22)], fascia, uvscale=1.0)
                        if gable_windows and rise > 2.0 and hw > 2.5:
                            gw = Wall(G, Q(se, T0 if sgn > 0 else T1, 0), Q(se, T1 if sgn > 0 else T0, 0))
                            n = 2 if hw > 4.5 else 1
                            for j in range(n):
                                xc = gw.L / 2 + (j - (n - 1) / 2) * 1.8
                                self.window(gw, xc, ze + 0.5, 0.9, min(1.3, rise - 1.2), 'sash')
                zf = lambda s, t: ze + max(0.0, hw - abs(t - tm)) * k
                if sr1 - sr0 > 0.1:
                    mid = Q((sr0 + sr1) / 2, tm, top + 0.05)
                    p0, p1 = Q(sr0, tm, 0), Q(sr1, tm, 0)
                    G.box(mid, (sr1 - sr0, 0.3, 0.12), mat, math.atan2(p1[1] - p0[1], p1[0] - p0[0]), uvscale=1.0)
            # fascia, soffit and gutter along both eaves
            for tt, zz, inner in ((ta, za, T0), (tb, zb, T1)):
                if abs(tt - inner) < 1e-3:
                    continue
                A, B = Q(se0, tt, zz - 0.2), Q(se1, tt, zz - 0.2)
                G.face([A, B, Q(se1, tt, zz + 0.04), Q(se0, tt, zz + 0.04)][:: (1 if tt < tm else -1)], fascia, uvscale=1.0)
                G.face([Q(se0, inner, zz - 0.2), Q(se1, inner, zz - 0.2), B, A][:: (-1 if tt < tm else 1)], fascia, uvscale=1.0)
                L = math.dist(A[:2], B[:2])
                g = Q((se0 + se1) / 2, tt + (-0.08 if tt < tm else 0.08), zz - 0.12)
                G.box(g, (L, 0.14, 0.12), GUTTER, math.atan2(B[1] - A[1], B[0] - A[0]), uvscale=1.0)
            self.roofs.append(((S0, S1, T0, T1), zf, Q, along_u))
        return self.roofs

    def main_roof(self):
        return max(self.roofs, key=lambda r: (r[0][1] - r[0][0]) * (r[0][3] - r[0][2]))

    def street_roof(self):
        """(roof, side) of the pitched roof whose long eave runs along the longest street wall."""
        best = None
        for i in sorted(self.street, key=lambda i: -self.walls[i].L)[:1]:
            w = self.walls[i]
            for r in self.roofs:
                if len(r) < 4:
                    continue
                (S0, S1, T0, T1), _, _, along_u = r
                u, wv = self.uw(w.at(w.L / 2, 0, 0.0)[:2])
                s, t = (u, wv) if along_u else (wv, -u)
                if not (S0 - 1 <= s <= S1 + 1):
                    continue
                for side, T in ((0, T0), (1, T1)):
                    d = abs(t - T)
                    if best is None or d < best[0]:
                        best = (d, r, side)
        if best is None or best[0] > 1.5:
            m = self.main_roof()
            return m, self.street_side()
        return best[1], best[2]

    def dormers(self, positions, width=1.4, height=1.3, side='both', mat=None, roof_mat=None, kind='gable'):
        """Small dormers on the main roof at fractions along the ridge; side 'street', 'both', 0 or 1."""
        if side == 'street':
            roof, sd_ = self.street_roof()
            sides = (sd_,)
        else:
            roof = self.main_roof()
            sides = (0, 1) if side == 'both' else (side,)
        (S0, S1, T0, T1), zf, Q, _ = roof
        roof_mat = roof_mat or 'M_Roof_Tiles_red'
        mat = mat or self.wall
        tm = (T0 + T1) / 2
        for f in positions:
            s = S0 + (S1 - S0) * f
            for sd in sides:
                sg = -1 if sd == 0 else 1
                tf = (T0 + 0.9) if sd == 0 else (T1 - 0.9)
                zb = zf(s, tf) + 0.05
                zt = zb + height
                slope = max(0.3, (zf(s, tm) - self.eave) / ((T1 - T0) / 2))
                tb = tf - sg * height / slope
                if abs(tb - tm) > abs(tf - tm):
                    tb = tm
                hw = width / 2
                fw = Wall(self.G, Q(s - hw, tf)[:2], Q(s + hw, tf)[:2]) if sd == 0 else Wall(self.G, Q(s + hw, tf)[:2], Q(s - hw, tf)[:2])
                fw.band(0, width, zb, zt, mat, [(0.22, width - 0.22, zb + 0.25, zt - 0.2)])
                fw.rect(0.22, width - 0.22, zb + 0.25, zt - 0.2, GLASS, -0.05, uv=GLASS_UV)
                fw.rect(width / 2 - 0.03, width / 2 + 0.03, zb + 0.25, zt - 0.2, self.frame, -0.02)
                fw.rect(0.15, width - 0.15, zb + 0.2, zb + 0.28, self.trim, 0.02)
                for e in (-hw, hw):
                    self.G.face([Q(s + e, tf, zb), Q(s + e, tb, zt), Q(s + e, tf, zt)], mat, uvscale=2.0)
                if kind == 'gable':
                    rz = zt + width / 2 * 0.8
                    for e in (-hw - 0.1, hw + 0.1):
                        pts = [Q(s + e, tf - sg * 0.15, zt - 0.05), Q(s + e, tb, zt - 0.05), Q(s, tb, rz), Q(s, tf - sg * 0.15, rz)]
                        self.G.face(pts if (e > 0) == (sd == 0) else pts[::-1], roof_mat, uvscale=1.5)
                    gp = [Q(s - hw, tf, zt), Q(s + hw, tf, zt), Q(s, tf, rz)]
                    self.G.face(gp if sd == 0 else gp[::-1], mat, uvscale=1.5)
                else:
                    pts = [Q(s - hw - 0.1, tf - sg * 0.15, zt + 0.1), Q(s + hw + 0.1, tf - sg * 0.15, zt + 0.1), Q(s + hw + 0.1, tb, zt + 0.25), Q(s - hw - 0.1, tb, zt + 0.25)]
                    self.G.face(pts if sd == 1 else pts[::-1], roof_mat, uvscale=1.5)

    def street_side(self):
        """Which long side of the main roof (0 = T0, 1 = T1) faces the street (the longest street wall decides)."""
        (S0, S1, T0, T1), _, _, along_u = self.main_roof()
        for i in sorted(self.street, key=lambda i: -self.walls[i].L):
            w = self.walls[i]
            u, wv = self.uw(w.at(w.L / 2, 0, 1.0)[:2])
            t = wv if along_u else -u
            return 0 if abs(t - T0) < abs(t - T1) else 1
        return 0

    def cross_gable(self, frac=0.5, width=4.0, height=None, side='street', pitch=45, roof_mat=None, windows=2):
        """A frontkvist: the wall rises into the roof with its own gable, perpendicular to the main ridge."""
        if side == 'street':
            roof, sd = self.street_roof()
        else:
            roof, sd = self.main_roof(), side
        (S0, S1, T0, T1), zf, Q, _ = roof
        roof_mat = roof_mat or 'M_Roof_Tiles_red'
        sg = -1 if sd == 0 else 1
        tw = T0 if sd == 0 else T1
        tm = (T0 + T1) / 2
        s = S0 + (S1 - S0) * frac
        hw = width / 2
        ze = self.eave
        h = height or self.storey * 0.85
        zt = ze + h
        rz = zt + hw * math.tan(math.radians(pitch))
        wall = Wall(self.G, Q(s - hw, tw)[:2], Q(s + hw, tw)[:2]) if sd == 0 else Wall(self.G, Q(s + hw, tw)[:2], Q(s - hw, tw)[:2])
        holes = []
        n = windows
        for j in range(n):
            xc = width * (j + 0.5) / n
            holes.append((xc - 0.5, xc + 0.5, ze + 0.5, ze + 0.5 + min(1.5, h - 0.7)))
        wall.band(0, width, ze - 0.4, zt, self.wall, holes)
        wall.poly([(0, zt), (width, zt), (hw, rz)], self.wall)
        for a, b, za, zb in holes:
            self.window(wall, (a + b) / 2, za, b - a, zb - za, 'sash')
        if self.timber:
            wall.rect(0, 0.14, ze - 0.4, zt, self.trim, 0.025)
            wall.rect(width - 0.14, width, ze - 0.4, zt, self.trim, 0.025)
        # side cheeks down to the main roof and the kvist's own roof back to the main ridge
        for e in (-hw, hw):
            back = tw - sg * ((zt - ze) / max(0.2, (zf(s, tm) - ze) / ((T1 - T0) / 2)))
            pts = [Q(s + e, tw, ze), Q(s + e, back, zt), Q(s + e, tw, zt)]
            self.G.face(pts if (e > 0) == (sd == 0) else pts[::-1], self.wall, uvscale=2.0)
        o = 0.4
        for e in (-hw - o, hw + o):
            pts = [Q(s + e, tw + sg * o, zt - o * 0.9), Q(s + e, tm, zt - o * 0.9), Q(s, tm, rz), Q(s, tw + sg * o, rz)]
            self.G.face(pts if (e > 0) == (sd == 0) else pts[::-1], roof_mat, uvscale=2.0)
        for e in (-hw - o, hw + o):
            a = Q(s + e, tw + sg * o, zt - o * 0.9 - 0.2)
            b = Q(s, tw + sg * o, rz - 0.2)
            self.G.face([a, b, (b[0], b[1], b[2] + 0.25), (a[0], a[1], a[2] + 0.25)], self.trim, uvscale=1.0)
            self.G.face([(a[0], a[1], a[2] + 0.25), (b[0], b[1], b[2] + 0.25), b, a], self.trim, uvscale=1.0)
        return wall, ze, zt, rz

    def chimney(self, fu, fw, mat='M_Wall_Brick_red_Blank', size=(0.7, 0.9), above=1.0):
        (S0, S1, T0, T1), zf, Q, _ = self.main_roof()
        s, t = S0 + (S1 - S0) * fu, T0 + (T1 - T0) * fw
        top = zf(s, (T0 + T1) / 2) + above
        p = Q(s, t, 0)
        z0 = zf(s, t) - 0.3
        a = math.atan2(Q(1, 0, 0)[1] - Q(0, 0, 0)[1], Q(1, 0, 0)[0] - Q(0, 0, 0)[0])
        self.G.box((p[0], p[1], (z0 + top) / 2), (size[0], size[1], top - z0), mat, a, uvscale=1.0)
        self.G.box((p[0], p[1], top + 0.06), (size[0] + 0.15, size[1] + 0.15, 0.12), 'M_Concrete', a, uvscale=1.0)

    def balcony(self, wall, x, storey, width=2.6, depth=1.2, rail='M_Wall_Wood_white_Blank', slab='M_Concrete', glass=False):
        w = self.walls[wall]
        z = self.ground + (storey - 2) * self.storey          # storey 2 = the first floor above the ground floor
        a, b = x - width / 2, x + width / 2
        c = w.at(x, z - 0.1, depth / 2)
        self.G.box(c, (width, depth, 0.2), slab, w.ang, uvscale=1.0)
        for (p, q) in (((a, depth), (b, depth)), ((a, 0.0), (a, depth)), ((b, depth), (b, 0.0))):
            P0, P1 = w.at(p[0], z, p[1]), w.at(q[0], z, q[1])
            m = rail if not glass else 'M_Wall_Glass_blue_Blank'
            pts = [P0, P1, (P1[0], P1[1], z + 1.0), (P0[0], P0[1], z + 1.0)]
            self.G.face(pts, m, uvscale=1.0)
            self.G.face(pts[::-1], m, uvscale=1.0)
        w.poly([(x - 0.45, z), (x + 0.45, z), (x + 0.45, z + 2.1), (x - 0.45, z + 2.1)], GLASS, 0.02, uv=GLASS_UV)

    def _quad2(self, pts, mat):
        self.G.face(pts, mat, uvscale=1.0)
        self.G.face(pts[::-1], mat, uvscale=1.0)

    def _railing(self, w, a, b, z, h, mat, step=0.45):
        """Handrail, bottom rail and balusters between wall-frame points a=(x, d) and b=(x, d) at height z."""
        A0, B0 = w.at(a[0], z, a[1]), w.at(b[0], z, b[1])
        for zz, t in ((z + h - 0.08, 0.08), (z + 0.1, 0.06)):
            self._quad2([(A0[0], A0[1], zz), (B0[0], B0[1], zz), (B0[0], B0[1], zz + t), (A0[0], A0[1], zz + t)], mat)
        L = math.hypot(B0[0] - A0[0], B0[1] - A0[1])
        n = max(1, int(L / step))
        ang = math.atan2(B0[1] - A0[1], B0[0] - A0[0])
        for k in range(n + 1):
            f = k / n
            self.G.box((A0[0] + (B0[0] - A0[0]) * f, A0[1] + (B0[1] - A0[1]) * f, z + h / 2), (0.05, 0.05, h), mat, ang, uvscale=1.0)

    def gallery(self, wall, x0, x1, storey=2, depth=1.4, stair='left', mat='M_Wall_Wood_white_Blank', roof_mat=None):
        """An open access gallery (loftgång) on posts along an upper storey with an outside stair down to the
        ground at one end ('left' = before x0, 'right' = after x1, None) — the white timber galleries of Swedish
        1940s apartment houses. roof_mat adds a lean-to roof over it."""
        w, G = self.walls[wall], self.G
        z = self.ground + (storey - 2) * self.storey
        G.box(w.at((x0 + x1) / 2, z - 0.1, depth / 2), (x1 - x0, depth, 0.2), mat, w.ang, uvscale=1.0)
        top = z + self.storey - 0.3 if roof_mat else z + 1.0
        n = max(2, round((x1 - x0) / 2.4) + 1)
        for k in range(n):
            x = x0 + 0.08 + (x1 - x0 - 0.16) * k / (n - 1)
            G.box(w.at(x, top / 2, depth - 0.08), (0.14, 0.14, top), mat, w.ang, uvscale=1.0)
        if roof_mat:
            G.box(w.at((x0 + x1) / 2, top + 0.06, depth / 2 + 0.05), (x1 - x0 + 0.3, depth + 0.3, 0.12), roof_mat, w.ang, uvscale=1.0)
        self._railing(w, (x0, depth - 0.05), (x1, depth - 0.05), z, 1.0, mat)
        if stair != 'right':
            self._railing(w, (x1 - 0.05, 0.0), (x1 - 0.05, depth), z, 1.0, mat)
        if stair != 'left':
            self._railing(w, (x0 + 0.05, 0.0), (x0 + 0.05, depth), z, 1.0, mat)
        for k in range(max(1, round((x1 - x0) / 6))):                     # flat doors onto the gallery
            xd = x0 + (x1 - x0) * (k + 0.5) / max(1, round((x1 - x0) / 6))
            w.rect(xd - 0.5, xd + 0.5, z, z + 2.1, self.door, 0.03, scale=1.0)
            w.rect(xd - 0.6, xd + 0.6, z + 2.1, z + 2.2, mat, 0.04)
        if stair:
            s = -1 if stair == 'left' else 1
            xs = x0 if stair == 'left' else x1
            steps = max(3, math.ceil(z / 0.19))
            rise, tread = z / steps, 0.27
            run = tread * (steps - 1)
            d0, d1 = depth - 1.05, depth - 0.05
            for k in range(1, steps):
                xc = xs + s * (k - 0.5) * tread
                G.box(w.at(xc, z - k * rise - 0.03, (d0 + d1) / 2), (tread + 0.03, d1 - d0, 0.06), mat, w.ang, uvscale=1.0)
            xe = xs + s * run
            for d in (d0, d1):
                P, Q = w.at(xs, z, d), w.at(xe, 0.0, d)
                self._quad2([(P[0], P[1], z - 0.3), (Q[0], Q[1], -0.05), (Q[0], Q[1], 0.15), (P[0], P[1], z + 0.02)], mat)
            P, Q = w.at(xs, z, d1), w.at(xe, 0.0, d1)
            self._quad2([(P[0], P[1], z + 0.92), (Q[0], Q[1], 0.92), (Q[0], Q[1], 1.0), (P[0], P[1], z + 1.0)], mat)
            for f in (0.0, 0.35, 0.7, 1.0):
                x = xs + s * run * f
                zb = z * (1 - f)
                G.box(w.at(x, zb + 0.5, d1), (0.07, 0.07, 1.0), mat, w.ang, uvscale=1.0)

    def porch(self, wall, x, width=2.2, depth=1.5, height=None, post='M_Wall_Wood_white_Blank', roof_mat='M_Roof_Tiles_red',
              steps=2):
        """An entrance porch: a door with a small gabled roof on two posts and steps (pair with facades(skip=…))."""
        w, G = self.walls[wall], self.G
        zc = height or 2.6
        hw, rise, D = width / 2 + 0.15, width * 0.35, depth + 0.15
        w.rect(x - 0.5, x + 0.5, 0.16 * steps, 2.25, self.door, 0.02, scale=1.0)
        w.rect(x - 0.32, x + 0.32, 1.45, 2.05, GLASS, 0.03, uv=GLASS_UV)
        w.rect(x - 0.62, x + 0.62, 2.25, 2.37, self.trim, 0.04)
        for xx in (x - hw + 0.15, x + hw - 0.15):
            G.box(w.at(xx, (0.3 + zc) / 2, depth - 0.1), (0.13, 0.13, zc - 0.3), post, w.ang, uvscale=1.0)
        L = [w.at(x - hw, zc, 0), w.at(x, zc + rise, 0), w.at(x, zc + rise, D), w.at(x - hw, zc, D)]
        R = [w.at(x + hw, zc, D), w.at(x, zc + rise, D), w.at(x, zc + rise, 0), w.at(x + hw, zc, 0)]
        self._quad2(L, roof_mat)
        self._quad2(R, roof_mat)
        tri = [w.at(x - hw + 0.05, zc, D - 0.05), w.at(x + hw - 0.05, zc, D - 0.05), w.at(x, zc + rise - 0.05, D - 0.05)]
        G.face(tri, post, uvscale=1.0)
        G.face(tri[::-1], post, uvscale=1.0)
        G.box(w.at(x, zc - 0.08, D - 0.1), (2 * hw - 0.1, 0.12, 0.16), post, w.ang, uvscale=1.0)
        for j in range(1, steps + 1):                                      # bottom step deepest, top step shallowest
            ext = (depth - 0.1) * (steps - j + 1) / steps
            st = w.at(x, 0.0, ext / 2)
            G.box((st[0], st[1], 0.16 * j - 0.08), (width, ext, 0.16), 'M_Concrete', w.ang, uvscale=1.0)

    def veranda(self, wall, x0, x1, depth=2.2, height=None, post='M_Wall_Wood_white_Blank', roof_mat='M_Roof_Metal_black',
                balcony=True, rail='M_Wall_Wood_white_Blank'):
        w = self.walls[wall]
        h = height or (self.ground - 0.3)
        G = self.G
        G.box(w.at((x0 + x1) / 2, 0.15, depth / 2), (x1 - x0, depth, 0.3), 'M_Concrete', w.ang, uvscale=1.0)
        n = max(2, round((x1 - x0) / 2.2) + 1)
        for k in range(n):
            x = x0 + 0.15 + (x1 - x0 - 0.3) * k / (n - 1)
            G.cyl(*w.at(x, 0.3, depth - 0.2)[:2], 0.3, 0.13, h - 0.3, post, seg=8)
        G.box(w.at((x0 + x1) / 2, h + 0.12, depth / 2), (x1 - x0 + 0.2, depth + 0.1, 0.25), roof_mat, w.ang, uvscale=1.0)
        w.ledge(x0, x1, h - 0.2, h, post, depth)
        if balcony:
            z = h + 0.25
            for (p, q) in (((x0, depth), (x1, depth)), ((x0, 0.0), (x0, depth)), ((x1, depth), (x1, 0.0))):
                P0, P1 = w.at(p[0], z, p[1]), w.at(q[0], z, q[1])
                pts = [P0, P1, (P1[0], P1[1], z + 0.95), (P0[0], P0[1], z + 0.95)]
                G.face(pts, rail, uvscale=1.0)
                G.face(pts[::-1], rail, uvscale=1.0)


def build(ctx, roof=None, facades=None, dormers=None, cross_gable=None, chimneys=(), balconies=(), veranda=None,
          sign=None, **house):
    """One call for a whole house; see House for the keyword arguments."""
    h = House(ctx, **house)
    h.facades(**(facades or {}))
    h.roof(**(roof or {}))
    if dormers:
        h.dormers(**dormers) if isinstance(dormers, dict) else h.dormers(dormers)
    if cross_gable:
        h.cross_gable(**cross_gable)
    for c in chimneys:
        h.chimney(*c)
    for b in balconies:
        h.balcony(**b)
    if veranda:
        h.veranda(**veranda)
    if sign:
        h.sign(**sign) if isinstance(sign, dict) else h.sign(sign)
    return h
