"""Download the ground heights for a city: Copernicus GLO-30 elevation → cities/<slug>/terrain.json.

    python3 pipeline/fetch_terrain.py <slug> [--force]

The Copernicus DEM (30 m, global, free) is published on AWS as one cloud-optimised GeoTIFF per
1°×1° tile. Only the internal 1024×1024 blocks that cover the city and a margin round it are read
with HTTP range requests and decoded here (deflate + floating-point predictor), so no GDAL is needed.
The result is a small lat/lon grid of heights in metres above sea level. It is a surface model
(buildings and tree tops included); prepare_city.py removes them with the OpenStreetMap footprints
and forests and turns the rest into the terrain under the city. Re-running reuses the file unless
--force. Without network the step only warns: the city is then built flat.
"""
from __future__ import annotations

import argparse
import json
import math
import struct
import urllib.error
import urllib.request
import zlib

import numpy as np

from common import EARTH, USER_AGENT, city_dir, load_place, say, step_done, write_json

BUCKET = 'https://copernicus-dem-30m.s3.amazonaws.com'
MARGIN_M = 600          # the surroundings beyond the play area (hills on the horizon)
ATTRIBUTION = ('Terrain: Copernicus DEM GLO-30 © DLR e.V. 2010-2014 and © Airbus Defence and Space GmbH 2014-2018, '
               'provided under COPERNICUS by the European Union and ESA')


def tile_name(lat_i: int, lon_i: int) -> str:
    ns = f'{"N" if lat_i >= 0 else "S"}{abs(lat_i):02d}'
    ew = f'{"E" if lon_i >= 0 else "W"}{abs(lon_i):03d}'
    return f'Copernicus_DSM_COG_10_{ns}_00_{ew}_00_DEM'


def get_range(url: str, start: int, length: int) -> bytes:
    req = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Range': f'bytes={start}-{start + length - 1}'})
    with urllib.request.urlopen(req, timeout=120) as res:
        return res.read()


class CogTile:
    """The full-resolution image of one Copernicus COG: tile layout and geo-referencing."""
    TYPES = {1: 'B', 2: 's', 3: 'H', 4: 'I', 11: 'f', 12: 'd', 16: 'Q'}

    def __init__(self, url: str):
        self.url = url
        head = get_range(url, 0, 1 << 16)
        self.e = '<' if head[:2] == b'II' else '>'
        off = struct.unpack(self.e + 'I', head[4:8])[0]
        n = struct.unpack(self.e + 'H', head[off:off + 2])[0]
        tags = {}
        for i in range(n):
            p = off + 2 + 12 * i
            tag, typ, cnt, val = struct.unpack(self.e + 'HHII', head[p:p + 12])
            fmt = self.TYPES.get(typ)
            if not fmt or fmt == 's':
                continue
            size = struct.calcsize(fmt) * cnt
            if size <= 4:
                raw = head[p + 8:p + 8 + size]
            else:
                raw = head[val:val + size] if val + size <= len(head) else get_range(url, val, size)
            tags[tag] = struct.unpack(self.e + fmt * cnt, raw)
        self.width, self.height = tags[256][0], tags[257][0]
        self.tw, self.th = tags[322][0], tags[323][0]
        self.offsets, self.counts = tags[324], tags[325]
        self.compression = tags.get(259, (1,))[0]
        self.predictor = tags.get(317, (1,))[0]
        if tags.get(258, (32,))[0] != 32 or tags.get(339, (3,))[0] != 3:
            raise ValueError('expected 32-bit float samples')
        sx, sy = tags[33550][:2]
        _, _, _, lon0, lat0, _ = tags[33922]
        keys = tags.get(34735, ())
        point = any(keys[k] == 1025 and keys[k + 3] == 2 for k in range(4, len(keys), 4))
        # Pixel centres: Copernicus uses PixelIsPoint (the tiepoint is the centre of pixel 0,0).
        self.lon0, self.lat0 = (lon0, lat0) if point else (lon0 + sx / 2, lat0 - sy / 2)
        self.dlon, self.dlat = sx, sy
        self.across = math.ceil(self.width / self.tw)

    def block(self, bi: int, bj: int) -> np.ndarray:
        k = bj * self.across + bi
        raw = get_range(self.url, self.offsets[k], self.counts[k])
        data = zlib.decompress(raw) if self.compression in (8, 32946) else raw
        if self.predictor == 3:
            # Floating-point predictor: per row, byte differences over 4 byte planes, most significant first.
            a = np.frombuffer(data, np.uint8).reshape(self.th, 4 * self.tw)
            a = np.cumsum(a, axis=1, dtype=np.uint8)
            return a.reshape(self.th, 4, self.tw).transpose(0, 2, 1).copy().view('>f4').reshape(self.th, self.tw).astype(np.float32)
        return np.frombuffer(data, self.e + 'f4').reshape(self.th, self.tw).astype(np.float32)

    def window(self, lat_n, lat_s, lon_w, lon_e):
        """(rows, cols, origin lat, origin lon, array) of the pixels covering a lat/lon box."""
        r0 = max(0, math.floor((self.lat0 - lat_n) / self.dlat))
        r1 = min(self.height - 1, math.ceil((self.lat0 - lat_s) / self.dlat))
        c0 = max(0, math.floor((lon_w - self.lon0) / self.dlon))
        c1 = min(self.width - 1, math.ceil((lon_e - self.lon0) / self.dlon))
        out = np.full((r1 - r0 + 1, c1 - c0 + 1), np.nan, np.float32)
        for bj in range(r0 // self.th, r1 // self.th + 1):
            for bi in range(c0 // self.tw, c1 // self.tw + 1):
                b = self.block(bi, bj)
                y0, x0 = bj * self.th, bi * self.tw
                ya, yb = max(r0, y0), min(r1, y0 + self.th - 1, self.height - 1)
                xa, xb = max(c0, x0), min(c1, x0 + self.tw - 1, self.width - 1)
                out[ya - r0:yb - r0 + 1, xa - c0:xb - c0 + 1] = b[ya - y0:yb - y0 + 1, xa - x0:xb - x0 + 1]
        return out, self.lat0 - r0 * self.dlat, self.lon0 + c0 * self.dlon


def fetch(place: dict) -> dict:
    lat, lon = place['center']
    half = place['size_m'] / 2 + MARGIN_M
    dlat = half / EARTH
    dlon = half / (EARTH * math.cos(math.radians(lat)))
    lat_s, lat_n, lon_w, lon_e = lat - dlat, lat + dlat, lon - dlon, lon + dlon
    # Output grid: the finest spacing of the tiles involved, in arc seconds (1" north-south).
    step_lat = 1 / 3600
    step_lon = step_lat / max(0.25, math.cos(math.radians(lat)))
    rows = math.ceil((lat_n - lat_s) / step_lat) + 1
    cols = math.ceil((lon_e - lon_w) / step_lon) + 1
    z = np.full((rows, cols), np.nan, np.float32)
    lats = lat_n - np.arange(rows) * step_lat
    lons = lon_w + np.arange(cols) * step_lon
    sources = []
    for lat_i in range(math.floor(lat_s), math.floor(lat_n) + 1):
        for lon_i in range(math.floor(lon_w), math.floor(lon_e) + 1):
            name = tile_name(lat_i, lon_i)
            url = f'{BUCKET}/{name}/{name}.tif'
            ys = (lats >= lat_i) & (lats < lat_i + 1)
            xs = (lons >= lon_i) & (lons < lon_i + 1)
            if not ys.any() or not xs.any():
                continue
            try:
                cog = CogTile(url)
            except urllib.error.HTTPError as exc:
                if exc.code in (403, 404):          # no tile: open sea
                    z[np.ix_(ys, xs)] = 0.0
                    sources.append(f'{name} (sea)')
                    continue
                raise
            arr, alat, alon = cog.window(lats[ys].max(), lats[ys].min(), lons[xs].min(), lons[xs].max())
            # Bilinear sampling of the tile window at the output grid.
            fy = (alat - lats[ys]) / cog.dlat
            fx = (lons[xs] - alon) / cog.dlon
            y0 = np.clip(np.floor(fy).astype(int), 0, arr.shape[0] - 2)
            x0 = np.clip(np.floor(fx).astype(int), 0, arr.shape[1] - 2)
            ty = np.clip(fy - y0, 0, 1)[:, None]
            tx = np.clip(fx - x0, 0, 1)[None, :]
            a, b = arr[np.ix_(y0, x0)], arr[np.ix_(y0, x0 + 1)]
            c, d = arr[np.ix_(y0 + 1, x0)], arr[np.ix_(y0 + 1, x0 + 1)]
            z[np.ix_(ys, xs)] = (a * (1 - tx) + b * tx) * (1 - ty) + (c * (1 - tx) + d * tx) * ty
            sources.append(name)
    z[(z < -500) | (z > 9000)] = np.nan
    if np.isnan(z).all():
        raise RuntimeError('no elevation data for this place')
    z = np.where(np.isnan(z), np.nanmin(z), z)
    return {'source': 'Copernicus DEM GLO-30 (DSM)', 'attribution': ATTRIBUTION, 'tiles': sources,
            'lat0': lat_n, 'lon0': lon_w, 'dlat': step_lat, 'dlon': step_lon, 'rows': rows, 'cols': cols,
            'z': [round(float(v), 1) for v in z.ravel()]}


def main(argv=None):
    ap = argparse.ArgumentParser(prog='fetch_terrain.py')
    ap.add_argument('slug')
    ap.add_argument('--force', action='store_true')
    args = ap.parse_args(argv)
    folder = city_dir(args.slug)
    out = folder / 'terrain.json'
    if out.exists() and not args.force:
        say(f'  terrain.json is already there (use --refresh to download again)')
        step_done(args.slug, 'terrain', cached=True)
        return
    try:
        data = fetch(load_place(args.slug))
    except Exception as exc:  # offline or the bucket is unreachable: build the city flat
        say(f'  ! no terrain ({exc}); the city will be flat. Try again later with: python3 wasteland.py build {args.slug} --only terrain')
        return
    write_json(out, data, compact=True)
    z = data['z']
    say(f'  {data["rows"]}×{data["cols"]} heights from {", ".join(data["tiles"])}: {min(z):.0f}–{max(z):.0f} m above sea level')
    step_done(args.slug, 'terrain', low=min(z), high=max(z))


if __name__ == '__main__':
    main()
