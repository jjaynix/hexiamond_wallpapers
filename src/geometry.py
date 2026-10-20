from math import sqrt
SQRT3_2 = sqrt(3) / 2

def axial_to_cartesian(q, r, scale=1):
    return ((q + r / 2) / scale, r * SQRT3_2 / scale)

def triangle_vertices(q, r, o):
    if o == 0:
        return [(q, r), (q + 1, r), (q, r + 1)]
    return [(q + 1, r), (q + 1, r + 1), (q, r + 1)]

def outline_axial(triangles):
    edges = set()
    for q, r, o in triangles:
        v = triangle_vertices(q, r, o)
        for i in range(3):
            edges.add((v[i], v[(i + 1) % 3]))
    boundary = {(a, b) for a, b in edges if (b, a) not in edges}
    nxt = {}
    for a, b in boundary:
        if a in nxt:
            raise ValueError('tile boundary touches itself at a vertex')
        nxt[a] = b
    start = min(nxt)
    loop, cur = ([start], nxt[start])
    while cur != start:
        loop.append(cur)
        cur = nxt[cur]
    if len(loop) != len(nxt):
        raise ValueError('tile has more than one boundary component (a hole)')
    out = []
    n = len(loop)
    for i in range(n):
        p0, p1, p2 = (loop[i - 1], loop[i], loop[(i + 1) % n])
        d1 = (p1[0] - p0[0], p1[1] - p0[1])
        d2 = (p2[0] - p1[0], p2[1] - p1[1])
        if d1[0] * d2[1] - d1[1] * d2[0] != 0:
            out.append(p1)
    return out

def polygon_points(triangles, scale=1):
    return [list(axial_to_cartesian(q, r, scale)) for q, r in outline_axial(triangles)]

def polygon_area(points):
    s = 0.0
    for i in range(len(points)):
        x0, y0 = points[i - 1]
        x1, y1 = points[i]
        s += x0 * y1 - x1 * y0
    return abs(s) / 2

def centroid_axial(triangles):
    sx = sy = 0.0
    for q, r, o in triangles:
        v = triangle_vertices(q, r, o)
        sx += sum((p[0] for p in v)) / 3
        sy += sum((p[1] for p in v)) / 3
    n = len(triangles)
    return (sx / n, sy / n)
