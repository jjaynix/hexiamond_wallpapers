from .wallpaper import D6, IDENTITY_INDEX, mat_vec, hnf, lattice_index, lattice_invariant, lattice_image, lattice_reduce, classify_group, S_of_triangle

def normalize_S(points):
    ax, ay = min(points, key=lambda s: (s[1], s[0]))
    qa, ra = (ax // 3, ay // 3)
    return tuple(sorted(((x - 3 * qa, y - 3 * ra) for x, y in points)))

def shape_orientations(blueprint):
    base = [S_of_triangle(*tri) for tri in blueprint]
    seen, out = ({}, [])
    for M in D6:
        norm = normalize_S([mat_vec(M, s) for s in base])
        if norm not in seen:
            seen[norm] = len(out)
            out.append(norm)
    return (out, 12 // len(out))
_ORIENT_MAP_CACHE = {}

def orientation_map(orientations):
    key = tuple(orientations)
    if key in _ORIENT_MAP_CACHE:
        return _ORIENT_MAP_CACHE[key]
    index = {shape: i for i, shape in enumerate(orientations)}
    table = []
    for shape in orientations:
        row = []
        for M in D6:
            img = [mat_vec(M, s) for s in shape]
            ax, ay = min(img, key=lambda s: (s[1], s[0]))
            qa, ra = (ax // 3, ay // 3)
            norm = tuple(sorted(((x - 3 * qa, y - 3 * ra) for x, y in img)))
            row.append((index[norm], qa, ra))
        table.append(row)
    _ORIENT_MAP_CACHE[key] = table
    return table

def dilate_blueprint(blueprint, m):
    if m == 1:
        return list(blueprint)
    out = []
    for q, r, o in blueprint:
        for X in range(m * q - 1, m * (q + 2) + 1):
            for Y in range(m * r - 1, m * (r + 2) + 1):
                for so in (0, 1):
                    Sx, Sy = (3 * X + 1 + so, 3 * Y + 1 + so)
                    if o == 0:
                        inside = Sx >= 3 * m * q and Sy >= 3 * m * r and (Sx + Sy <= 3 * m * (q + r + 1))
                    else:
                        inside = Sx <= 3 * m * (q + 1) and Sy <= 3 * m * (r + 1) and (Sx + Sy >= 3 * m * (q + r + 1))
                    if inside:
                        out.append((X, Y, so))
    assert len(out) == len(blueprint) * m * m, (len(out), len(blueprint) * m * m)
    return sorted(set(out))

def lattices_of_index(n):
    for a in range(1, n + 1):
        if n % a == 0:
            c = n // a
            for b in range(a):
                yield ((a, 0), (b, c))

def canonical_lattice(basis):
    best = None
    for M in D6:
        img = lattice_image(basis, M)
        if best is None or img < best:
            best = img
    return best

def canonical_lattices(n):
    return sorted({canonical_lattice(b) for b in lattices_of_index(n)})

class TorusProblem:

    def __init__(self, basis, orientations):
        self.basis = basis
        (self.a, _), (self.b, self.c) = basis
        self.n = self.a * self.c
        self.ntri = 2 * self.n
        self.orientations = orientations
        self.tile_size = len(orientations[0])
        self.full = (1 << self.ntri) - 1
        self._build_translation_tables()
        self._build_placements()

    def tri_id(self, X, Y):
        q, r = (X // 3, Y // 3)
        k = r // self.c
        cell = (r - k * self.c) * self.a + (q - k * self.b) % self.a
        return 2 * cell + (X % 3 - 1)

    def vec_cell(self, v):
        q, r = v
        k = r // self.c
        return (r - k * self.c) * self.a + (q - k * self.b) % self.a

    def cell_vec(self, cell):
        return (cell % self.a, cell // self.a)

    def _build_translation_tables(self):
        a, n = (self.a, self.n)
        reps = []
        for tid in range(self.ntri):
            cell, o = divmod(tid, 2)
            q, r = (cell % a, cell // a)
            reps.append((3 * q + 1 + o, 3 * r + 1 + o))
        self.tri_S = reps
        self.trans = []
        for cell in range(n):
            tq, tr = (cell % a, cell // a)
            self.trans.append([self.tri_id(X + 3 * tq, Y + 3 * tr) for X, Y in reps])

    def _build_placements(self):
        self.pl_mask, self.pl_orient, self.pl_t, self.pl_ids = ([], [], [], [])
        self.pl_S = []
        for oi, shape in enumerate(self.orientations):
            for cell in range(self.n):
                tq, tr = self.cell_vec(cell)
                S = [(x + 3 * tq, y + 3 * tr) for x, y in shape]
                ids = tuple((self.tri_id(x, y) for x, y in S))
                if len(set(ids)) < self.tile_size:
                    continue
                mask = 0
                for i in ids:
                    mask |= 1 << i
                self.pl_mask.append(mask)
                self.pl_orient.append(oi)
                self.pl_t.append((tq, tr))
                self.pl_ids.append(ids)
                self.pl_S.append(S)
        self.pl_key = [(oi, self.vec_cell(t)) for oi, t in zip(self.pl_orient, self.pl_t)]
        omap = orientation_map(self.orientations)
        self.mimg_id = []
        for oi, (tq, tr) in zip(self.pl_orient, self.pl_t):
            row = []
            for mi, M in enumerate(D6):
                o2, qa, ra = omap[oi][mi]
                Mt = mat_vec(M, (tq, tr))
                row.append((o2, qa + Mt[0], ra + Mt[1]))
            self.mimg_id.append(row)
        self.by_tri = [[] for _ in range(self.ntri)]
        for p, ids in enumerate(self.pl_ids):
            for i in ids:
                self.by_tri[i].append(p)

    def enumerate_solutions(self, callback, max_solutions):
        full = self.full
        pl_mask = self.pl_mask
        count = 0
        stop = False
        for o0 in range(len(self.orientations)):
            forced = next((p for p in range(len(pl_mask)) if self.pl_orient[p] == o0 and self.pl_t[p] == (0, 0)), None)
            if forced is None:
                continue
            allowed = [[p for p in lst if self.pl_orient[p] >= o0] for lst in self.by_tri]
            chosen = [forced]

            def rec(cov):
                nonlocal count, stop
                if cov == full:
                    count += 1
                    callback(list(chosen))
                    if count >= max_solutions:
                        stop = True
                    return
                free = ~cov & full
                low = free & -free
                for p in allowed[low.bit_length() - 1]:
                    m = pl_mask[p]
                    if m & cov:
                        continue
                    chosen.append(p)
                    rec(cov | m)
                    chosen.pop()
                    if stop:
                        return
            rec(pl_mask[forced])
            if stop:
                return (count, False)
        return (count, True)

    def _image_key(self, p, mi, t):
        oi, qa, ra = self.mimg_id[p][mi]
        return (oi, self.vec_cell((qa + t[0], ra + t[1])))

    def _is_symmetry(self, sol, mi, t, tkeys, tmasks_shift):
        for p in sol:
            if self._image_key(p, mi, t) not in tkeys:
                return False
        return True

    def analyse(self, sol):
        tkeys = {self.pl_key[p] for p in sol}
        p0 = sol[0]
        trans_vecs = []
        for tcell in range(1, self.n):
            t = self.cell_vec(tcell)
            if self._image_key(p0, IDENTITY_INDEX, t) in tkeys and self._is_symmetry(sol, IDENTITY_INDEX, t, tkeys, None):
                trans_vecs.append(t)
        basis2 = hnf([self.basis[0], self.basis[1]] + trans_vecs) if trans_vecs else self.basis
        a2, c2 = (basis2[0][0], basis2[1][1])
        elements = {IDENTITY_INDEX: (0, 0)}
        for mi, M in enumerate(D6):
            if mi == IDENTITY_INDEX or not lattice_invariant(basis2, M):
                continue
            found = None
            for tr in range(c2):
                for tq in range(a2):
                    t = (tq, tr)
                    if self._image_key(p0, mi, t) in tkeys and self._is_symmetry(sol, mi, t, tkeys, None):
                        found = t
                        break
                if found:
                    break
            if found:
                elements[mi] = found
        info = classify_group(basis2, elements)
        info['lattice'] = basis2
        info['elements'] = elements
        info['tiles_per_cell'] = len(sol) * lattice_index(basis2) // self.n
        return info

    def tile_orbits(self, sol, info):
        basis2, elements = (info['lattice'], info['elements'])
        cls = {}
        for p in sol:
            oi, t = (self.pl_orient[p], self.pl_t[p])
            cls[self.pl_key[p]] = (oi, lattice_reduce(basis2, t))
        parent = {c: c for c in set(cls.values())}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        by_key = {self.pl_key[p]: p for p in sol}
        for mi, t in elements.items():
            for p in sol:
                k2 = self._image_key(p, mi, t)
                assert k2 in by_key
                parent[find(cls[self.pl_key[p]])] = find(cls[k2])
        return len({find(c) for c in parent})

    def solution_tiles(self, sol):
        out = []
        for p in sol:
            out.append([(x // 3, y // 3, x % 3 - 1) for x, y in self.pl_S[p]])
        return out
