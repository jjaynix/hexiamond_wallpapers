# Wallpaper groups admitted by the twelve hexiamonds

## Definitions used

* **G is admitted** by a hexiamond when G, acting on one copy of it, generates a tiling of the plane, so G acts transitively on the tiles, under the rule `same_family`: G generates a tiling transitively AND has the same lattice family (oblique / rectangular / rhombic / hexagonal; paper Table 1) as the tiling's complete symmetry group.
* Tiles lie on the triangular grid (half-grid offsets are excluded).
* Mirror images of a tile are allowed.

## What is proved

* **Found = proved**: every row comes with an explicit tiling, re-verified by independent exact code (src/verify.py).
* **Not admitted = proved, within these definitions**: if G is transitive then (tiles per primitive cell) = |point group of G| / |stabiliser of the tile| <= 12, so only translation lattices of index <= 36 can occur; all of them were searched exhaustively (every plane group G on every such lattice, no solution cap).
* **Impossible for every hexiamond**: p4m, p4g, p4 (every edge lies in one of three directions, so no symmetry can be a 4-fold rotation).

## Coverage matrix (smallest orbit size; `-` = not admitted)

| Shape | p6m | p6 | p3m1 | p31m | p3 | cmm | pmm | pmg | pgg | p2 | cm | pm | pg | p1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Crown | - | - | - | - | - | - | - | - | 4 | 2 | 1 | - | 2 | - |
| Signpost (Pistol) | - | - | - | - | - | - | - | 4 | 4 | 2 | - | - | 2 | - |
| Butterfly | - | - | - | - | - | 1 | - | - | - | - | 1 | - | - | - |
| Crook (Club) | - | - | - | - | - | - | - | 4 | 4 | 2 | - | 2 | 2 | 1 |
| Lobster | - | - | - | - | - | - | - | 2 | 4 | 2 | 1 | - | 2 | - |
| Chevron (Bat) | - | - | - | 3 | 3 | - | - | 2 | 4 | 2 | 1 | - | 2 | - |
| Hook (Shoe) | - | - | - | - | 3 | - | - | 4 | 4 | 2 | - | - | 2 | - |
| Sphinx | - | - | - | - | - | - | - | 4 | 4 | 2 | - | - | 2 | - |
| Hexagon | 1 | 1 | 1 | 1 | 1 | - | - | - | - | - | - | - | - | - |
| Snake | - | 3 | - | - | 3 | - | - | 2 | 2 | 1 | - | 2 | 2 | 1 |
| Yacht | - | - | - | - | - | - | - | 4 | 4 | 2 | - | - | 2 | - |
| Bar (Rhomboid) | - | - | - | - | - | - | - | 2 | 2 | 1 | - | 2 | 2 | 1 |

## Per shape

### Crown

Tile symmetry: order 2 (6 orientations). 4 of the 14 possible groups admitted.

| Group | Rot. order | Mirror | Glide | Orbit size(s) | Full symmetry group of the simplest such tiling |
|---|---|---|---|---|---|
| pgg | 2 | No | Yes | 4 | pgg |
| p2 | 2 | No | No | 2 | p2 |
| cm | 1 | Yes | Yes | 1 | cm |
| pg | 1 | No | Yes | 2 | pg |

Not admitted: p6m, p6, p3m1, p31m, p3, cmm, pmm, pmg, pm, p1.

### Signpost (Pistol)

Tile symmetry: order 1 (12 orientations). 4 of the 14 possible groups admitted.

| Group | Rot. order | Mirror | Glide | Orbit size(s) | Full symmetry group of the simplest such tiling |
|---|---|---|---|---|---|
| pmg | 2 | Yes | Yes | 4 | pmg |
| pgg | 2 | No | Yes | 4 | pgg |
| p2 | 2 | No | No | 2 | p2 |
| pg | 1 | No | Yes | 2 | pg |

Not admitted: p6m, p6, p3m1, p31m, p3, cmm, pmm, cm, pm, p1.

### Butterfly

Tile symmetry: order 4 (3 orientations). 2 of the 14 possible groups admitted.

| Group | Rot. order | Mirror | Glide | Orbit size(s) | Full symmetry group of the simplest such tiling |
|---|---|---|---|---|---|
| cmm | 2 | Yes | Yes | 1 | cmm |
| cm | 1 | Yes | Yes | 1 | cmm |

Not admitted: p6m, p6, p3m1, p31m, p3, pmm, pmg, pgg, p2, pm, pg, p1.

### Crook (Club)

Tile symmetry: order 1 (12 orientations). 6 of the 14 possible groups admitted.

| Group | Rot. order | Mirror | Glide | Orbit size(s) | Full symmetry group of the simplest such tiling |
|---|---|---|---|---|---|
| pmg | 2 | Yes | Yes | 4 | pmg |
| pgg | 2 | No | Yes | 4 | pgg |
| p2 | 2 | No | No | 2 | p2 |
| pm | 1 | Yes | No | 2 | pm |
| pg | 1 | No | Yes | 2 | pg |
| p1 | 1 | No | No | 1 | p1 |

Not admitted: p6m, p6, p3m1, p31m, p3, cmm, pmm, cm.

### Lobster

Tile symmetry: order 2 (6 orientations). 5 of the 14 possible groups admitted.

| Group | Rot. order | Mirror | Glide | Orbit size(s) | Full symmetry group of the simplest such tiling |
|---|---|---|---|---|---|
| pmg | 2 | Yes | Yes | 2, 4 | pmg |
| pgg | 2 | No | Yes | 4 | pgg |
| p2 | 2 | No | No | 2 | p2 |
| cm | 1 | Yes | Yes | 1 | cm |
| pg | 1 | No | Yes | 2 | pmg |

Not admitted: p6m, p6, p3m1, p31m, p3, cmm, pmm, pm, p1.

### Chevron (Bat)

Tile symmetry: order 2 (6 orientations). 7 of the 14 possible groups admitted.

| Group | Rot. order | Mirror | Glide | Orbit size(s) | Full symmetry group of the simplest such tiling |
|---|---|---|---|---|---|
| p31m | 3 | Yes | Yes | 3 | p31m |
| p3 | 3 | No | No | 3 | p31m |
| pmg | 2 | Yes | Yes | 2, 4 | pmg |
| pgg | 2 | No | Yes | 4 | pgg |
| p2 | 2 | No | No | 2 | p2 |
| cm | 1 | Yes | Yes | 1 | cm |
| pg | 1 | No | Yes | 2 | pmg |

Not admitted: p6m, p6, p3m1, cmm, pmm, pm, p1.

### Hook (Shoe)

Tile symmetry: order 1 (12 orientations). 5 of the 14 possible groups admitted.

| Group | Rot. order | Mirror | Glide | Orbit size(s) | Full symmetry group of the simplest such tiling |
|---|---|---|---|---|---|
| p3 | 3 | No | No | 3 | p3 |
| pmg | 2 | Yes | Yes | 4 | pmg |
| pgg | 2 | No | Yes | 4 | pgg |
| p2 | 2 | No | No | 2 | p2 |
| pg | 1 | No | Yes | 2 | pg |

Not admitted: p6m, p6, p3m1, p31m, cmm, pmm, cm, pm, p1.

### Sphinx

Tile symmetry: order 1 (12 orientations). 4 of the 14 possible groups admitted.

| Group | Rot. order | Mirror | Glide | Orbit size(s) | Full symmetry group of the simplest such tiling |
|---|---|---|---|---|---|
| pmg | 2 | Yes | Yes | 4 | pmg |
| pgg | 2 | No | Yes | 4 | pgg |
| p2 | 2 | No | No | 2 | p2 |
| pg | 1 | No | Yes | 2 | pg |

Not admitted: p6m, p6, p3m1, p31m, p3, cmm, pmm, cm, pm, p1.

### Hexagon

Tile symmetry: order 12 (1 orientations). 5 of the 14 possible groups admitted.

| Group | Rot. order | Mirror | Glide | Orbit size(s) | Full symmetry group of the simplest such tiling |
|---|---|---|---|---|---|
| p6m | 6 | Yes | Yes | 1 | p6m |
| p6 | 6 | No | No | 1 | p6m |
| p3m1 | 3 | Yes | Yes | 1 | p6m |
| p31m | 3 | Yes | Yes | 1, 3 | p6m |
| p3 | 3 | No | No | 1, 3 | p6m |

Not admitted: cmm, pmm, pmg, pgg, p2, cm, pm, pg, p1.

### Snake

Tile symmetry: order 2 (6 orientations). 8 of the 14 possible groups admitted.

| Group | Rot. order | Mirror | Glide | Orbit size(s) | Full symmetry group of the simplest such tiling |
|---|---|---|---|---|---|
| p6 | 6 | No | No | 3 | p6 |
| p3 | 3 | No | No | 3 | p6 |
| pmg | 2 | Yes | Yes | 2, 4 | pmg |
| pgg | 2 | No | Yes | 2, 4 | pgg |
| p2 | 2 | No | No | 1, 2 | p2 |
| pm | 1 | Yes | No | 2 | pmg |
| pg | 1 | No | Yes | 2 | pgg |
| p1 | 1 | No | No | 1 | p2 |

Not admitted: p6m, p3m1, p31m, cmm, pmm, cm.

### Yacht

Tile symmetry: order 1 (12 orientations). 4 of the 14 possible groups admitted.

| Group | Rot. order | Mirror | Glide | Orbit size(s) | Full symmetry group of the simplest such tiling |
|---|---|---|---|---|---|
| pmg | 2 | Yes | Yes | 4 | pmg |
| pgg | 2 | No | Yes | 4 | pgg |
| p2 | 2 | No | No | 2 | p2 |
| pg | 1 | No | Yes | 2 | pg |

Not admitted: p6m, p6, p3m1, p31m, p3, cmm, pmm, cm, pm, p1.

### Bar (Rhomboid)

Tile symmetry: order 2 (6 orientations). 6 of the 14 possible groups admitted.

| Group | Rot. order | Mirror | Glide | Orbit size(s) | Full symmetry group of the simplest such tiling |
|---|---|---|---|---|---|
| pmg | 2 | Yes | Yes | 2, 4 | pmg |
| pgg | 2 | No | Yes | 2, 4 | pgg |
| p2 | 2 | No | No | 1, 2 | p2 |
| pm | 1 | Yes | No | 2 | pmg |
| pg | 1 | No | Yes | 2 | pg |
| p1 | 1 | No | No | 1 | p2 |

Not admitted: p6m, p6, p3m1, p31m, p3, cmm, pmm, cm.

Orbit size = tiles per primitive cell of G = |point group of G| / |stabiliser of the tile in G|. Mirror / Glide describe G itself (Glide = a glide reflection whose axis is not a mirror line).

## Supplementary: complete symmetry group of every tiling found (including non-isohedral)

Profiles: m=1, K=18. Exhaustive up to those bounds only.

| Shape | p6m | p6 | p3m1 | p31m | p3 | cmm | pmm | pmg | pgg | p2 | cm | pm | pg | p1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Crown | - | - | - | - | - | - | - | - | **4** | **2** | **1** | - | **2** | 3 |
| Signpost (Pistol) | - | 12 | - | - | - | - | - | **4** | **4** | **2** | 4 | 12 | **2** | 2 |
| Butterfly | - | - | - | - | - | **1** | - | - | - | - | - | - | - | - |
| Crook (Club) | - | 12 | - | - | 9 | - | - | **4** | **4** | **2** | - | **2** | **2** | **1** |
| Lobster | - | - | - | - | - | - | - | **2** | **4** | **2** | **1** | 4 | 4 | 3 |
| Chevron (Bat) | - | - | - | **3** | - | - | - | **2** | **4** | **2** | **1** | 4 | 4 | 3 |
| Hook (Shoe) | - | - | - | - | **3** | - | - | **4** | **4** | **2** | 4 | 12 | **2** | 5 |
| Sphinx | - | - | - | - | - | - | - | **4** | **4** | **2** | 4 | 8 | **2** | 4 |
| Hexagon | **1** | - | - | - | - | - | - | - | - | - | - | - | - | - |
| Snake | - | **3** | - | - | 9 | - | - | **2** | **2** | **1** | - | 6 | 4 | 4 |
| Yacht | - | 12 | - | - | - | - | - | **4** | **4** | **2** | 4 | 4 | **2** | 2 |
| Bar (Rhomboid) | - | 9 | - | - | - | - | - | **2** | **2** | **1** | 8 | 4 | **2** | 2 |

Cells = fewest tiles per primitive cell of a tiling whose FULL symmetry group is that type; bold = an isohedral tiling with that full group exists.
