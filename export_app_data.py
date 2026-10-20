import json
import os
from fractions import Fraction
from math import floor
from src import config
from src.geometry import polygon_points, axial_to_cartesian, centroid_axial
from src.groups import GROUP_ORDER_INDEX, POSSIBLE_GROUP_NAMES
from src.wallpaper import D6, gauss_reduce, lattice_reduce, rotation_order, is_reflection, S_of_triangle, mat_det

def _centre_of_rotation(rep):
    best = None
    for mi, t in rep['elements'].items():
        M = D6[int(mi)]
        if is_reflection(M):
            continue
        o = rotation_order(M)
        if o > 1 and (best is None or o > best[0]):
            best = (o, M, t)
    if best is None:
        return None
    _, M, t = best
    a, b, c, d = (1 - M[0][0], -M[0][1], -M[1][0], 1 - M[1][1])
    det = a * d - b * c
    return (Fraction(d * t[0] - b * t[1], det), Fraction(-c * t[0] + a * t[1], det))

def cell_images(rep):
    L2 = tuple(map(tuple, rep['lattice']))
    u1, u2 = gauss_reduce(L2)
    det = u1[0] * u2[1] - u1[1] * u2[0]
    seen, out = (set(), [])
    for tile in rep['tiles']:
        S = [S_of_triangle(*t) for t in tile]
        ax, ay = min(S, key=lambda s: (s[1], s[0]))
        qc, rc = lattice_reduce(L2, (ax // 3, ay // 3))
        key = tuple(sorted(((x - 3 * (ax // 3 - qc), y - 3 * (ay // 3 - rc)) for x, y in S)))
        if key in seen:
            continue
        seen.add(key)
        cq, cr = centroid_axial(tile)
        a = (cq * u2[1] - cr * u2[0]) / det
        b = (u1[0] * cr - u1[1] * cq) / det
        i, j = (floor(a), floor(b))
        sq, sr = (i * u1[0] + j * u2[0], i * u1[1] + j * u2[1])
        out.append([(q - sq, r - sr, o) for q, r, o in tile])
    assert len(out) == rep['tiles_per_cell']
    return (out, u1, u2)

def build_group_entry(g, rep, orbit_sizes=None):
    m = rep['refine']
    tiles, u1, u2 = cell_images(rep)
    c = _centre_of_rotation(rep)
    if c is None:
        cq, cr = centroid_axial(tiles[0])
        c = (Fraction(cq).limit_denominator(1000), Fraction(cr).limit_denominator(1000))
    center = axial_to_cartesian(float(c[0]), float(c[1]), m)
    images = []
    for tile in tiles:
        pts = [[p[0] - center[0], p[1] - center[1]] for p in polygon_points(tile, m)]
        images.append({'kind': 'tile', 'angle': 0.0, 'polygon': pts})
    return {'group': g, 'order': rep['rotation_order'], 'mirror': rep['mirror'], 'glide': rep['glide'], 'orbit_size': len(images), 'orbit_sizes': orbit_sizes or [len(images)], 'tile_orbits': 1, 'generated': True, 'full_group': rep['full_group'], 'refine': m, 'upgraded_from': None, 'elements': {str(k): list(v) for k, v in rep['elements'].items()}, 'center': list(center), 'polygon': images[0]['polygon'], 'images': images, 't1': list(axial_to_cartesian(*u1, scale=m)), 't2': list(axial_to_cartesian(*u2, scale=m))}

def export():
    with open(config.RESULTS_PATH) as f:
        study = json.load(f)
    entries = []
    for e in study['shapes']:
        groups = [build_group_entry(g, x['rep'], x['orbit_sizes']) for g, x in sorted(e['admitted'].items(), key=lambda kv: GROUP_ORDER_INDEX[kv[0]])]
        entries.append({'id': e['id'], 'name': e['name'], 'found': bool(groups), 'group': groups[0]['group'] if groups else None, 'search_time_seconds': sum((p['seconds'] for p in e['profiles'])), 'groups_not_found': [g for g in POSSIBLE_GROUP_NAMES if g not in e['admitted']], 'groups': groups})
    with open(config.APP_DATA_PATH, 'w') as f:
        f.write('const APP_DATA = ' + json.dumps({'hexiamonds': entries}) + ';')
    print(f'wrote {config.APP_DATA_PATH} ({os.path.getsize(config.APP_DATA_PATH) / 1024:.0f} KB)')
if __name__ == '__main__':
    export()
