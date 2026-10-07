"""Hämtpunkten, Borggatan 2: yellow-brick pickup point with a small entrance sign."""
import housekit

BRICK = 'M_Wall_Brick_yellow_Blank'
WHITE = 'M_Wall_Plaster_white_Blank'

h = housekit.House(ctx, levels=2, ground=3.55, storey=2.8, wall=BRICK,
                   trim='M_Wall_Brick_brown_Blank', frame=WHITE, lower=BRICK,
                   plinth='M_StoneWall', street=[1])
h.facades(window=(1.35, 1.45), pitch=3.1, kind='modern', cornice=False,
          plinth_h=0.4, entrance=True, door_at=0.18,
          canopy='M_Roof_Metal_black')
h.roof(shape='gabled', pitch=8, mat='M_Roof_Metal_grey',
       gable_mat=BRICK, gable_windows=False, overhang=0.25, max_rise=1.3)
h.sign('HÄMTPUNKTEN', wall=1, x=5.0, z=2.9, size=0.6,
       mat='M_Roof_Metal_red', board='M_Wall_Plaster_yellow_Blank')