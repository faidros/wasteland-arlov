"""Generate the narrator's voice lines for a city with ElevenLabs (text to dialogue).

Reads theme.json → voice.lines, writes cities/<slug>/media/voice-<name>.mp3 (+ voices.json with the
text hash, so unchanged lines are never paid for twice). Needs ELEVENLABS_API_KEY (.env).
The same API and conventions as .agents/skills/elevenlabs (generate_dialogue.py).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os

from common import city_dir, say, write_json

FALLBACK_MODELS = ['eleven_v3', 'eleven_multilingual_v2']


def main(argv=None):
    ap = argparse.ArgumentParser(prog='wasteland.py voices')
    ap.add_argument('slug')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--only')
    args = ap.parse_args(argv)
    folder = city_dir(args.slug)
    theme_path = folder / 'theme.json'
    if not theme_path.exists():
        raise SystemExit(f'No theme.json yet. Run: python3 wasteland.py theme {args.slug}')
    voice = json.loads(theme_path.read_text()).get('voice', {})
    lines = voice.get('lines', {})
    if args.only:
        lines = {k: v for k, v in lines.items() if k in args.only.split(',')}
    voice_id = os.environ.get('ELEVENLABS_VOICE_ID') or voice.get('voice_id')
    model = voice.get('model', 'eleven_v3')
    media = folder / 'media'
    media.mkdir(exist_ok=True)
    log_path = media / 'voices.json'
    log = json.loads(log_path.read_text()) if log_path.exists() else {}
    from elevenlabs import ElevenLabs
    client = ElevenLabs(api_key=os.environ['ELEVENLABS_API_KEY'])
    for name, text in lines.items():
        key = hashlib.sha256(f'{voice_id}|{model}|{text}'.encode()).hexdigest()[:16]
        out = media / f'voice-{name}.mp3'
        if out.exists() and log.get(name, {}).get('hash') == key and not args.force:
            say(f'  ✓ {name} (unchanged)')
            continue
        last = None
        for m in [model] + [x for x in FALLBACK_MODELS if x != model]:
            try:
                audio = b''.join(client.text_to_dialogue.convert(inputs=[{'text': text, 'voice_id': voice_id}], model_id=m))
                break
            except Exception as exc:  # unknown model or plan limits: try the next one
                last = exc
                audio = None
        if not audio:
            raise SystemExit(f'ElevenLabs failed for "{name}": {last}')
        out.write_bytes(audio)
        log[name] = {'hash': key, 'model': m, 'voice_id': voice_id, 'text': text}
        say(f'  ♪ {name}: {len(audio) // 1024} KB ({m})')
    write_json(log_path, log)
    say('Voice lines ready in media/. They are copied into the game pack.')


if __name__ == '__main__':
    main()
