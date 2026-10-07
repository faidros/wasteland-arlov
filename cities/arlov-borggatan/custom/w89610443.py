"""Komvux: two-storey red-brick school with pale frames and a clear entrance sign."""
import housekit

WHITE = 'M_Wall_Plaster_white_Blank'

h = housekit.House(ctx, levels=2, ground=3.6, storey=2.9,
                   wall='M_Wall_Brick_red_Blank', trim=WHITE,
                   frame=WHITE, plinth='M_StoneWall',
                   door='M_Wall_Wood_brown_Blank')
h.facades(window=(1.25, 1.55), pitch=2.8, kind='sash', cornice=True,
          plinth_h=0.5, entrance=True, canopy='M_Roof_Metal_black')
h.roof(shape='gabled', pitch=28, mat='M_Roof_Tiles_dark',
       gable_mat='M_Wall_Brick_red_Blank', gable_windows=False, max_rise=3.0)
h.sign('KOMVUX', wall=0, z=3.08, size=0.9,
       mat='M_Roof_Metal_black', board=WHITE)