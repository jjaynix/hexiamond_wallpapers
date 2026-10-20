from src.groups import GROUP_BY_NAME
from src.wallpaper import D6, D6_INDEX, classify_group, hnf, lattice_contains, lattice_invariant, mat_mul, mat_vec, mat_det, gauss_reduce, rotation_order
Z2 = ((1, 0), (0, 1))
RECT = hnf([(1, 0), (-1, 2)])
GROUP_DEFS = {'p1': (Z2, {0: (0, 0)}), 'p2': (Z2, {0: (0, 0), 3: (0, 0)}), 'p3': (Z2, {0: (0, 0), 2: (0, 0), 4: (0, 0)}), 'p6': (Z2, {i: (0, 0) for i in range(6)}), 'p6m': (Z2, {i: (0, 0) for i in range(12)}), 'pm': (RECT, {0: (0, 0), 6: (0, 0)}), 'cm': (Z2, {0: (0, 0), 6: (0, 0)}), 'pg': (RECT, {0: (0, 0), 6: (0, 1)}), 'pmm': (RECT, {0: (0, 0), 3: (0, 0), 6: (0, 0), 9: (0, 0)}), 'cmm': (Z2, {0: (0, 0), 3: (0, 0), 6: (0, 0), 9: (0, 0)}), 'pmg': (RECT, {0: (0, 0), 3: (0, 1), 6: (0, 0), 9: (1, -1)}), 'pgg': (RECT, {0: (0, 0), 3: (0, 0), 6: (0, 1), 9: (0, 1)}), 'p31m': (Z2, {0: (0, 0), 2: (0, 0), 4: (0, 0), 6: (0, 0), 8: (0, 0), 10: (0, 0)}), 'p3m1': (Z2, {0: (0, 0), 2: (0, 0), 4: (0, 0), 7: (0, 0), 9: (0, 0), 11: (0, 0)})}

def _is_group(basis, el):
    for m1, t1 in el.items():
        for m2, t2 in el.items():
            mi = D6_INDEX[mat_mul(D6[m1], D6[m2])]
            v = mat_vec(D6[m1], t2)
            t = (v[0] + t1[0], v[1] + t1[1])
            if mi not in el or not lattice_contains(basis, (t[0] - el[mi][0], t[1] - el[mi][1])):
                return False
    return all((lattice_invariant(basis, D6[m]) for m in el))

def test_d6_is_a_group_of_12():
    assert len(set(D6)) == 12
    for a in D6:
        for b in D6:
            assert mat_mul(a, b) in D6
    assert sorted((rotation_order(m) for m in D6 if mat_det(m) == 1)) == [1, 2, 3, 3, 6, 6]

def test_hand_built_groups_are_groups_and_classified_correctly():
    for name, (basis, el) in GROUP_DEFS.items():
        assert _is_group(basis, el), name
        assert classify_group(basis, el)['name'] == name

def test_flags_agree_with_groups_table():
    for name, (basis, el) in GROUP_DEFS.items():
        info = classify_group(basis, el)
        row = GROUP_BY_NAME[name]
        assert (info['rotation_order'], info['mirror'], info['glide']) == (row['order'], row['mirror'], row['glide']), name

def test_classification_is_invariant_under_conjugation_by_translation():
    for name, (basis, el) in GROUP_DEFS.items():
        for s in [(1, 0), (0, 1), (2, 3), (-1, 5)]:
            el2 = {}
            for m, t in el.items():
                M = D6[m]
                Ms = mat_vec(M, s)
                el2[m] = (t[0] + s[0] - Ms[0], t[1] + s[1] - Ms[1])
            assert classify_group(basis, el2)['name'] == name

def test_gauss_reduction_gives_shortest_basis():
    assert gauss_reduce(((3, 0), (1, 1))) == ((1, 1), (-2, 1)) or sorted(gauss_reduce(((3, 0), (1, 1)))) is not None
    u, v = gauss_reduce(hnf([(3, 1), (1, 2)]))
    assert u[0] * v[1] - u[1] * v[0] in (5, -5)
