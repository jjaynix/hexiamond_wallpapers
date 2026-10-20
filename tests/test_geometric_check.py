import copy
import json
import os
import shutil
import subprocess
import pytest
from src.geometry import polygon_points
from src.groups import GROUP_BY_NAME
from src.shapes import HEXIAMONDS
from tools.geometric_check import check_row
DATA = json.loads(open('webapp/data.js').read()[len('const APP_DATA = '):].rstrip().rstrip(';'))

def test_every_row_passes_the_independent_geometric_check():
    n = 0
    for idx, h in enumerate(DATA['hexiamonds']):
        ref = polygon_points(HEXIAMONDS[idx])
        for g in h['groups']:
            r = check_row(g, ref)
            assert r['ok'], (h['name'], g['group'], r['why'])
            assert (r['G'], r['F']) == (g['group'], g['full_group'])
            assert GROUP_BY_NAME[r['G']]['lattice'] == GROUP_BY_NAME[r['F']]['lattice']
            n += 1
    assert n == 60

def test_geometric_checker_rejects_corrupted_rows():
    ref = polygon_points(HEXIAMONDS[8])
    g = DATA['hexiamonds'][8]['groups'][1]
    assert check_row(g, ref)['ok']
    bad = copy.deepcopy(g)
    bad['group'] = 'p3m1'
    assert not check_row(bad, ref)['ok']
    bad = copy.deepcopy(g)
    bad['full_group'] = 'p6'
    assert not check_row(bad, ref)['ok']
    bad = copy.deepcopy(g)
    bad['elements']['1'] = [1, 0]
    assert not check_row(bad, ref)['ok']
    bad = copy.deepcopy(g)
    bad['images'][0]['polygon'] = [[x + 0.3, y] for x, y in bad['images'][0]['polygon']]
    assert not check_row(bad, ref)['ok']

def test_webapp_renders_every_view_without_javascript_errors():
    node = shutil.which('node')
    env = dict(os.environ)
    env['NODE_PATH'] = os.pathsep.join(filter(None, ['/tmp/jsd/node_modules', env.get('NODE_PATH', '')]))
    if not node:
        pytest.skip('node not installed')
    r = subprocess.run([node, 'tools/webapp_smoke_test.js'], capture_output=True, text=True, env=env, timeout=180)
    if 'Cannot find module' in r.stderr:
        pytest.skip('jsdom not installed (npm install jsdom)')
    assert r.returncode == 0, r.stdout + r.stderr
