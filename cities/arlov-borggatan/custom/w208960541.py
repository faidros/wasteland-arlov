"""Rapsvägen: yellow-brown brick tower with a vertical strip of pink balcony panels."""
import housekit

h = housekit.House(ctx, levels=8, wall='M_Wall_Brick_yellow_Blank',
                   trim='M_Roof_Metal_grey', lower='M_Wall_Brick_red_Blank', street=[2])
h.facades(window=(1.2, 1.45), pitch=2.8, kind='modern', cornice=False)
h.roof(shape='flat')
wall = 2
for storey in range(2, 9):
    h.balcony(wall, x=h.walls[wall].L * 0.68, storey=storey, width=3.5, depth=1.15,
              rail='M_Wall_Plaster_rose_Blank', glass=False)
"""Rapsvägen: yellow-brown brick tower with pink panel balconies."""
import housekit

h = housekit.House(ctx, levels=4, wall='M_Wall_Brick_yellow_Blank',
                   trim='M_Roof_Metal_grey', lower='M_Wall_Brick_red_Blank', street=[2])
h.facades(window=(1.2, 1.45), pitch=2.8, kind='modern', cornice=False)
h.roof(shape='flat')
wall = 2
for storey in (2, 3, 4):
    h.balcony(wall, x=h.walls[wall].L * 0.68, storey=storey, width=3.5, depth=1.15,
              rail='M_Wall_Plaster_rose_Blank', glass=False)