"""Lundavägen storefront row: Arlövs Trafikskola, Veterinär and Sibe Salongen."""
import housekit

BRICK = 'M_Wall_Brick_salmon_Blank'
WHITE = 'M_Wall_Plaster_white_Blank'
BLUE = 'M_Roof_Metal_blue'
RED = 'M_Roof_Metal_red'
GREEN = 'M_Roof_Metal_green'

h = housekit.House(ctx, levels=4, ground=3.8, storey=2.8, wall=BRICK,
                   trim='M_Wall_Brick_brown_Blank', frame=WHITE,
                   lower=BRICK, plinth='M_StoneWall', shop=True,
                   street=[1])
h.facades(window=(1.1, 1.45), pitch=2.55, kind='sash', shop_bays=4.4,
          sign_mat=WHITE, cornice=True, plinth_h=0.4,
          entrance=False, downpipes=True)
h.roof(shape='flat', mat='M_Roof_Metal_black', parapet=0.45)
h.sign('TRAFIKSKOLA', wall=1, x=9.3, z=3.18, size=0.48,
       mat=BLUE, board=WHITE)
h.sign('VETERINÄR', wall=1, x=28.4, z=3.18, size=0.52,
       mat=WHITE, board=RED)
h.sign('Sibe', wall=1, x=40.6, z=3.18, size=0.68,
       mat=WHITE, board=GREEN)
h.sign('BOYS SALONG', wall=1, x=46.6, z=3.18, size=0.4,
       mat=WHITE, board='M_Roof_Metal_black')