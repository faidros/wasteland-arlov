# Wasteland Builder

**Turn your town into a Mad Max battle-car game.** Name a place — a town, an old-town square, your
street — and an AI coding agent (Claude Code or Codex) builds it: real streets and buildings from
OpenStreetMap, an editable 3D city in Blender, and a browser game where armored cars fight raiders
through *your* streets. The title, splash screen, narrator and radio are made for the place.

![The generated Visby game's start screen](docs/images/visby-menu.jpg)

![Visby, generated from OpenStreetMap](docs/images/visby-overview.jpg)

| | |
|---|---|
| ![Street level](docs/images/visby-street.jpg) | ![Default splash screen](docs/images/visby-default-splash.jpg) |
| Stora torget, Visby — generated facades, paving, benches and lamps | The menu art Blender renders when no AI image is made |

## Quick start

You need **Python 3.10+**, **Node.js 20+**, **Blender 4.2+** and ~2 GB of disk.

```sh
git clone https://github.com/fltman/wasteland-builder.git
cd wasteland-builder
```

Open the folder in **Claude Code** (`claude`) or **Codex** (`codex`) and just say what you want:

> Build Visby.  ·  Bygg Ystad, liten karta.  ·  Make a wasteland of Dubrovnik's old town and give it a theme song.

The agent checks your setup, finds the place, shows you the area, builds the city (a few minutes),
writes the game's title and texts with local landmarks, and starts the game at
**http://localhost:5220**. Ask for more afterwards: *"make the cathedral look right"*, *"refine
Strandgatan from Street View"*, *"give the narrator a Gotland accent"*, *"put it online so my friends
can play"*.

Without an agent, three commands do the same:

```sh
python3 wasteland.py doctor              # installs and checks everything (once)
python3 wasteland.py make "Visby"        # find → build → play
python3 wasteland.py make "Lund" --size small   # small 600 m · medium 1 km (default) · large 1.6 km
```

## What gets built

1. **Place** — OpenStreetMap search (Nominatim); a square play area around it.
2. **Map data** — buildings, streets, sidewalks, squares, parks, water and coast, trees, walls, lamps
   and benches from OpenStreetMap.
3. **City model** (`cities/<slug>/city.blend`) — every building extruded with storeys, window facades
   and roofs (gabled, hipped, flat with parapets; churches get towers); raised sidewalks and kerbs,
   cobbles where the map says so, quay walls, bridges, trees, street furniture, rails, and a wall of
   rusty containers at the edge of the map. Heights, colours and materials come from OSM where mapped
   and from regional style presets (Nordic, brick north, Mediterranean …) where not.
4. **Game pack** — streamed 60 m tiles (a 1 km town is ~10–20 MB), the street graph for the AI,
   spawn point, map labels, supply drops.
5. **Theme** — title (*VISBY WASTELAND*), menu texts, narrator lines and prompts that name real
   landmarks and streets.

The game: three armored machines, machine guns, homing rockets, a flamethrower and mines, three waves of
raiders, free roam, and an **online arena** for up to eight friends.

## Make it yours

| | How | Needs |
|---|---|---|
| **Refinement rounds** for a street, an area or one building, from Street View | `refine-city` skill · `wasteland.py buildings / rebuild / render` | — |
| **Hand-modelled landmarks** | a Blender script per building, see [docs/custom-building-example.py](docs/custom-building-example.py) | — |
| **Splash art** with your town's landmarks | `imagegen` skill | Codex (built in), or `OPENAI_API_KEY` / `OPENROUTER_API_KEY` |
| **Narrator** who names your town | `elevenlabs` skill · `wasteland.py voices` | `ELEVENLABS_API_KEY` |
| **Soundtrack** | `suno-music` skill · `wasteland.py music --add` | a Suno account (web), or any MP3 |
| **Online multiplayer** on a small VPS (e.g. Vultr) | `deploy-arena` skill · [game/deploy/README.md](game/deploy/README.md) | a server, a domain |

Keys go in `.env` (copy `.env.example`). Everything is optional: without keys the game uses generic
narrator lines, the bundled soundtrack and a Blender-rendered splash screen.

![A refinement example: a church modelled by a custom script](docs/images/custom-church-example.jpg)

## Publish

```sh
python3 wasteland.py publish visby --arena wss://arena.example.com/ws
```
Upload `game/dist/` to any web host. The arena relay setup (Ubuntu VPS, nginx, Let's Encrypt) is one
command: see [game/deploy/README.md](game/deploy/README.md).

## How it works

```
place.py ─► fetch_osm.py ─► prepare_city.py ─► blender/build_city.py ─► blender/export_tiles.py ─► web/tiles.mjs ─► make_pack.py
Nominatim    OSM API +       Shapely: every      city.blend (editable)     raw GLB per 60 m tile      meshopt + WebP     map.json, config.json,
             Overpass        geometry decision                                                                         media → game/public/city
                             → city.json
```
See [AGENTS.md](AGENTS.md) for the layout and conventions, [game/README.md](game/README.md) for the
game and its city contract.

## På svenska

Klona repot, öppna mappen i Claude Code eller Codex och skriv till exempel *"Bygg Visby"*. Agenten
installerar det som behövs, hämtar kartdata från OpenStreetMap, bygger staden i Blender och startar
spelet på http://localhost:5220 med stadens namn, en egen startbild, berättarröst och musik. Be sedan
om förbättringsrundor för enskilda hus, gator eller områden utifrån Street View, eller om en server på
t.ex. Vultr så att ni kan spela online tillsammans.

## Credits and licenses

- Game engine, vehicles and shared effects: from **Kalmar Wasteland**; the city generator is inspired by
  **kalmar-kvarnholmen** — both by Anders Bjarby.
- Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), ODbL. Generated
  cities are derived databases: keep the attribution (the game shows it).
- Code: MIT ([LICENSE](LICENSE)). Bundled art, sounds and music: see [THIRD_PARTY.md](THIRD_PARTY.md).
- Built with Blender, three.js, three-mesh-bvh, glTF-Transform, meshoptimizer, Shapely, sharp and Vite.
