import numpy as np
import bisect
_PAIR_CACHE = {}

def _all_pairs_sorted_by_area(vectors):
    key = id(vectors)
    cached = _PAIR_CACHE.get(key)
    if cached is not None:
        return cached
    pairs = []
    for i in range(len(vectors)):
        for j in range(len(vectors)):
            if i == j:
                continue
            t1, t2 = (vectors[i], vectors[j])
            cross = abs(t1[0] * t2[1] - t1[1] * t2[0])
            if cross < 1e-09:
                continue
            pairs.append((t1, t2, cross))
    pairs.sort(key=lambda p: p[2])
    areas = [p[2] for p in pairs]
    _PAIR_CACHE[key] = (areas, pairs)
    return (areas, pairs)

def candidate_centers(pts, extra_pts=None):
    from .lattice import V1, V2
    raw = []
    if extra_pts is not None:
        raw.extend(extra_pts)
    if len(pts) > 0:
        inv_v2_y = 2.0 / np.sqrt(3)
        mus, nus = ([], [])
        for p in pts:
            nu = p[1] * inv_v2_y
            mu = p[0] - 0.5 * nu
            mus.append(mu)
            nus.append(nu)
        m_min = int(np.floor(min(mus))) - 1
        m_max = int(np.ceil(max(mus))) + 1
        n_min = int(np.floor(min(nus))) - 1
        n_max = int(np.ceil(max(nus))) + 1
        for m in range(m_min, m_max + 1):
            for n in range(n_min, n_max + 1):
                base = m * V1 + n * V2
                raw.append(base)
                raw.append(base + 0.5 * V1)
                raw.append(base + 0.5 * V2)
                raw.append(base + 0.5 * (V1 + V2))
                raw.append(base + (V1 + V2) / 3.0)
                raw.append(base + 2.0 * (V1 + V2) / 3.0)
    else:
        raw.extend(pts)
    uniq = []
    for c in raw:
        if not any((np.allclose(c, u, atol=1e-05) for u in uniq)):
            uniq.append(c)
    return uniq

def candidate_translations(max_index=6, min_len=0.4, max_len=12.0):
    from .lattice import V1, V2
    vecs = {}
    for m in range(-max_index, max_index + 1):
        for n in range(-max_index, max_index + 1):
            if m == 0 and n == 0:
                continue
            v = m * V1 + n * V2
            length = np.linalg.norm(v)
            if min_len < length <= max_len:
                vecs[m, n] = v
    return list(vecs.values())

def candidate_axis_angles(pts, center):
    return [0.0, 30.0, 60.0, 90.0, 120.0, 150.0]

def lattice_pairs(vectors, max_pairs=40):
    pairs = []
    for i in range(len(vectors)):
        for j in range(len(vectors)):
            if i == j:
                continue
            t1, t2 = (vectors[i], vectors[j])
            cross = t1[0] * t2[1] - t1[1] * t2[0]
            if abs(cross) < 1e-06:
                continue
            pairs.append((t1, t2, abs(cross)))
    pairs.sort(key=lambda p: p[2])
    return pairs[:max_pairs]

def lattice_pairs_matching_area(vectors, target_area, rel_tol, max_pairs=60):
    areas, all_pairs = _all_pairs_sorted_by_area(vectors)
    delta = rel_tol * max(target_area, 1)
    lo = bisect.bisect_left(areas, target_area - delta)
    hi = bisect.bisect_right(areas, target_area + delta)
    candidates = all_pairs[lo:hi]
    candidates = sorted(candidates, key=lambda p: np.linalg.norm(p[0]) + np.linalg.norm(p[1]))
    return candidates[:max_pairs]
