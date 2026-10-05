"""Export a city .blend as streamed web tiles for the game (raw GLBs; pipeline/web/tiles.mjs optimises them).

    Blender -b cities/<slug>/city.blend --python pipeline/blender/export_tiles.py -- <raw out dir>

- Objects carry wb_tile ('base' = always loaded: ground, water, curbs; 'c<i>_<j>' = 60 m tiles).
  Objects without it (e.g. added by hand in Blender) are placed by their bounding-box centre.
- Tiles carry geometry and material names only; every material is exported once into the
  material library (materials_000.glb …). The game swaps materials by exact name.
- Tinted materials: the Blender Mix node is removed for export; the tint travels as extras.tint
  and the game multiplies texels by it where the texture alpha (tint mask) says so.
- Images are kept in tile exports only so that Blender writes the UVs; tiles.mjs strips them.

Adapted from kalmar-kvarnholmen-web/tools/export_tiles.py.
"""
import json
import math
import os
import sys
import time

import bmesh
import bpy
from mathutils import Vector

args = sys.argv[sys.argv.index('--') + 1:]
OUT = os.path.abspath(args[0])
CELL = 60.0
os.makedirs(OUT, exist_ok=True)
t0 = time.time()

# ---------------------------------------------------------------- prepare materials for glTF
for m in bpy.data.materials:
    if not m.use_nodes:
        continue
    nt = m.node_tree
    bsdf = nt.nodes.get('Principled BSDF')
    for node in list(nt.nodes):
        if node.bl_idname == 'ShaderNodeMix' and bsdf is not None:
            a = {s.identifier: s for s in node.inputs}['A_Color']
            if a.links:
                nt.links.new(a.links[0].from_socket, bsdf.inputs['Base Color'])
            nt.nodes.remove(node)
    try:
        m.surface_render_method = 'DITHERED'
    except AttributeError:
        m.blend_method = 'OPAQUE'

# Non-mesh objects (cameras, lights) are not exported.
meshes = [o for o in bpy.data.objects if o.type == 'MESH' and not o.hide_render]
for o in bpy.data.objects:
    if o.type == 'MESH':
        o.hide_set(False)
        o.hide_viewport = False


def world_bounds(o):
    bb = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return (Vector((min(v.x for v in bb), min(v.y for v in bb), min(v.z for v in bb))),
            Vector((max(v.x for v in bb), max(v.y for v in bb), max(v.z for v in bb))))


groups, info = {}, {}
bpy.context.view_layer.update()
for o in meshes:
    mn, mx = world_bounds(o)
    tris = sum(len(p.vertices) - 2 for p in o.data.polygons)
    tile = o.get('wb_tile')
    if not tile:
        c = (mn + mx) / 2
        tile = f'c{math.floor(c.x / CELL)}_{math.floor(c.y / CELL)}'
    groups.setdefault(tile, []).append(o)
    info[o.name] = (mn, mx, tris)

tiles = []
for gid, objs in sorted(groups.items()):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, f'{gid}.glb'), export_format='GLB', use_selection=True,
        export_extras=True, export_apply=True, export_yup=True,
        export_image_format='JPEG', export_image_quality=40, export_materials='EXPORT',
        export_cameras=False, export_lights=False, export_texcoords=True,
    )
    mn = Vector((min(info[o.name][0][i] for o in objs) for i in range(3)))
    mx = Vector((max(info[o.name][1][i] for o in objs) for i in range(3)))
    tiles.append(dict(id=gid, min=[round(mn.x, 2), round(mn.z, 2), round(-mx.y, 2)], max=[round(mx.x, 2), round(mx.z, 2), round(-mn.y, 2)],
                      tris=sum(info[o.name][2] for o in objs), objects=len(objs)))
    print('TILE', gid, len(objs), tiles[-1]['tris'], flush=True)

# ---------------------------------------------------------------- material library
CHUNK = 150
used = sorted({m.name for objs in groups.values() for o in objs for m in o.data.materials if m})
parts = 0
for start in range(0, len(used), CHUNK):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for i, name in enumerate(used[start:start + CHUNK], start):
        me = bpy.data.meshes.new(f'lib_{i}')
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=0.5)
        bm.to_mesh(me)
        bm.free()
        me.uv_layers.new(name='UVMap')
        me.materials.append(bpy.data.materials[name])
        o = bpy.data.objects.new(f'lib_{name}', me)
        bpy.context.scene.collection.objects.link(o)
        o.location.x = i
        o.select_set(True)
    bpy.ops.export_scene.gltf(
        filepath=os.path.join(OUT, f'materials_{parts:03d}.glb'), export_format='GLB', use_selection=True,
        export_extras=True, export_apply=True, export_yup=True, export_image_format='AUTO',
        export_materials='EXPORT', export_cameras=False, export_lights=False,
    )
    parts += 1
    for img in bpy.data.images:
        if img.has_data:
            img.buffers_free()

json.dump(dict(cell=CELL, tiles=tiles, materials=len(used), material_parts=parts), open(os.path.join(OUT, 'tiles.json'), 'w'), indent=1)
print('EXPORT_TILES_OK', len(tiles), 'tiles', len(used), 'materials', f'{time.time() - t0:.0f}s', flush=True)
