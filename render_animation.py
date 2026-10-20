import json
import os
import sys
import numpy as np
from src import config
from src.animate import animate_tiling
from src.groups import GROUP_ORDER_INDEX
from src.shapes import SHAPE_IDS
from export_app_data import build_group_entry
shape_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 8
group = sys.argv[2] if len(sys.argv) > 2 and (not sys.argv[2].isdigit()) else None
rings = int(sys.argv[-1]) if len(sys.argv) > 1 and sys.argv[-1].isdigit() and (len(sys.argv) > 2) else 3
with open(config.RESULTS_PATH) as f:
    shape = json.load(f)['shapes'][shape_idx]
if not shape['admitted']:
    sys.exit(f"{shape['name']}: no wallpaper group found")
name = group or min(shape['admitted'], key=lambda g: GROUP_ORDER_INDEX[g])
if name not in shape['admitted']:
    sys.exit(f"{shape['name']}: {name} not found; available: {', '.join(shape['admitted'])}")
entry = build_group_entry(name, shape['admitted'][name]['rep'], shape['admitted'][name]['orbit_sizes'])
os.makedirs('artifacts/animations', exist_ok=True)
out = f'artifacts/animations/{SHAPE_IDS[shape_idx]}_{name}.gif'
animate_tiling([np.array(im['polygon']) for im in entry['images']], entry['t1'], entry['t2'], rings=rings, output_path=out)
print(f"{shape['name']}: {name}, {entry['orbit_size']} tile(s) per cell -> {out}")
