import re
from src.groups import GROUPS, GROUP_BY_NAME
from src.wallpaper import classify_group, rotation_centre_signature
from tests.test_wallpaper import GROUP_DEFS
FETT = {'p1': (False, False, 1, False), 'p2': (False, True, 2, False), 'pm': (True, False, 1, False), 'pg': (False, False, 1, True), 'cm': (True, False, 1, True), 'pmm': (True, True, 2, False), 'pmg': (True, True, 2, True), 'pgg': (False, True, 2, True), 'cmm': (True, True, 2, True), 'p4': (False, True, 4, False), 'p4m': (True, True, 4, True), 'p4g': (True, True, 4, True), 'p3': (False, True, 3, False), 'p31m': (True, True, 3, True), 'p3m1': (True, True, 3, True), 'p6': (False, True, 6, False), 'p6m': (True, True, 6, True)}

def _orbifold_centres(sig):
    if '*' in sig:
        before, after = sig.split('*', 1)
    else:
        before, after = (sig, '')
    digits = lambda t: sorted((int(c) for c in re.findall('[2-6]', t)), reverse=True)
    return (digits(before), digits(after))

def test_seventeen_groups_and_their_table_values_match_fett_table_5():
    assert len(GROUPS) == 17 and set(FETT) == set(GROUP_BY_NAME)
    for name, (refl, rot, order, glide) in FETT.items():
        g = GROUP_BY_NAME[name]
        assert (g['mirror'], g['order'], g['glide']) == (refl, order, glide), name
        assert (g['order'] > 1) == rot, name

def test_only_the_three_square_groups_are_impossible_for_hexiamonds():
    assert {g['name'] for g in GROUPS if not g['possible']} == {'p4', 'p4m', 'p4g'}
    assert all((g['lattice'] == 'square' for g in GROUPS if not g['possible']))
    assert all((g['lattice'] != 'square' for g in GROUPS if g['possible']))

def test_computed_features_agree_with_the_literature_for_all_14_possible_groups():
    seen = set()
    for _, (basis, el) in GROUP_DEFS.items():
        info = classify_group(basis, el)
        lit = GROUP_BY_NAME[info['name']]
        seen.add(info['name'])
        refl, rot, order, glide = FETT[info['name']]
        assert (info['mirror'], info['rotation_order'], info['glide']) == (refl, order, glide), info['name']
        assert info['lattice_type'] == lit['lattice'], info['name']
        assert info['point_group'] == lit['point_group'], info['name']
        off, on = rotation_centre_signature(basis, el)
        assert (off, on) == _orbifold_centres(lit['orbifold']), (info['name'], off, on, lit['orbifold'])
    assert seen == {g['name'] for g in GROUPS if g['possible']}

def test_glide_and_mirror_flags_follow_the_orbifold_symbol():
    for g in GROUPS:
        sig = g['orbifold']
        assert ('*' in sig) == g['mirror'] or g['name'] in ('pg', 'pgg'), g['name']

def test_p3m1_versus_p31m_criterion():
    for name, key in (('p3m1', 'p3m1'), ('p31m', 'p31m')):
        basis, el = GROUP_DEFS[key]
        off, on = rotation_centre_signature(basis, el)
        assert classify_group(basis, el)['name'] == name
        assert (off == []) == (name == 'p3m1') and on == ([3, 3, 3] if name == 'p3m1' else [3])
