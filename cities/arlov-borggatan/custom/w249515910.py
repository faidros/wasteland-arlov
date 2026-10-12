"""Low Lidl supermarket with light metal cladding, blue entrance details and a raised logo sign."""
import housekit

wall = 'M_Wall_Metal_grey_Blank'
blue = 'M_Wall_Metal_blue_Blank'
h = housekit.House(
    ctx, levels=1, ground=5.4, wall=wall, trim=blue, frame=blue,
    plinth='M_Concrete', door=blue, shop=True,
)
h.facades(
    window=(2.0, 2.7), pitch=3.6, margin=1.0, shop_bays=7.0,
    door_at=0.5, sign_mat=blue, cornice=False, plinth_h=0.25,
    canopy='M_Roof_Metal_blue',
)
h.roof(shape='flat', mat='M_Roof_Flat_tar')

wall_index = max(h.street, key=lambda index: h.walls[index].L)
logo_wall = h.walls[wall_index]
logo_x = logo_wall.L / 2
h.sign(
    'LIDL', wall=wall_index, x=logo_x, z=3.55, size=1.7,
    mat='M_Wall_Plaster_yellow_Blank', board=blue,
)
logo_wall.rect(logo_x - 3.2, logo_x + 3.2, 5.14, 5.3,
               'M_Wall_Metal_red_Blank', 0.16)