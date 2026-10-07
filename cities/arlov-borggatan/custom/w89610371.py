"""Vårbo Slöjdsalar: long workshop wing with deep windows and a shallow tiled roof."""
import housekit

WHITE = 'M_Wall_Plaster_white_Blank'

h = housekit.House(ctx, levels=1, ground=3.45, wall='M_Wall_Brick_brown_Blank',
                   trim=WHITE, frame=WHITE, plinth='M_StoneWall',
                   door='M_Wall_Wood_brown_Blank')
h.facades(window=(2.1, 1.35), pitch=3.25, kind='modern', cornice=False,
          plinth_h=0.45, entrance=True, canopy='M_Roof_Metal_black')
h.roof(shape='gabled', pitch=15, mat='M_Roof_Tiles_red',
       gable_mat='M_Wall_Brick_brown_Blank', gable_windows=False, max_rise=2.2)
h.sign('VÅRBO SLÖJDSALAR', wall=1, z=2.65, size=0.72,
       mat='M_Roof_Metal_black', board=WHITE)