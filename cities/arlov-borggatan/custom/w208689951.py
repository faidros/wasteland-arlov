"""w208689951: Borggatan 21, yellow villa with a broad central dormer and entrance porch."""
import housekit

h = housekit.House(ctx, levels=1, wall='M_Wall_Plaster_yellow_Blank', trim='M_Wall_Plaster_white_Blank', shop=False)
pw = max(h.street or range(len(h.walls)), key=lambda i: h.walls[i].L)
px = [h.walls[pw].L * 0.25, h.walls[pw].L * 0.75] if h.walls[pw].L > 14 else [h.walls[pw].L * 0.5]
skip = {pw: [(x - 1.1, x + 1.1) for x in px]}
h.facades(window=(1.1, 1.45), pitch=2.6, kind='sash', skip=skip, entrance=False)
h.roof(shape='gabled', pitch=45, mat='M_Roof_Tiles_red')
h.dormers([0.5], width=3.0, height=1.3, side='street', mat='M_Wall_Plaster_yellow_Blank', roof_mat='M_Roof_Tiles_red')
h.chimney(0.35, 0.55)
for x in px: h.porch(pw, x, roof_mat='M_Roof_Tiles_red')
