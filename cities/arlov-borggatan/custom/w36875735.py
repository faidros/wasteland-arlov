"""Rapsvägen: yellow-brick apartment block with repeated dark metal balconies."""
import housekit

h = housekit.House(ctx, levels=4, wall='M_Wall_Brick_yellow_Blank',
                   trim='M_Roof_Metal_grey', street=[1])
h.facades(window=(1.25, 1.5), pitch=2.8, kind='modern', cornice=False)
h.roof(shape='flat')
wall = 1
for storey in (2, 3, 4):
    for x in (h.walls[wall].L * 0.3, h.walls[wall].L * 0.7):
        h.balcony(wall, x=x, storey=storey, width=3.0, depth=0.9,
                  rail='M_Roof_Metal_grey', glass=False)
"""Rapsvägen: yellow-brick apartment block with dark metal balcony rails."""
import housekit

h = housekit.House(ctx, levels=4, wall='M_Wall_Brick_yellow_Blank',
                   trim='M_Roof_Metal_grey', street=[1])
h.facades(window=(1.25, 1.5), pitch=2.8, kind='modern', cornice=False)
h.roof(shape='flat')
wall = 1
for storey in (2, 3, 4):
    for x in (h.walls[wall].L * 0.3, h.walls[wall].L * 0.7):
        h.balcony(wall, x=x, storey=storey, width=3.0, depth=0.9,
                  rail='M_Roof_Metal_grey', glass=False)