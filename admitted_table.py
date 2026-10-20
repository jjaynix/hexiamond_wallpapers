import json
from src import config
from src.groups import GROUP_ORDER_INDEX, POSSIBLE_GROUP_NAMES

PAPER_TABLE4 = {
    'Crown': ['cm'],
    'Signpost (Pistol)': ['p2'],
    'Butterfly': ['cmm'],
    'Crook (Club)': ['p2', 'p1'],
    'Lobster': ['p2', 'cm'],
    'Chevron (Bat)': ['p31m', 'p2', 'cm'],
    'Hook (Shoe)': ['p3', 'p2'],
    'Sphinx': ['p2'],
    'Hexagon': ['p6m'],
    'Snake': ['p6', 'p2'],
    'Yacht': ['p2', 'cm'],
    'Bar (Rhomboid)': ['p2'],
}

OUT = 'artifacts/admitted_groups_table.md'

def format_table(headers, rows):
    cols = len(headers)
    widths = [len(h) for h in headers]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))
    header_str = '| ' + ' | '.join(str(h).ljust(widths[i]) for i, h in enumerate(headers)) + ' |'
    sep_str = '|-' + '-|-'.join('-' * widths[i] for i in range(cols)) + '-|'
    row_strs = ['| ' + ' | '.join(str(val).ljust(widths[i]) for i, val in enumerate(row)) + ' |' for row in rows]
    return '\n'.join([header_str, sep_str] + row_strs)

def main():
    study = json.load(open(config.RESULTS_PATH))
    t1_headers = ['Shape', 'Group', 'Rot. order', 'Mirror', 'Glide', 'Orbit size(s)']
    t1_rows = []
    t2_headers = ['Shape', 'In paper and admitted', 'In paper, NOT admitted', 'Admitted, missing from paper']
    t2_rows = []
    t3_headers = ['Shape', 'any transitive subgroup', 'same lattice family (reported)', 'full symmetry group only']
    t3_rows = []
    for e in study['shapes']:
        adm = e['admitted']
        for g in sorted(adm, key=lambda n: GROUP_ORDER_INDEX[n]):
            r = adm[g]['rep']
            t1_rows.append([
                e['name'],
                g,
                r['rotation_order'],
                'Yes' if r['mirror'] else 'No',
                'Yes' if r['glide'] else 'No',
                ', '.join(map(str, adm[g]['orbit_sizes'])),
            ])
        paper = PAPER_TABLE4[e['name']]
        extra = [g for g in sorted(adm, key=lambda n: GROUP_ORDER_INDEX[n]) if g not in paper]
        t2_rows.append([
            e['name'],
            ', '.join(g for g in paper if g in adm) or '-',
            ', '.join(g for g in paper if g not in adm) or '-',
            ', '.join(extra) or '-',
        ])
        r_rules = e['admitted_by_rule']
        t3_rows.append([
            e['name'],
            len(r_rules['any_subgroup']),
            len(r_rules['same_family']),
            len(r_rules['full_group']),
        ])
    t1_str = format_table(t1_headers, t1_rows)
    t2_str = format_table(t2_headers, t2_rows)
    t3_str = format_table(t3_headers, t3_rows)
    content = (
        '# Admitted wallpaper groups per hexiamond\n\n'
        f'Rule used: `{config.ADMISSION_RULE}`.\n\n'
        + t1_str + '\n\n'
        + '## Comparison with paper Table 4\n\n'
        + t2_str + '\n\n'
        + '## Number of admitted groups under each rule\n\n'
        + t3_str + '\n'
    )
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(content)
    print(t2_str)
    print('\nwrote', OUT)

if __name__ == '__main__':
    main()
