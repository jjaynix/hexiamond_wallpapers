from src.wallpaper import D6, D6_INDEX, classify_group, hnf, lattice_contains, lattice_invariant, mat_mul, mat_vec
C = hnf([(1, 1), (-1, 2)])
RECT = hnf([(3, 0), (-1, 2)])
in_C = lambda p: (p[0] - p[1]) % 3 == 0
GROUPS_ON_HONEYCOMB = {'p6m': (C, {i: (0, 0) for i in range(12)}), 'p6': (C, {i: (0, 0) for i in range(6)}), 'p3m1': (C, {0: (0, 0), 2: (0, 0), 4: (0, 0), 6: (0, 0), 8: (0, 0), 10: (0, 0)}), 'p31m': (C, {0: (0, 0), 2: (0, 0), 4: (0, 0), 7: (0, 0), 9: (0, 0), 11: (0, 0)}), 'p3': (C, {0: (0, 0), 2: (0, 0), 4: (0, 0)}), 'cmm': (C, {0: (0, 0), 3: (0, 0), 6: (0, 0), 9: (0, 0)}), 'cm': (C, {0: (0, 0), 6: (0, 0)}), 'p2': (C, {0: (0, 0), 3: (0, 0)}), 'p1': (C, {0: (0, 0)}), 'pg': (RECT, {0: (0, 0), 6: (1, 1)}), 'pgg': (RECT, {0: (0, 0), 3: (0, 0), 6: (1, 1), 9: (1, 1)}), 'pmg': (RECT, {0: (0, 0), 6: (0, 0), 3: (1, 1), 9: (2, -1)})}

def _check_group(L, el):
    for m1, t1 in el.items():
        for m2, t2 in el.items():
            mi = D6_INDEX[mat_mul(D6[m1], D6[m2])]
            v = mat_vec(D6[m1], t2)
            assert mi in el and lattice_contains(L, (v[0] + t1[0] - el[mi][0], v[1] + t1[1] - el[mi][1]))
    assert all((lattice_invariant(L, D6[m]) for m in el))
    window = [(q, r) for q in range(-9, 10) for r in range(-9, 10) if in_C((q, r))]
    for m, t in el.items():
        for c in window:
            im = mat_vec(D6[m], c)
            assert in_C((im[0] + t[0], im[1] + t[1])), (m, t, c)
    a, c2 = (L[0][0], L[1][1])
    orbit = set()
    for m, t in el.items():
        for i in range(-12, 13):
            for j in range(-12, 13):
                orbit.add((t[0] + i * L[0][0] + j * L[1][0], t[1] + i * L[0][1] + j * L[1][1]))
    assert all((c in orbit for c in window)), 'not transitive on the hexagon centres'

def test_honeycomb_is_generated_by_twelve_wallpaper_group_types():
    for name, (L, el) in GROUPS_ON_HONEYCOMB.items():
        _check_group(L, el)
        assert classify_group(L, el)['name'] == name, name
    assert len(GROUPS_ON_HONEYCOMB) == 12

def test_the_five_hexagonal_lattice_groups_are_among_them_and_p1_is_trivially_there():
    assert {'p3', 'p31m', 'p3m1', 'p6', 'p6m'} <= set(GROUPS_ON_HONEYCOMB)
    assert classify_group(C, {0: (0, 0)})['name'] == 'p1'

def test_search_engine_finds_exactly_these_twelve():
    from src.classify import search_transitive
    from src.shapes import HEXIAMONDS
    assert set(search_transitive(HEXIAMONDS[8], 12)['best']) == set(GROUPS_ON_HONEYCOMB)
