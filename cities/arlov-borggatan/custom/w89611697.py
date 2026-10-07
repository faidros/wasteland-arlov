"""Burlöv Center: low one-floor shopping mall on its mapped outline, with four entrances."""
import housekit
import math
import citylib

ring = citylib.ccw(ctx.footprint['outer'])
roof_z = 7.1
wall_mat = 'M_Wall_Concrete_light_Blank'
roof_mat = 'M_Roof_Flat_gravel'
glass_mat = 'M_Window_Pane'
roads = [r for r in ctx.data.get('roads', [])
         if r.get('kind') in ('primary', 'secondary', 'tertiary', 'residential', 'unclassified', 'service')]
cx = (min(p[0] for p in ring) + max(p[0] for p in ring)) / 2
cy = (min(p[1] for p in ring) + max(p[1] for p in ring)) / 2


def point_segment_distance(p, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length2 = dx * dx + dy * dy or 1e-9
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / length2))
    return math.dist(p, (a[0] + dx * t, a[1] + dy * t))


edges = []
for i, (a, b) in enumerate(zip(ring, ring[1:] + ring[:1])):
    length = math.dist(a, b)
    if length < 12:
        continue
    mid = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
    dx, dy = b[0] - a[0], b[1] - a[1]
    radial = (mid[0] - cx, mid[1] - cy)
    radial_len = math.hypot(*radial) or 1.0
    road_distance = min((point_segment_distance(mid, p, q)
                         for road in roads for p, q in zip(road['p'], road['p'][1:])),
                        default=1000.0)
    edges.append({'i': i, 'a': a, 'b': b, 'length': length, 'mid': mid,
                  'angle': math.atan2(dy, dx), 'radial': (radial[0] / radial_len, radial[1] / radial_len),
                  'road_distance': road_distance})

entrances = []
for target in ((0, 1), (1, 0), (0, -1), (-1, 0)):
    candidates = [e for e in edges if e['i'] not in entrances]
    best = min(candidates, key=lambda e: e['road_distance'] * 1.4
               + (1 - e['radial'][0] * target[0] - e['radial'][1] * target[1]) * 30
               - min(e['length'], 100) * 0.08)
    entrances.append(best['i'])

for i, (a, b) in enumerate(zip(ring, ring[1:] + ring[:1])):
    length = math.dist(a, b)
    if length < 0.01:
        continue
    angle = math.atan2(b[1] - a[1], b[0] - a[0])
    if i in entrances and length > 18:
        ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
        nx, ny = uy, -ux
        opening = min(14.0, length * 0.42)
        left = (a[0] + ux * (length - opening) / 2, a[1] + uy * (length - opening) / 2)
        right = (b[0] - ux * (length - opening) / 2, b[1] - uy * (length - opening) / 2)
        ctx.geo.wall(a, left, 0, roof_z, wall_mat)
        ctx.geo.wall(right, b, 0, roof_z, wall_mat)
        ctx.geo.wall(left, right, 3.3, roof_z, wall_mat)
        ctx.geo.wall(left, right, 0, 3.3, glass_mat)
        mid = ((left[0] + right[0]) / 2, (left[1] + right[1]) / 2)
        for frac in (0.25, 0.5, 0.75):
            point = (left[0] + ux * opening * frac + nx * 0.08,
                     left[1] + uy * opening * frac + ny * 0.08)
            ctx.geo.box((point[0], point[1], 1.65), (0.12, 0.16, 3.3),
                        'M_Roof_Metal_grey', angle, uvscale=1.0)
        canopy_center = (mid[0] + nx * 2.0, mid[1] + ny * 2.0, 4.0)
        ctx.geo.box(canopy_center, (opening + 2.4, 4.2, 0.4), 'M_Roof_Metal_green',
                    angle, uvscale=1.0)
        for offset in (-opening / 2, opening / 2):
            post = (mid[0] + ux * offset + nx * 2.0, mid[1] + uy * offset + ny * 2.0)
            ctx.geo.box((post[0], post[1], 1.8), (0.22, 0.22, 3.6),
                        'M_Roof_Metal_grey', angle, uvscale=1.0)
    else:
        ctx.geo.wall(a, b, 0, roof_z, wall_mat)
        if length > 32:
            count = max(2, int(length // 14))
            for k in range(count):
                t = (k + 0.5) / count
                p = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                p = (p[0] + math.sin(angle) * 0.04, p[1] - math.cos(angle) * 0.04)
                w = min(4.8, length / count * 0.55)
                ctx.geo.box((p[0], p[1], 1.85), (w, 0.12, 2.1), glass_mat, angle, uvscale=1.5)
    ctx.geo.wall(a, b, roof_z, roof_z + 0.65, 'M_Wall_Concrete_light_Blank')

ctx.geo.polygon(ring, roof_z + 0.65, roof_mat)

frame_x, frame_y, frame_angle, frame_length, frame_width = citylib.frame(ring)
for row in range(-3, 4):
    for column in range(-4, 5):
        u, w = column * 25.0, row * 24.0
        x, y = citylib.local(frame_x, frame_y, frame_angle, u, w)
        if housekit.inside((x, y), ring):
            ctx.geo.box((x, y, roof_z + 0.82), (17.0, 5.0, 0.28),
                        'M_Roof_Metal_grey', frame_angle, uvscale=2.0)

for entrance in entrances:
    sign = housekit.House(ctx, ring=ring, levels=1, ground=3.6, wall=wall_mat,
                          trim='M_Roof_Metal_grey', street=[entrance], party=[])
    sign.sign('BURLÖV CENTER', wall=entrance, x=sign.walls[entrance].L / 2,
              z=4.35, size=1.5, mat='M_Wall_Plaster_white_Blank', board='M_Roof_Metal_green')