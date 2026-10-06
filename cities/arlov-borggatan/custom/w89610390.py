"""Burlövs bibliotek: red-brick civic block with glazed ground floor and dark street balconies."""
import housekit

h = housekit.House(ctx, levels=4, wall='M_Wall_Brick_red_Blank', trim='M_Roof_Metal_grey', shop=True, street=[0])
h.facades(window=(1.8, 1.9), pitch=3.2, kind='modern', shop_bays=4.0, sign_mat='M_Roof_Metal_grey', cornice=False)
h.roof(shape='flat')
for k in range(4):
    h.balcony(0, x=h.walls[0].L * (k + 0.5) / 4, storey=2, width=4.4, depth=1.25,
              rail='M_Roof_Metal_black', glass=False)
