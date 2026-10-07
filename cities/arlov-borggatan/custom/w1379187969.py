"""Asia Restaurang, Dalbyvägen: low brick-based shop row with a named fascia."""
import housekit

BRICK = 'M_Wall_Brick_red_Blank'
WHITE = 'M_Wall_Plaster_white_Blank'

h = housekit.House(ctx, levels=1, ground=3.25, wall=BRICK,
                   trim='M_Wall_Brick_brown_Blank', frame=WHITE,
                   lower=BRICK, plinth='M_StoneWall', shop=True,
                   street=[1])
h.facades(window=(1.25, 1.35), pitch=3.6, kind='modern', shop_bays=4.6,
          sign_mat=WHITE, cornice=False, plinth_h=0.35,
          entrance=False, downpipes=False)
h.roof(shape='flat', parapet=0.25)
h.sign('ASIA RESTAURANG', wall=1, x=7.2, z=2.6, size=0.62,
       mat='M_Roof_Metal_red', board=WHITE)