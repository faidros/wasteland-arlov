# The battle-car game

A Three.js / WebGL Mad Max-style game that drives whatever city is installed in `public/city/`
(a link to `cities/<slug>/pack/`, set by `python3 ../wasteland.py play <slug>`). Extracted from
*Kalmar Wasteland* and made place-independent: every name, text, spawn point, map label, splash
screen, narrator line and radio playlist comes from the city pack's `config.json` and media.

```sh
npm install            # done by `python3 wasteland.py doctor`
npm run dev            # http://localhost:5220  (the city must be installed first)
npm test               # unit tests (+ checks against the installed city when there is one)
npm run build          # static site in dist/ — use `python3 wasteland.py publish <slug>` instead
```

**Modes:** Street War (three waves of raiders), Free Roam, Online Arena (up to eight drivers through
a small WebSocket relay, see `deploy/README.md`). **Machines:** Interceptor, Rust Hound, War Rig.
**Weapons:** twin machine guns, homing rockets, flamethrower, rear mines. **Driver's seat view**
with a riveted dashboard, live dials, warning lamps and a radio that shows the current track (`src/cockpit.js`). Ramming uses mass and
closing speed; facades take localized damage; light street furniture can be knocked loose.

| Control | Action |
|---|---|
| WASD / arrows | Drive; S brakes, then reverses |
| F / left click | Fire |
| Shift | Nitro |
| Space | Handbrake / drift |
| C / VIEW button | Chase → driver's seat → bonnet camera |
| Q | Look behind |
| Tab / M | Tactical map; click to set a waypoint |
| R | Respawn on a clear street |
| 1–4 / E | Choose weapon |
| Esc | Pause |

Touch controls appear on phones and tablets (`?touch=1` forces them).

## The city contract

`public/city/` must contain:
- `tiles/tiles.json`, `tiles/base.glb` (always loaded: ground, streets, water), `tiles/c<i>_<j>.glb`
  (streamed 60 m tiles), `tiles/materials.glb` and `tiles/materials-mobile.glb` (material library;
  tiles reference materials by name; `extras.tint` colours tintable textures through their alpha mask);
- `map.json` — `roads [{id, name, kind, w, p:[[x,z]…]}]`, `buildings [[[x,z]…]]` (2D collision and
  minimap), `areas [{k: land|green|road|path, p:[outer, …holes]}]` (land decides where you can drive),
  `land`, `bounds`;
- `config.json` — names/texts, `spawn {x,z,heading}`, `bounds`, `labels`, `districts`, `squares`,
  `crates`, `fires`, `splash`, `voices`, `music` (see `src/city-config.js` for defaults);
- optional `splash.jpg`, `audio/voice-*.mp3`, `audio/music.json` + tracks.

Coordinates: metres, three.js Y-up, x east, z south; heading 0 faces north (−z). Meshes whose name
contains `Furniture` are split into breakable props; material names containing glass/wood/metal pick
collision sounds.

Development pages: `/tools/mobile-preview.html`, `/tools/audio-preview.html`,
`/tools/arena-relay-check.html`; `?debug=1` adds effect demos. This is an arcade prototype, not a
simulation: no full rigid-body chassis, tire model or structural building collapse.
