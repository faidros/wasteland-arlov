"""Kayas Pizzeria, Lundavägen 7: low white shop with a turquoise fascia."""
import housekit

TURQUOISE = 'M_Roof_Metal_copper'
WHITE = 'M_Wall_Plaster_white_Blank'

h = housekit.House(ctx, levels=1, ground=3.25, wall=WHITE,
                   trim=WHITE, frame=WHITE, plinth='M_StoneWall',
                   lower=WHITE, shop=True, street=[2])
h.facades(window=(1.25, 1.55), pitch=2.7, kind='sash', shop_bays=4.4,
          sign_mat=TURQUOISE, cornice=False, plinth_h=0.25,
          entrance=False, downpipes=False)
h.roof(shape='hipped', pitch=18, mat='M_Roof_Tiles_dark',
       overhang=0.35, max_rise=1.6)
h.sign('KAYAS PIZZERIA', wall=2, x=4.7, z=2.68, size=0.58,
       mat=WHITE)