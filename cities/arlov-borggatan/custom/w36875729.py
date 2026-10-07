"""Kornvägen: yellow-brick block with turquoise stair-core panels and balcony stack."""
import housekit

h = housekit.House(ctx, levels=8, wall='M_Wall_Brick_yellow_Blank',
                   trim='M_Roof_Metal_grey', lower='M_Wall_Brick_red_Blank', street=[3])
h.facades(window=(1.25, 1.55), pitch=2.8, kind='modern', cornice=False)
h.roof(shape='flat')
wall, width, depth = 3, 3.0, 0.85
x = h.walls[wall].L * 0.68
h.stair_bay(wall, x=x, width=width, depth=depth,
            mat='M_Wall_Brick_yellow_Blank', glazed=False)
base = h.walls[wall]
front = housekit.Wall(h.G, base.at(x - width / 2, 0, depth + 0.06)[:2],
                      base.at(x + width / 2, 0, depth + 0.06)[:2])
for floor in range(8):
    z0 = 0.45 + floor * h.storey
    z1 = z0 + 2.15
    front.rect(0.18, width - 0.18, z0, z1, 'M_Window_Pane', scale=1.5)
    front.rect(0, width, z1, z1 + 0.22, 'M_Wall_Metal_green_Blank', 0.05)
    front.rect(0.12, width - 0.12, z0, z0 + 0.35, 'M_Wall_Metal_green_Blank', 0.05)
for storey in range(2, 9):
    h.balcony(wall, x=h.walls[wall].L * 0.3, storey=storey, width=2.8, depth=0.85,
              rail='M_Roof_Metal_grey')
"""Kornvägen: yellow-brick block with turquoise stair-core panels and balcony stack."""
import housekit

h = housekit.House(ctx, levels=4, wall='M_Wall_Brick_yellow_Blank',
                   trim='M_Roof_Metal_grey', lower='M_Wall_Brick_red_Blank', street=[3])
h.facades(window=(1.25, 1.55), pitch=2.8, kind='modern', cornice=False)
h.roof(shape='flat')
wall, width, depth = 3, 3.0, 0.85
x = h.walls[wall].L * 0.68
h.stair_bay(wall, x=x, width=width, depth=depth,
            mat='M_Wall_Brick_yellow_Blank', glazed=False)
base = h.walls[wall]
front = housekit.Wall(h.G, base.at(x - width / 2, 0, depth + 0.06)[:2],
                      base.at(x + width / 2, 0, depth + 0.06)[:2])
for floor in range(4):
    z0 = 0.45 + floor * h.storey
    z1 = z0 + 2.15
    front.rect(0.18, width - 0.18, z0, z1, 'M_Window_Pane', scale=1.5)
    front.rect(0, width, z1, z1 + 0.22, 'M_Wall_Metal_green_Blank', 0.05)
    front.rect(0.12, width - 0.12, z0, z0 + 0.35, 'M_Wall_Metal_green_Blank', 0.05)
for storey in (2, 3, 4):
    h.balcony(wall, x=h.walls[wall].L * 0.3, storey=storey, width=2.8, depth=0.85,
              rail='M_Roof_Metal_grey')