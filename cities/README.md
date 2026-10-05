# cities/

One folder per generated place (git-ignored — they are large and rebuildable):

| file | made by | edit? |
|---|---|---|
| `place.json` | `wasteland.py new` | yes: centre, size |
| `osm.json` | `fetch` (OSM API / Overpass, ODbL) | no |
| `city.json` | `prepare` | no — regenerated |
| `city.blend` | `blender` | in Blender if you like, then `build --from export` (a rebuild overwrites it) |
| `build/raw/` | `export` | no |
| `pack/` | `tiles`, `pack` — what the game loads | no |
| `theme.json` | `theme` | **yes**: title, texts, voice lines, prompts |
| `overrides.json` | you / refine-city | **yes**: corrected buildings, areas, roads |
| `custom/<id>.py` | you / refine-city | **yes**: hand-modelled buildings |
| `media/` | imagegen, voices, music | **yes**: splash.jpg, voice-*.mp3, music/ |
| `refinements.md` | refine-city | log of improvement rounds |
| `renders/` | `render` | review images |

To share a city without the big files, share `place.json`, `theme.json`, `overrides.json`,
`custom/` and `media/`; anyone can rebuild the rest with `python3 wasteland.py build <slug>`.
