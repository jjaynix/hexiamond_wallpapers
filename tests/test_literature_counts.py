import pytest
from tests.test_transitive import RES
from src.shapes import SHAPE_IDS
NAME = {i: SHAPE_IDS[i] for i in range(12)}

def sizes(idx, g, f=None):
    return {k: v for k, v in RES[idx]['pair_sizes'].items() if k[0] == g and (f is None or k[1] == f)}

def fundamental_domain_pairs(g, orbit):
    return {(i, f) for i in range(12) for (gg, f), v in RES[i]['pair_sizes'].items() if gg == g and orbit in v}

def test_p3_fundamental_domains_match_fukuda_table_1_for_n_6():
    pairs = fundamental_domain_pairs('p3', 3)
    shapes = {i for i, _ in pairs}
    assert len(shapes) == 4
    full = {i: sorted((f for j, f in pairs if j == i)) for i in shapes}
    assert sorted((g for fs in full.values() for g in fs)) == ['p3', 'p31m', 'p6', 'p6m']
    s6 = [i for i, fs in full.items() if 'p3' in fs]
    assert len(s6) == 1
    assert RES[s6[0]]['pair_sizes'] and NAME[s6[0]] == 'hexiamond_6'

def test_no_hexiamond_is_a_fundamental_domain_for_p31m_p6_p3m1_p6m():
    for g, orbit in (('p31m', 6), ('p6', 6), ('p3m1', 6), ('p6m', 12)):
        assert not fundamental_domain_pairs(g, orbit), g

def test_eight_hexiamonds_tile_by_translation_and_four_need_a_half_turn():
    p1 = {i for i in range(12) if sizes(i, 'p1')}
    p2_only = {i for i in range(12) if sizes(i, 'p2')} - p1
    assert len(p1) == 8 and len(p2_only) == 4
    assert {i for i in range(12) if sizes(i, 'p1') or sizes(i, 'p2')} == set(range(12))
    assert p2_only == {1, 6, 7, 10}
