from src.shapes import HEXIAMONDS
from src.tiling import shape_orientations, dilate_blueprint
from src.geometry import outline_axial, polygon_points, polygon_area
AREA = 6 * 3 ** 0.5 / 4

def test_twelve_distinct_connected_free_hexiamonds():
    assert len(HEXIAMONDS) == 12
    classes = set()
    for bp in HEXIAMONDS:
        assert len(set(bp)) == 6
        orients, stab = shape_orientations(bp)
        classes.add(frozenset(orients))
        assert len(orients) * stab == 12
    assert len(classes) == 12

def test_chirality_count_matches_literature():
    from src.wallpaper import D6, mat_vec, is_reflection, S_of_triangle
    from src.tiling import normalize_S
    chiral = 0
    for bp in HEXIAMONDS:
        base = [S_of_triangle(*t) for t in bp]
        rot = {normalize_S([mat_vec(M, s) for s in base]) for M in D6 if not is_reflection(M)}
        allo = {normalize_S([mat_vec(M, s) for s in base]) for M in D6}
        chiral += len(rot) < len(allo)
    assert chiral == 7

def test_outline_is_a_single_polygon_of_area_six_triangles():
    for bp in HEXIAMONDS:
        for m in (1, 2, 3):
            tri = dilate_blueprint(bp, m)
            assert len(tri) == 6 * m * m
            assert abs(polygon_area(polygon_points(tri, m)) - AREA) < 1e-09
            assert len(outline_axial(tri)) >= 3
