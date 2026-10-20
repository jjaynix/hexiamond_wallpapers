import copy
import pytest
from src.classify import search_shape, search_transitive
from src.shapes import HEXIAMONDS
from src.verify import verify_generated
RES = [search_transitive(bp, 12) for bp in HEXIAMONDS]

@pytest.mark.parametrize('idx', range(12))
def test_every_admitted_tiling_verifies_independently(idx):
    for rep in RES[idx]['by_pair'].values():
        assert verify_generated(rep, HEXIAMONDS[idx])
        assert len(rep['elements']) % rep['tiles_per_cell'] == 0
        assert rep['tiles_per_cell'] <= 12

def test_shapes_without_symmetry_admit_exactly_their_full_group_isohedral_types():
    for idx, bp in enumerate(HEXIAMONDS):
        if RES[idx]['stabiliser_order'] == 1:
            assert set(RES[idx]['best']) == set(search_shape(bp, max_tiles=12)['iso'])

def test_admitted_always_contains_the_full_group_isohedral_types():
    for idx, bp in enumerate(HEXIAMONDS):
        assert set(search_shape(bp, max_tiles=6)['iso']) <= set(RES[idx]['best'])

def test_hexagon_has_a_single_tiling_so_every_admitted_group_lies_inside_p6m():
    best = RES[8]['best']
    assert {'p6m', 'p6', 'p3m1', 'p31m', 'p3', 'p2', 'p1'} <= set(best)
    assert all((rep['full_group'] == 'p6m' for rep in best.values()))

def test_impossible_and_never_found_groups():
    admitted = set().union(*(set(r['best']) for r in RES))
    assert not admitted & {'p4', 'p4m', 'p4g', 'pmm'}

def test_verifier_rejects_a_group_that_is_not_transitive_or_not_a_symmetry():
    bp = HEXIAMONDS[8]
    rep = RES[8]['best']['p6']
    bad_type = copy.deepcopy(rep)
    bad_type['group'] = 'p3'
    with pytest.raises(AssertionError):
        verify_generated(bad_type, bp)
    p1 = copy.deepcopy(RES[8]['best']['p1'])
    p1['elements']['3'] = [1, 0]
    with pytest.raises(AssertionError):
        verify_generated(p1, bp)
