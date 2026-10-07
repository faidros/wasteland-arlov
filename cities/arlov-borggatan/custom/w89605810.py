"""Grönvägen: ten-storey red-brick apartment tower with a stacked balcony bay."""
import housekit

h = housekit.House(ctx, levels=10, wall='M_Wall_Brick_red_Blank',
                   trim='M_Roof_Metal_grey', street=[1])
h.facades(window=(1.2, 1.45), pitch=2.8, kind='modern', cornice=False)
h.roof(shape='flat')
wall, width = 1, 3.8
x = h.walls[wall].L * 0.78
h.stair_bay(wall, x=x, width=width, depth=1.0, mat='M_Wall_Brick_red_Blank', glazed=False)
base = h.walls[wall]
front = housekit.Wall(h.G, base.at(x - width / 2, 0, 1.06)[:2], base.at(x + width / 2, 0, 1.06)[:2])
for floor in range(10):
    z0 = 0.45 + floor * h.storey
    z1 = z0 + 2.15
    front.rect(0.2, width - 0.2, z0, z1, 'M_Window_Pane', scale=1.5)
    front.rect(0, width, z1, z1 + 0.25, 'M_Roof_Metal_grey', 0.05)
    for fraction in (1 / 3, 2 / 3):
        xc = width * fraction
        front.rect(xc - 0.045, xc + 0.045, z0, z1, 'M_Roof_Metal_grey', 0.06)
for storey in range(2, 11):
    h.balcony(wall, x=x, storey=storey, width=3.3, depth=0.95, rail='M_Roof_Metal_grey')