import copy
import pytest
from src.classify import search_shape
from src.shapes import HEXIAMONDS
from src.tiling import TorusProblem, canonical_lattices, shape_orientations, dilate_blueprint
from src.verify import verify_rep
K_CHECK = 4

def brute_force(blueprint, max_tiles, refine=1):
    orients, _ = shape_orientations(dilate_blueprint(blueprint, refine))
    found = {}
    for k in range(1, max_tiles + 1):
        for L in canonical_lattices(3 * refine * refine * k):
            tp = TorusProblem(L, orients)

            def cb(sol):
                info = tp.analyse(sol)
                found[info['name']] = min(found.get(info['name'], 10 ** 9), info['tiles_per_cell'])
            _, complete = tp.enumerate_solutions(cb, 2000000)
            assert complete
    return found

@pytest.mark.parametrize('idx', range(12))
def test_group_first_search_agrees_with_enumerating_all_tilings(idx):
    r = search_shape(HEXIAMONDS[idx], max_tiles=K_CHECK)
    fast = {g: v['tiles_per_cell'] for g, v in r['best'].items() if v['tiles_per_cell'] <= K_CHECK}
    assert fast == brute_force(HEXIAMONDS[idx], K_CHECK)
    assert r['exhaustive']

def test_hexagon_only_p6m():
    r = search_shape(HEXIAMONDS[8], max_tiles=6)
    assert set(r['best']) == {'p6m'} and r['best']['p6m']['tiles_per_cell'] == 1

def test_known_hand_derived_tilings_are_found():
    r = search_shape(HEXIAMONDS[11], max_tiles=3)
    assert r['best']['pmg']['tiles_per_cell'] == 2 and r['best']['p2']['tiles_per_cell'] == 1

def test_half_grid_offsets_add_cm_for_the_bar():
    plain = search_shape(HEXIAMONDS[11], max_tiles=2)
    half = search_shape(HEXIAMONDS[11], max_tiles=2, refine=2)
    assert 'cm' not in plain['best'] and half['best']['cm']['tiles_per_cell'] == 2

@pytest.mark.parametrize('refine,K', [(1, 6), (2, 3)])
def test_every_reported_tiling_verifies_in_the_plane(refine, K):
    for bp in HEXIAMONDS:
        r = search_shape(bp, max_tiles=K, refine=refine)
        for rep in list(r['best'].values()) + list(r['iso'].values()):
            assert verify_rep(rep, bp, refine)

def test_verifier_rejects_tampered_results():
    bp = HEXIAMONDS[11]
    rep = search_shape(bp, max_tiles=2)['best']['pmg']
    assert verify_rep(rep, bp)
    wrong_group = copy.deepcopy(rep)
    wrong_group['group'] = 'pgg'
    with pytest.raises(AssertionError):
        verify_rep(wrong_group, bp)
    missing_symmetry = copy.deepcopy(rep)
    missing_symmetry['elements'] = {k: v for k, v in rep['elements'].items() if k == 0}
    with pytest.raises(AssertionError):
        verify_rep(missing_symmetry, bp)
    overlapping = copy.deepcopy(rep)
    overlapping['tiles'][1] = overlapping['tiles'][0]
    with pytest.raises(AssertionError):
        verify_rep(overlapping, bp)
