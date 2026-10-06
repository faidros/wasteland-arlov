---
name: build-wasteland
description: Turn a real place (town, district, square or address) into a playable Mad Max battle-car game — OpenStreetMap → Blender city → web tiles → themed game with its own title, splash screen, voice lines and music. Use when the user names a place to build ("bygg Visby", "make Lund", "skapa en variant med Ystad", "generate my hometown"), wants a new city variant, or asks to continue/finish a city. Not for editing individual houses (use refine-city) or putting it online (use deploy-arena).
---

# Build a wasteland from a place

Everything runs through `python3 wasteland.py` in the repository root. Read `AGENTS.md` once for the
layout. Speak the user's language; keep them posted with one short line per stage.

## 0. First time on this machine

```sh
python3 wasteland.py doctor
```
It creates `.venv`, installs Node packages, finds Blender (4.2+), generates textures and links the
skills. Fix anything marked ✗ together with the user (install links are printed). Re-run until it says
**Ready**.

## 1. Pin down the place

```sh
python3 wasteland.py new "<place>" --size medium      # small 600 m · medium 1000 m · large 1600 m · or metres
```
- Show the user the chosen hit (`display_name`) and the OpenStreetMap link it prints. If the search
  lists several plausible hits (same name in two countries, a municipality vs the town), ask which one
  and rerun with `--pick N`, or use `--center lat,lon` for an exact spot (e.g. a square).
- Size: medium suits a town centre. Large takes longer and makes a heavier game; small is quickest.
- The folder name (slug) is printed: `cities/<slug>/`.

## 2. Build

```sh
python3 wasteland.py build <slug>        # 1–5 minutes; run it in the background and wait
```
Steps: fetch (OSM API, Overpass as backup) → terrain (Copernicus DEM heights, ~1 s) → prepare
(Shapely) → textures → blender (city.blend) → export (tiles) → tiles (meshopt/WebP) → pack (map.json +
config.json) → splash (Blender render).
Resume a failed run with `--from <step>`; `--refresh` downloads OSM data and terrain again. Without
network the terrain step only warns and the city is built flat; run `build <slug> --only terrain` and
`rebuild <slug>` later to add the hills. Hills and the surroundings beyond the play area come with it.

Check the result before going on:
```sh
python3 wasteland.py render <slug>       # overview + landmark cameras → cities/<slug>/renders/*.png
```
Look at the images. Expect: streets, buildings with windows and roofs, parks, water where the map has
it, churches with towers. If the area is wrong (mostly fields, cut-off old town), adjust `new` with a
different `--center`/`--size` and build again.

## 3. Theme: name, texts, voice lines, prompts

```sh
python3 wasteland.py theme <slug>        # writes cities/<slug>/theme.json and applies it
```
Then make it good — edit `theme.json` yourself:
- Ask the user (once) for the game's language and title if they have wishes; default title is
  `<PLACE> / WASTELAND`. Keep titles short (they are huge on screen).
- Use `facts.landmarks` and `facts.streets` for local colour: the intro, tagline and voice lines should
  name real places (the cathedral, the harbour, the main street). Keep it playful and non-hateful;
  don't mock real living people.
- Voice lines (`voice.lines`): `intro` and `win` must name the place; `wave`, `critical`, `repair`,
  `wrecked` are optional overrides. One or two sentences each, ElevenLabs audio tags in brackets.
- Tactical-map labels come from churches, stations, squares etc.; add others the user cares about
  with `map_labels` (a landmark name, or `{"name": "The Pier", "lat": …, "lon": …}`).
- Run `python3 wasteland.py theme <slug>` again to apply text changes.

## 4. Media (each optional — the game works without them)

Ask before using paid services the first time (image, voice and music generation cost money/credits).

| What | How | Without it |
|---|---|---|
| Splash screen | **imagegen** skill → `cities/<slug>/media/splash.jpg` | Blender render of the street with the car |
| Voice lines | **elevenlabs** skill → `python3 wasteland.py voices <slug>` | generic narrator lines, no place names |
| Music | **suno-music** skill → `python3 wasteland.py music <slug> --add …` | the bundled three-track soundtrack |

After adding media: `python3 wasteland.py build <slug> --only pack`.

## 5. Play and check

```sh
python3 wasteland.py play <slug>         # dev server on http://localhost:5220 — run in the background
```
If you have a browser tool, open it: the start screen must show the new title and splash, the status
line "<n> streets & paths / <Name> is ready", and ENTER THE STREET WAR must start a game on a street
(not inside a building, not in water). Press Tab for the tactical map: labels should be local places.
Otherwise ask the user to open the URL.

## 6. Finish

Tell the user: what was built (buildings, streets, landmarks from `python3 wasteland.py status <slug>`),
what is generic (estimated heights/colours where OSM has none) and the next options:
- refine streets/houses from Street View → **refine-city** skill
- publish the website and an online-arena server → `python3 wasteland.py publish <slug>` and **deploy-arena**

## Rules

- Never commit or print API keys; they live in `.env` (git-ignored).
- OpenStreetMap data is ODbL: keep the attribution (the game shows it). Don't loop downloads; reuse
  `osm.json` (`--refresh` only when needed).
- Long commands (build, play, render) go to the background; poll their output instead of blocking.
- If a step fails, read the last lines it printed, fix the cause, and resume with `--from <step>`.
