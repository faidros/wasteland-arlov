"""w208689940: Borggatan 25, white-painted brick villa with a broad central dormer."""
import housekit

h = housekit.House(ctx, levels=1, wall='M_Wall_Plaster_white_Blank', trim='M_Wall_Plaster_grey_Blank', shop=False)
h.facades(window=(1.1, 1.45), pitch=2.6, kind='sash')
h.roof(shape='gabled', pitch=45, mat='M_Roof_Tiles_dark')
h.dormers([0.5], width=3.6, height=1.35, side='street', mat='M_Wall_Plaster_white_Blank', roof_mat='M_Roof_Tiles_dark')
h.chimney(0.35, 0.55)
