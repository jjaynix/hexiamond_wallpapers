import argparse
import json
import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from src import config
from src.classify import search_shape, search_transitive, select_admitted
from src.groups import GROUPS, GROUP_ORDER_INDEX, POSSIBLE_GROUP_NAMES, IMPOSSIBLE_GROUP_NAMES
from src.shapes import HEXIAMONDS, SHAPE_IDS, SHAPE_NAMES
from src.verify import verify_rep, verify_generated
RULE_TEXT = {'any_subgroup': 'every group G that generates a tiling transitively counts (G need not be the full symmetry group)', 'same_family': "G generates a tiling transitively AND has the same lattice family (oblique / rectangular / rhombic / hexagonal; paper Table 1) as the tiling's complete symmetry group", 'full_group': 'G must be the complete symmetry group of the tiling it generates'}

def _jsonable(rep, refine):
    out = dict(rep)
    out['refine'] = refine
    out['elements'] = {str(k): list(v) for k, v in rep['elements'].items()}
    out['lattice'] = [list(v) for v in rep['lattice']]
    out['torus_lattice'] = [list(v) for v in rep['torus_lattice']]
    out['tiles'] = [[list(t) for t in tile] for tile in rep['tiles']]
    return out

def run_task(task):
    idx, m, K, cap, cache_dir = task
    path = os.path.join(cache_dir, f'shape{idx}_m{m}_K{K}.json')
    if os.path.exists(path):
        with open(path) as f:
            cached = json.load(f)
        if m != 1 or 'pairs' in cached.get('transitive', {}):
            return (idx, m, K, cached, True)
    t0 = time.time()
    r = search_shape(HEXIAMONDS[idx], max_tiles=K, solution_cap=cap, refine=m)
    out = {'orientations': r['orientations'], 'stabiliser_order': r['stabiliser_order'], 'searched': r['searched'], 'exhaustive': r['exhaustive'], 'capped': [[k, [list(v) for v in L], g] for k, L, g in r['capped']], 'best': {g: _jsonable(v, m) for g, v in r['best'].items()}, 'iso': {g: _jsonable(v, m) for g, v in r['iso'].items()}}
    if m == 1:
        t = search_transitive(HEXIAMONDS[idx], max_tiles=config.TRANSITIVE_MAX_TILES)
        out['transitive'] = {'pairs': {f'{g}|{f}': _jsonable(v, 1) for (g, f), v in t['by_pair'].items()}, 'pair_sizes': {f'{g}|{f}': v for (g, f), v in t['pair_sizes'].items()}, 'n_groups_searched': t['pairs']}
    out['seconds'] = time.time() - t0
    os.makedirs(cache_dir, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(out, f)
    return (idx, m, K, out, False)

def merge(results_by_shape):
    merged = []
    for idx in range(len(HEXIAMONDS)):
        runs = results_by_shape[idx]
        groups, admitted = ({}, {})
        for (m, K), run in sorted(runs.items()):
            for g, rep in run['best'].items():
                e = groups.setdefault(g, {'best': None, 'iso': None, 'found_by_refine': {}})
                e['found_by_refine'][m] = min(rep['tiles_per_cell'], e['found_by_refine'].get(m, 10 ** 9))
                key = (rep['tiles_per_cell'], rep['tile_orbits'], m)
                if e['best'] is None or key < (e['best']['tiles_per_cell'], e['best']['tile_orbits'], e['best']['refine']):
                    e['best'] = rep
            for g, rep in run['iso'].items():
                e = groups.setdefault(g, {'best': None, 'iso': None, 'found_by_refine': {}})
                if e['iso'] is None or (rep['tiles_per_cell'], m) < (e['iso']['tiles_per_cell'], e['iso']['refine']):
                    e['iso'] = rep
            if 'transitive' in run:
                tr = run['transitive']
                reps = {tuple(k.split('|')): v for k, v in tr['pairs'].items()}
                sizes = {tuple(k.split('|')): v for k, v in tr['pair_sizes'].items()}
                by_rule = {r: select_admitted(reps, sizes, r) for r in ('any_subgroup', 'same_family', 'full_group')}
                admitted = by_rule[config.ADMISSION_RULE]
        first = next(iter(runs.values()))
        merged.append({'id': SHAPE_IDS[idx], 'name': SHAPE_NAMES[SHAPE_IDS[idx]], 'orientations': first['orientations'], 'stabiliser_order': first['stabiliser_order'], 'profiles': [{'refine': m, 'max_tiles': K, 'exhaustive': run['exhaustive'], 'pairs_searched': run['searched'], 'seconds': round(run['seconds'], 1), 'capped': run['capped']} for (m, K), run in sorted(runs.items())], 'admitted': admitted, 'admitted_by_rule': {r: sorted(v) for r, v in by_rule.items()}, 'groups': groups})
    return merged

def verify_all(merged):
    n = 0
    for entry, bp in zip(merged, HEXIAMONDS):
        for g, e in entry['admitted'].items():
            verify_generated(e['rep'], bp, 1)
            n += 1
        for g, e in entry['groups'].items():
            for rep in (e['best'], e['iso']):
                if rep is not None:
                    verify_rep(rep, bp, rep['refine'])
                    n += 1
    return n

def write_report(merged, profiles, path):
    names = [g['name'] for g in GROUPS if g['possible']]
    L = ['# Wallpaper groups admitted by the twelve hexiamonds\n', '## Definitions used\n', '* **G is admitted** by a hexiamond when G, acting on one copy of it, generates a tiling of the plane, so G acts transitively on the tiles, under the rule `' + config.ADMISSION_RULE + '`: ' + RULE_TEXT[config.ADMISSION_RULE] + '.', '* Tiles lie on the triangular grid (half-grid offsets are excluded).', '* Mirror images of a tile are allowed.\n', '## What is proved\n', '* **Found = proved**: every row comes with an explicit tiling, re-verified by independent exact code (src/verify.py).', '* **Not admitted = proved, within these definitions**: if G is transitive then (tiles per primitive cell) = |point group of G| / |stabiliser of the tile| <= 12, so only translation lattices of index <= 36 can occur; all of them were searched exhaustively (every plane group G on every such lattice, no solution cap).', f"* **Impossible for every hexiamond**: {', '.join(IMPOSSIBLE_GROUP_NAMES)} (every edge lies in one of three directions, so no symmetry can be a 4-fold rotation).\n", '## Coverage matrix (smallest orbit size; `-` = not admitted)\n', '| Shape | ' + ' | '.join(names) + ' |', '|---|' + '---|' * len(names)]
    for e in merged:
        L.append(f"| {e['name']} | " + ' | '.join((str(min(e['admitted'][g]['orbit_sizes'])) if g in e['admitted'] else '-' for g in names)) + ' |')
    L.append('\n## Per shape\n')
    for e in merged:
        L.append(f"### {e['name']}\n")
        L.append(f"Tile symmetry: order {e['stabiliser_order']} ({e['orientations']} orientations). {len(e['admitted'])} of the 14 possible groups admitted.\n")
        L.append('| Group | Rot. order | Mirror | Glide | Orbit size(s) | Full symmetry group of the simplest such tiling |')
        L.append('|---|---|---|---|---|---|')
        for g in sorted(e['admitted'], key=lambda n: GROUP_ORDER_INDEX[n]):
            r = e['admitted'][g]['rep']
            L.append(f"| {g} | {r['rotation_order']} | {('Yes' if r['mirror'] else 'No')} | {('Yes' if r['glide'] else 'No')} | {', '.join(map(str, e['admitted'][g]['orbit_sizes']))} | {r['full_group']} |")
        L.append(f"\nNot admitted: {', '.join((g for g in POSSIBLE_GROUP_NAMES if g not in e['admitted'])) or 'none'}.\n")
    L.append('Orbit size = tiles per primitive cell of G = |point group of G| / |stabiliser of the tile in G|. Mirror / Glide describe G itself (Glide = a glide reflection whose axis is not a mirror line).\n')
    L.append('## Supplementary: complete symmetry group of every tiling found (including non-isohedral)\n')
    L.append('Profiles: ' + ', '.join((f'm={m}, K={K}' for m, K in profiles)) + '. Exhaustive up to those bounds only.\n')
    L.append('| Shape | ' + ' | '.join(names) + ' |')
    L.append('|---|' + '---|' * len(names))
    for e in merged:
        L.append(f"| {e['name']} | " + ' | '.join(('-' if g not in e['groups'] else f"**{e['groups'][g]['best']['tiles_per_cell']}**" if e['groups'][g]['iso'] else str(e['groups'][g]['best']['tiles_per_cell']) for g in names)) + ' |')
    L.append('\nCells = fewest tiles per primitive cell of a tiling whose FULL symmetry group is that type; bold = an isohedral tiling with that full group exists.\n')
    with open(path, 'w') as f:
        f.write('\n'.join(L))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--with-offsets', action='store_true', help='also search 1/m-grid offsets (outside the adopted definitions)')
    ap.add_argument('--workers', type=int, default=os.cpu_count() or 1)
    ap.add_argument('--shapes', type=int, nargs='*')
    ap.add_argument('--no-verify', action='store_true')
    args = ap.parse_args()
    profiles = list(config.QUICK_PROFILES if args.quick else config.SEARCH_PROFILES)
    if args.with_offsets:
        profiles += config.OFFSET_PROFILES
    shapes = args.shapes if args.shapes else list(range(len(HEXIAMONDS)))
    cache = config.CACHE_DIR + ('_quick' if args.quick else '')
    tasks = [(i, m, K, config.SOLUTION_CAP, cache) for m, K in profiles for i in shapes]
    t0 = time.time()
    by_shape = {i: {} for i in shapes}
    print(f'{len(tasks)} searches on {args.workers} worker(s)')
    with ProcessPoolExecutor(max_workers=args.workers) as ex:
        for f in as_completed([ex.submit(run_task, t) for t in tasks]):
            idx, m, K, out, cached = f.result()
            by_shape[idx][m, K] = out
            print(f"  {SHAPE_NAMES[SHAPE_IDS[idx]]:18} m={m} K={K:2} {out['seconds']:6.1f}s{(' (cached)' if cached else '')}", flush=True)
    if len(shapes) < len(HEXIAMONDS):
        print('partial run (--shapes): results not written')
        return
    merged = merge(by_shape)
    if not args.no_verify:
        print('independently verified', verify_all(merged), 'representative tilings in the plane')
    os.makedirs('artifacts', exist_ok=True)
    with open(config.RESULTS_PATH, 'w') as f:
        json.dump({'profiles': [list(p) for p in profiles], 'shapes': merged}, f)
    write_report(merged, profiles, config.REPORT_PATH)
    print(f'wrote {config.RESULTS_PATH} and {config.REPORT_PATH} ({time.time() - t0:.0f}s)')
if __name__ == '__main__':
    main()
