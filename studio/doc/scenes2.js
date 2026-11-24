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
  function caption(c, W, H, txt, u) {   // a lower third that slides in (motion graphics, owner 15 Nov 2026)
    if (!txt) return; const k = o3(clamp((u - .5) / .5)), out = clamp((u - 5.5) / .4); if (k <= 0 || out >= 1) return;
    c.save(); c.font = `600 30px ${BODY}`; const w = c.measureText(txt).width + 70, x = 80 - (1 - k) * (w + 120), y = H - BAR - 110;
    c.globalAlpha = 1 - out; c.fillStyle = 'rgba(12,9,6,.82)'; c.fillRect(x, y, w * Math.min(1, k * 1.4), 58); c.fillStyle = '#c8462e'; c.fillRect(x, y, 7, 58);
    c.fillStyle = '#f3e7cf'; c.textBaseline = 'middle'; c.save(); c.beginPath(); c.rect(x, y, w * Math.min(1, k * 1.4), 58); c.clip(); c.fillText(txt, x + 30, y + 30); c.restore(); c.restore() }
  function mark(c, W, H, m, u) {   // a circle drawn onto the picture, and its label (S.mark = {x, y, r, label})
    if (!m) return; const a = clamp((u - (m.at || 1.2)) / .7); if (a <= 0) return; const x = W * m.x, y = H * m.y, r = (m.r || .1) * H;
    c.save(); c.strokeStyle = '#e8b04a'; c.lineWidth = 7; c.lineCap = 'round'; c.shadowColor = 'rgba(0,0,0,.7)'; c.shadowBlur = 10;
    c.beginPath(); c.ellipse(x, y, r * 1.15, r, -.1, -1.6, -1.6 + 6.5 * a); c.stroke();
    if (m.label && a >= 1) { const b = o3(clamp((u - (m.at || 1.2) - .7) / .4)), lx = x + r * 1.2, ly = y - r * .9; c.beginPath(); c.moveTo(lx, ly); c.lineTo(lx + 80 * b, ly - 50 * b); c.stroke();
      c.font = `700 40px ${BODY}`; c.fillStyle = '#f3e7cf'; c.globalAlpha = b; c.fillText(m.label, lx + 92, ly - 56) }
    c.restore() }
  const cover = (im, W, H) => { const s = Math.max(W / im.width, H / im.height); return [im.width * s, im.height * s] };

  // ---------- photo: 2.5-D archival photo ----------
  SH['photo'] = (c, W, H, S, t, env) => {
    const u = S.u, d = S.dur || 8, k = io(clamp(u / d)), st = env.story, bg = IMG[`photos/${st}/${S.img}.jpg`], fg = IMG[`photos/${st}/${S.img}-fg.png`];
    c.fillStyle = '#0b0906'; c.fillRect(0, 0, W, H);
    if (!bg && S.fallback && SH[S.fallback.shot]) { SH[S.fallback.shot](c, W, H, Object.assign({}, S.fallback, { u: S.u, dur: S.dur }), t, env); return }   // the archival photo could not be fetched: its stand-in shot plays instead
    if (!bg) { c.fillStyle = '#e33'; c.font = `40px ${BODY}`; c.fillText('missing photo: ' + S.img, 80, 200); return }
    const mv = S.move || 'in', z0 = mv === 'out' ? 1.16 : 1.04, z1 = mv === 'out' ? 1.04 : 1.16, z = lerp(z0, z1, k), [bw, bh] = cover(bg, W, H),
      pan = S.pan || [mv === 'left' ? 60 : mv === 'right' ? -60 : 0, 0], fx0 = S.focus ? (S.focus[0] - .5) * bw * .3 : 0, fy0 = S.focus ? (S.focus[1] - .5) * bh * .3 : 0;
    const fyA = S.focus ? S.focus[1] : bh > H * 1.15 ? .22 : .5, py = Math.max(-(bh - H) / 2, Math.min((bh - H) / 2, (.5 - fyA) * bh));   // frame the focus (a tall portrait: its face), not the middle   // a tall portrait: frame its top (the face), not its middle (15 Nov 2026: a general's head was cut off)
    const draw = (im, depth) => { const zz = 1 + (z - 1) * depth; c.save(); c.translate(W / 2 - fx0 * k * depth + pan[0] * (k - .5) * depth, H / 2 + py - fy0 * k * depth + pan[1] * (k - .5) * depth); c.scale(zz, zz); c.drawImage(im, -bw / 2, -bh / 2, bw, bh); c.restore() };
    draw(bg, 1); if (S.fx && [].concat(S.fx).includes('fog')) fx(c, W, H, u, 'fog');
    if (fg) { c.save(); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 30; draw(fg, 1.9); c.restore() }
    tone(c, W, H, S.tone || 'sepia');
    c.save(); c.globalCompositeOperation = 'soft-light'; c.fillStyle = 'rgba(255,190,120,.18)'; c.fillRect(0, 0, W, H); c.restore();
    fx(c, W, H, u, [].concat(S.fx || []).filter(f => f !== 'fog')); vignette(c, W, H, .7); grain(c, W, H, .09); mark(c, W, H, S.mark, u); caption(c, W, H, S.caption, u);
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
        const LS = [].concat(S.lines || []), ys = [], n0 = n;
        for (const L of LS) { const s = L.slice(0, Math.max(0, n)); n -= L.length + 6; ys.push(y); c.fillText(s, -pw / 2 + 70, y); y += 56 }
        const tot = LS.reduce((a, L) => a + L.length + 6, 0), hi = S.hl == null ? LS.length - 1 : S.hl;   // a highlighter sweeps the key line once it is typed
        if (LS.length && S.hl !== false && hi >= 0) { const k = io(clamp((n0 - tot) / (S.speed || 22) / .5)); if (k > 0) { c.save(); c.globalCompositeOperation = 'multiply'; c.fillStyle = 'rgba(255,205,70,.75)'; c.fillRect(-pw / 2 + 62, ys[hi] - 38, (c.measureText(LS[hi]).width + 16) * k, 48); c.restore() } }
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
    c.font = `700 ${S.size || 150}px ${TYPE}`; const T = String(S.time || ''), num = T.match(/\d[\d,]*(\.\d+)?/);
    let shown;   // a number counts up to its value (motion graphics, owner 15 Nov 2026); other text is typed
    if (num && !/^\d{1,2} [A-Z]|^[A-Z]+ \d{4}$|^\d{4}$|BC|AD/.test(T)) { const v = parseFloat(num[0].replace(/,/g, '')), k = io(clamp(u / 1.1)), dec = (num[1] || '').length - 1;
      let s2 = (v * k).toFixed(Math.max(0, dec)); if (num[0].includes(',')) s2 = Number(s2).toLocaleString('en-US', { minimumFractionDigits: Math.max(0, dec), maximumFractionDigits: Math.max(0, dec) }); shown = T.replace(num[0], s2) }
    else shown = T.slice(0, Math.ceil(clamp(u / .7) * T.length));
    c.fillText(shown, W / 2, H * .5); const tw = c.measureText(T).width, rl = io(clamp((u - .9) / .5)); c.fillStyle = '#b3161c'; c.fillRect(W / 2 - tw / 2, H * .5 + 22, tw * rl, 6); c.fillStyle = '#f3e7cf';
    c.font = `400 40px ${TYPE}`; c.fillStyle = 'rgba(243,231,207,.8)'; c.fillText(S.place || '', W / 2, H * .5 + 80); if (S.date) { c.font = `400 30px ${TYPE}`; c.fillText(S.date, W / 2, H * .5 + 130) }
    if (S.tick !== false) { c.strokeStyle = '#b3161c'; c.lineWidth = 4; const r = 34, x = W / 2, y = H * .5 - (S.size || 150) - 40, a2 = Math.floor(u) / 60 * 6.283 + (S.sec || 0); c.beginPath(); c.arc(x, y, r, 0, 7); c.stroke(); c.beginPath(); c.moveTo(x, y); c.lineTo(x + Math.sin(a2) * r * .85, y - Math.cos(a2) * r * .85); c.stroke() }
    c.restore(); grain(c, W, H, .06);
  };

  // ---------- transitions between shots (owner, 15 Nov 2026: "modern editing", not a fade through black every time) ----------
  // whip (a fast pan with motion streaks), ink (a round wipe), push (the new shot shoves the old one up), zoom (through the old shot).
  // Dialogue cuts hard between lines; a chapter card keeps its own fade. The old shot keeps playing under the transition.
  const TR = .42, OFFS = {};
  function offc(i, W, H) { let o = OFFS[i]; if (!o) { const cv = document.createElement('canvas'); cv.width = W; cv.height = H; o = OFFS[i] = [cv, cv.getContext('2d')] } o[1].setTransform(1, 0, 0, 1, 0, 0); o[1].clearRect(0, 0, W, H); return o }
  G.SCENE_TRANSITION = (c, W, H, st, t, env) => {
    const S = st.scene, P = st.prev; if (!S || !P || S.u >= TR || S.shot === 'talk' || P.shot === 'talk' && S.shot === 'talk' || S.transition === 'cut') return false;
    const kind = S.transition || ['whip', 'ink', 'push', 'zoom', 'whip'][(st.sceneN || 0) % 5], k = io(clamp(S.u / TR));
    const [ca, xa] = offc(0, W, H), [cb, xb] = offc(1, W, H);
    G.SCENE(xa, W, H, Object.assign({}, P, { u: t - P.t, fadeOut: 0 }), t, env); G.SCENE(xb, W, H, Object.assign({}, S, { fadeIn: 0 }), t, env);
    c.save();
    if (kind === 'whip') { const d = W * k; for (let i = 3; i >= 0; i--) { c.globalAlpha = i ? .22 : 1; c.drawImage(ca, -d - i * 40 * Math.sin(Math.PI * k), 0); c.drawImage(cb, W - d - i * 40 * Math.sin(Math.PI * k), 0) } }
    else if (kind === 'push') { const d = H * k; c.drawImage(ca, 0, -d); c.drawImage(cb, 0, H - d); c.fillStyle = 'rgba(0,0,0,.5)'; c.fillRect(0, H - d - 6, W, 6) }
    else if (kind === 'zoom') { const z = 1 + k * .6; c.drawImage(cb, 0, 0); c.globalAlpha = 1 - k; c.translate(W / 2, H / 2); c.scale(z, z); c.drawImage(ca, -W / 2, -H / 2) }
    else { c.drawImage(ca, 0, 0); c.beginPath(); c.arc(W * .5, H * .5, Math.hypot(W, H) * .55 * k, 0, 7); c.clip(); c.drawImage(cb, 0, 0) }   // ink
    c.restore(); return true };

  // ---------- kinetic callouts on the spoken word (make_doc.py kinetic): numbers, money, years, names ----------
  G.SCENE_POP = (c, W, H, P) => {
    const u = P.u, d = P.dur || 2.4, inn = clamp(u / .28), out = clamp((u - d + .3) / .3); if (out >= 1) return;
    const bounce = inn < 1 ? 1 + Math.sin(inn * Math.PI) * .18 : 1, s = (.6 + .4 * o3(inn)) * bounce * (1 - .15 * out), L = P.side !== 'r';
    c.save(); c.globalAlpha = 1 - out;
    if (P.kind === 'name') {   // a name tag sliding in from the side
      c.font = `700 46px ${BODY}`; const w = c.measureText(P.text).width + 90, x = L ? 70 - (1 - o3(inn)) * (w + 100) : W - 70 - w + (1 - o3(inn)) * (w + 100), y = BAR + 70;
      c.fillStyle = 'rgba(12,9,6,.85)'; c.fillRect(x, y, w, 76); c.fillStyle = '#e8b04a'; c.fillRect(x, y, 10, 76); c.beginPath(); c.arc(x + 42, y + 38, 9, 0, 7); c.fill();
      c.fillStyle = '#f3e7cf'; c.textBaseline = 'middle'; c.fillText(P.text, x + 66, y + 40); c.restore(); return }
    const C = P.side === 'c', cx = C ? W * .5 : L ? W * .19 : W * .81, cy = C ? H * .2 : L ? H * .33 : H * .27, sc0 = C ? .72 : 1; c.translate(0, 0); c.translate(cx, cy); c.scale(s * sc0, s * sc0); c.rotate(C ? 0 : (L ? -1 : 1) * .03);
    const big = P.kind === 'year' ? 120 : 150; c.font = `800 ${big}px ${BODY}`; c.textAlign = 'center'; c.textBaseline = 'middle';
    const tw = c.measureText(P.text).width, lab = P.label || (P.kind === 'year' ? '' : ''), lw = lab ? (c.font = `700 40px ${BODY}`, c.measureText(lab).width) : 0, bw = Math.max(tw, lw) + 90, bh = big + (lab ? 70 : 30);
    c.fillStyle = 'rgba(10,8,6,.72)'; c.beginPath(); c.roundRect(-bw / 2, -big / 2 - 20, bw, bh, 18); c.fill();
    c.fillStyle = P.kind === 'money' ? '#e8c04a' : P.kind === 'year' ? '#d9c39a' : '#c8462e'; c.fillRect(-bw / 2, -big / 2 - 20, bw * o3(clamp((u - .2) / .4)), 8);
    if (P.kind === 'money') { c.save(); c.translate(-bw / 2 - 10, -big / 2 - 20); c.rotate(u * 3); c.fillStyle = '#e8c04a'; c.beginPath(); c.arc(0, 0, 34, 0, 7); c.fill(); c.strokeStyle = '#8a6a1c'; c.lineWidth = 5; c.stroke(); c.fillStyle = '#8a6a1c'; c.font = `800 40px ${BODY}`; c.fillText('$', 0, 2); c.restore() }
    if (P.kind === 'year') { c.strokeStyle = 'rgba(217,195,154,.8)'; c.lineWidth = 5; c.strokeRect(-bw / 2 + 12, -big / 2 - 8, bw - 24, bh - 24) }
    c.font = `800 ${big}px ${BODY}`; c.fillStyle = P.kind === 'money' ? '#f1d27a' : '#f3e7cf'; c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 12; c.fillText(P.text, 0, 6);
    if (lab) { c.shadowBlur = 0; c.font = `700 40px ${BODY}`; c.fillStyle = '#e8b04a'; c.fillText(lab, 0, big / 2 + 22) }
    c.restore() };

  // ---------- looks: the same film in other animation styles (owner, 15 Nov 2026: "show me 5 different animation styles") ----------
  // paper (cut paper: flat colour bands on a paper texture), ink (inked lines on sepia), flat (bright, clean vector), film (1900s newsreel).
  let LOOKBUF = null, PAPER = null;
  function lookDefs() {
    if (document.getElementById('lk-defs')) return; const d = document.createElement('div'); d.id = 'lk-defs';
    const post = (id, n) => `<filter id="${id}" color-interpolation-filters="sRGB"><feComponentTransfer>${['R', 'G', 'B'].map(k => `<feFunc${k} type="discrete" tableValues="${Array.from({ length: n }, (_, i) => (i / (n - 1)).toFixed(3)).join(' ')}"/>`).join('')}</feComponentTransfer></filter>`;
    d.innerHTML = `<svg width="0" height="0" style="position:absolute">${post('lk-post5', 9)}${post('lk-post4', 5)}
      <filter id="lk-ink" color-interpolation-filters="sRGB"><feColorMatrix type="saturate" values="0" result="g"/>
        <feConvolveMatrix in="g" order="3" kernelMatrix="-1 -1 -1 -1 8 -1 -1 -1 -1" preserveAlpha="true" result="e"/>
        <feColorMatrix in="e" type="matrix" values="-4 0 0 0 1  -4 0 0 0 1  -4 0 0 0 1  0 0 0 1 0" result="ei"/>
        <feComponentTransfer in="g" result="gc"><feFuncR type="linear" slope="1.45" intercept="-.12"/><feFuncG type="linear" slope="1.45" intercept="-.12"/><feFuncB type="linear" slope="1.45" intercept="-.12"/></feComponentTransfer>
        <feBlend in="gc" in2="ei" mode="multiply"/></filter></svg>`;
    document.body.appendChild(d) }
  function paperTex(W, H) {   // made once: fibres and blotches, multiplied over the frame
    if (PAPER) return PAPER; const cv = document.createElement('canvas'); cv.width = W; cv.height = H; const k = cv.getContext('2d');
    k.fillStyle = '#f4ead6'; k.fillRect(0, 0, W, H);
    for (let i = 0; i < 9000; i++) { const x = rnd(i * 1.3) * W, y = rnd(i * 2.7 + 5) * H, l = 4 + rnd(i * 3.1) * 26, a = rnd(i * 4.9) * 6.28;
      k.strokeStyle = `rgba(120,95,60,${.04 + rnd(i * 5.3) * .07})`; k.lineWidth = 1; k.beginPath(); k.moveTo(x, y); k.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); k.stroke() }
    for (let i = 0; i < 60; i++) { const g = k.createRadialGradient(rnd(i * 7.1) * W, rnd(i * 8.3) * H, 0, rnd(i * 7.1) * W, rnd(i * 8.3) * H, 60 + rnd(i * 9.7) * 220); g.addColorStop(0, 'rgba(150,120,80,.10)'); g.addColorStop(1, 'rgba(150,120,80,0)'); k.fillStyle = g; k.fillRect(0, 0, W, H) }
    return PAPER = cv }
  G.SCENE_LOOK = (c, W, H, t, name) => {
    lookDefs(); if (!LOOKBUF) { LOOKBUF = document.createElement('canvas'); LOOKBUF.width = W; LOOKBUF.height = H }
    const b = LOOKBUF.getContext('2d'); b.clearRect(0, 0, W, H); b.drawImage(c.canvas, 0, 0);
    c.save(); c.setTransform(1, 0, 0, 1, 0, 0);
    if (name === 'paper') {
      c.filter = 'blur(.8px) saturate(.72) sepia(.3) contrast(1.06) brightness(1.1)'; c.drawImage(LOOKBUF, 0, 0);
      c.globalCompositeOperation = 'multiply'; c.globalAlpha = .45; c.filter = 'url(#lk-ink)'; c.drawImage(LOOKBUF, 0, 0); c.globalAlpha = 1; c.filter = 'none';   // soft pencil lines
      c.globalCompositeOperation = 'multiply'; c.drawImage(paperTex(W, H), 0, 0); c.globalCompositeOperation = 'source-over';
      c.strokeStyle = 'rgba(60,40,20,.35)'; c.lineWidth = 26; c.strokeRect(0, 0, W, H) }
    else if (name === 'ink') {
      c.filter = 'url(#lk-ink) sepia(.6) contrast(1.22) brightness(1.0)'; c.drawImage(LOOKBUF, 0, 0); c.filter = 'none';
      c.globalCompositeOperation = 'multiply'; c.globalAlpha = .55; c.drawImage(paperTex(W, H), 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = 'source-over' }
    else if (name === 'flat') {   // bright and clean: more colour, lifted shadows, the dark film vignette washed out
      c.filter = 'saturate(1.55) brightness(1.2) contrast(1.12)'; c.drawImage(LOOKBUF, 0, 0); c.filter = 'none'; c.beginPath(); c.rect(0, BAR, W, H - 2 * BAR); c.clip();
      const g = c.createRadialGradient(W / 2, H / 2, H * .3, W / 2, H / 2, H * 1.0); g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(1, 'rgba(255,250,240,.28)'); c.globalCompositeOperation = 'screen'; c.fillStyle = g; c.fillRect(0, 0, W, H); c.globalCompositeOperation = 'source-over' }
    else if (name === 'film') {
      const fl = .92 + rnd(Math.floor(t * 24)) * .14, jx = (rnd(Math.floor(t * 12) * 3.3) - .5) * 5, jy = (rnd(Math.floor(t * 12) * 5.1) - .5) * 5;
      c.fillStyle = '#000'; c.fillRect(0, 0, W, H); c.filter = `sepia(.9) contrast(1.25) brightness(${fl.toFixed(3)}) blur(.6px)`; c.drawImage(LOOKBUF, jx, jy); c.filter = 'none';
      const f = Math.floor(t * 24);   // scratches, dust, a blotch now and then
      c.strokeStyle = 'rgba(255,250,235,.35)'; c.lineWidth = 2; for (let i = 0; i < 2; i++) { if (rnd(f * 1.7 + i) < .6) { const x = rnd(f * 3.3 + i * 9) * W; c.beginPath(); c.moveTo(x, 0); c.lineTo(x + (rnd(f + i) - .5) * 30, H); c.stroke() } }
      c.fillStyle = 'rgba(20,14,8,.7)'; for (let i = 0; i < 14; i++) { c.beginPath(); c.arc(rnd(f * 5.1 + i * 2.2) * W, rnd(f * 6.7 + i * 1.9) * H, .8 + rnd(f + i * 3) * 2.6, 0, 7); c.fill() }
      const g = c.createRadialGradient(W / 2, H / 2, H * .35, W / 2, H / 2, H * .95); g.addColorStop(0, 'rgba(0,0,0,0)'); g.addColorStop(1, 'rgba(0,0,0,.75)'); c.fillStyle = g; c.fillRect(0, 0, W, H) }
    c.restore() };

  // ---------- talk: a line of dialogue, acted (owner, 15 Nov 2026: characters talk, Paper Billions style) ----------
  // S = {who, name, preset, spec, side: 'l'|'r', other: {preset, spec}, text, mood, bg: <set shot>}. Shot / reverse shot: every line is
  // its own cut to the speaker, close up, the other character's shoulder dark in the foreground, the line typed in a name-tagged box.
  SH['talk'] = (c, W, H, S, t, env) => {
    const u = S.u, d = S.dur || 3, L = S.side === 'r';
    if (S.bg && SH.set) { c.save(); c.translate(W / 2, H / 2); c.scale(1.12, 1.12); c.translate(-W / 2, -H / 2); SH.set(c, W, H, Object.assign({}, S.bg, { u: u + (S.t || 0) % 7, dur: 30 }), t, env); c.restore(); c.fillStyle = 'rgba(8,6,4,.42)'; c.fillRect(0, 0, W, H) }
    else { const g = c.createRadialGradient(W * (L ? .7 : .3), H * .4, 50, W / 2, H / 2, W * .8); g.addColorStop(0, '#3a2a1c'); g.addColorStop(1, '#0a0705'); c.fillStyle = g; c.fillRect(0, 0, W, H) }
    glow(c, W * (L ? .66 : .34), H * .35, 600, '255,180,110', .22);
    const P = env.PRESETS || {}, talking = u > .1 && u < d - .35, open = talking ? Math.max(0, Math.sin(u * 13) * .6 + Math.sin(u * 7.3 + 1) * .4) : 0;
    if (env.drawChar) {
      const sp = Object.assign({}, P[S.preset] || {}, S.spec || {}, { facing: L ? -1 : 1, mood: S.mood || 'neutral', talk: open });
      const x = W * (L ? .6 : .4) + Math.sin(u * .7) * 6, sway = Math.sin(u * 1.3) * 4;
      env.drawChar(c, x, H * 1.06 + sway, H * .92, sp, u);
      if (S.other) {   // over the shoulder: the listener, dark, out of the frame's edge
        const [oc, k] = off(W, H, 5); const so = Object.assign({}, P[S.other.preset] || {}, S.other.spec || {}, { facing: L ? 1 : -1, mood: 'neutral' });
        env.drawChar(k, W * (L ? -.04 : 1.04), H * 1.5, H * 1.25, so, u + 3); k.save(); k.globalCompositeOperation = 'source-atop'; k.fillStyle = 'rgba(6,4,3,.86)'; k.fillRect(0, 0, W, H); k.restore(); c.drawImage(oc, 0, 0) } }
    // the line, in a box with the speaker's name
    const pad = 38, bw = Math.min(1500, W - 240), bx = (W - bw) / 2, by = H - 250, a = clamp(u / .2) * (1 - clamp((u - d + .25) / .25));
    c.save(); c.globalAlpha = a; c.fillStyle = 'rgba(10,8,6,.86)'; c.fillRect(bx, by, bw, 170); c.fillStyle = '#e8b04a'; c.fillRect(bx, by, 8, 170);
    c.font = `700 30px ${BODY}`; c.fillStyle = '#e8b04a'; c.textAlign = 'left'; c.textBaseline = 'top'; c.fillText((S.name || S.who || '').toUpperCase(), bx + pad, by + 22);
    c.font = `500 44px ${BODY}`; c.fillStyle = '#f3e7cf'; const words = (S.text || '').split(' '); let rem = Math.floor(u * 42), yy = by + 66, ln = '';   // typed at 42 letters a second
    for (const w of words) { const tst = ln ? ln + ' ' + w : w; if (c.measureText(tst).width > bw - pad * 2) { c.fillText(ln.slice(0, Math.max(0, rem)), bx + pad, yy); rem -= ln.length + 1; yy += 52; ln = w } else ln = tst }
    c.fillText(ln.slice(0, Math.max(0, rem)), bx + pad, yy);
    c.restore(); vignette(c, W, H, .55); grain(c, W, H, .06);
  };

  // ---------- close: coverage, the same scene from close up on its main character (a real second camera, not a zoom on a still) ----------
  SH['close'] = (c, W, H, S, t, env) => {
    const u = S.u, a = S.actor || {}, L = (a.facing || 1) < 0;
    if (S.bg && SH.set) { c.save(); c.translate(W / 2, H / 2); c.scale(1.35, 1.35); c.translate(-W / 2 - (L ? -200 : 200), -H / 2 + 60); SH.set(c, W, H, Object.assign({}, S.bg, { parts: (S.bg.parts || []).filter(p => !['actors', 'people'].includes(p.type)), u: u + (S.from || 0), dur: 30 }), t, env); c.restore(); c.fillStyle = 'rgba(8,6,4,.25)'; c.fillRect(0, 0, W, H) }
    const P = (env.PRESETS || {})[a.preset] || {}; glow(c, W * (L ? .62 : .38), H * .35, 600, '255,180,110', .18);
    if (env.drawChar) { const sp = Object.assign({}, P, a.spec || {}, { facing: L ? -1 : 1, mood: a.mood || 'neutral', talk: a.talk ? Math.max(0, Math.sin(u * 13) * .6 + Math.sin(u * 7.3 + 1) * .4) : 0 });
      env.drawChar(c, W * (L ? .6 : .4) + Math.sin(u * .6) * 8, H * 1.08 + Math.sin(u * 1.2) * 4, H * .95, sp, u) }
    vignette(c, W, H, .6); grain(c, W, H, .06) };

  // ---------- set: an illustrated scene composed from parts ----------
  const SKY = { dawn: ['#2b3350', '#d98a62'], day: ['#7fa3c0', '#e6e1cf'], dusk: ['#1d2140', '#d0603a'], night: ['#050912', '#1a2640'], storm: ['#1b1f26', '#4a5058'] };
  const ridge = (c, W, H, y, amp, col, seed) => { c.fillStyle = col; c.beginPath(); c.moveTo(-300, H + 300); for (let x = -300; x <= W + 300; x += 14) { const v = Math.sin(x * .004 + seed) * .5 + Math.sin(x * .011 + seed * 2) * .3 + Math.sin(x * .029 + seed * 3) * .12; c.lineTo(x, y - amp * v) } c.lineTo(W + 300, H + 300); c.fill() };
  const tree = (c, x, y, h, col) => { c.fillStyle = col; c.beginPath(); c.moveTo(x, y - h); for (let i = 0; i < 5; i++) { const f = (i + 1) / 5; c.lineTo(x + h * .22 * f, y - h + h * f * .95); c.lineTo(x + h * .08 * f, y - h + h * f * .95) } c.lineTo(x + h * .03, y); c.lineTo(x - h * .03, y); for (let i = 4; i >= 0; i--) { const f = (i + 1) / 5; c.lineTo(x - h * .08 * f, y - h + h * f * .95); c.lineTo(x - h * .22 * f, y - h + h * f * .95) } c.fill() };
  let UJ = null;   // the Union Jack, drawn once and waved in slices (17 Nov 2026: plain stripes didn't read as the British flag)
  function unionJack() { if (UJ) return UJ; const W = 300, H = 150, cv = document.createElement('canvas'); cv.width = W; cv.height = H; const k = cv.getContext('2d');
    k.fillStyle = '#012169'; k.fillRect(0, 0, W, H); k.save(); k.beginPath(); k.rect(0, 0, W, H); k.clip();
    k.strokeStyle = '#fff'; k.lineWidth = 30; k.beginPath(); k.moveTo(0, 0); k.lineTo(W, H); k.moveTo(W, 0); k.lineTo(0, H); k.stroke();
    k.strokeStyle = '#c8102e'; k.lineWidth = 10; k.beginPath(); k.moveTo(0, 0); k.lineTo(W, H); k.moveTo(W, 0); k.lineTo(0, H); k.stroke(); k.restore();
    k.fillStyle = '#fff'; k.fillRect(W / 2 - 25, 0, 50, H); k.fillRect(0, H / 2 - 25, W, 50); k.fillStyle = '#c8102e'; k.fillRect(W / 2 - 15, 0, 30, H); k.fillRect(0, H / 2 - 15, W, 30);
    return UJ = cv }
  function flag(c, x, y, w, h, cols, u, vertical) { if (cols === FLAGS.cu) { flag(c, x, y, w, h, FLAGS.cu.slice(), u); c.fillStyle = '#cf142b'; c.beginPath(); c.moveTo(x, y); c.lineTo(x + w * .42, y + h / 2 + Math.sin(-u * 4) * h * .02); c.lineTo(x, y + h); c.closePath(); c.fill();
      c.fillStyle = '#fff'; c.font = `${h * .32}px serif`; c.textAlign = 'center'; c.fillText('★', x + w * .14, y + h * .62); return }
    if (cols === FLAGS.pe) return flag(c, x, y, w, h, FLAGS.pe.slice(), u, true);
    if (cols === FLAGS.uk) { const im = unionJack(), n = 24; for (let s = 0; s < n; s++) { const f = s / n, dy = Math.sin(f * 5 - u * 4) * h * .08 * f;
      c.drawImage(im, im.width * f, 0, im.width / n + 1, im.height, x + w * f, y + dy, w / n + 1, h) } return }
    for (let i = 0; i < cols.length; i++) { c.fillStyle = cols[i]; c.beginPath(); const n = cols.length;
      const a = i / n, b = (i + 1) / n; c.moveTo(x, y + h * a); for (let s = 0; s <= 12; s++) { const f = s / 12; c.lineTo(x + w * f, y + h * a + Math.sin(f * 5 - u * 4) * h * .08 * f) } for (let s = 12; s >= 0; s--) { const f = s / 12; c.lineTo(x + w * f, y + h * b + Math.sin(f * 5 - u * 4) * h * .08 * f) } c.fill() }
    if (cols === FLAGS.jp) { const dy = Math.sin(.5 * 5 - u * 4) * h * .08 * .5; c.fillStyle = '#bc002d'; c.beginPath(); c.arc(x + w * .5, y + h * .5 + dy, h * .3, 0, 7); c.fill() } }
  const FLAGS = { us: ['#b22234', '#fff', '#b22234', '#fff', '#b22234', '#fff', '#b22234'], uk: ['#012169', '#c8102e', '#012169'], hbc: ['#c8102e', '#c8102e', '#fff'], fr: ['#0055a4', '#fff', '#ef4135'], de: ['#000', '#fff', '#c00'], ru: ['#fff', '#0039a6', '#d52b1e'], jp: ['#fff', '#fff', '#fff'], cu: ['#002a8f', '#fff', '#002a8f', '#fff', '#002a8f'], pe: ['#d91023', '#fff', '#d91023'], red: ['#b3161c'], white: ['#eee'] };
  function ship(c, x, y, s, u, o = {}) {   // a sailing warship (o.steam adds a funnel and smoke)
    c.save(); c.translate(x, y + Math.sin(u * 1.2 + x) * 3 * s); c.scale(s * (o.facing || 1), s); const col = o.col || '#15110d';
    if (o.modern) {   // a 20th-century steel ship (WW2 stories): long low hull, bridge, gun turrets, one funnel, a thin mast; no sails
      c.fillStyle = col; c.beginPath(); c.moveTo(-280, -30); c.lineTo(300, -30); c.lineTo(270, 18); c.lineTo(-260, 18); c.closePath(); c.fill();
      c.fillRect(-120, -78, 150, 48); c.fillRect(-80, -118, 80, 40); c.fillRect(-52, -170, 6, 52);   // superstructure, bridge, mast
      for (const gx of [120, 200, -200]) { c.fillRect(gx - 22, -52, 44, 22); c.fillRect(gx + (gx > 0 ? 18 : -60), -46, 42, 7) }   // turrets and barrels
      c.fillStyle = 'rgba(230,220,190,.45)'; for (let i = 0; i < 6; i++) c.fillRect(-105 + i * 22, -64, 10, 7);
      if (o.flag) flag(c, -270, -96, 46, 30, FLAGS[o.flag] || [o.flag], u);
      c.fillStyle = col; c.fillRect(40, -120, 34, 90); c.restore();
      if (o.steam !== false) smoke(c, x + 57 * s * (o.facing || 1), y - 120 * s, u + x, 260 * s, .18, x); return }
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
  // ---------- actors: full-body cartoon characters that act (owner, 15 Nov 2026: "like a movie with a story going on") ----------
  // a = {preset, spec, x, y (foot, 0-1), h (height, share of H), facing, pose, mood, talk, prop, walk: [x0, x1, t0, t1], act: [[t, pose], ...]}
  // poses: idle, point, rifle, aim, fire, wave, shrug, hips, hold, toast, dig, think, cross, run. The head comes from chars.js (drawChar),
  // the body is drawn here: coat, arms with hands, legs with a walking cycle, props.
  const SKIN = '#f2c9a0', INK2 = '#1a1210';
  function limb(c, x0, y0, a1, l1, a2, l2, w, col, hand) {   // a1/a2: angles from straight down, radians (positive = forward)
    const x1 = x0 + Math.sin(a1) * l1, y1 = y0 + Math.cos(a1) * l1, x2 = x1 + Math.sin(a1 + a2) * l2, y2 = y1 + Math.cos(a1 + a2) * l2;
    c.lineCap = 'round'; c.lineJoin = 'round'; c.strokeStyle = INK2; c.lineWidth = w + 6; c.beginPath(); c.moveTo(x0, y0); c.lineTo(x1, y1); c.lineTo(x2, y2); c.stroke();
    c.strokeStyle = col; c.lineWidth = w; c.beginPath(); c.moveTo(x0, y0); c.lineTo(x1, y1); c.lineTo(x2, y2); c.stroke();
    if (hand) { c.fillStyle = hand; c.beginPath(); c.arc(x2, y2, w * .62, 0, 7); c.fill(); c.strokeStyle = INK2; c.lineWidth = 3; c.stroke() }
    return [x2, y2] }
  const POSES = {   // [shoulder, elbow] for the front arm and the back arm, radians; ~0 = hanging down
    idle: [[.12, .15], [-.1, .12]], point: [[1.45, 0], [-.1, .1]], rifle: [[.9, -.9], [.5, -.6]], aim: [[1.4, -.15], [1.1, .25]], fire: [[1.4, -.15], [1.1, .25]],
    wave: [[2.6, .5], [-.1, .1]], shrug: [[.9, -1.9], [.9, -1.9]], hips: [[.55, -1.9], [.55, -1.9]], hold: [[.7, -.9], [-.1, .1]], toast: [[2.1, -.9], [-.1, .1]],
    dig: [[.8, .2], [.6, .5]], think: [[.4, -2.4], [.3, -1.5]], cross: [[.4, -1.6], [.35, -1.5]], run: [[.9, -1.4], [-.8, -1.2]] };
  function actor(c, W, H, a, u, env) {
    const P = (env.PRESETS || {})[a.preset] || {}, sp = Object.assign({ coat: '#3a4a6a', coat2: '#e9e2d0', trim: '#d4a72c' }, P, a.spec || {});
    let x = W * (a.x == null ? .5 : a.x), f = a.facing || 1, moving = false;
    if (a.walk) { const [x0, x1, t0, t1] = a.walk, k = clamp((u - (t0 || 0)) / Math.max(.1, (t1 == null ? 8 : t1) - (t0 || 0))); x = W * lerp(x0, x1, io(k)); moving = k > 0 && k < 1; if (x1 !== x0) f = x1 > x0 ? 1 : -1 }
    let pose = a.pose || 'idle'; for (const [t, p] of (a.act || [])) if (u >= t) pose = p;
    if (pose === 'run') moving = true;
    const foot = H * (a.y == null ? .9 : a.y), Hb = H * (a.h || .5), R = Hb / 4.9, charH = R / .235, neck = foot - R * 2.75, hip = neck + R * 1.4;
    const ph = moving ? u * (pose === 'run' ? 11 : 7) : 0, bob = moving ? Math.abs(Math.sin(ph)) * R * .08 : Math.sin(u * 1.6 + x) * R * .025, lw = R * .3;
    c.save(); c.translate(0, -bob);
    // shadow
    c.fillStyle = 'rgba(0,0,0,.28)'; c.beginPath(); c.ellipse(x, foot + bob, R * 1.1, R * .18, 0, 0, 7); c.fill();
    // legs (walking cycle)
    const trous = sp.trousers || shade2(sp.coat, -.45), sw = moving ? Math.sin(ph) * (pose === 'run' ? .7 : .45) : 0;
    for (const k of [-1, 1]) { const hx = x + k * R * .28; limb(c, hx, hip, sw * k, R * .68, Math.max(0, -sw * k) * .6, R * .62, lw * 1.15, trous, null);
      const fx = hx + Math.sin(sw * k) * R * .68, fy = hip + Math.cos(sw * k) * R * .68 + R * .62; c.fillStyle = INK2; c.beginPath(); c.ellipse(fx + f * R * .1, Math.min(foot, fy), R * .26, R * .12, 0, 0, 7); c.fill() }
    // back arm, body, front arm
    const [fa, ba] = POSES[pose] || POSES.idle, swing = moving ? Math.sin(ph) * .5 : Math.sin(u * 1.3) * .04, wv = pose === 'wave' ? Math.sin(u * 9) * .35 : 0;
    const shY = neck + R * .25, arm = (side, A, sgn) => limb(c, x + side * R * .62, shY, f * (A[0] + sgn * swing) + (side === f ? wv * f : 0), R * .78, f * A[1], R * .72, lw, sp.coat, sp.skin || SKIN);
    arm(-f, ba, -1);
    c.fillStyle = sp.coat; c.strokeStyle = INK2; c.lineWidth = 6; c.beginPath();   // coat
    c.moveTo(x - R * .62, neck); c.quadraticCurveTo(x - R * .8, neck + R * .2, x - R * .78, hip + R * .25); c.lineTo(x + R * .78, hip + R * .25); c.quadraticCurveTo(x + R * .8, neck + R * .2, x + R * .62, neck); c.closePath(); c.fill(); c.stroke();
    c.fillStyle = sp.coat2; c.beginPath(); c.moveTo(x - R * .22, neck); c.lineTo(x, neck + R * .55); c.lineTo(x + R * .22, neck); c.closePath(); c.fill(); c.stroke();
    c.fillStyle = sp.trim; for (let i = 0; i < 3; i++) { c.beginPath(); c.arc(x, neck + R * (.7 + i * .25), R * .055, 0, 7); c.fill() }
    // head (chars.js), clipped at the neck so its bust is not drawn
    const hy = neck - R * .95, yb = hy + charH * .6; c.save(); c.beginPath(); c.rect(x - R * 3, -H, R * 6, neck + R * .05 + H); c.clip();
    const tk = a.talk && (a.talk === true || (u >= a.talk[0] && u <= a.talk[1])) ? Math.max(0, Math.sin(u * 13) * .6 + Math.sin(u * 7.3 + 1) * .4) : 0;
    if (env.drawChar) env.drawChar(c, x, yb, charH, Object.assign({}, sp, { facing: f, mood: a.mood || 'neutral', talk: tk }), u + x * .001);
    c.restore();
    const hand = arm(f, fa, 1);
    // props
    const pr = a.prop || (['rifle', 'aim', 'fire'].includes(pose) ? 'rifle' : pose === 'toast' ? 'cup' : pose === 'dig' ? 'shovel' : pose === 'hold' ? 'paper' : null);
    if (pr) { c.save(); c.translate(hand[0], hand[1]); c.lineCap = 'round';
      if (pr === 'rifle') { const ang = pose === 'rifle' ? -.9 : -.05; c.rotate(f * ang); c.scale(f, 1); c.strokeStyle = '#3a2614'; c.lineWidth = R * .16; c.beginPath(); c.moveTo(-R * .6, 0); c.lineTo(R * .5, 0); c.stroke(); c.strokeStyle = '#555'; c.lineWidth = R * .08; c.beginPath(); c.moveTo(R * .4, 0); c.lineTo(R * 1.6, 0); c.stroke();
        if (pose === 'fire' && (u % 2.2) < .12) { c.fillStyle = 'rgba(255,220,120,.95)'; c.beginPath(); c.arc(R * 1.75, 0, R * .3, 0, 7); c.fill() } }
      else if (pr === 'cup') { c.fillStyle = '#c9c2b0'; c.fillRect(-R * .14, -R * .38, R * .28, R * .34); c.strokeStyle = INK2; c.lineWidth = 3; c.strokeRect(-R * .14, -R * .38, R * .28, R * .34) }
      else if (pr === 'paper') { c.rotate(-.2 * f); c.fillStyle = '#efe6cf'; c.fillRect(-R * .1, -R * .55, R * .5 * f, R * .65); c.strokeStyle = INK2; c.lineWidth = 3; c.strokeRect(-R * .1, -R * .55, R * .5 * f, R * .65) }
      else if (pr === 'shovel') { const d = Math.sin(u * 3) * .3; c.rotate(f * (.6 + d)); c.strokeStyle = '#5a3a22'; c.lineWidth = R * .1; c.beginPath(); c.moveTo(0, -R * .4); c.lineTo(0, R * 1.2); c.stroke(); c.fillStyle = '#777'; c.fillRect(-R * .2, R * 1.1, R * .4, R * .4) }
      else if (pr === 'coin') { c.fillStyle = '#e8c04a'; c.beginPath(); c.arc(R * .1 * f, -R * .1, R * .16, 0, 7); c.fill() }
      else if (pr === 'lamp') { glow(c, 0, -R * .2, R * 2, '255,190,110', .5); c.fillStyle = '#e8b04a'; c.fillRect(-R * .12, -R * .4, R * .24, R * .3) }
      c.restore() }
    c.restore() }
  function shade2(hex, k) { const n = parseInt((hex || '#555555').slice(1), 16), r = n >> 16, g = (n >> 8) & 255, b = n & 255, m = v => Math.max(0, Math.min(255, Math.round(v + (k < 0 ? v * k : (255 - v) * k)))); return `rgb(${m(r)},${m(g)},${m(b)})` }
  G.SCENE_ACTOR = actor;

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
    graves: (c, W, H, u, p) => {   // a cemetery: rows of headstones and a few crosses, smaller towards the back (p.n per row, p.rows, p.col)
      const rows = p.rows || 3, n = p.n || 9, y0 = H * (p.y || .78); c.fillStyle = p.col || '#a8a294'; c.strokeStyle = 'rgba(20,15,10,.7)'; c.lineWidth = 3;
      for (let r = 0; r < rows; r++) { const s = .55 + r * .25, y = y0 + r * H * .06, gap = W / (n - .5);
        for (let i = 0; i < n; i++) { const x = gap * (i + (r % 2 ? .5 : .25)) + Math.sin(i * 7.1 + r * 3) * 12, h = 70 * s, w = 38 * s;
          if ((i + r * 2) % 5 === 2) { c.fillRect(x - w * .14, y - h * 1.15, w * .28, h * 1.15); c.fillRect(x - w * .5, y - h * .85, w, w * .28) }
          else { c.beginPath(); c.moveTo(x - w / 2, y); c.lineTo(x - w / 2, y - h + w / 2); c.arc(x, y - h + w / 2, w / 2, Math.PI, 0); c.lineTo(x + w / 2, y); c.fill(); c.stroke() } } } },
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
    actors: (c, W, H, u, p, S) => { const env = S._env || {}; for (const a of [...(p.list || [])].sort((m, n) => (m.y || .9) - (n.y || .9))) actor(c, W, H, a, u, env) },
    people: (c, W, H, u, p, S) => { for (const q of (p.list || [])) {
        if (q.photo && IMG[`photos/${S._story}/${q.photo}-fg.png`]) { const im = IMG[`photos/${S._story}/${q.photo}-fg.png`], h = H * (q.h || .8), w = im.width * h / im.height, x = W * q.x - w / 2, y = H * (q.y || 1.02) - h + Math.sin(u * 1.5 + q.x * 9) * 3;
          c.save(); c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 30; c.drawImage(im, x, y, w, h); c.restore(); continue }
        if (S._env && S._env.drawChar) {   // owner, 15 Nov 2026: acting cartoon characters instead of black silhouettes
          const pose = q.pose === 'lean' ? 'think' : q.pose || (['hips', 'cross', 'idle', 'shrug'][Math.floor(rnd(q.x * 31) * 4)]);
          actor(c, W, H, { preset: q.preset || p.preset || (q.hat === 'wide' ? 'settler' : 'civilian'), spec: q.spec, x: q.x, y: Math.min(.97, (q.y || 1.04) - .06), h: (q.h || .8) * .78, facing: q.facing, pose, mood: q.mood, talk: q.talk, act: q.act, walk: q.walk, prop: q.prop }, u + q.x * 3, S._env); continue }
        figure(c, W, H, W * q.x, H * (q.y || 1.04), H * (q.h || .8), q, u + q.x * 10, W * (p.lx || .5), H * (p.ly || .4), p.warm || '255,170,90') } },
    // ---- Miami / 20th-century parts (The Real Vice City, 19 Nov 2026) ----
    palms: (c, W, H, u, p) => {   // a row of palm trees; wind (0-1) bends them, storm makes them thrash
      const y = H * (p.y || .74), n = p.n || 7, wind = p.wind || .15;
      for (let i = 0; i < n; i++) { const x = W * ((p.x0 != null ? p.x0 : .04) + i * (p.gap || .14) + (rnd(i * 3 + (p.seed || 1)) - .5) * .04), h = (p.h || 420) * (.75 + rnd(i + 7 + (p.seed || 1)) * .45);
        const sway = Math.sin(u * (1.2 + wind * 3) + i) * (12 + wind * 60) + wind * 120, tx = x + sway, ty = y - h;
        c.strokeStyle = p.col || '#3a2a1a'; c.lineCap = 'round'; c.lineWidth = 16 * (h / 420); c.beginPath(); c.moveTo(x, y); c.quadraticCurveTo(x + sway * .2 + (rnd(i) - .5) * 60, y - h * .5, tx, ty); c.stroke();
        c.strokeStyle = p.leaf || '#22381c'; c.lineWidth = 7 * (h / 420);
        for (let k = 0; k < 9; k++) { const a = -Math.PI / 2 + (k - 4) * .38 + Math.sin(u * (2 + wind * 6) + k + i) * (.05 + wind * .25) + wind * .6, L = 150 * (h / 420) * (.8 + rnd(k + i) * .4);
          const ex = tx + Math.cos(a) * L, ey = ty + Math.sin(a) * L * .55 + L * .35; c.beginPath(); c.moveTo(tx, ty); c.quadraticCurveTo(tx + Math.cos(a) * L * .55, ty + Math.sin(a) * L * .6 - 20, ex, ey); c.stroke() } } },
    city: (c, W, H, u, p) => {   // a modern skyline: towers, lit windows at night, neon trims
      const y = H * (p.y || .7), n = p.n || 16, night = p.night;
      for (let i = 0; i < n; i++) { const w = 70 + rnd(i * 5 + (p.seed || 2)) * 110, h = (p.h || 360) * (.4 + rnd(i * 7 + (p.seed || 2)) * .9), x = (W + 200) * i / n - 100 + rnd(i) * 30;
        c.fillStyle = p.col || (night ? '#141826' : '#5a6474'); c.fillRect(x, y - h, w, h);
        for (let r = 0; r < h / 26 - 1; r++) for (let k = 0; k < w / 22 - 1; k++) { const on = rnd(i * 31 + r * 7 + k) > (night ? .55 : 2);
          c.fillStyle = on ? 'rgba(255,214,140,.85)' : night ? 'rgba(40,50,70,.6)' : 'rgba(200,215,230,.35)'; c.fillRect(x + 8 + k * 22, y - h + 10 + r * 26, 12, 14) }
        if (p.neon && rnd(i + 99) > .55) { const col = ['255,60,170', '40,220,255', '255,140,40'][i % 3]; c.save(); c.globalCompositeOperation = 'lighter'; c.strokeStyle = `rgba(${col},${.7 + Math.sin(u * 3 + i) * .2})`; c.lineWidth = 5; c.shadowColor = `rgb(${col})`; c.shadowBlur = 24; c.strokeRect(x + 4, y - h + 4, w - 8, h * .12); c.restore() } }
      if (night) glow(c, W / 2, y, W * .7, '255,90,180', .06) },
    deco: (c, W, H, u, p) => {   // Art Deco hotel fronts in pastel, with neon signs at night
      const y = H * (p.y || .78), n = p.n || 5, cols = ['#f2b5c4', '#a8e0d8', '#f6e0a8', '#c8b8f0', '#f4f0e6'], words = p.words || ['HOTEL', 'BAR', 'CAFE', 'HOTEL', 'GRILL'];
      for (let i = 0; i < n; i++) { const w = W / n - 30, x = i * W / n + 15, h = (p.h || 360) * (.85 + rnd(i + 3) * .3);
        c.fillStyle = p.night ? '#3a3448' : cols[i % cols.length]; c.fillRect(x, y - h, w, h); c.fillRect(x + w * .35, y - h - 60, w * .3, 60);
        c.fillStyle = 'rgba(0,0,0,.18)'; for (let r = 0; r < 3; r++) c.fillRect(x + 20, y - h + 60 + r * 90, w - 40, 14);
        c.fillStyle = p.night ? 'rgba(255,210,140,.7)' : 'rgba(40,60,80,.55)'; for (let r = 0; r < 3; r++) for (let k = 0; k < 4; k++) c.fillRect(x + 22 + k * (w - 44) / 4, y - h + 84 + r * 90, (w - 44) / 4 - 14, 40);
        if (p.night || p.neon) { const col = ['255,60,170', '40,220,255', '255,180,60'][i % 3]; c.save(); c.globalCompositeOperation = 'lighter'; c.font = `700 ${Math.round(w * .16)}px ${BODY}`; c.textAlign = 'center';
          c.fillStyle = `rgba(${col},${rnd(Math.floor(u * 6) + i) > .08 ? .95 : .3})`; c.shadowColor = `rgb(${col})`; c.shadowBlur = 30; c.fillText(words[i % words.length], x + w / 2, y - h + 40); c.restore() } } },
    neon: (c, W, H, u, p) => { const x = W * (p.x || .5), y = H * (p.y || .3), col = p.col || '255,60,170'; c.save(); c.globalCompositeOperation = 'lighter'; c.font = `700 ${p.size || 110}px ${BODY}`; c.textAlign = 'center';
      c.fillStyle = `rgba(${col},${rnd(Math.floor(u * 8)) > .1 ? .95 : .25})`; c.shadowColor = `rgb(${col})`; c.shadowBlur = 50; c.fillText(p.text || 'VICE', x, y); c.restore() },
    boats: (c, W, H, u, p) => {   // small overloaded boats, bobbing, people standing shoulder to shoulder
      const y = H * (p.y || .7), n = p.n || 4;
      for (let i = 0; i < n; i++) { const s = (p.s || .7) * (1 - i * .12), x = W * ((p.x || .15) + i * (p.gap || .22)) + Math.sin(u * .3 + i) * 20 + (p.drift || 0) * u * 6, b = Math.sin(u * 1.4 + i * 1.7) * 8, yy = y + i * 18 * s + b;
        c.save(); c.translate(x, yy); c.scale(s, s); c.rotate(Math.sin(u * 1.1 + i) * .03);
        c.fillStyle = ['#d8d2c4', '#3a5a7a', '#8a3a2a', '#e8e0c8'][i % 4]; c.beginPath(); c.moveTo(-260, -60); c.lineTo(260, -60); c.lineTo(200, 30); c.lineTo(-220, 30); c.closePath(); c.fill();
        c.fillStyle = 'rgba(0,0,0,.25)'; c.fillRect(-250, -40, 500, 10); c.fillStyle = '#ece6d6'; c.fillRect(60, -150, 90, 90);
        if (p.crowded !== false) for (let k = 0; k < 22; k++) { const px = -230 + k * 21 + rnd(k + i) * 6, ph = 70 + rnd(k * 3 + i) * 25; c.fillStyle = ['#2a2420', '#4a3a30', '#6a4a3a', '#1a1a22'][k % 4];
          c.beginPath(); c.arc(px, -60 - ph, 11, 0, 7); c.fill(); c.fillRect(px - 9, -60 - ph + 8, 18, ph - 8) }
        c.restore() } },
    car: (c, W, H, u, p) => {   // a 1970s/80s car: sedan, van ("text" on the side) or police (lights); drive: [x0, x1, t0, t1]
      const s = p.s || 1, k = p.kind || 'sedan', y = H * Math.min(p.y || .86, .8 + .05 / s); let x = W * (p.x || .5);   // never let a car sink below the frame
      if (p.drive) { const [a, b, t0, t1] = p.drive, f = clamp((u - t0) / Math.max(.1, t1 - t0), 0, 1); x = W * lerp(a, b, io(f)) }
      c.save(); c.translate(x, y); c.scale(s * (p.facing || 1), s); const body = p.col || (k === 'police' ? '#e8e8e8' : k === 'van' ? '#f0ece0' : '#7a2a2a');
      c.fillStyle = 'rgba(0,0,0,.35)'; c.beginPath(); c.ellipse(0, 4, 240, 18, 0, 0, 7); c.fill();
      c.fillStyle = body; if (k === 'van') { c.beginPath(); c.roundRect(-230, -210, 440, 180, 18); c.fill(); c.fillStyle = '#2a3440'; c.fillRect(150, -190, 55, 60) }
      else { c.beginPath(); c.roundRect(-240, -100, 480, 70, 14); c.fill(); c.beginPath(); c.moveTo(-130, -100); c.lineTo(-80, -160); c.lineTo(90, -160); c.lineTo(140, -100); c.closePath(); c.fill(); c.fillStyle = '#2a3440'; c.fillRect(-70, -150, 70, 44); c.fillRect(10, -150, 70, 44) }
      if (k === 'police') { c.fillStyle = '#1f3a6a'; c.fillRect(-240, -80, 480, 18); const on = Math.floor(u * 6) % 2; c.fillStyle = on ? '#ff2a2a' : '#2a6aff'; c.fillRect(-30, -178, 60, 18); glow(c, 0, -170, 160, on ? '255,40,40' : '40,110,255', .5) }
      if (p.text) { c.fillStyle = p.textCol || '#b3202a'; c.font = `700 30px ${BODY}`; c.textAlign = 'center'; String(p.text).split('|').forEach((ln, i) => c.fillText(ln, -10, -150 + i * 36)) }
      c.fillStyle = '#111'; for (const wx of [-150, 150]) { c.beginPath(); c.arc(wx, -28, 38, 0, 7); c.fill(); c.fillStyle = '#888'; c.beginPath(); c.arc(wx, -28, 14, 0, 7); c.fill(); c.fillStyle = '#111' }
      c.restore() },
    bus: (c, W, H, u, p) => {   // a city bus (Havana's route 79 Leyland); drive: [x0, x1, t0, t1]
      const s = p.s || 1, y = H * Math.min(p.y || .86, .82 + .04 / s); let x = W * (p.x || .5);
      if (p.drive) { const [a, b, t0, t1] = p.drive, f = clamp((u - t0) / Math.max(.1, t1 - t0), 0, 1); x = W * lerp(a, b, f * f) }
      c.save(); c.translate(x, y); c.scale(s * (p.facing || 1), s); c.fillStyle = 'rgba(0,0,0,.35)'; c.beginPath(); c.ellipse(0, 4, 380, 20, 0, 0, 7); c.fill();
      c.fillStyle = p.col || '#d8c070'; c.beginPath(); c.roundRect(-380, -260, 760, 230, 22); c.fill(); c.fillStyle = '#6a3a2a'; c.fillRect(-380, -110, 760, 16);
      c.fillStyle = '#2a3440'; for (let i = 0; i < 6; i++) c.fillRect(-340 + i * 112, -230, 90, 80);
      c.fillStyle = '#111'; c.font = `700 44px ${BODY}`; c.textAlign = 'center'; c.fillText(p.route || '79', 330, -180);
      c.fillStyle = '#111'; for (const wx of [-250, 240]) { c.beginPath(); c.arc(wx, -28, 44, 0, 7); c.fill() } c.restore() },
    trench: (c, W, H, u, p) => {   // a WW1 trench seen end-on: earth walls, sandbag parapet, fire step, duckboards, wet floor (p.y floor line, p.w width, p.wet)
      const y = H * (p.y || .9), cx = W * (p.x || .5), w = W * (p.w || .62), top = H * (p.top || .38), mud = p.col || '#4b3a28';
      c.fillStyle = shade2(mud, -.25); c.fillRect(-300, top - 40, W + 600, y - top + 400);
      c.fillStyle = mud; c.beginPath(); c.moveTo(-300, top); c.lineTo(cx - w / 2, top + 30); c.lineTo(cx - w / 2 + 60, y); c.lineTo(cx + w / 2 - 60, y); c.lineTo(cx + w / 2, top + 30); c.lineTo(W + 300, top); c.lineTo(W + 300, H + 300); c.lineTo(-300, H + 300); c.closePath(); c.fill();
      for (let i = 0; i < 26; i++) { const sx = -40 + i * (W + 80) / 26, sy = top - 26 + (i % 2) * 6; c.fillStyle = i % 3 ? '#8a7a58' : '#7a6a4a'; c.beginPath(); c.roundRect(sx, sy, (W + 80) / 26 + 6, 30, 10); c.fill(); c.strokeStyle = '#2a2016'; c.lineWidth = 2; c.stroke() }
      c.fillStyle = shade2(mud, .12); c.fillRect(cx - w / 2 + 30, y - 120, 120, 120); c.fillStyle = 'rgba(0,0,0,.25)'; c.fillRect(cx - w / 2 + 30, y - 120, 120, 8);
      for (let x = cx - w / 2 + 70; x < cx + w / 2 - 70; x += 46) { c.fillStyle = '#5a4630'; c.fillRect(x, y - 10, 38, 12) }
      c.strokeStyle = 'rgba(30,20,10,.6)'; c.lineWidth = 3; for (let x = cx - w / 2 + 10; x < cx + w / 2; x += 90) { c.beginPath(); c.moveTo(x, top + 40); c.lineTo(x + 14, y - 20); c.stroke() }
      if (p.wet) { c.fillStyle = 'rgba(120,130,130,.35)'; c.fillRect(cx - w / 2 + 60, y - 4, w - 120, 18) } },
    wire: (c, W, H, u, p) => {   // barbed wire on posts across no man's land (p.y, p.h, p.x0, p.x1)
      const y = H * (p.y || .8), h = p.h || 90, x0 = W * (p.x0 || -.05), x1 = W * (p.x1 || 1.05); c.strokeStyle = p.col || '#2a2622'; c.lineWidth = 5;
      for (let x = x0; x < x1; x += 160) { c.beginPath(); c.moveTo(x, y + 6); c.lineTo(x + 8, y - h); c.stroke() }
      c.lineWidth = 2; for (let x = x0; x < x1; x += 18) { const r = h * .4; c.beginPath(); c.ellipse(x, y - h * .5, r * .45, r, 0, 0, 7); c.stroke() }
      c.lineWidth = 2; for (const f of [.25, .7]) { c.beginPath(); c.moveTo(x0, y - h * f); for (let x = x0; x < x1; x += 30) c.lineTo(x, y - h * f + Math.sin(x) * 4); c.stroke() } },
    craters: (c, W, H, u, p) => {   // a shell-torn field: overlapping craters, some with water, broken tree stumps (p.n, p.seed, p.water)
      const n = p.n || 9, y0 = H * (p.y || .7); for (let i = 0; i < n; i++) { const x = rnd(i + (p.seed || 3)) * W, y = y0 + rnd(i * 7 + 1) * (H - y0) * .8, r = 80 + rnd(i * 3 + 2) * 120;
        c.fillStyle = 'rgba(20,14,8,.55)'; c.beginPath(); c.ellipse(x, y, r, r * .28, 0, 0, 7); c.fill(); c.fillStyle = 'rgba(110,90,60,.5)'; c.beginPath(); c.ellipse(x, y - r * .2, r * 1.05, r * .12, 0, Math.PI, 0); c.fill();
        if (p.water && i % 2 === 0) { c.fillStyle = 'rgba(140,150,150,.45)'; c.beginPath(); c.ellipse(x, y + r * .04, r * .7, r * .15, 0, 0, 7); c.fill() } }
      c.fillStyle = '#2a2018'; for (let i = 0; i < (p.stumps || 4); i++) { const x = rnd(i * 11 + 5) * W, h = 120 + rnd(i * 13) * 160; c.beginPath(); c.moveTo(x - 12, y0 + 10); c.lineTo(x - 6, y0 - h); c.lineTo(x + 4, y0 - h + 20); c.lineTo(x + 12, y0 + 10); c.fill() } },
    fence: (c, W, H, u, p) => { const y = H * (p.y || .84), x0 = W * (p.x0 || 0), x1 = W * (p.x1 || 1), h = p.h || 220, br = p.broken;
      c.strokeStyle = p.col || '#2a2a2a'; c.lineWidth = 6; for (let x = x0; x < x1; x += 40) { if (br && Math.abs(x - W * br) < 140) continue; c.beginPath(); c.moveTo(x, y); c.lineTo(x, y - h); c.stroke() }
      c.lineWidth = 4; for (const f of [.15, .55, .95]) { c.beginPath(); c.moveTo(x0, y - h * f); if (br) { c.lineTo(W * br - 140, y - h * f); c.moveTo(W * br + 140, y - h * f) } c.lineTo(x1, y - h * f); c.stroke() } },
    highway: (c, W, H, u, p) => {   // an elevated expressway on concrete pillars, traffic lights streaming
      const y = H * (p.y || .45), t = p.t || 46; c.fillStyle = p.col || '#8a8a86'; c.fillRect(-300, y, W + 600, t); c.fillStyle = 'rgba(0,0,0,.25)'; c.fillRect(-300, y + t, W + 600, 14);
      for (let x = 60; x < W; x += 300) { c.fillStyle = '#7a7a76'; c.fillRect(x, y + t, 60, H); c.fillStyle = 'rgba(0,0,0,.18)'; c.fillRect(x + 40, y + t, 20, H) }
      c.save(); c.globalCompositeOperation = 'lighter'; for (let i = 0; i < 12; i++) { const x = ((u * 260 + i * 260) % (W + 400)) - 200; glow(c, x, y - 10, 40, i % 2 ? '255,230,180' : '255,60,40', .7) } c.restore() },
    houses: (c, W, H, u, p) => {   // small wooden houses with porches (Overtown, Colored Town)
      const y = H * (p.y || .78), n = p.n || 6, cols = ['#d8c8a8', '#a8b8a0', '#e8d0b8', '#b8a898', '#c8d8d8'];
      for (let i = 0; i < n; i++) { const w = W / n - 40, x = i * W / n + 20, h = 170 + rnd(i + (p.seed || 4)) * 40; c.fillStyle = cols[i % 5]; c.fillRect(x, y - h, w, h);
        c.fillStyle = '#4a3a2a'; c.beginPath(); c.moveTo(x - 20, y - h); c.lineTo(x + w / 2, y - h - 90); c.lineTo(x + w + 20, y - h); c.closePath(); c.fill();
        c.fillStyle = p.night ? 'rgba(255,200,120,.8)' : '#2a3440'; c.fillRect(x + w * .15, y - h + 40, w * .22, 50); c.fillRect(x + w * .63, y - h + 40, w * .22, 50); c.fillStyle = '#3a2a1a'; c.fillRect(x + w * .42, y - 100, w * .16, 100);
        c.fillStyle = '#6a5a4a'; c.fillRect(x - 10, y - 110, w + 20, 10); for (let k = 0; k < 5; k++) c.fillRect(x - 5 + k * (w + 10) / 4, y - 110, 6, 110) } },
    train: (c, W, H, u, p) => {   // a steam train crossing (Flagler's railway, 1896)
      const y = H * (p.y || .8); let x = W * (p.x || .5); if (p.drive) { const [a, b, t0, t1] = p.drive, f = clamp((u - t0) / Math.max(.1, t1 - t0), 0, 1); x = W * lerp(a, b, f) }
      c.fillStyle = '#3a2a1a'; c.fillRect(-300, y + 6, W + 600, 10); c.save(); c.translate(x, y); c.scale(p.s || 1, p.s || 1);
      c.fillStyle = '#1c1c20'; c.fillRect(-260, -150, 300, 130); c.fillRect(40, -200, 150, 180); c.fillRect(-200, -220, 40, 70); c.fillStyle = '#b3202a'; c.fillRect(-260, -40, 450, 14);
      for (let k = 1; k < 4; k++) { c.fillStyle = k % 2 ? '#5a3a22' : '#4a3020'; c.fillRect(-260 - k * 330, -170, 310, 150); c.fillStyle = 'rgba(255,220,150,.6)'; for (let w = 0; w < 4; w++) c.fillRect(-240 - k * 330 + w * 72, -150, 50, 40) }
      c.fillStyle = '#111'; for (let k = -12; k < 3; k++) { c.beginPath(); c.arc(k * 85, -14, 26, 0, 7); c.fill() } c.restore();
      smoke(c, x - 180 * (p.s || 1), y - 220 * (p.s || 1), u, 260, .25, 3) },
    tv: (c, W, H, u, p) => {   // a TV / monitor glowing in a dark room, a neon city on screen (generic, never a game's own art)
      const x = W * (p.x || .5), y = H * (p.y || .55), w = p.w || 760, h = w * .56; c.fillStyle = '#0c0c10'; c.beginPath(); c.roundRect(x - w / 2 - 24, y - h / 2 - 24, w + 48, h + 48, 18); c.fill();
      const g = c.createLinearGradient(0, y - h / 2, 0, y + h / 2); g.addColorStop(0, '#ff5aa8'); g.addColorStop(.55, '#ffb35a'); g.addColorStop(.56, '#1a2a4a'); g.addColorStop(1, '#0a1020'); c.fillStyle = g; c.fillRect(x - w / 2, y - h / 2, w, h);
      c.save(); c.beginPath(); c.rect(x - w / 2, y - h / 2, w, h); c.clip(); c.fillStyle = '#ffd27a'; c.beginPath(); c.arc(x, y + h * .05, h * .22, Math.PI, 0); c.fill();
      for (let i = 0; i < 14; i++) { const bw = w / 18, bh = h * (.15 + rnd(i + 5) * .35), bx = x - w / 2 + i * w / 14; c.fillStyle = '#1a1028'; c.fillRect(bx, y + h * .06 - bh, bw, bh) }
      for (let i = 0; i < 5; i++) { const px = x - w / 2 + (i + .5) * w / 5 + Math.sin(u + i) * 4; c.strokeStyle = '#0c1a14'; c.lineWidth = 6; c.beginPath(); c.moveTo(px, y + h / 2); c.lineTo(px + 8, y + h * .1); c.stroke() }
      c.restore(); glow(c, x, y, w * .9, '255,120,180', .25); c.fillStyle = '#0c0c10'; c.fillRect(x - 40, y + h / 2 + 24, 80, H) },
    shopfront: (c, W, H, u, p) => {   // a store front in a shopping centre, its sign lettered on (e.g. CROWN LIQUORS)
      const y = H * (p.y || .82), x = W * (p.x || .5), w = p.w || 1100, h = p.h || 480; c.fillStyle = p.col || '#d8d0c0'; c.fillRect(x - w / 2, y - h, w, h);
      c.fillStyle = '#2a3440'; c.fillRect(x - w / 2 + 40, y - h + 150, w - 80, h - 150); c.fillStyle = 'rgba(200,220,240,.18)'; c.fillRect(x - w / 2 + 40, y - h + 150, w - 80, 40);
      c.fillStyle = p.signCol || '#b3202a'; c.fillRect(x - w / 2 + 60, y - h + 30, w - 120, 90); c.fillStyle = '#fff'; c.font = `700 64px ${BODY}`; c.textAlign = 'center'; c.fillText(p.text || 'STORE', x, y - h + 98) },
  };
  SH['set'] = (c, W, H, S, t, env) => {
    const u = S.u, C = cam(S, W, H), tm = S.time || 'day', sky = SKY[S.weather === 'storm' ? 'storm' : tm] || SKY.day; S._story = env.story; S._env = env;
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
