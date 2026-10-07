"""Jakob Pers Plats: red-brick apartment block with a projecting glazed stair tower."""
import housekit

h = housekit.House(ctx, levels=4, wall='M_Wall_Brick_red_Blank', trim='M_Roof_Metal_grey', street=[0])
h.facades(window=(1.25, 1.55), pitch=2.8, kind='modern', cornice=False)
h.roof(shape='flat')
wall, width, depth, x = 0, 3.8, 1.0, h.walls[0].L * 0.62
h.stair_bay(wall, x=x, width=width, depth=depth, mat='M_Wall_Brick_red_Blank', glazed=False)
base = h.walls[wall]
front = housekit.Wall(h.G, base.at(x - width / 2, 0, depth + 0.06)[:2], base.at(x + width / 2, 0, depth + 0.06)[:2])
for floor in range(4):
    z0 = 0.45 + floor * h.storey
    z1 = z0 + 2.25
    front.rect(0.2, width - 0.2, z0, z1, 'M_Window_Pane', scale=1.5)
    front.rect(0, width, z1, z1 + 0.28, 'M_Wall_Metal_red_Blank', 0.04)
    for fraction in (1 / 3, 2 / 3):
        xc = width * fraction
        front.rect(xc - 0.045, xc + 0.045, z0, z1, 'M_Roof_Metal_grey', 0.06)