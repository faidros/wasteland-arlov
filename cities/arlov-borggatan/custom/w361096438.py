"""Kornvägen: yellow-brick five-storey block with glazed turquoise stair core and garages."""
import housekit

h = housekit.House(ctx, levels=5, wall='M_Wall_Brick_yellow_Blank',
                   trim='M_Roof_Metal_grey', lower='M_Wall_Brick_red_Blank', street=[1, 3], party=[])
wall = 3
length = h.walls[wall].L
garage_x = (length * 0.25, length * 0.52)
core_x, core_width = length * 0.82, 2.8
skip = {wall: [(x - 1.55, x + 1.55) for x in garage_x] +
              [(core_x - core_width / 2, core_x + core_width / 2)]}
h.facades(window=(1.2, 1.5), pitch=2.8, kind='modern', skip=skip,
          entrance=False, cornice=False)
h.roof(shape='flat')
for x in garage_x:
    h.garage(wall, x, width=2.8, height=2.4, mat='M_Wall_Metal_grey_Blank')
h.stair_bay(wall, x=core_x, width=core_width, depth=0.85,
            mat='M_Wall_Brick_yellow_Blank', glazed=False)
base = h.walls[wall]
front = housekit.Wall(h.G, base.at(core_x - core_width / 2, 0, 0.91)[:2],
                      base.at(core_x + core_width / 2, 0, 0.91)[:2])
for floor in range(5):
    z0 = 0.5 + floor * h.storey
    z1 = z0 + 2.1
    front.rect(0.18, core_width - 0.18, z0, z1, 'M_Window_Pane', scale=1.5)
    front.rect(0, core_width, z1, z1 + 0.22, 'M_Wall_Metal_green_Blank', 0.05)
    front.rect(0.12, core_width - 0.12, z0, z0 + 0.4, 'M_Wall_Metal_green_Blank', 0.05)
"""Kornvägen: yellow-brick five-storey block with a glazed turquoise stair core and garages."""
import housekit

h = housekit.House(ctx, levels=5, wall='M_Wall_Brick_yellow_Blank',
                   trim='M_Roof_Metal_grey', lower='M_Wall_Brick_red_Blank', street=[1, 3], party=[])
wall, core_wall = 3, 3
length = h.walls[wall].L
garage_x = (length * 0.25, length * 0.52)
core_x, core_width = length * 0.82, 2.8
skip = {wall: [(x - 1.55, x + 1.55) for x in garage_x] +
              [(core_x - core_width / 2, core_x + core_width / 2)]}
h.facades(window=(1.2, 1.5), pitch=2.8, kind='modern', skip=skip,
          entrance=False, cornice=False)
h.roof(shape='flat')
for x in garage_x:
    h.garage(wall, x, width=2.8, height=2.4, mat='M_Wall_Metal_grey_Blank')
h.stair_bay(core_wall, x=core_x, width=core_width, depth=0.85,
            mat='M_Wall_Brick_yellow_Blank', glazed=False)
base = h.walls[core_wall]
front = housekit.Wall(h.G, base.at(core_x - core_width / 2, 0, 0.91)[:2],
                      base.at(core_x + core_width / 2, 0, 0.91)[:2])
for floor in range(5):
    z0 = 0.5 + floor * h.storey
    z1 = z0 + 2.1
    front.rect(0.18, core_width - 0.18, z0, z1, 'M_Window_Pane', scale=1.5)
    front.rect(0, core_width, z1, z1 + 0.22, 'M_Wall_Metal_green_Blank', 0.05)
    front.rect(0.12, core_width - 0.12, z0, z0 + 0.4, 'M_Wall_Metal_green_Blank', 0.05)