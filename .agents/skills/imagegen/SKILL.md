---
name: imagegen
description: Generate or repaint bitmap art for a city's game — above all the menu splash screen (16:9 key art with the town's real landmarks and an armored car) — with Codex's built-in image tool, OpenAI GPT Image or Gemini via OpenRouter. Use when the user wants a splash/menu image, key art, a poster or a new look for the start screen of a generated city ("gör en splashbild för Visby", "make cover art"). Not for textures of the 3D city (those are procedural).
---

# Images for a generated city

The menu shows `cities/<slug>/media/splash.jpg` behind the HTML title (the title is text in the
page, never in the image). Without it the game uses `media/splash-default.jpg`, a Blender render of
the generated street with the Interceptor — which is also the best **composition reference**.

## Splash screen recipe

1. Read `cities/<slug>/theme.json` → `splash_prompt` (already names the place and landmarks) and
   `facts.landmarks`. Improve the prompt with what the town is known for: the cathedral's towers, the
   harbour cranes, a ring wall, half-timbered houses, a square. Keep these constraints:
   - wide 16:9 landscape, **car on the right third, calm dark space on the left** for the title
   - dusk, dust, rust, warm orange light, charcoal shadows (matches the game's fog and HUD)
   - an armored post-apocalyptic muscle car (ram plow, riveted plates, roof guns)
   - **no text, no logos, no watermarks, no recognisable real people**
2. Generate, using what your environment offers:
   - **Codex**: the built-in image generation tool (no key needed). Attach/view
     `media/splash-default.jpg` as a reference image and ask for a repaint in the same composition.
     Save the chosen result into the project (built-in images land under `$CODEX_HOME/generated_images/`
     — copy it, don't leave it there).
   - **Claude Code or a terminal** (needs `OPENAI_API_KEY` or `OPENROUTER_API_KEY` in `.env`):
     ```sh
     .venv/bin/python .agents/skills/imagegen/scripts/generate_image.py \
       --prompt "<prompt>" --reference cities/<slug>/media/splash-default.jpg \
       --out cities/<slug>/media/splash.jpg --size 1920x1080
     ```
     `--provider openai|openrouter` picks the service (default: whichever key exists, OpenAI first);
     `--model` overrides the default (`gpt-image-2`, falling back to `gpt-image-1`;
     `google/gemini-3-pro-image-preview` on OpenRouter). Drop `--reference` for a free composition.
   - Gemini/OpenRouter can also be reached through a `gemini-imagegen` skill if one is installed.
3. Look at the result. Reject images with text, mangled cars, the car on the left, or no sense of the
   place. One or two retries with a sharper prompt are normal.
4. Save as `cities/<slug>/media/splash.jpg` (1920×1080 JPEG; the script crops and resizes) and apply:
   ```sh
   python3 wasteland.py build <slug> --only pack
   ```
5. Record the final prompt in `cities/<slug>/media/splash-prompt.md` (provider, model, date). Image
   generation costs money: ask the user before the first paid call in a session.

## Other images

The same script makes social-media cards (`--size 1200x630`) or posters (`--size keep`). Shared game
art (fire, smoke, rust textures in `game/public/art/`) is common to every city — leave it alone unless
the user asks; record prompts in `game/art/*.md` if you change it.
