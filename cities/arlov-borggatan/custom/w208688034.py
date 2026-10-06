"""w208688034: Borggatan 30, red brick villa with light window surrounds and a steep dark gable roof."""
import housekit

h = housekit.House(ctx, levels=1, wall='M_Wall_Brick_red_Blank', trim='M_Wall_Plaster_white_Blank', shop=False)
h.surrounds = True
h.facades(window=(1.1, 1.45), pitch=2.6, kind='sash')
h.roof(shape='gabled', pitch=45, mat='M_Roof_Tiles_dark')
h.chimney(0.35, 0.55)
