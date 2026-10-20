import pytest
from src.classify import select_admitted
from src.groups import GROUP_BY_NAME
from tests.test_transitive import RES
RULES = ('full_group', 'same_family', 'any_subgroup')
PAPER = {0: ['cm'], 1: ['p2'], 2: ['cmm'], 3: ['p2', 'p1'], 4: ['p2', 'cm'], 5: ['p31m', 'p2', 'cm'], 6: ['p3', 'p2'], 7: ['p2'], 8: ['p6m'], 9: ['p6', 'p2'], 10: ['p2', 'cm'], 11: ['p2']}

def sel(idx, rule):
    return select_admitted(RES[idx]['by_pair'], RES[idx]['pair_sizes'], rule)

@pytest.mark.parametrize('idx', range(12))
def test_rules_are_nested(idx):
    full, fam, anyg = (set(sel(idx, r)) for r in RULES)
    assert full <= fam <= anyg

@pytest.mark.parametrize('idx', range(12))
def test_same_family_rule_really_requires_the_same_lattice_family(idx):
    for g, e in sel(idx, 'same_family').items():
        assert e['full_groups'], g
        assert all((GROUP_BY_NAME[f]['lattice'] == GROUP_BY_NAME[g]['lattice'] for f in e['full_groups']))
        assert GROUP_BY_NAME[e['rep']['full_group']]['lattice'] == GROUP_BY_NAME[g]['lattice']

def test_hexagon_gets_exactly_the_five_hexagonal_lattice_groups_under_the_same_family_rule():
    assert set(sel(8, 'same_family')) == {'p3', 'p31m', 'p3m1', 'p6', 'p6m'}
    assert set(sel(8, 'full_group')) == {'p6m'}
    assert len(sel(8, 'any_subgroup')) == 12

def test_shapes_without_symmetry_do_not_depend_on_the_rule():
    for idx in range(12):
        if RES[idx]['stabiliser_order'] == 1:
            assert set(sel(idx, 'full_group')) == set(sel(idx, 'same_family')) == set(sel(idx, 'any_subgroup'))

@pytest.mark.parametrize('idx', range(12))
def test_every_group_in_the_papers_table_4_is_admitted_except_yachts_cm(idx):
    got = set(sel(idx, 'same_family'))
    missing = {g for g in PAPER[idx] if g not in got}
    assert missing == ({'cm'} if idx == 10 else set())
