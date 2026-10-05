"""Offline self-test of the geometry pipeline (no network, no Blender):

    .venv/bin/python -m unittest discover tests

A synthetic OpenStreetMap extract (coast, two streets, houses, an apartment block, a church, a park,
trees) goes through prepare_city.py and make_pack.py; the results are checked for sea/land, buildings,
roofs, sidewalks, the spawn point and the game map.
"""
import json
import shutil
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'pipeline'))

import buildings  # noqa: E402
import make_pack  # noqa: E402
import prepare_city  # noqa: E402
from common import CITIES, Projection  # noqa: E402

SLUG = '_selftest'
CENTER = (55.0, 13.0)
P = Projection(*CENTER)


def ll(x, y):
    lat, lon = P.latlon(x, y)
    return {'lat': lat, 'lon': lon}


def way(i, pts, **tags):
    return {'type': 'way', 'id': i, 'tags': tags, 'geometry': [ll(*p) for p in pts]}


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]


class PipelineTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        folder = CITIES / SLUG
        shutil.rmtree(folder, ignore_errors=True)
        folder.mkdir(parents=True)
        place = {'name': 'Testby', 'query': 'Testby', 'display_name': 'Testby, Testland', 'country_code': 'se', 'center': list(CENTER),
                 'size_m': 600, 'bbox': [0, 0, 0, 0], 'attribution': 'Map data © OpenStreetMap contributors (ODbL)'}
        (folder / 'place.json').write_text(json.dumps(place))
        elements = [
            # Coastline west→east at y = -150: land on the left (north), sea to the south.
            way(1, [(-500, -150), (500, -150)], natural='coastline'),
            way(2, [(-320, 0), (320, 0)], highway='residential', name='Testgatan'),
            way(3, [(0, -140), (0, 320)], highway='tertiary', name='Kyrkvägen', surface='sett'),
            way(10, rect(20, 12, 40, 24), building='house'),
            way(11, rect(-40, 12, -20, 24), building='house', **{'building:colour': '#a33a2a', 'building:material': 'wood'}),
            way(12, rect(20, -30, 60, -12), building='apartments', **{'building:levels': '5'}),
            way(13, rect(-80, 40, -40, 56), building='church', amenity='place_of_worship', name='Testby kyrka'),
            way(14, rect(60, 40, 75, 52), building='yes', **{'roof:shape': 'hipped'}),
            way(15, rect(-200, 60, -100, 160), leisure='park', name='Testparken'),
            {'type': 'node', 'id': 100, 'tags': {'natural': 'tree'}, **ll(-150, 100)},
            {'type': 'node', 'id': 101, 'tags': {'highway': 'street_lamp'}, **ll(10, 6)},
        ]
        (folder / 'osm.json').write_text(json.dumps({'elements': elements}))
        prepare_city.main([SLUG])
        make_pack.main([SLUG])
        cls.city = json.loads((folder / 'city.json').read_text())
        cls.config = json.loads((folder / 'pack/config.json').read_text())
        cls.map = json.loads((folder / 'pack/map.json').read_text())

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(CITIES / SLUG, ignore_errors=True)

    def test_sea_from_coastline(self):
        water = self.city['stats']['water_m2']
        self.assertAlmostEqual(water, 600 * 150, delta=600 * 150 * 0.03)
        self.assertTrue(self.city['shore'], 'the coast needs quay walls')

    def test_buildings_and_roofs(self):
        b = {x['id']: x for x in self.city['buildings']}
        self.assertEqual(len(b), 5)
        self.assertEqual(b['w12']['levels'], 5)
        self.assertGreater(b['w12']['h'], 15)
        self.assertEqual(b['w11']['style'], 'wood')
        self.assertEqual(b['w11']['colour'], 'falu')
        self.assertEqual(b['w14']['roof_style'] != 'flat', True)
        church = b['w13']
        self.assertIn('roof', church['parts'])
        tallest = max(church['parts']['roof']['v'][2::3])
        self.assertGreater(tallest, church['h'] * 2, 'the church gets a tower with a spire')
        for x in self.city['buildings']:
            self.assertIn('upper', x['parts'])

    def test_streets_and_surfaces(self):
        layers = self.city['surfaces']
        for name in ('asphalt', 'cobble', 'sidewalk', 'park', 'ground'):
            self.assertIn(name, layers)
        self.assertTrue(self.city['curbs'])
        self.assertEqual({r['name'] for r in self.city['roads']}, {'Testgatan', 'Kyrkvägen'})
        self.assertTrue(any(p['k'] == 'lamp' and not p.get('gen') for p in self.city['props']))

    def test_game_pack(self):
        sp = self.config['spawn']
        self.assertIn(sp['street'], ('Testgatan', 'Kyrkvägen'))
        self.assertLess(abs(sp['x']) + abs(sp['z']), 120)
        self.assertEqual(self.config['title']['top'], 'TESTBY')
        self.assertTrue(any(l[0] == 'TESTBY KYRKA' or l[0] == 'TESTPARKEN' for l in self.config['labels']))
        half = 300
        for r in self.map['roads']:
            for x, z in r['p']:
                self.assertLessEqual(abs(x), half)
                self.assertLessEqual(abs(z), half)
        self.assertTrue(any(a['k'] == 'land' for a in self.map['areas']))

    def test_building_listing(self):
        import contextlib
        import io
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            buildings.main([SLUG, '--street', 'Testgatan', '--json'])
        rows = json.loads(out.getvalue())
        self.assertTrue(rows)
        self.assertTrue(rows[0]['view']['streetview'].startswith('https://www.google.com/maps/'))


if __name__ == '__main__':
    unittest.main()
