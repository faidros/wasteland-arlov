"""Medborgar Huset: red-brick municipal building with a raised entrance sign."""
import housekit

BRICK = 'M_Wall_Brick_red_Blank'
WHITE = 'M_Wall_Plaster_white_Blank'

h = housekit.House(ctx, levels=4, ground=3.8, storey=3.0,
                   wall=BRICK, trim='M_Wall_Brick_brown_Blank',
                   frame=WHITE, lower='M_Wall_Brick_brown_Blank',
                   plinth='M_StoneWall', street=[2])
h.facades(window=(1.35, 1.65), pitch=2.9, kind='modern', cornice=False,
          plinth_h=0.5, entrance=True, door_at=0.5,
          canopy='M_Roof_Metal_black')
h.roof(shape='flat', parapet=0.55)
h.sign('MEDBORGAR HUSET', wall=2, x=17.6, z=2.82, size=0.68,
       mat=WHITE, board=BRICK)