---
name: refine-city
description: Improvement rounds for a generated city — correct individual houses, a whole street or an area (heights, storeys, roof shapes, colours, materials, shopfronts, road surfaces) from Google Street View, satellite views and the user's own photos, or hand-model landmarks in Blender. Use when the user says a building/street looks wrong, asks to "förbättra/förfina Storgatan", "make the cathedral look right", "run a refinement pass", or wants more realism in a built city.
---

# Refine a city from Street View

The generator guesses where OpenStreetMap is silent (storeys, colours, roofs). A refinement round
replaces guesses with observations, the way the kalmar-kvarnholmen project improved its town pass by
pass. Three levels, cheapest first:

1. **Overrides** — corrected facts per building/area/street in `cities/<slug>/overrides.json`.
2. **Area rules** — one setting for every building inside a polygon or radius.
3. **Custom models** — a Blender script per landmark in `cities/<slug>/custom/<building id>.py`.

## A round, step by step

1. **Scope** with the user: one street, a square and its surroundings, or a single landmark. Keep a
   round to ~5–25 buildings.
2. **List what the generator made:**
   ```sh
   python3 wasteland.py buildings <slug> --street "Strandgatan" --json
   python3 wasteland.py buildings <slug> --near "Stora torget" --radius 80 --json
   ```
   Each row: id, name, kind, levels, height, wall style/colour, roof, a Street View link aimed at the
   facade (`view.streetview`) and a Blender camera spec (`view.render`).
3. **Look at reality.** With a browser tool open each Street View link and take a screenshot; for
   roof shapes use the satellite view `https://www.google.com/maps/@<lat>,<lon>,60m/data=!3m1!1e3`.
   Count storeys, note wall colour/material, roof shape and colour, shopfronts, towers, gables.
   Street View is a visual reference only: do **not** save Google imagery into the repository.
   **Photos and other pictures:** look in `cities/<slug>/references/` for the user's own photos,
   drawings or postcards (ask what each shows if the file name doesn't say). Openly licensed photos can
   be found on Wikimedia Commons (`https://commons.wikimedia.org/w/index.php?search=<landmark>`); if you
   download one, keep it in `references/` with its licence and author in `references/SOURCES.md`.
   Ask the user for local knowledge when something is unclear — it often beats any picture.
4. **Write overrides** (merge into the existing file, keep earlier entries):
   ```json
   {
     "buildings": {
       "w564108911": {"building:levels": 3, "height": 11.5, "roof:shape": "gabled", "roof:colour": "#7a3b2e",
                      "style": "stone", "colour": "limestone", "note": "Street View 2026-10: stepped gable, limestone"},
       "w455294740": {"building:colour": "#e3c58f", "building:material": "plaster", "roof:shape": "hipped"},
       "w455294757": {"hide": true, "note": "demolished"}
     },
     "areas": [
       {"center": [57.6405, 18.2930], "radius": 60, "buildings": {"roof:shape": "gabled", "style": "plaster"}},
       {"polygon": [[57.64, 18.29], [57.641, 18.29], [57.641, 18.292]], "buildings": {"building:levels": 2}}
     ],
     "roads": {"Strandgatan": {"surface": "sett", "width": 7}, "w123456": {"sidewalk": "no"}}
   }
   ```
   Building keys: any OSM tag (`building:levels`, `height`, `min_height`, `roof:shape` = flat|gabled|hipped|pyramidal,
   `roof:height`, `roof:colour`, `roof:material`, `building:colour`, `building:material`), plus
   `style` (plaster, brick, wood, stone, concrete, glass, metal), `colour` (a palette name from
   `pipeline/style.json` for that style), `roof` (flat|gabled|hipped|pyramidal), `hide`, `no_tower`,
   and free-text `note`. Specific building entries win over area rules.
   Road keys: `surface` (asphalt, sett, paving_stones, gravel …), `width`, `sidewalk` (both|left|right|no), `hide`.
5. **Rebuild and compare:**
   ```sh
   python3 wasteland.py rebuild <slug>                       # ~1 min, keeps OSM data and media
   python3 wasteland.py render <slug> --street "Strandgatan" # street-level views → cities/<slug>/renders/
   ```
   Put each render next to its Street View screenshot and adjust. Two or three iterations are normal.
6. **Log the round** in `cities/<slug>/refinements.md`: date, scope, what changed and why (Street View
   date/heading, which photo in `references/`, user knowledge). This is the project's memory for later rounds.

## Custom models for landmarks

When overrides are not enough (a cathedral with two towers, a castle, a stepped gable), write
`cities/<slug>/custom/<id>.py`. It replaces the generated building with that id at the next rebuild.
Start from `docs/custom-building-example.py`. The script gets `ctx`:
- `ctx.footprint` — `{'outer': [[x, y], …], 'holes': […]}` in metres (x east, y north), `ctx.b` — the generated record
- `ctx.geo` — draw with `.prism(ring, z0, z1, mat)`, `.box((x, y, z), (w, d, h), mat, angle)`,
  `.wall(a, b, z0, z1, mat)`, `.cyl(x, y, z, r, h, mat, seg, r2)`, `.polygon(ring, z, mat)`, `.quad(pts, mat)`
- materials: roles `'upper'`, `'ground'`, `'blank'`, `'roof'`, `'flat'` (the building's own colours) or
  any library name, e.g. `'M_Roof_Metal_copper'`, `'M_StoneWall'`, `'M_Wall_Stone_limestone_Blank'`

Facade textures repeat per window bay (≈3.2 m) and storey (3 m), so draw walls with `ctx.geo.wall`
using `uvscale` ≈ 3 to keep windows the right size. Keep custom models under ~20 000 triangles; the
game streams them like any tile. Rebuild and render as above.

## Done

Summarise the round for the user (buildings changed, before/after renders in `cities/<slug>/renders/`),
then `python3 wasteland.py play <slug>` if they want to drive it.
