# Hexiamond Wallpaper Group Patterns

Computational search and visualization of wallpaper symmetry groups admitted by the 12 hexiamonds on a triangular grid.

## Overview

A hexiamond is a polyiamond composed of 6 equilateral triangles. This project computes the valid wallpaper groups formed by tiling copies of each hexiamond across the plane, analyzes their symmetry elements (rotations, mirrors, glide reflections), and provides an interactive web visualizer.

## Features

- **Exact Symmetry Classification**: Enumerates periodic tilings and classifies their wallpaper symmetry groups using integer and rational arithmetic.
- **Independent Verification**: Re-verifies tilings and group structures in the plane without torus artifacts.
- **Interactive Visualizer**: An interactive web viewer displaying tilings, rotation centers, and triangular grid overlays.

## Project Structure

```
├── admitted_table.py       # Generates formatted markdown tables of admitted groups
├── export_app_data.py      # Exports computed tilings to webapp/data.js
├── run_full_study.py       # Runs the complete enumeration and classification search
├── src/                    # Core geometry, lattice, tiling, and classification modules
├── tests/                  # Verification and test suites
└── webapp/                 # Interactive visualizer (HTML, CSS, JS)
```

## Getting Started

### 1. Run the Study

To execute the wallpaper group search across all 12 hexiamonds:

```bash
python run_full_study.py
```

### 2. Generate Admitted Groups Table

To generate the formatted comparison table:

```bash
python admitted_table.py
```

Outputs are saved in the `artifacts/` directory.

### 3. Launch the Web Visualizer

Open `webapp/index.html` in any modern web browser to interactively explore each hexiamond's tiling patterns, rotation centers, and symmetries.
