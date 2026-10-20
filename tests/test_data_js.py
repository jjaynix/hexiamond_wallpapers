from tools.check_data_js import check_row
import json

def test_every_row_of_the_shipped_data_is_an_exact_tiling_with_the_claimed_group():
    s = open('webapp/data.js').read()
    data = json.loads(s[s.index('{'):].rstrip().rstrip(';'))
    rows = 0
    for h in data['hexiamonds']:
        for g in h['groups']:
            r = check_row(g)
            assert r['ok'] and r['group'] == g['group'], (h['name'], g['group'], r)
            rows += 1
    study = json.load(open('artifacts/study_results.json'))
    assert rows == sum((len(e['admitted']) for e in study['shapes']))
