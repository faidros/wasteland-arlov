"""X-tra Dalbyvägen: low grey-clad store with full-height glazing and a red X-TRA sign."""
import housekit

h = housekit.House(ctx, levels=1, wall='M_Wall_Metal_grey_Blank', trim='M_Wall_Plaster_white_Blank', shop=True, ground=5.2, plinth='M_Concrete')
h.facades(window=(1.4, 1.2), pitch=3.2, kind='modern', sign_mat='M_Wall_Metal_grey_Blank')
h.sign('X-TRA', size=0.9, mat='M_Wall_Plaster_white_Blank', board='M_Roof_Metal_red')
h.roof(shape='flat')
