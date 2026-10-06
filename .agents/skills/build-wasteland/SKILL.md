---
name: build-wasteland
description: Turn a real place (town, district, square or address) into a playable Mad Max battle-car game — OpenStreetMap + terrain (Lantmäteriet/Copernicus) → Blender city → web tiles → themed game with its own title, splash screen, voice lines and music, and optional refinement of the buildings from photos and Street View. Use when the user names a place to build ("bygg Visby", "make Lund", "skapa en variant med Ystad", "generate my hometown"), wants a new city variant, or asks to continue/finish a city. Not for editing individual houses (use refine-city) or putting it online (use deploy-arena).
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

## 1b. Ask once, up front

Right after the place is pinned, ask everything that needs the user in one round. Use the question tool
if you have one: four questions at most per call, multiSelect where several answers fit. Then work
through the whole flow without stopping.

1. **Language and title** of the game. Default: English, `<PLACE> / WASTELAND`.
2. **Terrain.**
   - Swedish place without `LANTMATERIET_USER` in `.env`: offer Lantmäteriet's 1 m ground model (free;
     needs a Geotorget account and a free order, see 2b) or Copernicus now (automatic, 30 m, hills
     a little softer).
   - Elsewhere: Copernicus is used automatically; only mention it.
3. **Media (paid services; ask before using them):**
   - a splash image (imagegen);
   - voice lines that name the place (ElevenLabs);
   - a soundtrack of its own (Suno, uses the user's credits).
   Each is optional, and the game works without them.
4. **Refinement:**
   - none;
   - known buildings and places from photos found online (church, station, town hall, what the user
     names);
   - Street View rounds for the centre;
   - Street View rounds for the whole town until the user says stop.
   Several can be chosen.

Note the answers in `cities/<slug>/refinements.md` (top), so a later session knows the plan.

## 2. Build

```sh
python3 wasteland.py build <slug>        # 1–5 minutes; run it in the background and wait
```
Steps: fetch (OSM API, Overpass as backup) → terrain (heights: Lantmäteriet 1 m for Swedish places when
.env has LANTMATERIET_USER/PASSWORD, else Copernicus 30 m; seconds) → prepare
(Shapely) → textures → blender (city.blend) → export (tiles) → tiles (meshopt/WebP) → pack (map.json +
config.json) → splash (Blender render).
Resume a failed run with `--from <step>`; `--refresh` downloads OSM data and terrain again. Without
network the terrain step only warns and the city is built flat; run `build <slug> --only terrain` and
`rebuild <slug>` later to add the hills. Hills and the surroundings beyond the play area come with it.

### 2b. Lantmäteriet terrain (Swedish places, if the user wants it)

1. **The account.** The user creates it themselves on https://geotorget.lantmateriet.se/: "Logga in" →
   "Skapa konto" → privatperson, with the e-mail address as user name. You may open the pages in the
   browser, but never create an account or type their personal details.
2. **The order.** Logged in, open "Markhöjdmodell Nedladdning"
   (https://geotorget.lantmateriet.se/geodataprodukter/markhojdmodell-nedladdning-api) → Beställning →
   Lägg i varukorg → Varukorg.
   - It costs 0 kr. Placing it means accepting "Användningsvillkor för värdefulla datamängder".
   - Do it only after the user says yes in chat, or let them click.
   - The access shows at once under Mitt konto → Behörigheter, and a confirmation mail follows.
3. **The password.** Create `.env` (git-ignored, `chmod 600`) with `LANTMATERIET_USER=<e-mail>` and an
   empty `LANTMATERIET_PASSWORD=`. The user fills in the password themselves, for example with
   `! open -e .env` in Claude Code. Never ask for it in chat.
   Check that it is set without printing it:
   `awk -F= '/^LANTMATERIET_PASSWORD=/{print (length($2)>0?"set":"empty")}' .env`
4. **The download.** `python3 wasteland.py build <slug> --only terrain --refresh`, then
   `python3 wasteland.py rebuild <slug>`.
   The step prints "Lantmäteriet Markhöjdmodell (DTM)" when it worked, and names the reason when it
   fell back to Copernicus (for example HTTP 401/403: no access ordered yet).

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
- Language and title come from 1b; default title is `<PLACE> / WASTELAND`. Keep titles short (they
  are huge on screen).
- Use `facts.landmarks` and `facts.streets` for local colour: the intro, tagline and voice lines should
  name real places (the cathedral, the harbour, the main street). Keep it playful and non-hateful;
  don't mock real living people.
- Voice lines (`voice.lines`): `intro` and `win` must name the place; `wave`, `critical`, `repair`,
  `wrecked` are optional overrides. One or two sentences each, ElevenLabs audio tags in brackets.
- Tactical-map labels come from churches, stations, squares etc.; add others the user cares about
  with `map_labels` (a landmark name, or `{"name": "The Pier", "lat": …, "lon": …}`).
- Run `python3 wasteland.py theme <slug>` again to apply text changes.

## 4. Media (what the user chose in 1b)

Only what the user said yes to in 1b (they cost money or credits). Ask again before a second paid
round, for example new voices after the lines change.

| What | How | Without it |
|---|---|---|
| Splash screen | **imagegen** skill → `cities/<slug>/media/splash.jpg` | Blender render of the street with the car |
| Voice lines | **elevenlabs** skill → `python3 wasteland.py voices <slug>` | generic narrator lines, no place names |
| Music | **suno-music** skill → `python3 wasteland.py music <slug> --add …` | the bundled three-track soundtrack |

After adding media: `python3 wasteland.py build <slug> --only pack`.

## 4b. Refine the buildings (what the user chose in 1b)

Follow the **refine-city** skill.

**Known buildings and places:**
- Search for photos online: Wikimedia Commons; for Swedish places DigitaltMuseum, Kringla and the
  municipality.
- Save openly licensed ones in `references/<landmark>/`, with `SOURCES.md` (author, licence, URL).
- Write a hand-made `custom/<id>.py`.
- Compare renders with the photos.
- Put important places on the tactical map with `map_labels`.

**Street View rounds:**
```sh
python3 wasteland.py survey <slug> plan --near "<the main square or street>" --out /tmp/<slug>-sv
# screenshot each link → /tmp/<slug>-sv/<index>.jpg (keep Street View frames out of the repository)
python3 wasteland.py survey <slug> compare /tmp/<slug>-sv
```
- Write what each sheet shows into `overrides.json` (style, colour, roof, storeys, a descriptive
  `note`), and set area mixes for whole districts.
- Then `python3 wasteland.py seed <slug> --ids … --force` and `python3 wasteland.py rebuild <slug>`,
  hand-edit the scripts that need more, and compare again.
- For the whole town, start with `survey <slug> plan --out …` (everything not yet checked) and keep
  doing rounds until the user says stop.
- Log every round in `refinements.md`. A map of which houses are hand-made, checked, from an area rule
  or still guessed helps the user follow along.

## 5. Play and check

```sh
python3 wasteland.py play <slug>         # dev server on http://localhost:5220 — run in the background
```
If you have a browser tool, open it: the start screen must show the new title and splash, the status
line "<n> streets & paths / <Name> is ready", and ENTER THE STREET WAR must start a game on a street
(not inside a building, not in water). Press Tab for the tactical map: labels should be local places.
Otherwise ask the user to open the URL.

## 6. Finish

Tell the user:
- what was built: buildings, streets and landmarks from `python3 wasteland.py status <slug>`;
- which terrain it stands on (Lantmäteriet or Copernicus);
- what was refined and what is still generic (estimated heights and colours where OSM has none).

Then the next options:
- more refinement rounds → **refine-city** skill
- publish the website and an online-arena server → `python3 wasteland.py publish <slug>` and **deploy-arena**

## Rules

- Never commit or print API keys or passwords; they live in `.env` (git-ignored). The user types
  passwords into `.env` themselves.
- Creating accounts, accepting terms and placing orders: the user's decision. Open the pages and
  explain, act only on an explicit yes, and never fill in credentials.
- OpenStreetMap data is ODbL: keep the attribution (the game shows it). Don't loop downloads; reuse
  `osm.json` (`--refresh` only when needed).
- Long commands (build, play, render) go to the background; poll their output instead of blocking.
- If a step fails, read the last lines it printed, fix the cause, and resume with `--from <step>`.
