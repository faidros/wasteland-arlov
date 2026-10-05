#!/usr/bin/env python3
"""Generate (or repaint) an image with OpenAI GPT Image or Google Gemini via OpenRouter.

    python generate_image.py --prompt "…" --out cities/visby/media/splash.jpg \
        [--reference cities/visby/media/splash-default.jpg] [--size 1920x1080] [--provider auto|openai|openrouter]

Keys come from the environment or the repository's .env: OPENAI_API_KEY or OPENROUTER_API_KEY.
Only the Python standard library is needed to call the APIs; Pillow (in .venv) crops/resizes the
result to --size. Codex users can instead draw with Codex's built-in image tool (no key needed).
"""
from __future__ import annotations

import argparse
import base64
import io
import json
import mimetypes
import os
import re
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


def load_env():
    env = ROOT / '.env'
    if env.exists():
        for line in env.read_text().splitlines():
            m = re.match(r'\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$', line)
            if m and not line.lstrip().startswith('#') and m.group(2) and m.group(1) not in os.environ:
                os.environ[m.group(1)] = m.group(2).strip().strip('"\'')


def post(url, headers, body, timeout=300):
    req = urllib.request.Request(url, data=body, headers={'User-Agent': 'wasteland-builder', **headers})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f'{e.code}: {e.read().decode(errors="replace")[:600]}') from None


def openai_image(prompt, reference, model):
    key = os.environ['OPENAI_API_KEY']
    auth = {'Authorization': f'Bearer {key}'}
    if reference:
        boundary = uuid.uuid4().hex
        parts = []
        for name, value in (('model', model), ('prompt', prompt), ('size', '1536x1024'), ('quality', 'high'), ('n', '1')):
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode())
        mime = mimetypes.guess_type(reference)[0] or 'image/jpeg'
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; filename="{Path(reference).name}"\r\nContent-Type: {mime}\r\n\r\n'.encode()
                     + Path(reference).read_bytes() + b'\r\n')
        parts.append(f'--{boundary}--\r\n'.encode())
        data = post('https://api.openai.com/v1/images/edits', {**auth, 'Content-Type': f'multipart/form-data; boundary={boundary}'}, b''.join(parts))
    else:
        data = post('https://api.openai.com/v1/images/generations', {**auth, 'Content-Type': 'application/json'},
                    json.dumps({'model': model, 'prompt': prompt, 'size': '1536x1024', 'quality': 'high', 'n': 1}).encode())
    return base64.b64decode(data['data'][0]['b64_json'])


def openrouter_image(prompt, reference, model):
    content = [{'type': 'text', 'text': ('Repaint this reference as described, keeping its composition: ' if reference else 'Generate an image: ') + prompt}]
    if reference:
        mime = mimetypes.guess_type(reference)[0] or 'image/jpeg'
        content.append({'type': 'image_url', 'image_url': {'url': f'data:{mime};base64,' + base64.b64encode(Path(reference).read_bytes()).decode()}})
    data = post('https://openrouter.ai/api/v1/chat/completions',
                {'Authorization': f'Bearer {os.environ["OPENROUTER_API_KEY"]}', 'Content-Type': 'application/json'},
                json.dumps({'model': model, 'modalities': ['image', 'text'], 'messages': [{'role': 'user', 'content': content}]}).encode())
    msg = data['choices'][0]['message']
    for img in msg.get('images') or []:
        url = img.get('image_url', {}).get('url', '')
        if url.startswith('data:image'):
            return base64.b64decode(url.split(',', 1)[1])
    raise RuntimeError(f'No image in the reply: {str(msg.get("content"))[:300]}')


def main():
    load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument('--prompt', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--reference', help='image to use as composition reference (image-to-image)')
    ap.add_argument('--size', default='1920x1080', help='final WxH (centre crop + resize); "keep" leaves it as generated')
    ap.add_argument('--provider', default='auto', choices=['auto', 'openai', 'openrouter'])
    ap.add_argument('--model', help='default: gpt-image-2 (OpenAI) / google/gemini-3-pro-image-preview (OpenRouter)')
    a = ap.parse_args()
    provider = a.provider
    if provider == 'auto':
        provider = 'openai' if os.environ.get('OPENAI_API_KEY') else 'openrouter' if os.environ.get('OPENROUTER_API_KEY') else None
    if not provider:
        sys.exit('No image API key. Add OPENAI_API_KEY or OPENROUTER_API_KEY to .env — or, in Codex, use the built-in image tool.')
    print(f'Generating with {provider} …', flush=True)
    if provider == 'openai':
        models = [a.model] if a.model else ['gpt-image-2', 'gpt-image-1']
        last = None
        for m in models:
            try:
                raw = openai_image(a.prompt, a.reference, m)
                break
            except RuntimeError as exc:  # older accounts may not have the newest model
                last = exc
                print(f'  {m}: {str(exc)[:160]}', flush=True)
        else:
            sys.exit(f'OpenAI image generation failed: {last}')
    else:
        raw = openrouter_image(a.prompt, a.reference, a.model or 'google/gemini-3-pro-image-preview')
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw)).convert('RGB')
        if a.size != 'keep':
            w, h = (int(v) for v in a.size.split('x'))
            scale = max(w / im.width, h / im.height)
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
            left, top = (im.width - w) // 2, (im.height - h) // 2
            im = im.crop((left, top, left + w, top + h))
        im.save(out, quality=90) if out.suffix.lower() in ('.jpg', '.jpeg') else im.save(out)
    except ImportError:
        out.write_bytes(raw)
    print(f'Saved {out}')


if __name__ == '__main__':
    main()
