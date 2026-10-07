"""Vårboskolan: low brick teaching wing with pale stone details and a raised school sign."""
import housekit

WHITE = 'M_Wall_Plaster_white_Blank'

h = housekit.House(ctx, levels=1, ground=3.8, wall='M_Wall_Brick_red_Blank',
                   trim=WHITE, frame=WHITE, lower='M_Wall_Brick_brown_Blank',
                   plinth='M_StoneWall')
h.facades(window=(1.55, 1.8), pitch=4.2, kind='modern', cornice=False,
          plinth_h=0.55, entrance=True, canopy='M_Roof_Metal_grey')
h.roof(shape='gabled', pitch=22, mat='M_Roof_Tiles_red',
       gable_mat='M_Wall_Brick_red_Blank', gable_windows=False, max_rise=2.8)
h.sign('VÅRBOSKOLAN', wall=14, z=3.05, size=0.9,
       mat='M_Roof_Metal_blue', board=WHITE)