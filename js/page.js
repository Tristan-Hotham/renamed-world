/* The renamed world: the map (The Inked World with every official renaming of a place, coloured by wave), a decade
 * slider, wave toggles, search by old or new name, and popups with each place's name history.
 * Dr Tristan Hotham, Independent researcher, 2026. MIT licence. */
(function () {
  'use strict';
  const qs = new URLSearchParams(location.search);
  const BASE = window.INKBASE;
  const V = '?v=20261108';
  const ENGINE = ['js/curated.js', 'js/ink-palette.js', 'js/ink-icons.js', 'js/ink-houses.js', 'js/ink-map.js', 'js/ink-extras.js'];
  const esc = s => String(s ?? '').replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const norm = s => String(s).normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase();
  const small = matchMedia('(max-width:800px)').matches;
  let map = null, D = null, on = null, dec = 2030, cum = false;

  document.getElementById('theme').addEventListener('click', () => {
    const r = document.documentElement, dark = r.dataset.theme ? r.dataset.theme === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
    r.dataset.theme = dark ? 'light' : 'dark';
  });
  const ct = document.getElementById('cartouche');
  const fold = f => ct.classList.toggle('folded', f);
  if (small) fold(true);
  document.getElementById('ctToggle').addEventListener('click', () => fold(!ct.classList.contains('folded')));
  document.getElementById('ctFold').addEventListener('click', () => fold(true));
  function loadScripts(list) {
    return list.reduce((p, src) => p.then(() => new Promise((res, rej) => {
      const el = document.createElement('script'); el.src = BASE + src + V; el.onload = res; el.onerror = () => rej(new Error('script ' + src)); document.head.appendChild(el);
    })), Promise.resolve());
  }

  // ---------------- the most renamed places table
  (function () {
    const t = document.getElementById('mostT'); if (!t || !window.MOST) return;
    t.innerHTML = '<tr><th>Place</th><th>Country</th><th class="r">Renamings</th><th>Names in order</th></tr>' + window.MOST.map(r =>
      `<tr><td>${esc(r[0])}</td><td>${esc(r[1])}</td><td class="r">${r[2]}</td><td>${esc(r[3])}</td></tr>`).join('');
  })();

  // ---------------- filters
  function filt() {
    const f = ['all', ['in', ['get', 'w'], ['literal', on.map((v, i) => v ? i : -1).filter(i => i >= 0)]]];
    if (dec < 2030) f.push(cum ? ['<', ['get', 'y'], dec + 10] : ['all', ['>=', ['get', 'y'], dec], ['<', ['get', 'y'], dec + 10]]);
    else f.push(['>=', ['get', 'y'], 0]);
    return f;
  }
  function apply() {
    if (!map || !map.getLayer('ev')) return;
    const f = filt();
    map.setFilter('ev', f); map.setFilter('evl', f);
    const cnt = new Array(D.waves.length).fill(0); let n = 0;
    for (const e of D.events) { const y = e[1]; const inT = dec >= 2030 || (cum ? y < dec + 10 : (y >= dec && y < dec + 10)); if (inT) { cnt[e[2]]++; if (on[e[2]]) n++; } }
    document.querySelectorAll('.wv').forEach((el, i) => { el.querySelector('.c').textContent = cnt[i].toLocaleString('en-GB'); el.classList.toggle('off', !on[i]); el.setAttribute('aria-pressed', on[i]); });
    (document.getElementById('cnt') || {}).textContent = n.toLocaleString('en-GB') + ' renamings shown';
    document.getElementById('yr').textContent = dec >= 2030 ? 'All years' : (cum ? 'to ' + (dec + 9) : dec + 's');
  }
  function setupKey() {
    const box = document.getElementById('wv');
    box.innerHTML = D.waves.map((w, i) => `<div class="wv" role="button" tabindex="0" aria-pressed="true" data-i="${i}"><i style="background:${D.wave_col[i]}"></i>${esc(D.wave_name[i])}<span class="c"></span></div>`).join('');
    box.querySelectorAll('.wv').forEach(el => {
      const t = () => { const i = +el.dataset.i; on[i] = !on[i]; apply(); };
      el.addEventListener('click', t); el.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); t(); } });
    });
    const s = document.getElementById('dec');
    s.addEventListener('input', () => { dec = +s.value; apply(); });
    document.getElementById('cum').addEventListener('change', e => { cum = e.target.checked; apply(); });
    let timer = null;
    const play = document.getElementById('play');
    play.addEventListener('click', () => {
      if (timer) { clearInterval(timer); timer = null; play.textContent = '▶'; return; }
      play.textContent = '❚❚'; if (dec >= 2020) dec = 1790;
      timer = setInterval(() => { dec += 10; if (dec > 2020) { clearInterval(timer); timer = null; play.textContent = '▶'; dec = 2030; } s.value = dec; apply(); }, 900);
    });
  }

  // ---------------- popups
  function popup(pi, ll) {
    const p = D.places[pi];
    const evs = D.events.filter(e => e[0] === pi).sort((a, b) => a[1] - b[1]);
    let h = `<b class="t">${esc(p[1])}</b><div class="nt">${esc(p[5] || p[4])} · <a href="https://www.wikidata.org/wiki/${esc(p[0])}" target="_blank" rel="noopener">Wikidata ${esc(p[0])}</a></div>`;
    h += '<ul class="hist">' + evs.map(e => `<li class="ev"><span class="yr">${e[1]}</span> ${esc(e[3])} → <b>${esc(e[4])}</b><br><span style="color:${D.wave_col[e[2]]}">●</span> ${esc(D.wave_name[e[2]])}${e[5] ? ' · back to an earlier name' : ''}</li>`).join('') + '</ul>';
    if (p[6] && p[6].length) {
      h += `<div class="nt">All official names recorded, in the language of the renamings:</div><ul class="hist">` +
        p[6].map(n => `<li>${esc(n[0])} <span class="yr">${n[1] != null ? n[1] : '?'} to ${n[2] != null ? n[2] : 'now'}</span></li>`).join('') + '</ul>';
    }
    h += '<div class="nt">Official name (P1448) with its dates, from Wikidata. Wave: my classification.</div>';
    new maplibregl.Popup({ maxWidth: '320px' }).setLngLat(ll || [p[2], p[3]]).setHTML(h).addTo(map);
  }

  // ---------------- search
  function setupSearch() {
    const q = document.getElementById('q'), sug = document.getElementById('sug');
    const idx = [];
    D.places.forEach((p, i) => { const names = new Set([p[1]].concat((p[6] || []).map(n => n[0]))); D.events.forEach(e => { if (e[0] === i) { names.add(e[3]); names.add(e[4]); } }); names.forEach(n => idx.push([norm(n), n, i])); });
    let items = [], k = -1;
    const show = () => {
      const v = norm(q.value.trim()); sug.innerHTML = ''; k = -1;
      if (v.length < 2) { sug.style.display = 'none'; return; }
      const seen = new Set(), st = [], inn = [];
      for (const [n, raw, i] of idx) { if (seen.has(i)) continue; if (n.startsWith(v)) { st.push([raw, i]); seen.add(i); } else if (v.length > 3 && n.includes(v)) { inn.push([raw, i]); seen.add(i); } if (st.length > 14) break; }
      items = st.concat(inn).slice(0, 12);
      items.forEach(([raw, i], j) => { const p = D.places[i]; const li = document.createElement('li'); li.setAttribute('role', 'option');
        li.innerHTML = `${esc(raw)} <span>${raw !== p[1] ? 'now ' + esc(p[1]) + ' · ' : ''}${esc(p[5] || p[4])}</span>`;
        li.addEventListener('mousedown', e => { e.preventDefault(); pick(j); }); sug.appendChild(li); });
      sug.style.display = items.length ? 'block' : 'none';
    };
    const pick = j => { const it = items[j]; if (!it) return; const p = D.places[it[1]]; q.value = it[0]; sug.style.display = 'none'; fold(true);
      map.flyTo({ center: [p[2], p[3]], zoom: Math.max(map.getZoom(), 8), duration: 1400 }); map.once('moveend', () => popup(it[1])); };
    q.addEventListener('input', show);
    q.addEventListener('keydown', e => {
      const lis = [...sug.children];
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') { e.preventDefault(); k = Math.max(0, Math.min(lis.length - 1, k + (e.key === 'ArrowDown' ? 1 : -1))); lis.forEach((l, i) => l.setAttribute('aria-selected', i === k)); }
      else if (e.key === 'Enter') { e.preventDefault(); if (!items.length) show(); pick(k < 0 ? 0 : k); }
      else if (e.key === 'Escape') sug.style.display = 'none';
    });
    q.addEventListener('blur', () => setTimeout(() => sug.style.display = 'none', 150));
  }

  // ---------------- layers
  function setupLayers() {
    const feats = D.events.map((e, j) => { const p = D.places[e[0]]; return { type: 'Feature', id: j, properties: { pi: e[0], y: e[1], w: e[2], n: e[4] }, geometry: { type: 'Point', coordinates: [p[2], p[3]] } }; });
    map.addSource('ev', { type: 'geojson', data: { type: 'FeatureCollection', features: feats }, attribution: 'Renamings: Wikidata (CC0), my classification' });
    const col = ['match', ['get', 'w']]; D.wave_col.forEach((c, i) => col.push(i, c)); col.push('#888');
    map.addLayer({ id: 'ev', type: 'circle', source: 'ev', paint: { 'circle-color': col, 'circle-stroke-color': '#2B2119',
      'circle-stroke-width': ['interpolate', ['linear'], ['zoom'], 2, 0.2, 8, 0.8], 'circle-radius': ['interpolate', ['linear'], ['zoom'], 1, 1.6, 4, 2.6, 8, 5, 12, 7], 'circle-opacity': 0.9 } });
    map.addLayer({ id: 'evl', type: 'symbol', source: 'ev', minzoom: 7.5, layout: { 'text-field': ['get', 'n'], 'text-font': ['Ink Italic'], 'text-size': 13, 'text-offset': [0, 0.9], 'text-anchor': 'top', 'text-optional': true },
      paint: { 'text-color': '#2B2119', 'text-halo-color': 'rgba(251,245,228,0.95)', 'text-halo-width': 1.6 } });
    map.on('click', 'ev', e => { const f = e.features[0]; if (f) popup(f.properties.pi, e.lngLat); });
    map.on('mouseenter', 'ev', () => map.getCanvas().style.cursor = 'pointer');
    map.on('mouseleave', 'ev', () => map.getCanvas().style.cursor = '');
    const lp = document.getElementById('lp'), btn = document.getElementById('lyrBtn');
    btn.addEventListener('click', e => { e.stopPropagation(); const o = lp.classList.toggle('open'); btn.setAttribute('aria-expanded', o); });
    document.addEventListener('click', e => { if (!lp.contains(e.target) && e.target !== btn) { lp.classList.remove('open'); btn.setAttribute('aria-expanded', false); } });
    const vis = (id, v) => map.setLayoutProperty(id, 'visibility', v ? 'visible' : 'none');
    document.getElementById('lyEv').addEventListener('change', e => { vis('ev', e.target.checked); vis('evl', e.target.checked && document.getElementById('lyLab').checked); });
    document.getElementById('lyLab').addEventListener('change', e => vis('evl', e.target.checked && document.getElementById('lyEv').checked));
    const boxes = [...lp.querySelectorAll('input[data-g]')], modern = document.getElementById('modern');
    const base = () => {
      const m = modern.checked;
      boxes.forEach(b => { const g = b.dataset.g; const inkOnly = ['mountains', 'forests', 'sea', 'tint'].includes(g); try { InkMap.setGroup(map, g, b.checked && !(m && inkOnly)); } catch (e) { } });
      try { InkMap.setGroup(map, 'paper', !m); InkMap.setGroup(map, 'modern', m); InkMap.setGroup(map, 'coast', !m); if (m) InkMap.setGroup(map, 'roads', false); } catch (e) { }
    };
    boxes.forEach(b => b.addEventListener('change', base)); modern.addEventListener('change', base); base();
  }

  // ---------------- start
  fetch('data/places.json').then(r => r.json()).then(j => {
    D = j; on = D.waves.map(() => true);
    setupKey();
    if (small) { const k = document.getElementById('keys'); const lp = document.getElementById('lp'); lp.insertBefore(k.firstElementChild, lp.children[1]); k.remove(); }
    const opts = { base: BASE, winter: false };
    if (qs.get('tj')) opts.tilejson = qs.get('tj');
    if (qs.get('dem')) opts.dem = qs.get('dem');
    if (qs.get('demmax')) opts.demMax = +qs.get('demmax');
    const at = (qs.get('at') || '').split(',').map(Number);
    opts.mapOptions = at.length === 3 && at.every(isFinite) ? { center: [at[1], at[0]], zoom: at[2] } : { center: small ? [40, 48] : [45, 47], zoom: small ? 1.9 : 2.7 };
    return loadScripts(ENGINE).then(() => InkMap.create('map', opts));
  }).then(m => {
    map = m; m.__inkWinter = false; window.__map = m;
    const n = document.getElementById('nojs'); if (n) n.remove();
    m.addControl(new maplibregl.NavigationControl({ showCompass: false }), 'bottom-right');
    const foldAt = () => document.querySelectorAll('.maplibregl-ctrl-attrib.maplibregl-compact').forEach(at => { at.classList.remove('maplibregl-compact-show'); at.removeAttribute('open'); });
    m.once('idle', foldAt); setTimeout(foldAt, 1500);
    try { ['heritage', 'flight', 'animals', 'farms', 'towns'].forEach(g => InkMap.setGroup(m, g, false)); } catch (e) { }
    setupLayers(); setupSearch();
    if (qs.get('decade')) { dec = +qs.get('decade'); document.getElementById('dec').value = dec; }
    apply();
    if (qs.get('place')) { const i = D.places.findIndex(p => p[0] === qs.get('place')); if (i >= 0) { map.jumpTo({ center: [D.places[i][2], D.places[i][3]], zoom: Math.max(map.getZoom(), 7) }); popup(i); } }
    document.getElementById('mapWrap').addEventListener('pointerdown', e => { if (e.target.closest && e.target.closest('.cartouche,.ov,.lp,.tl,.keys,.mfs-btn,.maplibregl-ctrl')) return; fold(true); }, { capture: true, passive: true, once: true });
  }).catch(e => { console.error(e); const n = document.getElementById('nojs'); if (n) n.textContent = 'The map could not load: ' + e.message; });
})();
