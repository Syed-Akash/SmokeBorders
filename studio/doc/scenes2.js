// Smoke & Borders film shots, part 2 (owner, 14 Nov 2026: "every episode its own unique scenes, like real documentaries and
// movies; the map only where it's necessary"). Four kinds of shot, all described per beat in the story JSON:
//   photo  a real archival photo in 2.5-D (smoke/photo.py made a background + cut-out subject): the camera drifts, the subject
//          moves against the background, grain, grade, optional smoke/fog/dust/embers/rain, a small archive caption
//   doc    a document filling the frame: telegram, letter, order, newspaper, treaty; lines type out, a stamp lands
//   card   the minute-by-minute card: a big time ("11:40 P.M.") over a place and date, a ticking second hand
//   set    an illustrated scene composed from parts: sky (time of day, weather), land/sea, hills, forest, coast, town, fort,
//          camp, ships, soldiers, crowd, cannons, farm, animals, flags, fires, people, interior rooms; so every episode
//          builds its own scenes instead of reusing a fixed set
(function (G) {
  const K = G.SCENE_KIT, { clamp, lerp, io, o3, rnd, glow, rain, smoke, dust, figure, cam, layer, off, TYPE, SERIF, BODY, BAR } = K, SH = G.SCENE_SHOTS;
  const IMG = {}; G.SCENE_IMG = IMG;
  // every image the timeline needs is loaded before the first frame (doc.html awaits this in init)
  G.SCENE_PRELOAD = async (events, story) => {
    const want = new Set();
    for (const e of events) if (e.k === 'scene') {
      if (e.shot === 'photo' && e.img) { want.add(`photos/${story}/${e.img}.jpg`); want.add(`photos/${story}/${e.img}-fg.png`) }
      for (const p of (e.people || [])) if (p.photo) want.add(`photos/${story}/${p.photo}-fg.png`)
      for (const part of (e.parts || [])) for (const q of (part.list || [])) if (q.photo) want.add(`photos/${story}/${q.photo}-fg.png`)   // photo cut-outs standing in a set
    }
    await Promise.all([...want].map(src => new Promise(ok => { const im = new Image(); im.onload = () => { IMG[src] = im; ok() }; im.onerror = () => ok(); im.src = src })));
  };
  let NOISE = null;
  function grain(c, W, H, a = .07) {
    if (!NOISE) { NOISE = document.createElement('canvas'); NOISE.width = NOISE.height = 256; const k = NOISE.getContext('2d'), d = k.createImageData(256, 256);
      for (let i = 0; i < d.data.length; i += 4) { const v = Math.random() * 255; d.data[i] = d.data[i + 1] = d.data[i + 2] = v; d.data[i + 3] = 255 } k.putImageData(d, 0, 0) }
    c.save(); c.globalAlpha = a; c.globalCompositeOperation = 'overlay'; const ox = (Math.random() * 256) | 0, oy = (Math.random() * 256) | 0;
    for (let x = -ox; x < W; x += 256) for (let y = -oy; y < H; y += 256) c.drawImage(NOISE, x, y); c.restore() }
  function vignette(c, W, H, a = .6) { const g = c.createRadialGradient(W / 2, H / 2, H * .35, W / 2, H / 2, W * .75); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, `rgba(0,0,0,${a})`); c.fillStyle = g; c.fillRect(0, 0, W, H) }
  function fx(c, W, H, u, list) {
    for (const f of [].concat(list || [])) {
      if (f === 'smoke') for (let i = 0; i < 6; i++) smoke(c, W * (.1 + i * .17), H * 1.02, u + i, H * .9, .07, i);
      else if (f === 'fog') { for (let i = 0; i < 7; i++) { const x = ((rnd(i) * W * 1.6 + u * (12 + i * 4)) % (W * 1.6)) - W * .3, y = H * (.45 + rnd(i + 3) * .45), r = 300 + rnd(i + 5) * 300, g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, 'rgba(210,215,220,.22)'); g.addColorStop(1, 'rgba(210,215,220,0)'); c.fillStyle = g; c.fillRect(x - r, y - r, 2 * r, 2 * r) } }
      else if (f === 'dust') dust(c, W / 2, H / 2, W * .6, H * .45, u, 90);
      else if (f === 'embers') { c.save(); c.globalCompositeOperation = 'lighter'; for (let i = 0; i < 70; i++) { const x = (rnd(i) * W + Math.sin(u + i) * 30), y = H - ((u * (40 + rnd(i + 1) * 60) + rnd(i + 2) * H) % H); c.fillStyle = `rgba(255,${140 + rnd(i) * 80 | 0},60,${.4 + rnd(i + 4) * .5})`; c.beginPath(); c.arc(x, y, 1 + rnd(i + 3) * 2.5, 0, 7); c.fill() } c.restore() }
      else if (f === 'rain') rain(c, W, H, u, 380, .22, .16);
      else if (f === 'snow') { c.fillStyle = 'rgba(255,255,255,.8)'; for (let i = 0; i < 160; i++) { const x = (rnd(i) * W + Math.sin(u * .8 + i) * 30), y = (rnd(i + 1) * H + u * (30 + rnd(i + 2) * 40)) % H; c.beginPath(); c.arc(x, y, 1 + rnd(i + 3) * 2, 0, 7); c.fill() } }
      else if (f === 'light') { c.save(); c.globalCompositeOperation = 'screen'; const g = c.createLinearGradient(0, 0, W, H); g.addColorStop(0, 'rgba(255,200,140,.25)'); g.addColorStop(.4, 'rgba(255,200,140,0)'); c.fillStyle = g; c.fillRect(0, 0, W, H); c.restore() }
    } }
  function tone(c, W, H, t) {   // archival grade: sepia (default), bw, warm, cold
    if (t === 'none') return; c.save(); c.globalCompositeOperation = 'color'; c.fillStyle = t === 'bw' ? '#808080' : t === 'cold' ? 'rgba(90,110,140,.55)' : t === 'warm' ? 'rgba(170,110,60,.45)' : 'rgba(150,110,70,.65)'; c.fillRect(0, 0, W, H); c.restore() }
  function caption(c, W, H, txt, u) { if (!txt) return; c.save(); c.globalAlpha = clamp((u - .6) / .6) * .85; c.font = `400 24px ${TYPE}`; c.fillStyle = '#e9dcc0'; c.shadowColor = '#000'; c.shadowBlur = 8; c.textAlign = 'right'; c.fillText(txt, W - 60, H - BAR - 24); c.restore() }
  const cover = (im, W, H) => { const s = Math.max(W / im.width, H / im.height); return [im.width * s, im.height * s] };

  // ---------- photo: 2.5-D archival photo ----------
  SH['photo'] = (c, W, H, S, t, env) => {
    const u = S.u, d = S.dur || 8, k = io(clamp(u / d)), st = env.story, bg = IMG[`photos/${st}/${S.img}.jpg`], fg = IMG[`photos/${st}/${S.img}-fg.png`];
    c.fillStyle = '#0b0906'; c.fillRect(0, 0, W, H);
    if (!bg && S.fallback && SH[S.fallback.shot]) { SH[S.fallback.shot](c, W, H, Object.assign({}, S.fallback, { u: S.u, dur: S.dur }), t, env); return }   // the archival photo could not be fetched: its stand-in shot plays instead
    if (!bg) { c.fillStyle = '#e33'; c.font = `40px ${BODY}`; c.fillText('missing photo: ' + S.img, 80, 200); return }
    const mv = S.move || 'in', z0 = mv === 'out' ? 1.16 : 1.04, z1 = mv === 'out' ? 1.04 : 1.16, z = lerp(z0, z1, k), [bw, bh] = cover(bg, W, H),
      pan = S.pan || [mv === 'left' ? 60 : mv === 'right' ? -60 : 0, 0], fx0 = S.focus ? (S.focus[0] - .5) * bw * .3 : 0, fy0 = S.focus ? (S.focus[1] - .5) * bh * .3 : 0;
    const draw = (im, depth) => { const zz = 1 + (z - 1) * depth; c.save(); c.translate(W / 2 - fx0 * k * depth + pan[0] * (k - .5) * depth, H / 2 - fy0 * k * depth + pan[1] * (k - .5) * depth); c.scale(zz, zz); c.drawImage(im, -bw / 2, -bh / 2, bw, bh); c.restore() };
    draw(bg, 1); if (S.fx && [].concat(S.fx).includes('fog')) fx(c, W, H, u, 'fog');
    if (fg) { c.save(); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 30; draw(fg, 1.9); c.restore() }
    tone(c, W, H, S.tone || 'sepia');
    c.save(); c.globalCompositeOperation = 'soft-light'; c.fillStyle = 'rgba(255,190,120,.18)'; c.fillRect(0, 0, W, H); c.restore();
    fx(c, W, H, u, [].concat(S.fx || []).filter(f => f !== 'fog')); vignette(c, W, H, .7); grain(c, W, H, .09); caption(c, W, H, S.caption, u);
  };

  // ---------- doc: a document filling the frame ----------
  SH['doc'] = (c, W, H, S, t) => {
    const u = S.u, C = cam(Object.assign({ push: .06 }, S), W, H), kind = S.kind || 'letter';
    c.fillStyle = '#20150d'; c.fillRect(0, 0, W, H);
    layer(c, C, W, H, 1, () => {
      for (let i = 0; i < 40; i++) { c.strokeStyle = `rgba(10,5,2,${.2 + rnd(i) * .2})`; c.lineWidth = 2 + rnd(i + 1) * 5; c.beginPath(); c.moveTo(-200, i * 34); c.lineTo(W + 200, i * 34 + Math.sin(i) * 9); c.stroke() }
      c.save(); c.translate(W / 2, H / 2 + 10); c.rotate(S.tilt != null ? S.tilt : -.02);
      const pw = kind === 'newspaper' ? 1100 : 900, ph = 900, paper = kind === 'telegram' ? '#e8d9a8' : kind === 'newspaper' ? '#dcd3bd' : '#ece2c8';
      c.fillStyle = 'rgba(0,0,0,.5)'; c.fillRect(-pw / 2 + 20, -ph / 2 + 24, pw, ph); c.fillStyle = paper; c.fillRect(-pw / 2, -ph / 2, pw, ph);
      const gg = c.createRadialGradient(0, 0, 100, 0, 0, pw * .8); gg.addColorStop(0, 'rgba(120,80,30,0)'); gg.addColorStop(1, 'rgba(120,80,30,.35)'); c.fillStyle = gg; c.fillRect(-pw / 2, -ph / 2, pw, ph);
      c.fillStyle = '#2a1d12'; c.textAlign = 'center'; let y = -ph / 2 + 90;
      if (kind === 'newspaper') { c.font = `900 64px ${SERIF}`; c.fillText(S.paper || 'THE DAILY NEWS', 0, y); y += 26; c.fillRect(-pw / 2 + 40, y, pw - 80, 4); y += 30; c.font = `400 22px ${TYPE}`; c.fillText(S.date || '', 0, y); y += 16; c.fillRect(-pw / 2 + 40, y, pw - 80, 2); y += 90;
        c.font = `900 ${S.headSize || 80}px ${SERIF}`; for (const L of [].concat(S.head || [])) { c.fillText(L, 0, y); y += (S.headSize || 80) * 1.05 } y += 20;
        c.globalAlpha = .45; for (let i = 0; i < 9; i++) for (let col = 0; col < 3; col++) c.fillRect(-pw / 2 + 60 + col * 330, y + i * 34, 300 - rnd(i * 3 + col) * 60, 10); c.globalAlpha = 1 }
      else {
        if (kind === 'telegram') { c.font = `700 40px ${BODY}`; c.fillText(S.header || 'TELEGRAM', 0, y); y += 20; c.fillRect(-pw / 2 + 50, y, pw - 100, 3); y += 60 }
        else { c.font = `italic 400 30px ${SERIF}`; c.fillText(S.header || '', 0, y); y += 70 }
        c.textAlign = 'left'; c.font = kind === 'telegram' ? `700 34px ${TYPE}` : `italic 400 36px ${SERIF}`; let n = Math.floor(u * (S.speed || 22));
        for (const L of [].concat(S.lines || [])) { const s = L.slice(0, Math.max(0, n)); n -= L.length + 6; c.fillText(s, -pw / 2 + 70, y); y += 56 }
        if (S.sign) { c.font = `italic 400 34px ${SERIF}`; c.textAlign = 'right'; c.globalAlpha = clamp(n / 20); c.fillText(S.sign, pw / 2 - 70, ph / 2 - 80); c.globalAlpha = 1 } }
      if (S.stamp) { const k = clamp((u - (S.stampAt || 2.2)) / .25); if (k > 0) { c.save(); c.translate(pw * .22, ph * .28); c.rotate(-.18); c.scale(1.6 - .6 * k, 1.6 - .6 * k); c.globalAlpha = .85 * k; c.strokeStyle = '#b3161c'; c.lineWidth = 7; c.font = `700 56px ${BODY}`; const w = c.measureText(S.stamp).width + 50; c.strokeRect(-w / 2, -45, w, 90); c.fillStyle = '#b3161c'; c.textAlign = 'center'; c.fillText(S.stamp, 0, 20); c.restore() } }
      c.restore();
    });
    glow(c, W * .35, H * .25, 900, '255,190,110', .12); vignette(c, W, H, .65); grain(c, W, H, .06);
  };

  // ---------- card: the minute-by-minute clock ----------
  SH['card'] = (c, W, H, S) => {
    const u = S.u; c.fillStyle = '#070605'; c.fillRect(0, 0, W, H); glow(c, W / 2, H / 2, 700, '255,170,90', .1);
    const a = clamp(u / .4); c.save(); c.globalAlpha = a; c.textAlign = 'center'; c.fillStyle = '#f3e7cf';
    c.font = `700 ${S.size || 150}px ${TYPE}`; const T = String(S.time || ''); c.fillText(T.slice(0, Math.ceil(clamp(u / .7) * T.length)), W / 2, H * .5);
    c.font = `400 40px ${TYPE}`; c.fillStyle = 'rgba(243,231,207,.8)'; c.fillText(S.place || '', W / 2, H * .5 + 80); if (S.date) { c.font = `400 30px ${TYPE}`; c.fillText(S.date, W / 2, H * .5 + 130) }
    if (S.tick !== false) { c.strokeStyle = '#b3161c'; c.lineWidth = 4; const r = 34, x = W / 2, y = H * .5 - (S.size || 150) - 40, a2 = Math.floor(u) / 60 * 6.283 + (S.sec || 0); c.beginPath(); c.arc(x, y, r, 0, 7); c.stroke(); c.beginPath(); c.moveTo(x, y); c.lineTo(x + Math.sin(a2) * r * .85, y - Math.cos(a2) * r * .85); c.stroke() }
    c.restore(); grain(c, W, H, .06);
  };

  // ---------- set: an illustrated scene composed from parts ----------
  const SKY = { dawn: ['#2b3350', '#d98a62'], day: ['#7fa3c0', '#e6e1cf'], dusk: ['#1d2140', '#d0603a'], night: ['#050912', '#1a2640'], storm: ['#1b1f26', '#4a5058'] };
  const ridge = (c, W, H, y, amp, col, seed) => { c.fillStyle = col; c.beginPath(); c.moveTo(-300, H + 300); for (let x = -300; x <= W + 300; x += 14) { const v = Math.sin(x * .004 + seed) * .5 + Math.sin(x * .011 + seed * 2) * .3 + Math.sin(x * .029 + seed * 3) * .12; c.lineTo(x, y - amp * v) } c.lineTo(W + 300, H + 300); c.fill() };
  const tree = (c, x, y, h, col) => { c.fillStyle = col; c.beginPath(); c.moveTo(x, y - h); for (let i = 0; i < 5; i++) { const f = (i + 1) / 5; c.lineTo(x + h * .22 * f, y - h + h * f * .95); c.lineTo(x + h * .08 * f, y - h + h * f * .95) } c.lineTo(x + h * .03, y); c.lineTo(x - h * .03, y); for (let i = 4; i >= 0; i--) { const f = (i + 1) / 5; c.lineTo(x - h * .08 * f, y - h + h * f * .95); c.lineTo(x - h * .22 * f, y - h + h * f * .95) } c.fill() };
  function flag(c, x, y, w, h, cols, u, vertical) { for (let i = 0; i < cols.length; i++) { c.fillStyle = cols[i]; c.beginPath(); const n = cols.length;
      const a = i / n, b = (i + 1) / n; c.moveTo(x, y + h * a); for (let s = 0; s <= 12; s++) { const f = s / 12; c.lineTo(x + w * f, y + h * a + Math.sin(f * 5 - u * 4) * h * .08 * f) } for (let s = 12; s >= 0; s--) { const f = s / 12; c.lineTo(x + w * f, y + h * b + Math.sin(f * 5 - u * 4) * h * .08 * f) } c.fill() } }
  const FLAGS = { us: ['#b22234', '#fff', '#b22234', '#fff', '#b22234', '#fff', '#b22234'], uk: ['#012169', '#c8102e', '#012169'], hbc: ['#c8102e', '#c8102e', '#fff'], fr: ['#0055a4', '#fff', '#ef4135'], de: ['#000', '#fff', '#c00'], ru: ['#fff', '#0039a6', '#d52b1e'], jp: ['#fff', '#fff', '#fff'], red: ['#b3161c'], white: ['#eee'] };
  function ship(c, x, y, s, u, o = {}) {   // a sailing warship (o.steam adds a funnel and smoke)
    c.save(); c.translate(x, y + Math.sin(u * 1.2 + x) * 3 * s); c.scale(s * (o.facing || 1), s); const col = o.col || '#15110d';
    c.fillStyle = col; c.beginPath(); c.moveTo(-230, -40); c.lineTo(250, -40); c.quadraticCurveTo(230, 10, 190, 20); c.lineTo(-200, 20); c.quadraticCurveTo(-230, 0, -230, -40); c.fill();
    c.fillStyle = 'rgba(230,220,190,.55)'; for (let i = 0; i < 9; i++) c.fillRect(-170 + i * 40, -28, 16, 9);
    c.strokeStyle = col; c.lineWidth = 6; for (const mx of [-120, 20, 150]) { c.beginPath(); c.moveTo(mx, -40); c.lineTo(mx, -300); c.stroke(); c.fillStyle = o.sails === false ? 'transparent' : 'rgba(225,215,190,.9)';
      for (const [sy, sw] of [[-280, 70], [-220, 95], [-150, 115]]) { c.beginPath(); c.moveTo(mx - sw, sy); c.quadraticCurveTo(mx, sy + 20, mx + sw, sy); c.lineTo(mx + sw * .9, sy + 52); c.quadraticCurveTo(mx, sy + 70, mx - sw * .9, sy + 52); c.fill() } }
    c.lineWidth = 2; c.beginPath(); c.moveTo(250, -40); c.lineTo(330, -90); c.lineTo(150, -300); c.stroke();
    if (o.flag) flag(c, -230, -150, 60, 38, FLAGS[o.flag] || [o.flag], u);
    if (o.steam) { c.fillStyle = col; c.fillRect(70, -120, 26, 80); c.restore(); smoke(c, x + 83 * s * (o.facing || 1), y - 120 * s, u + x, 300 * s, .2, x); return }
    c.restore() }
  function soldier(c, x, y, h, col, u, o = {}) { const st = o.march ? Math.sin(u * 6 + x) * .25 : 0; c.save(); c.translate(x, y); c.scale(h / 100, h / 100); c.fillStyle = col;
    c.fillRect(-9, -60, 18, 34); c.beginPath(); c.arc(0, -70, 8, 0, 7); c.fill(); c.fillRect(-7, -86, 14, 10);
    c.save(); c.translate(-4, -27); c.rotate(st); c.fillRect(-4, 0, 8, 27); c.restore(); c.save(); c.translate(4, -27); c.rotate(-st); c.fillRect(-4, 0, 8, 27); c.restore();
    c.fillStyle = o.gun || '#2a1f16'; c.fillRect(8, -95, 3, 60); if (o.accent) { c.fillStyle = o.accent; c.fillRect(-9, -60, 18, 4) } c.restore() }
  const PARTS = {
    sea: (c, W, H, u, p) => { const y = H * (p.y || .62), g = c.createLinearGradient(0, y, 0, H); g.addColorStop(0, p.col || '#33485a'); g.addColorStop(1, '#0d1720'); c.fillStyle = g; c.fillRect(-300, y, W + 600, H);
      c.strokeStyle = 'rgba(220,230,240,.13)'; c.lineWidth = 2; for (let i = 0; i < 60; i++) { const yy = y + Math.pow(rnd(i), 1.6) * (H - y), xx = (rnd(i + 1) * W + u * 10 * (1 + rnd(i + 2))) % (W + 200) - 100, w = 20 + (yy - y) * .3; c.beginPath(); c.moveTo(xx, yy); c.lineTo(xx + w, yy); c.stroke() } },
    land: (c, W, H, u, p) => { const y = H * (p.y || .66), cols = { grass: ['#5d6b3a', '#2c3418'], mud: ['#4b3a28', '#1e160e'], snow: ['#d9dde2', '#8a929a'], sand: ['#c9b48a', '#7d6a48'], street: ['#4a4540', '#1b1916'], floor: ['#3a2618', '#140c06'] }[p.kind || 'grass'];
      const g = c.createLinearGradient(0, y, 0, H); g.addColorStop(0, cols[0]); g.addColorStop(1, cols[1]); c.fillStyle = g; c.beginPath(); c.moveTo(-300, H + 300); for (let x = -300; x <= W + 300; x += 30) c.lineTo(x, y - Math.sin(x * .003 + (p.seed || 1)) * 14); c.lineTo(W + 300, H + 300); c.fill() },
    hills: (c, W, H, u, p) => { const n = p.n || 3, base = H * (p.y || .6); for (let i = 0; i < n; i++) { const f = i / Math.max(1, n - 1); ridge(c, W, H, base - (n - 1 - i) * 26, (p.amp || 120) * (1 - f * .35), p.cols ? p.cols[i] : `rgb(${lerp(140, 45, f) | 0},${lerp(150, 55, f) | 0},${lerp(160, 50, f) | 0})`, i * 3 + (p.seed || 1)) } },
    forest: (c, W, H, u, p) => { const y = H * (p.y || .66); for (let i = 0; i < (p.n || 60); i++) { const x = rnd(i + (p.seed || 0)) * (W + 400) - 200, h = (p.h || 160) * (.6 + rnd(i + 7) * .7); tree(c, x, y + rnd(i + 3) * 30, h, p.col || '#1c2414') } },
    coast: (c, W, H, u, p) => { const y = H * (p.y || .6), x0 = W * (p.x0 != null ? p.x0 : -.1), x1 = W * (p.x1 != null ? p.x1 : .45); c.fillStyle = p.col || '#2b3324'; c.beginPath(); c.moveTo(x0, y + 6);
      for (let s = 0; s <= 30; s++) { const f = s / 30, x = lerp(x0, x1, f); c.lineTo(x, y - Math.sin(f * Math.PI) * (p.h || 110) * (.7 + .3 * Math.sin(f * 9 + 1)) ) } c.lineTo(x1, y + 6); c.fill();
      if (p.trees !== false) for (let i = 0; i < 30; i++) { const f = rnd(i + 40), x = lerp(x0, x1, f); tree(c, x, y - Math.sin(f * Math.PI) * (p.h || 110) * .9 + 8, 40 + rnd(i) * 40, p.col || '#1d241a') } },
    town: (c, W, H, u, p) => { const y = H * (p.y || .66), lit = p.night; for (let i = 0; i < (p.n || 14); i++) { const x = W * (p.x0 || 0) + i * (p.gap || 130) + rnd(i) * 30, w = 90 + rnd(i + 1) * 60, h = (p.h || 120) * (.7 + rnd(i + 2) * .8);
        c.fillStyle = p.col || '#2a221b'; c.fillRect(x, y - h, w, h); c.beginPath(); c.moveTo(x - 8, y - h); c.lineTo(x + w / 2, y - h - 46); c.lineTo(x + w + 8, y - h); c.fill();
        for (let r = 0; r < Math.floor(h / 45); r++) for (let k = 0; k < 2; k++) { const on = rnd(i * 9 + r * 3 + k) > (lit ? .45 : 2); c.fillStyle = on ? 'rgba(255,200,120,.85)' : 'rgba(0,0,0,.35)'; c.fillRect(x + 18 + k * (w - 52), y - h + 18 + r * 45, 16, 22) } }
      if (lit) glow(c, W / 2, y - 40, W * .6, '255,170,90', .08) },
    fort: (c, W, H, u, p) => { const y = H * (p.y || .66), x = W * (p.x || .5), w = p.w || 700, h = p.h || 120; c.fillStyle = p.col || '#3b2c1e'; for (let i = 0; i < w / 22; i++) { const xx = x - w / 2 + i * 22; c.beginPath(); c.moveTo(xx, y); c.lineTo(xx, y - h); c.lineTo(xx + 11, y - h - 16); c.lineTo(xx + 22, y - h); c.lineTo(xx + 22, y); c.fill() }
      c.fillRect(x - w / 2 - 40, y - h - 90, 80, h + 90); c.fillRect(x + w / 2 - 40, y - h - 90, 80, h + 90); if (p.flag) { c.fillRect(x - 3, y - h - 220, 6, 220); flag(c, x + 3, y - h - 220, 110, 66, FLAGS[p.flag] || [p.flag], u) } },
    camp: (c, W, H, u, p) => { const y = H * (p.y || .7); for (let i = 0; i < (p.n || 9); i++) { const x = W * (p.x0 || .1) + i * (p.gap || 150), s = .8 + rnd(i) * .3; c.fillStyle = p.col || '#d8cfb4'; c.beginPath(); c.moveTo(x - 60 * s, y); c.lineTo(x, y - 90 * s); c.lineTo(x + 60 * s, y); c.fill(); c.fillStyle = 'rgba(0,0,0,.35)'; c.beginPath(); c.moveTo(x, y - 90 * s); c.lineTo(x + 60 * s, y); c.lineTo(x + 10 * s, y); c.fill() }
      if (p.fire) { glow(c, W * p.fire, y + 10, 260, '255,140,50', .55); smoke(c, W * p.fire, y, u, 300, .15, 4) } },
    ships: (c, W, H, u, p) => { for (let i = 0; i < (p.n || 1); i++) { const s = (p.s || .7) * (1 - i * .18), x = W * (p.x || .55) + i * (p.gap || -330) + (p.sail ? u * 8 * (p.facing || 1) : 0); ship(c, x, H * (p.y || .62) - i * 12, s, u, p) } },
    soldiers: (c, W, H, u, p) => { const y = H * (p.y || .78); for (let r = 0; r < (p.rows || 2); r++) for (let i = 0; i < (p.n || 14); i++) { const x = W * (p.x0 || .1) + i * (p.gap || 56) + r * 20 + (p.march ? u * 30 : 0); soldier(c, x, y + r * 26, (p.h || 120) * (1 + r * .12), p.col || '#1a1410', u, { march: p.march, accent: p.accent }) } },
    cannons: (c, W, H, u, p) => { const y = H * (p.y || .76); for (let i = 0; i < (p.n || 3); i++) { const x = W * (p.x0 || .3) + i * (p.gap || 220); c.fillStyle = '#16120e'; c.save(); c.translate(x, y - 34); c.rotate(-.12 * (p.facing || 1)); c.fillRect(-20, -12, 150 * (p.facing || 1), 24); c.restore(); c.beginPath(); c.arc(x, y - 20, 26, 0, 7); c.fill();
        if (p.fire && (u + i * .9) % 3 < .25) { glow(c, x + 160 * (p.facing || 1), y - 50, 160, '255,200,120', .9) } } },
    crowd: (c, W, H, u, p) => { const y = H * (p.y || .85); for (let i = 0; i < (p.n || 70); i++) { const x = rnd(i) * (W + 200) - 100, s = .7 + rnd(i + 1) * .6, b = Math.sin(u * 2 + i) * 3; c.fillStyle = p.col || '#120e0b'; c.beginPath(); c.arc(x, y - 92 * s + b, 13 * s, 0, 7); c.fill(); c.fillRect(x - 17 * s, y - 80 * s + b, 34 * s, 80 * s);
        if (p.hats && rnd(i + 2) > .4) c.fillRect(x - 15 * s, y - 108 * s + b, 30 * s, 8 * s) } },
    farm: (c, W, H, u, p) => { const y = H * (p.y || .68), x = W * (p.x || .7), s = p.s || 1; c.save(); c.translate(x, y); c.scale(s, s); c.fillStyle = p.col || '#4a3420'; c.fillRect(-160, -120, 320, 120); c.beginPath(); c.moveTo(-180, -120); c.lineTo(0, -210); c.lineTo(180, -120); c.fill();
        c.fillStyle = 'rgba(0,0,0,.4)'; for (let i = 0; i < 10; i++) c.fillRect(-160 + i * 32, -120, 3, 120); c.fillStyle = p.night ? 'rgba(255,200,120,.9)' : 'rgba(30,20,10,.8)'; c.fillRect(-90, -80, 36, 40); c.fillRect(60, -80, 36, 40); c.restore();
        c.strokeStyle = '#3a2a18'; c.lineWidth = 4; for (let i = 0; i < 14; i++) { const fx = x - 600 * s + i * 50 * s; c.beginPath(); c.moveTo(fx, y + 30); c.lineTo(fx, y - 20); c.stroke() } c.beginPath(); c.moveTo(x - 600 * s, y - 10); c.lineTo(x - 650 * s + 14 * 50 * s, y - 10); c.stroke() },
    animal: (c, W, H, u, p) => { const x = W * (p.x || .4) + (p.walk ? Math.sin(u * .4) * 40 : 0), y = H * (p.y || .82), s = p.s || 1, kind = p.kind || 'pig', b = Math.sin(u * 3) * 2;
      c.save(); c.translate(x, y); c.scale(s * (p.facing || 1), s); c.fillStyle = p.col || (kind === 'pig' ? '#2a1d18' : '#d6d0c2');
      if (kind === 'pig') { c.beginPath(); c.ellipse(0, -60 + b, 95, 52, 0, 0, 7); c.fill(); c.beginPath(); c.ellipse(92, -66 + b, 34, 30, 0, 0, 7); c.fill(); c.fillRect(118, -72 + b, 22, 20); c.beginPath(); c.moveTo(80, -90); c.lineTo(96, -118); c.lineTo(104, -88); c.fill();
        for (const lx of [-60, -30, 40, 66]) c.fillRect(lx, -20, 16, 28); c.strokeStyle = c.fillStyle; c.lineWidth = 4; c.beginPath(); c.arc(-100, -72, 12, 0, 5); c.stroke() }
      else if (kind === 'elephant') {   // a war elephant in silhouette (Rome vs Carthage), the trunk swinging as it walks
        const sw = Math.sin(u * 1.4) * .12, st = Math.sin(u * 2.2);
        c.beginPath(); c.ellipse(0, -210 + b, 190, 120, 0, 0, 7); c.fill();                                   // body
        c.beginPath(); c.ellipse(175, -250 + b, 78, 70, -.2, 0, 7); c.fill();                                 // head
        c.beginPath(); c.ellipse(130, -255 + b, 52, 72, .25, 0, 7); c.fill();                                 // ear
        c.save(); c.translate(225, -230 + b); c.rotate(sw); c.lineCap = 'round'; c.strokeStyle = c.fillStyle; c.lineWidth = 30;
        c.beginPath(); c.moveTo(0, 0); c.quadraticCurveTo(40, 90, 10, 170); c.stroke(); c.lineWidth = 8; c.strokeStyle = '#d9cfb8'; c.beginPath(); c.moveTo(-5, 30); c.quadraticCurveTo(50, 50, 70, 20); c.stroke(); c.restore();   // trunk, tusk
        for (const [lx, ph] of [[-120, 0], [-60, Math.PI], [70, Math.PI], [130, 0]]) { const lift = Math.max(0, Math.sin(u * 2.2 + ph)) * (p.walk ? 14 : 0); c.fillRect(lx - 24, -130 + b - lift, 48, 130) }
        c.strokeStyle = c.fillStyle; c.lineWidth = 5; c.beginPath(); c.moveTo(-188, -220); c.quadraticCurveTo(-215, -170 + st * 6, -205, -130); c.stroke();   // tail
        if (p.tower) { c.fillStyle = '#3a2618'; c.fillRect(-90, -370 + b, 140, 60); c.fillStyle = '#5a3a22'; c.fillRect(-100, -318 + b, 160, 14) } }
      else { c.beginPath(); c.ellipse(0, -60 + b, 70, 42, 0, 0, 7); c.fill(); c.beginPath(); c.ellipse(70, -70 + b, 24, 18, 0, 0, 7); c.fill(); c.fillStyle = '#222'; for (const lx of [-40, -15, 25, 45]) c.fillRect(lx, -25, 9, 30) }
      c.restore() },
    flagpole: (c, W, H, u, p) => { const x = W * (p.x || .5), y = H * (p.y || .7), h = p.h || 420; c.fillStyle = '#1a140f'; c.fillRect(x - 4, y - h, 8, h); flag(c, x + 4, y - h, p.w || 180, (p.w || 180) * .6, FLAGS[p.flag] || [p.flag || '#b3161c'], u) },
    fire: (c, W, H, u, p) => { const x = W * (p.x || .5), y = H * (p.y || .8); glow(c, x, y, p.r || 400, '255,120,40', .7); c.save(); c.globalCompositeOperation = 'lighter'; for (let i = 0; i < 26; i++) { const a = rnd(i), hh = (60 + rnd(i + 1) * 120) * (1 + .3 * Math.sin(u * 9 + i)); c.fillStyle = `rgba(255,${120 + a * 100 | 0},40,.35)`; c.beginPath(); c.moveTo(x - 50 + a * 100, y); c.quadraticCurveTo(x - 30 + a * 60, y - hh * .6, x - 40 + a * 80 + Math.sin(u * 6 + i) * 10, y - hh); c.quadraticCurveTo(x - 10 + a * 60, y - hh * .5, x - 30 + a * 100, y); c.fill() } c.restore(); smoke(c, x, y - 100, u, 500, .2, 3) },
    room: (c, W, H, u, p) => { const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, p.wall || '#2a1d14'); g.addColorStop(1, '#120c08'); c.fillStyle = g; c.fillRect(-300, -300, W + 600, H + 600); c.strokeStyle = 'rgba(0,0,0,.35)'; c.lineWidth = 3; for (let x = -300; x < W + 300; x += 170) { c.beginPath(); c.moveTo(x, -300); c.lineTo(x, H * .72); c.stroke() }
      c.fillStyle = p.floor || '#1c120a'; c.fillRect(-300, H * .72, W + 600, H); if (p.window) { const wx = W * p.window, wy = H * .18, ww = 360, wh = 420, n = p.night; const sg = c.createLinearGradient(0, wy, 0, wy + wh); sg.addColorStop(0, n ? '#0c1426' : '#a8bfd0'); sg.addColorStop(1, n ? '#1b2640' : '#e6e0cc'); c.fillStyle = sg; c.fillRect(wx, wy, ww, wh); c.strokeStyle = '#0a0705'; c.lineWidth = 16; c.strokeRect(wx, wy, ww, wh); c.lineWidth = 8; c.beginPath(); c.moveTo(wx + ww / 2, wy); c.lineTo(wx + ww / 2, wy + wh); c.moveTo(wx, wy + wh / 2); c.lineTo(wx + ww, wy + wh / 2); c.stroke();
        if (!n) { c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = 'rgba(255,230,180,.08)'; c.beginPath(); c.moveTo(wx, wy + wh); c.lineTo(wx + ww, wy + wh); c.lineTo(wx + ww + 500, H); c.lineTo(wx + 300, H); c.fill(); c.restore() } }
      if (p.portrait) { const px = W * p.portrait; c.fillStyle = '#5a4020'; c.fillRect(px - 110, H * .16, 220, 280); c.fillStyle = '#2a2018'; c.fillRect(px - 92, H * .16 + 18, 184, 244); c.fillStyle = '#4a3a2a'; c.beginPath(); c.arc(px, H * .16 + 110, 46, 0, 7); c.fill(); c.fillRect(px - 70, H * .16 + 160, 140, 100) }
      if (p.flag) flag(c, W * (p.flagX || .8), H * .2, 200, 130, FLAGS[p.flag] || [p.flag], u) },
    table: (c, W, H, u, p) => { const y = H * (p.y || .72), x = W * (p.x || .5), w = p.w || 900; c.fillStyle = p.col || '#2a1a10'; c.beginPath(); c.moveTo(x - w / 2, y); c.lineTo(x + w / 2, y); c.lineTo(x + w / 2 + 80, y + 110); c.lineTo(x - w / 2 - 80, y + 110); c.fill(); c.fillStyle = '#1a0f09'; c.fillRect(x - w / 2 - 80, y + 110, w + 160, H);
      c.fillStyle = p.cloth || '#ddd2b4'; for (let i = 0; i < (p.papers || 4); i++) { c.save(); c.translate(x - w * .35 + i * w * .22, y + 50); c.transform(1, 0, -.3, .35, 0, 0); c.rotate(rnd(i) - .5); c.fillRect(-60, -80, 120, 160); c.restore() }
      if (p.lamp) { const lx = x + w * (p.lamp - .5); c.fillStyle = '#0f4a2c'; c.beginPath(); c.moveTo(lx - 90, y - 150); c.quadraticCurveTo(lx, y - 210, lx + 90, y - 150); c.fill(); c.fillStyle = '#5c4320'; c.fillRect(lx - 5, y - 150, 10, 150); glow(c, lx, y - 140, 700, '255,190,110', .45) }
      if (p.candles) for (let i = 0; i < p.candles; i++) { const cx = x - w * .3 + i * w * .6 / Math.max(1, p.candles - 1); c.fillStyle = '#e8dcc0'; c.fillRect(cx - 6, y - 50, 12, 50); glow(c, cx, y - 58, 160, '255,190,110', .6 + .1 * Math.sin(u * 9 + i)) } },
    people: (c, W, H, u, p, S) => { for (const q of (p.list || [])) {
        if (q.photo && IMG[`photos/${S._story}/${q.photo}-fg.png`]) { const im = IMG[`photos/${S._story}/${q.photo}-fg.png`], h = H * (q.h || .8), w = im.width * h / im.height, x = W * q.x - w / 2, y = H * (q.y || 1.02) - h + Math.sin(u * 1.5 + q.x * 9) * 3;
          c.save(); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 30; c.drawImage(im, x, y, w, h); c.restore(); continue }
        figure(c, W, H, W * q.x, H * (q.y || 1.04), H * (q.h || .8), q, u + q.x * 10, W * (p.lx || .5), H * (p.ly || .4), p.warm || '255,170,90') } },
  };
  SH['set'] = (c, W, H, S, t, env) => {
    const u = S.u, C = cam(S, W, H), tm = S.time || 'day', sky = SKY[S.weather === 'storm' ? 'storm' : tm] || SKY.day; S._story = env.story;
    layer(c, C, W, H, .1, () => { const g = c.createLinearGradient(0, -300, 0, H * .7); g.addColorStop(0, sky[0]); g.addColorStop(1, sky[1]); c.fillStyle = g; c.fillRect(-300, -300, W + 600, H + 600);
      if (tm === 'night') { c.fillStyle = 'rgba(255,255,255,.8)'; for (let i = 0; i < 120; i++) c.fillRect(rnd(i) * W, rnd(i + 1) * H * .5, 1.5, 1.5); glow(c, W * .78, H * .16, 140, '220,230,255', .5) }
      else if (tm === 'dawn' || tm === 'dusk') glow(c, W * (S.sunX || .7), H * .55, 700, '255,170,90', .55); else glow(c, W * (S.sunX || .75), H * .12, 500, '255,245,215', .4);
      for (let i = 0; i < (S.clouds == null ? 6 : S.clouds); i++) { const x = ((rnd(i) * W * 1.6 + u * 8 * (1 + rnd(i + 1))) % (W * 1.6)) - W * .3, y = 60 + rnd(i + 2) * H * .3, r = 220 + rnd(i + 3) * 260, g2 = c.createRadialGradient(x, y, 0, x, y, r);
        g2.addColorStop(0, tm === 'night' ? 'rgba(40,50,70,.5)' : 'rgba(240,235,225,.35)'); g2.addColorStop(1, 'rgba(240,235,225,0)'); c.fillStyle = g2; c.save(); c.translate(x, y); c.scale(1, .35); c.translate(-x, -y); c.fillRect(x - r, y - r, 2 * r, 2 * r); c.restore() } });
    for (const p of (S.parts || [])) { const f = PARTS[p.type]; if (!f) continue; layer(c, C, W, H, p.depth != null ? p.depth : .5, () => f(c, W, H, u, p, S)) }
    // life in every outdoor shot: grass moving in the wind up front, birds crossing the sky, drifting light
    const ground = (S.parts || []).find(p => p.type === 'land' && ['grass', 'mud', 'sand', 'snow'].includes(p.kind || 'grass'));
    if (ground) layer(c, C, W, H, 1.15, () => { const y0 = H * Math.max(ground.y || .66, .8); c.strokeStyle = ground.kind === 'snow' ? 'rgba(200,205,210,.8)' : 'rgba(30,38,18,.85)'; c.lineCap = 'round';
      for (let i = 0; i < 150; i++) { const x = rnd(i + 50) * (W + 300) - 150, y = y0 + rnd(i + 51) * (H - y0 + 60), h = 20 + rnd(i + 52) * 50 * (y / H), sw = Math.sin(u * 1.6 + x * .01) * 10 * (h / 60);
        c.lineWidth = 2 + rnd(i + 53) * 2; c.beginPath(); c.moveTo(x, y); c.quadraticCurveTo(x + sw * .3, y - h * .6, x + sw, y - h); c.stroke() } });
    if (tm !== 'night' && !(S.parts || []).some(p => p.type === 'room')) { c.strokeStyle = 'rgba(25,25,25,.55)'; c.lineWidth = 2.5; for (let i = 0; i < 5; i++) { const bx = ((rnd(i + 9) * W + u * (35 + i * 6)) % (W + 300)) - 150, by = 140 + rnd(i + 10) * 180 + Math.sin(u * 2 + i) * 8, w = Math.sin(u * 8 + i) * 8;
        c.beginPath(); c.moveTo(bx - 12, by - w); c.quadraticCurveTo(bx - 4, by - 4, bx, by); c.quadraticCurveTo(bx + 4, by - 4, bx + 12, by - w); c.stroke() } }
    if (tm === 'night') { c.fillStyle = 'rgba(5,10,25,.35)'; c.fillRect(0, 0, W, H) } else if (tm === 'dawn' || tm === 'dusk') { c.save(); c.globalCompositeOperation = 'soft-light'; c.fillStyle = 'rgba(255,140,70,.35)'; c.fillRect(0, 0, W, H); c.restore() }
    fx(c, W, H, u, [].concat(S.fx || []).concat(S.weather === 'rain' || S.weather === 'storm' ? ['rain'] : S.weather === 'fog' ? ['fog'] : S.weather === 'snow' ? ['snow'] : []));
    vignette(c, W, H, .55); grain(c, W, H, .06);
  };
})(typeof window !== 'undefined' ? window : globalThis);
