"""Preserve the Kal P Dals gata industrial hall and add its oversized SAAB facade sign."""
import housekit
import math

g = ctx.geo
ring = ctx.footprint['outer']
height = ctx.b['h']
wall = ctx.mat('blank')

g.prism(ring, 0, height, wall, top=False)
g.polygon(ring, height, ctx.mat('flat'))

h = housekit.House(ctx, levels=1, ground=height, wall=wall)
camera_x, camera_y = -820.1, 136.7
street_walls = h.street or range(len(h.walls))

def camera_distance(index):
    candidate = h.walls[index]
    along = max(0.0, min(candidate.L,
                         (camera_x - candidate.p[0]) * candidate.t[0]
                         + (camera_y - candidate.p[1]) * candidate.t[1]))
    x = candidate.p[0] + candidate.t[0] * along
    y = candidate.p[1] + candidate.t[1] * along
    return math.hypot(camera_x - x, camera_y - y)

wall_index = min(street_walls, key=camera_distance)
sign_wall = h.walls[wall_index]
sign_x = (camera_x - sign_wall.p[0]) * sign_wall.t[0] + (camera_y - sign_wall.p[1]) * sign_wall.t[1]
sign_x = max(9.0, min(sign_wall.L - 9.0, sign_x))
h.sign('SAAB', wall=wall_index, x=sign_x, size=4.8, z=1.0,
       mat='M_Wall_Plaster_white_Blank',
       board='M_Wall_Metal_blue_Blank')