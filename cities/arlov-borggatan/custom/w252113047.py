"""Jakob Pers Plats: red-brick apartment block with repeated dark metal balconies."""
import housekit

h = housekit.House(ctx, levels=4, wall='M_Wall_Brick_red_Blank', trim='M_Roof_Metal_grey', street=[3])
h.facades(window=(1.35, 1.55), pitch=2.9, kind='modern', cornice=False)
h.roof(shape='flat')
wall = 3
count = max(2, int(h.walls[wall].L // 5.8))
width = min(4.2, h.walls[wall].L / count * 0.72)
for storey in (2, 3, 4):
    for k in range(count):
        h.balcony(wall, x=h.walls[wall].L * (k + 0.5) / count, storey=storey,
                  width=width, depth=1.15, rail='M_Roof_Metal_grey')