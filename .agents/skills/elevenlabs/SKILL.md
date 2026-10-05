---
name: elevenlabs
description: Voices and sounds for the battle-car game with ElevenLabs — the narrator's voice lines that name the city (intro, victory, waves, warnings), choosing or describing a narrator voice, and regenerating shared sound effects (engines, guns, impacts). Use when the user wants the game to speak about their town, a different narrator, new voice lines ("låt berättaren säga Visby", "make the announcer sound like…"), or new/better sound effects.
---

# ElevenLabs voices and sounds

Needs `ELEVENLABS_API_KEY` in `.env` (https://elevenlabs.io/app/settings/api-keys). Generation costs
credits: tell the user what will be generated (number of lines/effects) before the first paid call.
Without a key the game still works with its generic narrator lines.

## Narrator lines for a city

The lines live in `cities/<slug>/theme.json` → `voice`:
```json
"voice": {"voice_id": "JBFqnCBsd6RMkjVDRZzb", "model": "eleven_v3",
          "lines": {"intro": "…", "win": "…", "wave": "…", "critical": "…", "repair": "…", "wrecked": "…"}}
```
| line | when the game plays it | notes |
|---|---|---|
| intro | a run starts | must name the place; 2–3 sentences |
| win | all three waves cleared | must name the place |
| wave | a new wave arrives | a landmark or street makes it local |
| critical | armor is breaking | short and urgent |
| repair | a repair crate is picked up | short |
| wrecked | the player dies | short, somber |

Writing tips: one idea per line, spoken length 3–9 seconds, audio tags in brackets steer delivery
(`[gravelly]`, `[urgent]`, `[pause]`, `[excited]`, `[somber]`, `[whispers]`). Write in the game's
language (`theme.json` → `language`); the v3 model speaks many languages — check pronunciation of
local names by listening, and spell them phonetically in the text if needed.

Generate (only new or changed lines are paid for):
```sh
python3 wasteland.py voices <slug>                 # all lines in theme.json
python3 wasteland.py voices <slug> --only intro,win --force
```
Files land in `cities/<slug>/media/voice-*.mp3` and are copied into the game pack. Lines that are
missing fall back to the shared generic recordings in `game/public/audio/`.

## Choosing a voice

- Keep the default gravelly narrator, or set `voice.voice_id` (or `ELEVENLABS_VOICE_ID` in `.env`).
- To find voices: `.venv/bin/python -c "from elevenlabs import ElevenLabs;import os;c=ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY']);[print(v.voice_id,v.name,(v.labels or {})) for v in c.voices.search(page_size=30).voices]"`
  (load `.env` into the environment first, e.g. `set -a; . ./.env; set +a`).
- To describe a new voice for ElevenLabs Voice Design, write a 300-character description: tone,
  pitch, pace, texture, emotion, accent, special qualities — e.g. *"Deep, gravelly male voice with a
  weary, battle-worn timbre. Slow, deliberate pace with clipped consonants. Low bass, dusty rasp,
  controlled intensity…"* Count the characters; exactly 300 reads best in their UI.

## Longer dialogue

`scripts/generate_dialogue.py` takes a JSON array of `{"text", "voice_id"}` items (several voices
allowed), splits it into ≤2000-character chunks, caches each chunk by content hash and joins the
result (ffmpeg or pydub): `.venv/bin/python .agents/skills/elevenlabs/scripts/generate_dialogue.py -i lines.json -o out.mp3 --model eleven_v3`.

## Sound effects (shared by every city)

`scripts/sound_effects.py` holds the prompts for all `game/public/audio/sfx-*.mp3` (engine, gun,
explosion, impacts by material, scrape, nitro, pickup, rocket, mine, flamethrower). To change one,
edit its prompt and run `.venv/bin/python .agents/skills/elevenlabs/scripts/sound_effects.py --only gun --force`.
Prompt advice and API parameters (duration 0.5–30 s, `loop` for seamless loops, `prompt_influence`):
`references/sound-effects.md`. Keep effects dry, isolated, "no music, no voices".
