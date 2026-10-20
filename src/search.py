from itertools import product
from .wallpaper import D6, D6_INDEX, IDENTITY_INDEX, mat_mul, mat_vec, lattice_invariant, lattice_reduce, classify_group, lattice_index, hnf
from .tiling import TorusProblem, canonical_lattices, shape_orientations

def _closure(indices):
    S = {IDENTITY_INDEX} | set(indices)
    changed = True
    while changed:
        changed = False
        for a in list(S):
            for b in list(S):
                c = D6_INDEX[mat_mul(D6[a], D6[b])]
                if c not in S:
                    S.add(c)
                    changed = True
    return frozenset(S)

def _all_subgroups():
    subs = {_closure([])}
    for a in range(12):
        subs.add(_closure([a]))
        for b in range(a + 1, 12):
            subs.add(_closure([a, b]))
    return sorted(subs, key=lambda s: (len(s), sorted(s)))
D6_SUBGROUPS = _all_subgroups()
assert len(D6_SUBGROUPS) == 16, len(D6_SUBGROUPS)

def _generators(P):
    gens, cur = ([], _closure([]))
    for m in sorted(P):
        if m not in cur:
            gens.append(m)
            cur = _closure(gens)
        if cur == P:
            break
    return gens

def _compose(L, g, h):
    (m1, t1), (m2, t2) = (g, h)
    mi = D6_INDEX[mat_mul(D6[m1], D6[m2])]
    v = mat_vec(D6[m1], t2)
    return (mi, lattice_reduce(L, (v[0] + t1[0], v[1] + t1[1])))

def _build_group(L, P, gens, ts):
    elems = {IDENTITY_INDEX: (0, 0)}
    gl = [(m, lattice_reduce(L, t)) for m, t in zip(gens, ts)]
    frontier = [(IDENTITY_INDEX, (0, 0))]
    while frontier:
        nxt = []
        for e in frontier:
            for g in gl:
                mi, t = _compose(L, g, e)
                if mi in elems:
                    if elems[mi] != t:
                        return None
                else:
                    elems[mi] = t
                    nxt.append((mi, t))
        frontier = nxt
    if set(elems) != set(P):
        return None
    for a in elems.items():
        for b in elems.items():
            mi, t = _compose(L, a, b)
            if elems[mi] != t:
                return None
    return elems
D6_INVERSE = [next((j for j in range(12) if mat_mul(D6[i], D6[j]) == D6[0])) for i in range(12)]

def _stabiliser(L):
    return [mi for mi in range(12) if lattice_invariant(L, D6[mi])]

def _canonical_form(L, elems, stab, vecs):
    best = None
    for mi in stab:
        M = D6[mi]
        Minv = D6[D6_INVERSE[mi]]
        for s in vecs:
            out = []
            for ni, t in elems.items():
                N = D6[ni]
                N2 = mat_mul(mat_mul(M, N), Minv)
                n2 = D6_INDEX[N2]
                Mt = mat_vec(M, t)
                Ns = mat_vec(N2, s)
                t2 = lattice_reduce(L, (Mt[0] + s[0] - Ns[0], Mt[1] + s[1] - Ns[1]))
                out.append((n2, t2))
            out.sort()
            key = tuple(out)
            if best is None or key < best:
                best = key
    return best

def _first_generator_reps(L, M):
    cols = [(1 - M[0][0], -M[1][0]), (-M[0][1], 1 - M[1][1])]
    vecs = [L[0], L[1]] + [c for c in cols if c != (0, 0)]
    big = hnf(vecs)
    a, c = (big[0][0], big[1][1])
    return [(q, r) for r in range(c) for q in range(a)]

def plane_groups_with_lattice(L):
    a, c = (L[0][0], L[1][1])
    vecs = [(q, r) for r in range(c) for q in range(a)]
    stab = _stabiliser(L)
    seen = set()
    out = []
    for P in D6_SUBGROUPS:
        if not all((m in stab for m in P)):
            continue
        gens = _generators(P)
        if not gens:
            candidates = [()]
        else:
            first = _first_generator_reps(L, D6[gens[0]])
            candidates = ((t1,) + rest for t1 in first for rest in product(vecs, repeat=len(gens) - 1))
        for ts in candidates:
            elems = _build_group(L, P, gens, ts)
            if elems is None:
                continue
            key = _canonical_form(L, elems, stab, vecs)
            if key in seen:
                continue
            seen.add(key)
            out.append(dict(key))
    return out

def group_orbits(tp, elems):
    key_to_p = {k: p for p, k in enumerate(tp.pl_key)}
    seen, options = (set(), [])
    for p in range(len(tp.pl_key)):
        orbit = frozenset((key_to_p[tp._image_key(p, mi, t)] for mi, t in elems.items()))
        if orbit in seen:
            continue
        seen.add(orbit)
        mask, ok = (0, True)
        for q in orbit:
            m = tp.pl_mask[q]
            if mask & m:
                ok = False
                break
            mask |= m
        if ok:
            options.append((mask, tuple(sorted(orbit))))
    return options

def invariant_covers(tp, options, callback, max_solutions):
    full = tp.full
    by_tri = [[] for _ in range(tp.ntri)]
    for oi, (mask, _) in enumerate(options):
        m = mask
        while m:
            low = m & -m
            by_tri[low.bit_length() - 1].append(oi)
            m ^= low
    count = 0
    status = 'exhausted'
    chosen = []

    def rec(cov):
        nonlocal count, status
        if cov == full:
            count += 1
            sol = [p for oi in chosen for p in options[oi][1]]
            if callback(sol, len(chosen)):
                status = 'stopped'
            elif count >= max_solutions:
                status = 'capped'
            return
        free = ~cov & full
        low = free & -free
        for oi in by_tri[low.bit_length() - 1]:
            m = options[oi][0]
            if m & cov:
                continue
            chosen.append(oi)
            rec(cov | m)
            chosen.pop()
            if status != 'exhausted':
                return
    rec(0)
    return (count, status)
