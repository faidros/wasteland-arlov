"""w208689956: Borggatan 23, red brick villa with one small central dormer."""
import housekit

h = housekit.House(ctx, levels=1, wall='M_Wall_Brick_red_Blank', trim='M_Wall_Plaster_white_Blank', shop=False)
h.facades(window=(1.1, 1.45), pitch=2.6, kind='sash')
h.roof(shape='gabled', pitch=45, mat='M_Roof_Tiles_dark')
h.dormers([0.5], width=1.5, height=1.2, side='street', mat='M_Wall_Brick_red_Blank', roof_mat='M_Roof_Tiles_dark')
h.chimney(0.35, 0.55)
