"""Arlövs Livs, Lundavägen 27: yellow-brick shop frontage with tobacco signage."""
import housekit

BRICK = 'M_Wall_Brick_yellow_Blank'
BLUE = 'M_Roof_Metal_blue'

h = housekit.House(ctx, levels=4, ground=3.6, storey=3.0, wall=BRICK,
                   trim='M_Wall_Brick_brown_Blank', frame='M_Wall_Plaster_white_Blank',
                   lower='M_Wall_Brick_yellow_Blank', plinth='M_StoneWall',
                   shop=True)
h.facades(window=(1.15, 1.45), pitch=2.7, kind='sash', shop_bays=7.5,
          sign_mat=BLUE, awnings='M_Roof_Metal_red', cornice=True,
          plinth_h=0.4, entrance=False, downpipes=True)
h.roof(shape='flat', mat='M_Roof_Metal_black', parapet=0.55)
h.sign('ARLOVS LIVS TOBAK', wall=1, x=8.8, z=2.98, size=0.5,
       mat='M_Wall_Plaster_yellow_Blank', board=BLUE)