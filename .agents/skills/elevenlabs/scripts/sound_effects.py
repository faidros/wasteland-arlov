#!/usr/bin/env python3
"""Regenerate the game's shared sound effects with ElevenLabs (text to sound effects).

    .venv/bin/python .agents/skills/elevenlabs/scripts/sound_effects.py [--only gun,rocket] [--force]

Writes game/public/audio/sfx-<name>.mp3 and keeps game/public/audio/generation.json in sync.
Existing files are kept unless --force. Needs ELEVENLABS_API_KEY (.env). The prompts are the ones the
original Kalmar Wasteland sounds were made with; edit them to change the character of a sound.
"""
import argparse, json, os, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / 'game/public/audio'
# name: (prompt, seconds, loop)
EFFECTS = {
 'engine':('Close recorded supercharged V8 engine idling steadily, gravelly low mechanical rumble, constant speed, seamless looping engine texture, no music, no voices.',5,True),
 'gun':('A short tight twin machine gun burst, four crunchy metallic shots, mechanical cycling, dry outdoor recording, no music, no voices.',1,False),
 'explosion':('One cinematic car explosion: sharp metal cracking, deep bass blast and brief falling debris, isolated effect, no music, no voices.',3,False),
 'impact':('A single heavy steel car ram collision, crunching metal and brief shattered glass, dry close recorded impact, no music, no voices.',1.5,False),
 'impact-metal-light':('One small vehicle bumper dent: short dry sheet steel clunk and a loose bolt rattle, low intensity parking collision, instant attack, isolated close game sound, no music or speech.',.7,False),
 'impact-metal-heavy':('One violent armored truck collision: immediate deep bass thud with tearing buckling steel, chassis groan and falling metal fragments, powerful compact single impact, dry close recording, no music or speech.',1.3,False),
 'impact-concrete':('One heavy steel car crashing into a concrete wall: instant blunt deep thump, sharp stone crack and falling crunchy masonry grit, short heavy mechanical impact, isolated dry game sound, no music or speech.',1.2,False),
 'impact-wood':('One car smashing a wooden bench: immediate dry timber snap, splintering planks and small pieces rattling onto cobblestones, short isolated close impact, no music or speech.',.9,False),
 'impact-glass':('One immediate shattering glass impact: crisp brittle snap followed by a short shower of tinkling glass fragments onto stone, isolated dry close recorded single sound, no music or speech.',.8,False),
 'scrape-metal':('Continuous abrasive steel bodywork scraping along coarse concrete, gritty midrange grinding, occasional metallic squeaks and loose panel vibration, steady seamless loop, no impact blast, no music or speech.',1.8,True),
 'nitro':('A short powerful pressurized nitrous oxide boost: fast air hiss into roaring jet exhaust whoosh, isolated vehicle game effect, no music or voices.',2,False),
 'pickup':('A short satisfying scavenged metal pickup chime, three bright resonant metal notes over a soft mechanical click, no voice, no music.',1,False),
 'rocket':('A single vehicle mounted rocket launcher firing, forceful metallic thump followed immediately by a hot rocket motor hiss and short doppler whoosh, dry isolated sound, no music or voices.',1.6,False),
 'mine':('A heavy magnetic land mine dropping onto cobblestones with a metallic clack, followed by two quiet electronic arming chirps, close isolated game sound, no music or voices.',1.2,False),
 'flame':('A vehicle flamethrower jet, fierce pressurized roaring gas with a crackling hot flame, constant even intensity for the whole clip, no start or end transient, no music or voices.',1.6,True)
}


def main():
    env = ROOT / '.env'
    if env.exists():
        for line in env.read_text().splitlines():
            m = re.match(r'\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$', line)
            if m and m.group(2) and m.group(1) not in os.environ:
                os.environ[m.group(1)] = m.group(2).strip().strip('"\'')
    ap = argparse.ArgumentParser()
    ap.add_argument('--only')
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()
    from elevenlabs import ElevenLabs
    client = ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])
    wanted = set(a.only.split(',')) if a.only else set(EFFECTS)
    for name, (prompt, seconds, loop) in EFFECTS.items():
        path = OUT / f'sfx-{name}.mp3'
        if name not in wanted or (path.exists() and not a.force):
            continue
        print('Generating', name, flush=True)
        data = client.text_to_sound_effects.convert(text=prompt, duration_seconds=seconds, prompt_influence=.5,
                                                    model_id='eleven_text_to_sound_v2', loop=loop)
        path.write_bytes(b''.join(data))
    meta_path = OUT / 'generation.json'
    meta = json.loads(meta_path.read_text())
    meta['effects'] = sorted(set(meta.get('effects', [])) | {n for n in EFFECTS if (OUT / f'sfx-{n}.mp3').exists()})
    meta_path.write_text(json.dumps(meta, indent=2))
    print('Sound effects ready.')


if __name__ == '__main__':
    main()
