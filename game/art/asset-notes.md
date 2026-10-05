# Asset provenance (shared by every city)

These assets come from **Kalmar Wasteland**, the game this engine was extracted from, and are the same
in every generated city. Place-specific media (splash, narrator lines naming the town, the city's own
music) are made per city under `cities/<slug>/media/` — see the skills in `.agents/skills/`.

## Vehicles

`art/battlecars.blend` and `tools/build-vehicles.py` (Blender 4.2+, tested with 5.2) build the three
cars: Interceptor (07), Rust Hound (13) and War Rig (88) → `public/models/*.glb`. `npm run models`
re-exports them; `VEHICLE_LETTERING=...` sets the rear lettering text. At runtime the game hides the
lettering and paints the installed city's name on the rear instead (`src/vehicles.js`).
`src/vehicle-design.js` upgrades the silhouettes at load time.

## Bitmaps (`public/art/`)

Generated with the Imagegen tool (OpenAI). Prompts: `wasteland-image-prompts.md` (rust/grunge surface,
fire plume), `fire-atlas-v2.md` (eight-frame fire atlas). `dust-smoke.png`: a soft transparent dusty
smoke puff for particles.

## Audio (`public/audio/`)

- Sound effects: ElevenLabs `eleven_text_to_sound_v2`; prompts live in
  `.agents/skills/elevenlabs/scripts/sound_effects.py`. Some material impacts were made in the
  ElevenLabs web UI (`audio-2026-10-05.md`). `sfx-wind` and `sfx-fire` are ambience loops from an
  earlier Kalmar project.
- Narrator: four place-neutral lines (wave, critical, repair, wrecked; scripts in `voice-*.json`).
  Each city adds its own intro and victory lines naming the town.
- Music: three instrumental Suno tracks (Sandstorm Pursuit, Iron Tide, Dusk Convoy), made in the
  official Suno web app; prompts in `suno-*.md`, song links in `public/audio/music.json`.
  Check the Suno account's plan terms before publishing the game commercially.

The original Kalmar menu artwork is kept as an example in `docs/images/kalmar-splash-example.jpg`.
