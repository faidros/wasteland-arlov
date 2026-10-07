"""Jakob Pers Plats: low blue kiosk with broad service glazing and a red canopy."""
import housekit

h = housekit.House(ctx, levels=1, ground=3.0, wall='M_Wall_Plaster_blue_Blank',
                   trim='M_Wall_Plaster_white_Blank', shop=True, street=[2])
h.facades(window=(1.8, 1.8), pitch=2.5, kind='modern', shop_bays=3.0,
          sign_mat='M_Roof_Metal_red', awnings='M_Roof_Metal_red', cornice=False)
h.roof(shape='flat')