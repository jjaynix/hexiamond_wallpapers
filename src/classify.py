from .groups import GROUPS, GROUP_ORDER_INDEX, POSSIBLE_GROUP_NAMES, GROUP_BY_NAME
from .search import plane_groups_with_lattice, group_orbits, invariant_covers
from .tiling import TorusProblem, canonical_lattices, shape_orientations, dilate_blueprint
from .wallpaper import classify_group, lattice_index

def _make_rep(tp, sol, info, orbits):
    tiles = tp.solution_tiles(sol)
    return {'group': info['name'], 'rotation_order': info['rotation_order'], 'mirror': info['mirror'], 'glide': info['glide'], 'tiles_per_cell': info['tiles_per_cell'], 'tile_orbits': orbits, 'isohedral': orbits == 1, 'torus_lattice': tp.basis, 'lattice': info['lattice'], 'elements': info['elements'], 'tiles': tiles}

def search_shape(blueprint, max_tiles=12, solution_cap=200000, refine=1, log=None):
    orientations, stabiliser = shape_orientations(dilate_blueprint(blueprint, refine))
    cell_factor = 3 * refine * refine
    best, iso, capped = ({}, {}, [])
    searched = 0
    for k in range(1, max_tiles + 1):
        for L in canonical_lattices(cell_factor * k):
            tp = TorusProblem(L, orientations)
            if not tp.pl_mask:
                continue
            for elems in plane_groups_with_lattice(L):
                searched += 1
                target = classify_group(L, elems)['name']
                options = group_orbits(tp, elems)
                if not options:
                    continue

                def consider(sol, n_orbits=None):
                    info = tp.analyse(sol)
                    name, kk = (info['name'], info['tiles_per_cell'])
                    cur, cur_iso = (best.get(name), iso.get(name))
                    need_best = cur is None or kk < cur['tiles_per_cell'] or (kk == cur['tiles_per_cell'] and (not cur['isohedral']))
                    need_iso = cur_iso is None or kk < cur_iso['tiles_per_cell']
                    if need_best or need_iso:
                        orbits = tp.tile_orbits(sol, info)
                        rep = _make_rep(tp, sol, info, orbits)
                        if need_best and (cur is None or (kk, orbits) < (cur['tiles_per_cell'], cur['tile_orbits'])):
                            best[name] = rep
                        if orbits == 1 and need_iso:
                            iso[name] = rep
                    exact = name == target and info['lattice'] == L and (set(info['elements']) == set(elems))
                    return exact
                for mask, orbit in options:
                    if mask == tp.full:
                        consider(list(orbit))
                if target not in best:
                    count, status = invariant_covers(tp, options, consider, solution_cap)
                    if status == 'capped':
                        capped.append((k, L, target))
        if log:
            log(k, sorted(best, key=lambda g: GROUP_ORDER_INDEX[g]))
    return {'orientations': len(orientations), 'stabiliser_order': stabiliser, 'max_tiles': max_tiles, 'refine': refine, 'best': best, 'iso': iso, 'capped': capped, 'searched': searched, 'exhaustive': not capped}

def _make_generated_rep(tp, orbit, info_G, elems, L, full):
    return {'group': info_G['name'], 'rotation_order': info_G['rotation_order'], 'mirror': info_G['mirror'], 'glide': info_G['glide'], 'tiles_per_cell': len(orbit), 'tile_orbits': 1, 'isohedral': True, 'generated': True, 'full_group': full['name'], 'torus_lattice': tp.basis, 'lattice': L, 'elements': elems, 'tiles': tp.solution_tiles(list(orbit))}

def select_admitted(pair_reps, pair_sizes, rule):
    assert rule in ('any_subgroup', 'same_family', 'full_group'), rule
    out = {}
    for (g, f), rep in pair_reps.items():
        if rule == 'full_group' and g != f:
            continue
        if rule == 'same_family' and GROUP_BY_NAME[g]['lattice'] != GROUP_BY_NAME[f]['lattice']:
            continue
        e = out.setdefault(g, {'rep': rep, 'orbit_sizes': set(), 'full_groups': set()})
        e['orbit_sizes'] |= set(pair_sizes[g, f])
        e['full_groups'].add(f)
        if (rep['tiles_per_cell'], rep['full_group'] != g, rep['full_group']) < (e['rep']['tiles_per_cell'], e['rep']['full_group'] != g, e['rep']['full_group']):
            e['rep'] = rep
    for e in out.values():
        e['orbit_sizes'], e['full_groups'] = (sorted(e['orbit_sizes']), sorted(e['full_groups']))
    return out

def search_transitive(blueprint, max_tiles=12, refine=1):
    orientations, stabiliser = shape_orientations(dilate_blueprint(blueprint, refine))
    cell_factor = 3 * refine * refine
    by_pair, sizes, pairs = ({}, {}, 0)
    for k in range(1, max_tiles + 1):
        for L in canonical_lattices(cell_factor * k):
            tp = TorusProblem(L, orientations)
            if not tp.pl_mask:
                continue
            for elems in plane_groups_with_lattice(L):
                pairs += 1
                info = None
                for mask, orbit in group_orbits(tp, elems):
                    if mask != tp.full:
                        continue
                    info = info or classify_group(L, elems)
                    full = tp.analyse(list(orbit))
                    key = (info['name'], full['name'])
                    sizes.setdefault(key, set()).add(len(orbit))
                    if key not in by_pair:
                        by_pair[key] = _make_generated_rep(tp, orbit, info, elems, L, full)
    pair_sizes = {k: sorted(v) for k, v in sizes.items()}
    any_sub = select_admitted(by_pair, pair_sizes, 'any_subgroup')
    return {'orientations': len(orientations), 'stabiliser_order': stabiliser, 'max_tiles': max_tiles, 'refine': refine, 'pairs': pairs, 'by_pair': by_pair, 'pair_sizes': pair_sizes, 'best': {g: e['rep'] for g, e in any_sub.items()}, 'orbit_sizes': {g: e['orbit_sizes'] for g, e in any_sub.items()}}
