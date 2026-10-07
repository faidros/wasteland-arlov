"""Segevägen: pale nine-storey apartment block with repeated street balconies."""
import housekit

h = housekit.House(ctx, levels=9, wall='M_Wall_Plaster_white_Blank',
                   trim='M_Wall_Plaster_white_Blank', lower='M_Wall_Brick_red_Blank', street=[2])
h.facades(window=(1.35, 1.55), pitch=2.9, kind='modern', cornice=False)
h.roof(shape='flat')
wall = 2
count = max(3, int(h.walls[wall].L // 7.0))
width = min(4.4, h.walls[wall].L / count * 0.72)
for storey in range(2, 10):
    for k in range(count):
        h.balcony(wall, x=h.walls[wall].L * (k + 0.5) / count, storey=storey,
                  width=width, depth=1.0, rail='M_Roof_Metal_grey')