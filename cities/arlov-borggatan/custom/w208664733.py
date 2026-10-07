"""Jouren Livs, Lundavägen 65: corner shop with a striped blue awning."""
import housekit

BRICK = 'M_Wall_Brick_yellow_Blank'
BLUE = 'M_Roof_Metal_blue'
WHITE = 'M_Wall_Plaster_white_Blank'

h = housekit.House(ctx, levels=3, ground=3.5, storey=3.0, wall=BRICK,
                   trim='M_Wall_Brick_brown_Blank', frame=WHITE,
                   lower='M_Wall_Brick_brown_Blank', plinth='M_StoneWall',
                   shop=True)
h.facades(window=(1.05, 1.45), pitch=2.5, kind='sash', shop_bays=3.8,
          sign_mat=BLUE, awnings=[BLUE, WHITE], cornice=True,
          plinth_h=0.35, entrance=False, downpipes=True)
h.roof(shape='flat', mat='M_Roof_Metal_black', parapet=0.55)
h.sign('JOUREN LIVS', wall=0, x=8.5, z=2.88, size=0.56,
       mat=WHITE, board=BLUE)