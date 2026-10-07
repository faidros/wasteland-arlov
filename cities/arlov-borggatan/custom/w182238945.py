"""Arlövs teater/Hundramannasalen: ochre 1892 hall with a dentil cornice and black metal roof."""
import housekit

h = housekit.House(ctx, levels=1, ground=3.7, wall='M_Wall_Plaster_ochre_Blank',
                   trim='M_Wall_Plaster_white_Blank', plinth='M_Concrete')
h.surrounds = True
h.facades(window=(1.25, 1.65), pitch=2.9, kind='sash', cornice=True, plinth_h=0.55)
h.roof(shape='gabled', pitch=38, mat='M_Roof_Metal_black', overhang=0.5,
       gable_mat='M_Wall_Plaster_ochre_Blank', max_rise=5.5)
h.dormers([0.25, 0.5, 0.75], width=1.6, height=1.15, side='both',
          mat='M_Wall_Plaster_ochre_Blank', roof_mat='M_Roof_Metal_black')
h.cross_gable(frac=0.32, width=4.0, height=1.3, side='street', pitch=42,
              roof_mat='M_Roof_Metal_black', windows=2)
h.chimney(0.18, 0.6, mat='M_Wall_Brick_red_Blank')
for i in h.street:
    wall = h.walls[i]
    count = int(wall.L / 0.42)
    for k in range(count):
        x = (k + 0.5) * wall.L / count
        h.G.box(wall.at(x, h.eave - 0.22, 0.18), (0.16, 0.2, 0.12),
                'M_Wall_Plaster_white_Blank', wall.ang)