from .wallpaper import D6, IDENTITY_INDEX, mat_vec, lattice_contains, lattice_invariant, lattice_reduce, lattice_index, classify_group, S_of_triangle
from .tiling import normalize_S, dilate_blueprint

def _tile_S(tile):
    return [S_of_triangle(*t) for t in tile]

def _canon(L, S):
    ax, ay = min(S, key=lambda s: (s[1], s[0]))
    qa, ra = (ax // 3, ay // 3)
    qc, rc = lattice_reduce(L, (qa, ra))
    dq, dr = (qa - qc, ra - rc)
    return tuple(sorted(((x - 3 * dq, y - 3 * dr) for x, y in S)))

def verify_rep(rep, blueprint, refine=1):
    L2 = tuple(map(tuple, rep['lattice']))
    base = dilate_blueprint(blueprint, refine)
    base_S = [S_of_triangle(*t) for t in base]
    size = len(base_S)
    allowed = {normalize_S([mat_vec(M, s) for s in base_S]) for M in D6}
    reps = {}
    for tile in rep['tiles']:
        S = _tile_S(tile)
        assert len(S) == size and len(set(S)) == size, 'wrong tile size'
        assert normalize_S(S) in allowed, 'tile not congruent to the prototile'
        reps[_canon(L2, S)] = None
    k = len(reps)
    assert k == rep['tiles_per_cell'], f"tiles per cell {k} != {rep['tiles_per_cell']}"
    seen = set()
    for S in reps:
        for X, Y in S:
            q, r, o = (X // 3, Y // 3, X % 3 - 1)
            cls = (lattice_reduce(L2, (q, r)), o)
            assert cls not in seen, 'two tiles overlap'
            seen.add(cls)
    assert len(seen) == 2 * lattice_index(L2), 'tiles do not cover the plane'
    a2, c2 = (L2[0][0], L2[1][1])
    first = next(iter(reps))
    found = {}
    for mi, M in enumerate(D6):
        if not lattice_invariant(L2, M):
            continue
        for tr in range(c2):
            for tq in range(a2):
                ok = True
                for S in reps:
                    img = [(mat_vec(M, s)[0] + 3 * tq, mat_vec(M, s)[1] + 3 * tr) for s in S]
                    if _canon(L2, img) not in reps:
                        ok = False
                        break
                if ok:
                    if mi == IDENTITY_INDEX and (tq, tr) != (0, 0):
                        raise AssertionError("L' is not the full translation group")
                    assert mi not in found, 'two cosets for one linear part'
                    found[mi] = (tq, tr)
    reported = {int(m): tuple(t) for m, t in rep['elements'].items()}
    assert set(found) == set(reported), f'symmetry set differs: {sorted(found)} vs {sorted(reported)}'
    for mi, t in found.items():
        d = (t[0] - reported[mi][0], t[1] - reported[mi][1])
        assert lattice_contains(L2, d), 'different coset for a symmetry'
    info = classify_group(L2, found)
    assert info['name'] == rep['group'], f"type {info['name']} != {rep['group']}"
    assert (info['mirror'], info['glide'], info['rotation_order']) == (rep['mirror'], rep['glide'], rep['rotation_order'])
    return True

def verify_generated(rep, blueprint, refine=1):
    from .wallpaper import D6_INDEX, mat_mul
    L = tuple(map(tuple, rep['lattice']))
    allowed = None
    if blueprint is not None:
        base_S = [S_of_triangle(*t) for t in dilate_blueprint(blueprint, refine)]
        allowed = {normalize_S([mat_vec(M, s) for s in base_S]) for M in D6}
    reps = {}
    for tile in rep['tiles']:
        S = _tile_S(tile)
        assert len(set(S)) == 6 * refine * refine, 'wrong tile size'
        assert allowed is None or normalize_S(S) in allowed, 'tile not congruent to the prototile'
        reps[_canon(L, S)] = None
    assert len(reps) == rep['tiles_per_cell'] == len(rep['tiles']), 'tiles not distinct modulo L'
    seen = set()
    for S in reps:
        for X, Y in S:
            cls = (lattice_reduce(L, (X // 3, Y // 3)), X % 3 - 1)
            assert cls not in seen, 'two tiles overlap'
            seen.add(cls)
    assert len(seen) == 2 * lattice_index(L), 'tiles do not cover the plane'
    el = {int(m): tuple(t) for m, t in rep['elements'].items()}
    assert el.get(IDENTITY_INDEX) is not None and lattice_contains(L, el[IDENTITY_INDEX])
    for mi, (tq, tr) in el.items():
        assert lattice_invariant(L, D6[mi]), 'lattice not invariant under a point-group element'
        for S in reps:
            img = [(mat_vec(D6[mi], s)[0] + 3 * tq, mat_vec(D6[mi], s)[1] + 3 * tr) for s in S]
            assert _canon(L, img) in reps, 'a group element does not map the tiling to itself'
    for m1, t1 in el.items():
        for m2, t2 in el.items():
            mi = D6_INDEX[mat_mul(D6[m1], D6[m2])]
            v = mat_vec(D6[m1], t2)
            d = (v[0] + t1[0] - el[mi][0], v[1] + t1[1] - el[mi][1])
            assert mi in el and lattice_contains(L, d), 'elements do not form a group'
    first = next(iter(reps))
    orbit = {_canon(L, [(mat_vec(D6[mi], s)[0] + 3 * tq, mat_vec(D6[mi], s)[1] + 3 * tr) for s in first]) for mi, (tq, tr) in el.items()}
    assert orbit == set(reps), 'G is not transitive on the tiles'
    info = classify_group(L, el)
    assert info['name'] == rep['group'], f"type {info['name']} != {rep['group']}"
    assert (info['mirror'], info['glide'], info['rotation_order']) == (rep['mirror'], rep['glide'], rep['rotation_order'])
    return True
