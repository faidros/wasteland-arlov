"""OKQ8 Automat at Lundavägen 9: coordinate-anchored canopy, pumps and roadside pylon."""
import math
import housekit

LAT, LON = 55.6299842, 13.0693557
lat0, lon0 = ctx.data['place']['center']
site = ((LON - lon0) * 111320.0 * math.cos(math.radians(lat0)),
        (LAT - lat0) * 111320.0)
segments = []
for road in ctx.data.get('roads', []):
    if road.get('name') not in ('Lundavägen', 'Storgatan') or len(road.get('p', [])) < 2:
        continue
    for a, b in zip(road['p'], road['p'][1:]):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length_squared = dx * dx + dy * dy
        if not length_squared:
            continue
        fraction = max(0.0, min(1.0, ((site[0] - a[0]) * dx + (site[1] - a[1]) * dy) / length_squared))
        closest = (a[0] + fraction * dx, a[1] + fraction * dy)
        distance = math.hypot(site[0] - closest[0], site[1] - closest[1])
        segments.append((distance, a, b, closest))
_, road_a, road_b, closest = min(segments, key=lambda row: row[0])
dx, dy = road_b[0] - road_a[0], road_b[1] - road_a[1]
length = math.hypot(dx, dy) or 1.0
t = (dx / length, dy / length)
into = (site[0] - closest[0], site[1] - closest[1])
into_length = math.hypot(*into) or 1.0
into = (into[0] / into_length, into[1] / into_length)
angle = math.atan2(t[1], t[0])


def point(center, along, across):
    return (center[0] + t[0] * along + into[0] * across,
            center[1] + t[1] * along + into[1] * across)


canopy = point(site, 0, 4.0)
canopy_length, canopy_width, roof_z = 15.0, 9.0, 5.0
for along in (-6.4, 6.4):
    for across in (-3.5, 3.5):
        x, y = point(canopy, along, across)
        ctx.geo.box((x, y, 2.48), (0.28, 0.28, 4.85), 'M_Roof_Metal_grey', angle, uvscale=1.0)
ctx.geo.box((canopy[0], canopy[1], roof_z), (canopy_length, canopy_width, 0.42),
            'M_Roof_Metal_grey', angle, uvscale=2.0)
for across in (-canopy_width / 2 + 0.13, canopy_width / 2 - 0.13):
    x, y = point(canopy, 0, across)
    ctx.geo.box((x, y, 4.73), (canopy_length, 0.16, 0.3), 'M_Roof_Metal_blue', angle, uvscale=1.0)
ctx.geo.box((canopy[0], canopy[1], 4.48), (canopy_length, canopy_width, 0.08),
            'M_Roof_Metal_red', angle, uvscale=1.0)

# Four dispensers on two raised islands, kept inside the forecourt canopy.
for along in (-3.6, 3.6):
    island = point(canopy, along, 0)
    ctx.geo.box((island[0], island[1], 0.18), (1.2, 7.0, 0.36), 'M_Concrete', angle, uvscale=1.0)
    for across in (-2.0, 2.0):
        x, y = point(island, 0, across)
        ctx.geo.box((x, y, 1.25), (0.78, 0.62, 1.8), 'M_Roof_Metal_grey', angle, uvscale=1.0)
        px, py = point((x, y), 0, 0.34)
        ctx.geo.box((px, py, 1.5), (0.5, 0.08, 0.54), 'M_Roof_Metal_blue', angle, uvscale=1.0)
        ctx.geo.box((px, py, 0.99), (0.5, 0.08, 0.12), 'M_Roof_Metal_red', angle, uvscale=1.0)

# The pylon stands on the roadside edge, with readable signs on both faces.
pylon = point(site, 0, -7.0)
ctx.geo.box((pylon[0], pylon[1], 2.7), (0.42, 0.42, 5.4), 'M_Roof_Metal_grey', angle, uvscale=1.0)
sign_width, sign_depth = 4.0, 0.36
tx, ty = point(pylon, 0, 0.25)
side = (-t[1], t[0])
sign_ring = [
    (tx - t[0] * sign_width / 2 - side[0] * sign_depth / 2,
     ty - t[1] * sign_width / 2 - side[1] * sign_depth / 2),
    (tx + t[0] * sign_width / 2 - side[0] * sign_depth / 2,
     ty + t[1] * sign_width / 2 - side[1] * sign_depth / 2),
    (tx + t[0] * sign_width / 2 + side[0] * sign_depth / 2,
     ty + t[1] * sign_width / 2 + side[1] * sign_depth / 2),
    (tx - t[0] * sign_width / 2 + side[0] * sign_depth / 2,
     ty - t[1] * sign_width / 2 + side[1] * sign_depth / 2),
]
sign = housekit.House(ctx, ring=sign_ring, levels=1, wall='M_Roof_Metal_blue',
                      trim='M_Roof_Metal_grey', street=[0, 2], party=[])
for wall in (0, 2):
    sign.sign('OKQ8', wall=wall, x=sign_width / 2, z=4.55, size=1.15,
              mat='M_Wall_Plaster_white_Blank', board='M_Roof_Metal_blue')
    sign.sign('AUTOMAT', wall=wall, x=sign_width / 2, z=3.58, size=0.48,
              mat='M_Wall_Plaster_white_Blank', board='M_Roof_Metal_red')