const { JSDOM, VirtualConsole } = require('jsdom');
const fs = require('fs'), path = require('path');
const dir = path.resolve(__dirname, '..', 'webapp');
const html = fs.readFileSync(path.join(dir, 'index.html'), 'utf8').replace(/<link[^>]*fonts.googleapis[^>]*>/g, '');
const errors = [];
const vc = new VirtualConsole();
vc.on('jsdomError', e => errors.push('jsdomError: ' + e.message));
vc.on('error', (...a) => errors.push('console.error: ' + a.join(' ')));
const dom = new JSDOM(html, { runScripts: 'dangerously', resources: 'usable', pretendToBeVisual: true,
                              url: 'file://' + path.join(dir, 'index.html'), virtualConsole: vc });
dom.window.addEventListener('error', e => errors.push('window error: ' + e.message));
dom.window.addEventListener('load', () => {
  const w = dom.window, d = w.document;
  const data = w.eval('APP_DATA');
  const hexBtns = [...d.querySelectorAll('#hex-list .hex-btn')];
  let combos = 0, polys = 0, problems = [];
  if (hexBtns.length !== data.hexiamonds.length) problems.push(`hexiamond buttons ${hexBtns.length} != ${data.hexiamonds.length}`);
  hexBtns.forEach((hb, i) => {
    hb.click();
    const gBtns = [...d.querySelectorAll('#group-list .hex-btn')];
    const expected = data.hexiamonds[i].groups.length;
    if (gBtns.length !== expected) problems.push(`${data.hexiamonds[i].name}: ${gBtns.length} group buttons != ${expected}`);
    gBtns.forEach((gb, j) => {
      gb.click();
      const t = d.getElementById('timeline');
      t.value = t.max; t.dispatchEvent(new w.Event('input'));
      const layer = d.getElementById('hex-trans-layer');
      const ps = [...layer.querySelectorAll('polygon')];
      const name = `${data.hexiamonds[i].name} / ${data.hexiamonds[i].groups[j].group}`;
      if (ps.length < data.hexiamonds[i].groups[j].images.length) problems.push(`${name}: only ${ps.length} polygons drawn`);
      for (const p of ps) if (/NaN|undefined|Infinity/.test(p.getAttribute('points') || 'NaN')) { problems.push(`${name}: bad coordinates`); break; }
      if (!d.getElementById('insight').textContent.includes(data.hexiamonds[i].groups[j].group)) problems.push(`${name}: insight text missing`);
      const legend = d.querySelectorAll('#legend .legend-item').length;
      if (legend < 1) problems.push(`${name}: empty legend`);
      polys += ps.length; combos++;
    });
  });
  d.getElementById('toggle-lattice').checked = false; d.getElementById('toggle-lattice').dispatchEvent(new w.Event('change'));
  d.getElementById('toggle-center').checked = true; d.getElementById('toggle-center').dispatchEvent(new w.Event('change'));
  d.getElementById('btn-play').click(); d.getElementById('btn-reset').click();
  console.log(`clicked ${hexBtns.length} shapes and ${combos} (shape, group) views; ${polys} tile polygons drawn at full progress`);
  const all = problems.concat(errors);
  console.log(all.length ? 'PROBLEMS:\n  ' + all.join('\n  ') : 'no JavaScript errors, every view rendered');
  process.exit(all.length ? 1 : 0);
});
