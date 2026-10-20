import json
import math
import random
import sys
import numpy as np
SQ3 = math.sqrt(3)
TOL = 1e-06
AREA6 = 6 * SQ3 / 4

def centroid_area(P):
    a = cx = cy = 0.0
    for i in range(len(P)):
        x0, y0 = P[i]
        x1, y1 = P[(i + 1) % len(P)]
        c = x0 * y1 - x1 * y0
        a += c
        cx += (x0 + x1) * c
        cy += (y0 + y1) * c
    a /= 2
    return ((cx / (6 * a), cy / (6 * a)), abs(a))

def simplify(P):
    out = []
    for i in range(len(P)):
        a, b, c = (P[i - 1], P[i], P[(i + 1) % len(P)])
        if abs((b[0] - a[0]) * (c[1] - b[1]) - (b[1] - a[1]) * (c[0] - b[0])) > 1e-09:
            out.append(b)
    return out

def same_polygon(P, Q):
    return len(P) == len(Q) and all((min((math.hypot(p[0] - q[0], p[1] - q[1]) for q in Q)) < TOL for p in P))

def signature(P):
    return sorted((round(math.hypot(p[0] - q[0], p[1] - q[1]), 6) for i, p in enumerate(P) for q in P[i + 1:]))

class Patch:

    def __init__(self, cell, t1, t2, R=5):
        self.cell, self.t1, self.t2, self.R = (cell, np.array(t1), np.array(t2), R)
        self.tiles, self.bucket = ([], {})
        for i in range(-R, R + 1):
            for j in range(-R, R + 1):
                sh = i * self.t1 + j * self.t2
                for k, poly in enumerate(cell):
                    P = [(x + sh[0], y + sh[1]) for x, y in poly]
                    c, _ = centroid_area(P)
                    idx = len(self.tiles)
                    self.tiles.append((k, i, j, P, c))
                    self.bucket.setdefault((math.floor(c[0] * 4), math.floor(c[1] * 4)), []).append(idx)

    def find(self, P):
        c, _ = centroid_area(P)
        bx, by = (math.floor(c[0] * 4), math.floor(c[1] * 4))
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for idx in self.bucket.get((bx + dx, by + dy), ()):
                    if math.hypot(self.tiles[idx][4][0] - c[0], self.tiles[idx][4][1] - c[1]) < 1e-05 and same_polygon(P, self.tiles[idx][3]):
                        return idx
        return None

    def test_tiles(self, r=2):
        return [t for t in self.tiles if abs(t[1]) <= r and abs(t[2]) <= r]

def apply(M, t, P):
    return [(M[0][0] * x + M[0][1] * y + t[0], M[1][0] * x + M[1][1] * y + t[1]) for x, y in P]

def maps_tiling(patch, M, t):
    return all((patch.find(apply(M, t, T[3])) is not None for T in patch.test_tiles()))

def linear_parts():
    out = []
    for k in range(6):
        th = k * math.pi / 3
        out.append(((math.cos(th), -math.sin(th)), (math.sin(th), math.cos(th))))
    for k in range(6):
        th = k * math.pi / 3
        out.append(((math.cos(th), math.sin(th)), (math.sin(th), -math.cos(th))))
    return out

def reduce_mod_lattice(v, t1, t2):
    Lm = np.array([[t1[0], t2[0]], [t1[1], t2[1]]])
    fr = np.linalg.solve(Lm, np.array(v))
    fl = np.floor(fr + 1e-09)
    return np.array(v) - fl[0] * np.array(t1) - fl[1] * np.array(t2)

def find_group(patch, t1, t2):
    Lm = np.array([[t1[0], t2[0]], [t1[1], t2[1]]])
    Linv = np.linalg.inv(Lm)
    A0 = next((t for t in patch.tiles if t[0] == 0 and t[1] == 0 and (t[2] == 0)))
    cands = [t for t in patch.tiles if abs(t[1]) <= 1 and abs(t[2]) <= 1]
    found, seen = ([], set())
    for M in linear_parts():
        c0 = (M[0][0] * A0[4][0] + M[0][1] * A0[4][1], M[1][0] * A0[4][0] + M[1][1] * A0[4][1])
        for B in cands:
            t = (B[4][0] - c0[0], B[4][1] - c0[1])
            fr = Linv @ np.array(t)
            key = (tuple((round(v, 4) + 0.0 for r in M for v in r)), round(fr[0] % 1, 5) % 1.0, round(fr[1] % 1, 5) % 1.0)
            if key in seen:
                continue
            if maps_tiling(patch, M, t):
                seen.add(key)
                found.append((M, t))
    return found

def rot_order(M):
    k = round(math.atan2(M[1][0], M[0][0]) / (math.pi / 3)) % 6
    return 1 if k == 0 else 6 // math.gcd(k, 6)

def classify_geometric(elements, t1, t2, in_translations):
    t1, t2 = (np.array(t1), np.array(t2))
    Lm = np.array([[t1[0], t2[0]], [t1[1], t2[1]]])
    Linv = np.linalg.inv(Lm)
    win = [(i, j) for i in range(-4, 5) for j in range(-4, 5)]
    n = 1
    mirror_lines, any_glide, mirror_dirs, centres = ([], False, set(), {})
    for M, t in elements:
        t = np.array(t)
        det = M[0][0] * M[1][1] - M[0][1] * M[1][0]
        if det > 0:
            o = rot_order(M)
            if o == 1:
                continue
            n = max(n, o)
            I_M = np.array([[1 - M[0][0], -M[0][1]], [-M[1][0], 1 - M[1][1]]])
            for i in range(0, 4):
                for j in range(0, 4):
                    c = np.linalg.solve(I_M, t + i * t1 + j * t2)
                    fr = Linv @ c
                    key = (round(fr[0] % 1, 5) % 1.0, round(fr[1] % 1, 5) % 1.0)
                    centres[key] = max(centres.get(key, 1), o)
        else:
            phi = math.atan2(M[1][0], M[0][0]) / 2
            d = np.array([math.cos(phi), math.sin(phi)])
            nn = np.array([-math.sin(phi), math.cos(phi)])
            for i, j in win:
                tw = t + i * t1 + j * t2
                glide = tw @ d * d
                if in_translations(glide):
                    mirror_lines.append((round(phi % math.pi, 5) % round(math.pi, 5), tw @ nn / 2, nn))
                    mirror_dirs.add(round(phi % math.pi, 4) % round(math.pi, 4))
                else:
                    any_glide = True
    has_mirror = bool(mirror_lines)

    def on_mirror(c_frac):
        c = Lm @ np.array(c_frac)
        for s_off in range(-1, 2):
            for s2 in range(-1, 2):
                cc = c + s_off * t1 + s2 * t2
                if any((abs(cc @ nn - s) < 1e-06 for _, s, nn in mirror_lines)):
                    return True
        return False
    if n == 6:
        return 'p6m' if has_mirror else 'p6'
    if n == 3:
        if not has_mirror:
            return 'p3'
        return 'p3m1' if all((on_mirror(c) for c, o in centres.items() if o == 3)) else 'p31m'
    if n == 2:
        if not has_mirror:
            return 'pgg' if any_glide else 'p2'
        if len(mirror_dirs) == 1:
            return 'pmg'
        return 'pmm' if all((on_mirror(c) for c, o in centres.items() if o == 2)) else 'cmm'
    if not has_mirror:
        return 'pg' if any_glide else 'p1'
    return 'cm' if any_glide else 'pm'

def axial_to_cart_matrix(Max):
    B = np.array([[1, 0.5], [0, SQ3 / 2]])
    return B @ np.array(Max, dtype=float) @ np.linalg.inv(B)

def check_row(g, blueprint_poly=None, seed=1):
    from src.wallpaper import D6
    out = {'ok': True, 'why': []}
    cx, cy = g['center']
    cell = [simplify([(p[0] + cx, p[1] + cy) for p in im['polygon']]) for im in g['images']]
    t1, t2 = (g['t1'], g['t2'])
    sig0 = signature(blueprint_poly) if blueprint_poly else signature(cell[0])
    for P in cell:
        if abs(centroid_area(P)[1] - AREA6) > 1e-09 or signature(P) != sig0:
            out['ok'] = False
            out['why'].append('tile is not a hexiamond congruent to the others')
    patch = Patch(cell, t1, t2)
    rnd = random.Random(seed)
    pts = [(u * t1[0] + v * t2[0], u * t1[1] + v * t2[1]) for u, v in ((rnd.random(), rnd.random()) for _ in range(1500))]
    polys = [T[3] for T in patch.test_tiles()]
    arr = np.array(pts)
    counts = np.zeros(len(pts), dtype=int)
    for P in polys:
        inside = np.zeros(len(pts), dtype=bool)
        for a in range(len(P)):
            x0, y0 = P[a]
            x1, y1 = P[(a + 1) % len(P)]
            cond = (y0 > arr[:, 1]) != (y1 > arr[:, 1])
            xint = (x1 - x0) * (arr[:, 1] - y0) / (y1 - y0 + 1e-300) + x0
            inside ^= cond & (arr[:, 0] < xint)
        counts += inside
    if not np.all(counts == 1):
        out['ok'] = False
        out['why'].append(f'cover failed at {int(np.sum(counts != 1))} sample points')
    F = find_group(patch, t1, t2)
    Lm = np.array([[t1[0], t2[0]], [t1[1], t2[1]]])
    Linv = np.linalg.inv(Lm)
    in_F = lambda v: maps_tiling(patch, ((1, 0), (0, 1)), tuple(reduce_mod_lattice(v, t1, t2)))
    out['F'] = classify_geometric(F, t1, t2, in_F)
    if g.get('elements'):
        Bm = np.array([[1, 0.5], [0, SQ3 / 2]])
        G = []
        for mi, ta in g['elements'].items():
            M = axial_to_cart_matrix(D6[int(mi)])
            t = reduce_mod_lattice(Bm @ np.array(ta, dtype=float), t1, t2)
            if not maps_tiling(patch, M, t):
                out['ok'] = False
                out['why'].append(f'generating element {mi} is not a symmetry of the tiling')
            G.append((M, t))

        def in_lattice(v):
            fr = Linv @ np.array(v)
            return all((abs(x - round(x)) < 1e-06 for x in fr))
        for M1, t1_ in G:
            for M2, t2_ in G:
                M, t = (M1 @ M2, M1 @ t2_ + t1_)
                if not any((np.allclose(M, Me, atol=1e-06) and in_lattice(t - te) for Me, te in G)):
                    out['ok'] = False
                    out['why'].append('elements are not closed under composition')
        A0 = cell[0]
        ks = {0}
        for M, t in G:
            idx = patch.find(apply(M, t, A0))
            ks.add(patch.tiles[idx][0] if idx is not None else -1)
        if ks != set(range(len(cell))):
            out['ok'] = False
            out['why'].append(f'G not transitive on the {len(cell)} tiles of its cell (reaches {sorted(ks)})')
        out['G'] = classify_geometric(G, t1, t2, in_lattice)
        if out['G'] != g['group']:
            out['ok'] = False
            out['why'].append(f"G is {out['G']}, claimed {g['group']}")
        if out['F'] != g.get('full_group', out['F']):
            out['ok'] = False
            out['why'].append(f"full group is {out['F']}, claimed {g['full_group']}")
    elif out['F'] != g['group']:
        out['ok'] = False
        out['why'].append(f"full group is {out['F']}, claimed {g['group']}")
    return out

def main(path):
    from src.geometry import polygon_points
    from src.groups import GROUP_BY_NAME
    from src.shapes import HEXIAMONDS
    s = open(path).read()
    data = json.loads(s[s.index('{'):].rstrip().rstrip(';'))
    bad = 0
    for idx, h in enumerate(data['hexiamonds']):
        ref = polygon_points(HEXIAMONDS[idx])
        for g in h['groups']:
            r = check_row(g, ref)
            if r['ok'] and 'G' in r:
                fam_ok = GROUP_BY_NAME[r['G']]['lattice'] == GROUP_BY_NAME[r['F']]['lattice']
                r['ok'] &= fam_ok or not g.get('generated')
                if not fam_ok:
                    r['why'].append('G and F are in different lattice families')
            bad += not r['ok']
            print(f"{('OK ' if r['ok'] else 'BAD')} {h['name']:18} claims {g['group']:5} | geometry: G={r.get('G', '-'):5} F={r['F']:5} {'; '.join(r['why'])}", flush=True)
    print(f'\n{bad} row(s) failed the independent geometric check')
    return bad
if __name__ == '__main__':
    sys.exit(1 if main(sys.argv[1]) else 0)
