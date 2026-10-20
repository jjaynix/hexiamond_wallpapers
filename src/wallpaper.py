from fractions import Fraction
from math import gcd
ROT60 = ((0, -1), (1, 1))
FLIP = ((1, 1), (0, -1))
IDENTITY = ((1, 0), (0, 1))

def mat_mul(A, B):
    return ((A[0][0] * B[0][0] + A[0][1] * B[1][0], A[0][0] * B[0][1] + A[0][1] * B[1][1]), (A[1][0] * B[0][0] + A[1][1] * B[1][0], A[1][0] * B[0][1] + A[1][1] * B[1][1]))

def mat_vec(M, v):
    return (M[0][0] * v[0] + M[0][1] * v[1], M[1][0] * v[0] + M[1][1] * v[1])

def mat_det(M):
    return M[0][0] * M[1][1] - M[0][1] * M[1][0]

def _build_d6():
    mats = []
    R = IDENTITY
    for _ in range(6):
        mats.append(R)
        R = mat_mul(ROT60, R)
    rots = list(mats)
    for R in rots:
        mats.append(mat_mul(R, FLIP))
    return tuple(mats)
D6 = _build_d6()
D6_INDEX = {m: i for i, m in enumerate(D6)}
IDENTITY_INDEX = 0
assert len(set(D6)) == 12 and all((abs(mat_det(m)) == 1 for m in D6))

def rotation_order(M):
    P, k = (M, 1)
    while P != IDENTITY:
        P = mat_mul(M, P)
        k += 1
    return k

def is_reflection(M):
    return mat_det(M) == -1

def cross(u, v):
    return u[0] * v[1] - u[1] * v[0]

def hnf(vectors):
    top = None
    zeros = []
    for v in vectors:
        v = (int(v[0]), int(v[1]))
        if top is None:
            top = v
            continue
        x1, y1 = top
        x2, y2 = v
        while y2 != 0:
            k = y1 // y2
            x1, y1, x2, y2 = (x2, y2, x1 - k * x2, y1 - k * y2)
        top = (x1, y1)
        if x2 != 0:
            zeros.append((x2, 0))
    if top is None:
        raise ValueError('empty generating set')
    if top[1] < 0:
        top = (-top[0], -top[1])
    a = 0
    for z in zeros:
        a = gcd(a, abs(z[0]))
    if top[1] == 0:
        raise ValueError('lattice has rank < 2')
    if a == 0:
        raise ValueError('lattice has rank < 2')
    return ((a, 0), (top[0] % a, top[1]))

def lattice_index(basis):
    return basis[0][0] * basis[1][1]

def lattice_contains(basis, v):
    (a, _), (b, c) = basis
    q, r = v
    if r % c:
        return False
    k = r // c
    return (q - k * b) % a == 0

def lattice_image(basis, M):
    return hnf([mat_vec(M, basis[0]), mat_vec(M, basis[1])])

def lattice_invariant(basis, M):
    return all((lattice_contains(basis, mat_vec(M, b)) for b in basis))

def lattice_reduce(basis, v):
    (a, _), (b, c) = basis
    q, r = v
    k = r // c
    return ((q - k * b) % a, r - k * c)

def norm2(v):
    return v[0] * v[0] + v[1] * v[1] + v[0] * v[1]

def gauss_reduce(basis):
    u, v = (basis[0], basis[1])
    while True:
        if norm2(u) > norm2(v):
            u, v = (v, u)
        dot2 = 2 * (u[0] * v[0] + u[1] * v[1]) + u[0] * v[1] + u[1] * v[0]
        uu2 = 2 * norm2(u)
        k = (2 * dot2 + uu2) // (2 * uu2)
        if k == 0:
            break
        v = (v[0] - k * u[0], v[1] - k * u[1])
    if norm2(u) > norm2(v):
        u, v = (v, u)
    return (u, v)

def lattice_generator_on_line(basis, e):
    b1, b2 = basis
    A, B = (cross(b1, e), cross(b2, e))
    g = gcd(abs(A), abs(B))
    if g == 0:
        raise ValueError('degenerate lattice')
    x, y = (B // g, -A // g)
    return (x * b1[0] + y * b2[0], x * b1[1] + y * b2[1])

def _primitive(v):
    g = gcd(abs(v[0]), abs(v[1]))
    return (v[0] // g, v[1] // g)

def _add(A, B):
    return ((A[0][0] + B[0][0], A[0][1] + B[0][1]), (A[1][0] + B[1][0], A[1][1] + B[1][1]))

def _sub(A, B):
    return ((A[0][0] - B[0][0], A[0][1] - B[0][1]), (A[1][0] - B[1][0], A[1][1] - B[1][1]))

def reflection_axes(M):
    plus = _add(IDENTITY, M)
    minus = _sub(IDENTITY, M)

    def first_nonzero_column(A):
        for col in ((A[0][0], A[1][0]), (A[0][1], A[1][1])):
            if col != (0, 0):
                return _primitive(col)
        raise ValueError('zero matrix')
    return (first_nonzero_column(plus), first_nonzero_column(minus))

def lattice_is_centred(basis, M):
    d, n = reflection_axes(M)
    ud = lattice_generator_on_line(basis, d)
    un = lattice_generator_on_line(basis, n)
    ratio = abs(cross(ud, un)) / lattice_index(basis)
    if ratio == 1:
        return False
    if ratio == 2:
        return True
    raise AssertionError(f'lattice not compatible with reflection (index ratio {ratio})')

def has_pure_mirror(basis, M, t):
    P = _add(IDENTITY, M)
    w0 = mat_vec(P, t)
    w1 = mat_vec(P, basis[0])
    w2 = mat_vec(P, basis[1])
    j = 0 if any((x[0] for x in (w0, w1, w2))) else 1
    A, B, C = (w1[j], w2[j], -w0[j])
    g = gcd(abs(A), abs(B))
    if g == 0:
        return C == 0
    return C % g == 0

def _inverse_2x2(A):
    d = mat_det(A)
    return ((Fraction(A[1][1], d), Fraction(-A[0][1], d)), (Fraction(-A[1][0], d), Fraction(A[0][0], d)))

def _fvec(M, v):
    return (M[0][0] * v[0] + M[0][1] * v[1], M[1][0] * v[0] + M[1][1] * v[1])

def _three_fold_centres_on_mirrors(basis, elements):
    rot3 = [m for m in elements if not is_reflection(D6[m]) and rotation_order(D6[m]) == 3]
    refl = [m for m in elements if is_reflection(D6[m])]
    R = D6[rot3[0]]
    t_r = elements[rot3[0]]
    inv = _inverse_2x2(_sub(IDENTITY, R))
    for i in range(3):
        for j in range(3):
            v = (i * basis[0][0] + j * basis[1][0], i * basis[0][1] + j * basis[1][1])
            c = _fvec(inv, (t_r[0] + v[0], t_r[1] + v[1]))
            on_mirror = False
            for m in refl:
                M, t = (D6[m], elements[m])
                w = _fvec(_sub(IDENTITY, M), c)
                s = (w[0] - t[0], w[1] - t[1])
                if s[0].denominator == 1 and s[1].denominator == 1 and lattice_contains(basis, (int(s[0]), int(s[1]))):
                    on_mirror = True
                    break
            if not on_mirror:
                return False
    return True

def classify_group(basis, elements):
    rots = [m for m in elements if not is_reflection(D6[m])]
    refl = [m for m in elements if is_reflection(D6[m])]
    n_rot = len(rots)
    n_ref = len(refl)
    max_order = max((rotation_order(D6[m]) for m in rots))
    assert n_rot == max_order, 'point group must be cyclic in its rotation part'
    pure = {m: has_pure_mirror(basis, D6[m], elements[m]) for m in refl}
    centred = {m: lattice_is_centred(basis, D6[m]) for m in refl}
    if n_ref == 0:
        name = {1: 'p1', 2: 'p2', 3: 'p3', 6: 'p6'}[n_rot]
    else:
        assert n_ref == n_rot, 'point group must be dihedral'
        if n_rot == 1:
            m = refl[0]
            name = ('cm' if centred[m] else 'pm') if pure[m] else 'pg'
        elif n_rot == 2:
            if any(centred.values()):
                name = 'cmm'
            else:
                k = sum(pure.values())
                name = {2: 'pmm', 1: 'pmg', 0: 'pgg'}[k]
        elif n_rot == 3:
            name = 'p3m1' if _three_fold_centres_on_mirrors(basis, elements) else 'p31m'
        else:
            name = 'p6m'
    mirror = any(pure.values())
    glide = any((not pure[m] or centred[m] for m in refl))
    if max_order in (3, 6):
        lattice = 'hexagonal'
    elif n_ref == 0:
        lattice = 'oblique'
    else:
        lattice = 'rhombic' if any(centred.values()) else 'rectangular'
    return {'name': name, 'rotation_order': max_order, 'mirror': mirror, 'glide': glide, 'point_group': ('C' if n_ref == 0 else 'D') + str(n_rot), 'lattice_type': lattice}

def apply_to_S(M, t, S):
    X, Y = S
    return (M[0][0] * X + M[0][1] * Y + 3 * t[0], M[1][0] * X + M[1][1] * Y + 3 * t[1])

def S_of_triangle(q, r, o):
    return (3 * q + 1 + o, 3 * r + 1 + o)

def triangle_of_S(S):
    X, Y = S
    o = X % 3 - 1
    assert o in (0, 1) and Y % 3 - 1 == o, f'not a triangle: {S}'
    return (X // 3, Y // 3, o)

def _frac_coords(basis, c):
    (a, _), (b, cc) = basis
    y = Fraction(c[1]) / cc
    x = (Fraction(c[0]) - y * b) / a
    return (x % 1, y % 1)

def _point(basis, f):
    (a, _), (b, cc) = basis
    return (f[0] * a + f[1] * b, f[1] * cc)

def _on_a_mirror(basis, elements, c):
    for m, t in elements.items():
        M = D6[m]
        if not is_reflection(M):
            continue
        w = _fvec(_sub(IDENTITY, M), c)
        s = (w[0] - t[0], w[1] - t[1])
        if s[0].denominator == 1 and s[1].denominator == 1 and lattice_contains(basis, (int(s[0]), int(s[1]))):
            return True
    return False

def rotation_centre_signature(basis, elements):
    centres = {}
    for mi, t in elements.items():
        M = D6[mi]
        if is_reflection(M) or mi == IDENTITY_INDEX:
            continue
        o = rotation_order(M)
        I_M = _sub(IDENTITY, M)
        inv, det = (_inverse_2x2(I_M), abs(mat_det(I_M)))
        for i in range(det):
            for j in range(det):
                v = (i * basis[0][0] + j * basis[1][0], i * basis[0][1] + j * basis[1][1])
                key = _frac_coords(basis, _fvec(inv, (t[0] + v[0], t[1] + v[1])))
                centres[key] = max(centres.get(key, 1), o)
    parent = {k: k for k in centres}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for key in list(centres):
        P = _point(basis, key)
        for mi, t in elements.items():
            image = _fvec(D6[mi], P)
            img = _frac_coords(basis, (image[0] + t[0], image[1] + t[1]))
            assert img in centres and centres[img] == centres[key]
            parent[find(key)] = find(img)
    off, on = ([], [])
    for root in {find(k) for k in centres}:
        (on if _on_a_mirror(basis, elements, _point(basis, root)) else off).append(centres[root])
    return (sorted(off, reverse=True), sorted(on, reverse=True))
