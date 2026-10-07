"""Geukahuset, Lundavägen 29: yellow brick, half-timbered upper facade and green turret."""
import math
import housekit

BRICK = 'M_Wall_Brick_yellow_Blank'
TIMBER = 'M_Wall_Wood_brown_Blank'
ROOF = 'M_Roof_Metal_black'

h = housekit.House(ctx, levels=4, ground=4.0, storey=3.0, wall=BRICK,
                   trim=TIMBER, frame='M_Wall_Plaster_white_Blank',
                   lower='M_StoneWall', plinth='M_StoneWall',
                   shop=True, timber=True)
h.facades(window=(1.05, 1.65), pitch=2.55, kind='sash', shop_bays=5.0,
          sign_mat='M_Wall_Brick_brown_Blank', cornice=False,
          plinth_h=0.45, entrance=False, downpipes=False)
h.roof(shape='gabled', pitch=43, mat=ROOF, gable_mat=BRICK,
       overhang=0.6, max_rise=7.5, ridge='long')
h.cross_gable(frac=0.39, width=6.0, height=2.8, pitch=48,
              side='street', roof_mat=ROOF, windows=3)
h.cross_gable(frac=0.76, width=4.5, height=2.2, pitch=46,
              side='street', roof_mat=ROOF, windows=2)

# The exposed upper storey uses a simple dark timber grid around the sash windows.
for index in h.street:
    wall = h.walls[index]
    if wall.L < 7.0:
        continue
    lower = h.ground + h.storey
    upper = h.eave - 0.12
    wall.ledge(0, wall.L, lower, lower + 0.18, TIMBER, 0.08)
    wall.ledge(0, wall.L, upper - 0.18, upper, TIMBER, 0.08)
    room = wall.L - 1.8
    count = int((room - 1.05) // 2.55) + 1 if room >= 1.05 else 0
    start = 0.9 + (room - ((count - 1) * 2.55 + 1.05)) / 2 if count else 0
    centers = [start + i * 2.55 + 0.525 for i in range(count)]
    posts = [0.12] + [(a + b) / 2 for a, b in zip(centers, centers[1:])] + [wall.L - 0.12]
    for x in posts:
        wall.rect(x - 0.09, x + 0.09, lower, upper, TIMBER, 0.08)

# Stone archivolts frame the street-facing shop windows.
for index in h.street:
    wall = h.walls[index]
    if wall.L < 7.0:
        continue
    count = max(1, round((wall.L - 0.8) / 5.0))
    bay = (wall.L - 0.8) / count
    for i in range(count):
        center = 0.4 + (i + 0.5) * bay
        outer = min(1.45, (bay - 0.55) / 2)
        inner = outer - 0.25
        spring = 2.2
        wall.ledge(center - outer - 0.12, center - outer + 0.12, 0.0, spring,
                   'M_StoneWall', 0.08)
        wall.ledge(center + outer - 0.12, center + outer + 0.12, 0.0, spring,
                   'M_StoneWall', 0.08)
        for segment in range(8):
            a0, a1 = math.pi * segment / 8, math.pi * (segment + 1) / 8
            points = [
                (center + outer * math.cos(a0), spring + outer * math.sin(a0)),
                (center + outer * math.cos(a1), spring + outer * math.sin(a1)),
                (center + inner * math.cos(a1), spring + inner * math.sin(a1)),
                (center + inner * math.cos(a0), spring + inner * math.sin(a0)),
            ]
            wall.poly(points, 'M_StoneWall', 0.08, scale=1.0)

# A round corner turret and its green metal spire mark the western end of the facade.
front_index = max(h.street, key=lambda i: h.walls[i].L) if h.street else max(
    range(len(h.walls)), key=lambda i: h.walls[i].L)
front = h.walls[front_index]
tower_x, tower_y, _ = front.at(front.L - min(2.7, front.L * 0.12), 1.2, 0.0)
tower_bottom = h.eave + 2.5
tower_eave = h.eave + 6.5
ctx.geo.cyl(tower_x, tower_y, tower_bottom, 2.0,
            tower_eave - tower_bottom, BRICK, seg=16)
facing = math.atan2(front.n[1], front.n[0])
for level in (tower_bottom + 0.75,):
    for offset in (-0.62, 0.0, 0.62):
        angle = facing + offset
        radial = (math.cos(angle), math.sin(angle))
        tangent = (-radial[1], radial[0])
        center = (tower_x + radial[0] * 2.04, tower_y + radial[1] * 2.04)
        width, height = 0.7, 1.35
        frame = [
            (center[0] - tangent[0] * width / 2, center[1] - tangent[1] * width / 2, level),
            (center[0] + tangent[0] * width / 2, center[1] + tangent[1] * width / 2, level),
            (center[0] + tangent[0] * width / 2, center[1] + tangent[1] * width / 2, level + height),
            (center[0] - tangent[0] * width / 2, center[1] - tangent[1] * width / 2, level + height),
        ]
        ctx.geo.face(frame, 'M_Wall_Plaster_white_Blank', uvscale=1.0)
        pane_center = (tower_x + radial[0] * 2.06, tower_y + radial[1] * 2.06)
        inset = 0.12
        pane = [
            (pane_center[0] - tangent[0] * (width / 2 - inset), pane_center[1] - tangent[1] * (width / 2 - inset), level + inset),
            (pane_center[0] + tangent[0] * (width / 2 - inset), pane_center[1] + tangent[1] * (width / 2 - inset), level + inset),
            (pane_center[0] + tangent[0] * (width / 2 - inset), pane_center[1] + tangent[1] * (width / 2 - inset), level + height - inset),
            (pane_center[0] - tangent[0] * (width / 2 - inset), pane_center[1] - tangent[1] * (width / 2 - inset), level + height - inset),
        ]
        ctx.geo.face(pane, 'M_Window_Pane', uvscale=1.0)
ctx.geo.cyl(tower_x, tower_y, tower_eave, 2.05, 1.2, ROOF,
            seg=16, r2=1.45, cap=False)
ctx.geo.cyl(tower_x, tower_y, tower_eave + 1.2, 1.48, 6.2,
            'M_Roof_Metal_green', seg=16, r2=0.0, cap=False)