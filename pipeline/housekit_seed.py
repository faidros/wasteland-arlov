"""Write starter housekit scripts (cities/<slug>/custom/<id>.py) from surveyed overrides.

    python3 pipeline/housekit_seed.py <slug> [--ids w1,w2 …] [--force]

Every building in overrides.json that has a style, colour and roof gets a script built from those
facts and the keywords in its Street View `note` (balconies, dormers, awnings/canopies, cross gable,
mansard, chimneys, veranda, galleries with outside stairs, entrance porches, 1950s/60s/modern blocks,
garages, halls). The script is a starting point:
look at the house from the street (refine-city skill), compare with the photo and edit it by hand.
Existing scripts are kept unless --force, and --force only replaces starter scripts: a script whose
docstring no longer carries the starter marker has been edited by hand and is never overwritten.
"""
from __future__ import annotations

import argparse
import json
import re

from common import city_dir

WALL_STYLE = {'plaster': 'Plaster', 'brick': 'Brick', 'wood': 'Wood', 'stone': 'Stone', 'concrete': 'Concrete', 'glass': 'Glass', 'metal': 'Metal'}
ROOF_STYLE = {'tiles': 'Tiles', 'metal': 'Metal', 'slate': 'Slate'}
STARTER = 'Starter script from housekit_seed.py'      # the marker of an untouched starter script


def has(note, *words):
    return any(re.search(w, note, re.I) for w in words)


def script_for(bid, e, b):
    note = e.get('note', '')
    style, colour = e.get('style', b['style']), e.get('colour', b['colour'])
    shape = e.get('roof', 'gabled')
    rs, rc = e.get('roof_style', 'metal'), e.get('roof_colour', 'black')
    levels = int(e.get('building:levels', b['levels']))
    shop = bool(e.get('shopfront', False))
    height = e.get('height')
    timber = style == 'wood'
    wall = f"M_Wall_{WALL_STYLE[style]}_{colour}_Blank"
    trim = 'M_Wall_Wood_white_Blank' if timber else ('M_Wall_Plaster_grey_Blank' if colour == 'white' else 'M_Wall_Plaster_white_Blank')
    block = has(note, r'\b(19)?[56]0s\b', 'block', 'modern', 'point block', 'office') or (has(note, 'apartment') and style != 'wood')
    half = has(note, '1½')                     # 1½-storey villa: one storey under a steep roof with gable windows
    villa = has(note, 'villa')                 # a villa with a garage stays a house: one garage door at the end
    hall = not villa and (has(note, 'hall', 'warehouse', 'workshop', 'store\\b', 'barn', 'garage', 'shed', 'industrial') or (height and levels == 1 and float(height) >= 4.5 and not half))
    kind = 'modern' if (block or hall) else 'sash'
    if has(note, 'arched', 'round-arched'):
        kind = 'arched'
    garages = has(note, 'garage', 'big doors', 'barn', 'carport')
    win = (1.4, 1.2) if hall else ((1.2, 1.45) if block else (1.1, 1.45))
    pitch = {'tiles': 34, 'slate': 32, 'metal': 26}.get(rs, 28)
    if shape == 'hipped':
        pitch -= 4
    if has(note, 'steep') or half:
        pitch = 45
    if has(note, 'mansard'):
        shape = 'mansard'
    ground = None
    if levels == 1 and height and not half:
        ground = max(3.0, float(height) - (0.0 if shape == 'flat' else 1.0))
    lines = [f'"""{b.get("name") or bid}: {note or "surveyed"}\n(Starter script from housekit_seed.py — compare with the photo and edit by hand.)"""',
             'import housekit', '']
    args = [f"levels={levels}", f"wall='{wall}'", f"trim='{trim}'", f"shop={shop}"]
    if ground:
        args.append(f"ground={ground:.1f}")
    if has(note, 'red trim', 'red window', 'red frames', 'red-painted window'):
        args.append("frame='M_Wall_Wood_falu_Blank'")
    elif has(note, 'brown window', 'brown frames'):
        args.append("frame='M_Wall_Wood_brown_Blank'")
    if hall:
        args.append("plinth='M_Concrete'")
    lines.append(f"h = housekit.House(ctx, {', '.join(args)})")
    if not timber and has(note, 'surround', 'white trim'):
        lines.append('h.surrounds = True')
    fac = [f"window=({win[0]}, {win[1]})", f"pitch={3.2 if hall else (2.9 if block else 2.6)}", f"kind='{kind}'"]
    if has(note, 'awning') or (has(note, 'canop') and not has(note, 'porch', 'gabled canop', 'entrance canop')):
        if has(note, 'striped'):
            aw = "['M_Wall_Plaster_white_Blank', 'M_Roof_Metal_red']"
        elif has(note, 'blue'):
            aw = "['M_Wall_Metal_blue_Blank']"
        elif has(note, r'\bred\b'):
            aw = "['M_Roof_Metal_red']"
        else:
            aw = "['M_Wall_Plaster_white_Blank']"
        fac.append(f"awnings={aw}")
        if not shop:
            fac.append('upper_awnings=True')
    if shop:
        fac.append("sign_mat='M_Wall_Plaster_white_Blank'" if not timber else "sign_mat='M_Wall_Wood_white_Blank'")
    m = re.search(r'(mustard|ochre|red|blue|green|copper|brown)[- ]?(brown )?panels', note, re.I)
    if m:
        pc = {'mustard': 'M_Wall_Wood_ochre_Blank', 'ochre': 'M_Wall_Wood_ochre_Blank', 'red': 'M_Wall_Wood_falu_Blank',
              'blue': 'M_Wall_Metal_blue_Blank', 'green': 'M_Wall_Metal_green_Blank', 'copper': 'M_Wall_Wood_brown_Blank',
              'brown': 'M_Wall_Wood_brown_Blank'}[m.group(1).lower()]
        fac.append(f"panels='{pc}'")
    porches = has(note, 'entrance porch', 'porches') and not garages
    if porches:
        lines += ['pw = max(h.street or range(len(h.walls)), key=lambda i: h.walls[i].L)',
                  'px = [h.walls[pw].L * 0.25, h.walls[pw].L * 0.75] if h.walls[pw].L > 14 else [h.walls[pw].L * 0.5]',
                  'skip = {pw: [(x - 1.1, x + 1.1) for x in px]}']
        fac += ['skip=skip', 'entrance=False']
    if garages:
        lines += ['st = max(h.street or range(len(h.walls)), key=lambda i: h.walls[i].L)',
                  'L = h.walls[st].L',
                  'n = max(1, int(L // 3.4)) if L < 30 else max(1, int(L // 3.2))',
                  ('xs = [max(1.6, L - 2.2)]' if villa else
                   'xs = [L * (k + 0.5) / n for k in range(n)] if ' + ('True' if has(note, 'garage row', 'garages', 'carport') else 'False') + ' else [L * 0.5]'),
                  "skip = {st: [(x - 1.4, x + 1.4) for x in xs]}"]
        fac.append('skip=skip')
        if not villa:
            fac.append('entrance=False')
        else:
            fac.append('door_at=0.3')
    lines.append(f"h.facades({', '.join(fac)})")
    if garages:
        door = ('M_Wall_Wood_brown_Blank' if has(note, 'brown doors') else
                'M_Wall_Wood_weathered_Blank' if has(note, 'grey doors', 'grey garage doors') else 'M_Wall_Wood_white_Blank')
        lines.append(f"for x in xs: h.garage(st, x, mat='{door}')")
    roofmat = f"M_Roof_{ROOF_STYLE.get(rs, 'Metal')}_{rc}"
    if shape == 'flat':
        lines.append("h.roof(shape='flat')")
    else:
        lines.append(f"h.roof(shape='{shape}', pitch={pitch}, mat='{roofmat}')")
        if has(note, 'cross gable', 'central gable', 'pointed gable', 'gable dormer', 'gabled dormer'):
            lines.append(f"h.cross_gable(frac=0.5, width=4.5, pitch=48, roof_mat='{roofmat}', windows=2)")
        if has(note, 'dormer') and not has(note, 'gable dormer'):
            lines.append(f"h.dormers([0.3, 0.7], side='street', mat='{wall}', roof_mat='{roofmat}')")
        if has(note, 'chimney') or (not hall and not block):
            lines.append("h.chimney(0.35, 0.55)")
    if has(note, 'balcon') and not has(note, 'gallery'):
        glass = 'True' if has(note, 'glazed balcon', 'glass') else 'False'
        rail = "'M_Roof_Metal_green'" if has(note, 'green balcon') else ("'M_Roof_Metal_red'" if has(note, 'red balcon') else ("'M_Wall_Plaster_white_Blank'" if not timber else "'M_Wall_Wood_white_Blank'"))
        lines += ['st = sorted(h.street, key=lambda i: -h.walls[i].L)',
                  f'for i in st[:1]:',
                  f'    n = max(1, int(h.walls[i].L // 8))',
                  f'    for s in range(2, {levels} + 1):',
                  f'        for k in range(n):',
                  f'            h.balcony(i, x=h.walls[i].L * (k + 0.5) / n, storey=s, width=2.6, depth=1.1, rail={rail}, glass={glass})']
    if has(note, 'gallery', 'external stair'):
        lines += ['st = sorted(h.street or range(len(h.walls)), key=lambda i: -h.walls[i].L)[0]',
                  'L = h.walls[st].L',
                  "h.gallery(st, L * 0.3, L * 0.8, stair='left')"]
    if porches:
        lines.append(f"for x in px: h.porch(pw, x, roof_mat='{roofmat if shape != 'flat' else 'M_Roof_Metal_black'}')")
    if has(note, 'veranda'):
        lines += ['st = sorted(h.street, key=lambda i: -h.walls[i].L)',
                  "if st: h.veranda(st[0], h.walls[st[0]].L * 0.3, h.walls[st[0]].L * 0.7)"]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(prog='housekit_seed.py')
    ap.add_argument('slug')
    ap.add_argument('--ids', help='comma separated building ids (default: every surveyed building)')
    ap.add_argument('--force', action='store_true')
    ap.add_argument('--unsurveyed', action='store_true', help='also every other building ≥ 25 m², from its generated look')
    args = ap.parse_args(argv)
    folder = city_dir(args.slug)
    ov = json.loads((folder / 'overrides.json').read_text())['buildings']
    city = {b['id']: b for b in json.loads((folder / 'city.json').read_text())['buildings']}
    if args.ids is not None and not args.ids.strip(','):
        ap.error('--ids is empty')                      # never fall back to "every building" by accident
    wanted = set(args.ids.split(',')) if args.ids else None
    out = folder / 'custom'
    out.mkdir(exist_ok=True)
    n = 0
    kept = []

    def replaceable(path):
        if not path.exists():
            return True
        if not args.force:
            return False
        if STARTER not in path.read_text():             # edited by hand: keep it
            kept.append(path.stem)
            return False
        return True
    for bid, e in ov.items():
        if wanted and bid not in wanted:
            continue
        cid = bid if bid in city else bid + 'r' if bid + 'r' in city else None
        if not cid or 'style' not in e or e.get('hide'):
            continue
        path = out / f'{cid}.py'
        if not replaceable(path):
            continue
        path.write_text(script_for(cid, e, city[cid]))
        n += 1
    if args.unsurveyed:
        import hashlib
        surveyed = set(ov) | {k + 'r' for k in ov}
        for cid, b in city.items():
            path = out / f'{cid}.py'
            if cid in surveyed or (wanted and cid not in wanted) or not replaceable(path):
                continue
            ring = b['footprint']['outer']
            area = abs(sum(ring[i][0] * ring[(i + 1) % len(ring)][1] - ring[(i + 1) % len(ring)][0] * ring[i][1] for i in range(len(ring)))) / 2
            if area < 25 or b['style'] not in WALL_STYLE or b.get('landmark'):
                continue
            h = int(hashlib.sha1(cid.encode()).hexdigest()[:6], 16) / 0xFFFFFF
            shape = 'flat' if b['roof_style'] == 'flat' else ('hipped' if h < 0.3 else 'gabled')
            e = {'style': b['style'], 'colour': b['colour'], 'roof': shape, 'roof_style': b['roof_style'], 'roof_colour': b['roof_colour'],
                 'building:levels': b['levels'], 'shopfront': bool(b['parts'].get('ground')),
                 'note': ('garden shed or garage' if area < 45 else '') + (' hall' if b['kind'] in ('industrial', 'warehouse', 'retail', 'garages') else '')}
            if area < 45:
                e['building:levels'] = 1
            path.write_text(script_for(cid, e, b).replace('compare with the photo and edit by hand',
                                                         'generated look, not surveyed yet'))
            n += 1
    print(f'{n} starter scripts written to cities/{args.slug}/custom/')
    if kept:
        print(f'{len(kept)} hand-edited scripts kept: {", ".join(sorted(kept))}')


if __name__ == '__main__':
    main()
