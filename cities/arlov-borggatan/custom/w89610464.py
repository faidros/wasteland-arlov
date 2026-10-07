"""Kulturskolan: low red-brick wing with broad windows and a raised school sign."""
import housekit

WHITE = 'M_Wall_Plaster_white_Blank'

h = housekit.House(ctx, levels=1, ground=3.65, wall='M_Wall_Brick_red_Blank',
                   trim=WHITE, frame=WHITE, lower='M_Wall_Brick_brown_Blank',
                   plinth='M_StoneWall')
h.facades(window=(1.8, 1.9), pitch=4.4, kind='modern', cornice=False,
          plinth_h=0.5, entrance=True, canopy='M_Roof_Metal_red')
h.roof(shape='gabled', pitch=24, mat='M_Roof_Tiles_red',
       gable_mat='M_Wall_Brick_red_Blank', gable_windows=False, max_rise=2.8)
h.sign('KULTURSKOLAN', wall=0, z=2.9, size=0.78,
       mat='M_Roof_Metal_black', board=WHITE)