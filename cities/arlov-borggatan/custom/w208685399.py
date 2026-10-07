"""Dalbyvägen 4: red-brick apartment block with white balconies and Arlövs kebab signage."""
import housekit

h = housekit.House(ctx, levels=4, wall='M_Wall_Brick_red_Blank',
                   trim='M_Wall_Plaster_white_Blank', shop=True, street=[13])
h.facades(window=(1.3, 1.5), pitch=2.9, kind='sash', shop_bays=4.2,
          sign_mat='M_Roof_Metal_red', entrance=False, cornice=False)
h.roof(shape='flat')
h.sign('ARLÖVS KEBAB', wall=13, x=h.walls[13].L / 2,
       z=h.ground - 0.62, size=0.63, mat='M_Wall_Plaster_white_Blank', board='M_Roof_Metal_red')
for storey in (2, 3, 4):
    for fraction in (0.23, 0.48, 0.73):
        h.balcony(13, x=h.walls[13].L * fraction, storey=storey,
                  width=2.8, depth=1.05, rail='M_Wall_Plaster_white_Blank')