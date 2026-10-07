"""Malmö Sopstation, Lundavägen 13: yellow-brick second-hand shop."""
import housekit

BRICK = 'M_Wall_Brick_yellow_Blank'
WHITE = 'M_Wall_Plaster_white_Blank'
BLUE = 'M_Wall_Plaster_blue_Blank'

h = housekit.House(ctx, levels=2, ground=3.55, storey=3.0, wall=BRICK,
                   trim='M_Wall_Brick_brown_Blank', frame=WHITE,
                   lower=BRICK, plinth='M_StoneWall', shop=True,
                   street=[0])
h.facades(window=(1.15, 1.5), pitch=2.8, kind='sash', shop_bays=4.5,
          sign_mat=WHITE, cornice=False, plinth_h=0.3,
          entrance=False, downpipes=True)
h.roof(shape='hipped', pitch=22, mat='M_Roof_Tiles_dark',
       overhang=0.35, max_rise=2.0)
h.sign('SopStationen', wall=0, x=8.1, z=2.96, size=0.78,
       mat='M_Roof_Metal_red')
h.sign('SECONDHANDBUTIK', wall=0, x=13.0, z=3.04, size=0.5,
       mat=BLUE)