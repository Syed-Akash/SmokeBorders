// Smoke & Borders cinematic scenes (owner, 11 Nov 2026: "viewers should feel like they are watching a movie").
// Full-screen illustrated shots drawn on the canvas, with depth layers that move as the camera drifts, practical light, rain,
// smoke and dust, silhouettes that breathe and move, cinema bars and a film grade. The story cuts between shots
// like a film, and returns to the map when the map explains something.
// API: SCENE(ctx, W, H, S, t, env) where S = {shot, u (seconds into the shot), dur, ...options}; env = {LAND, d3, drawChar, PRESETS}
// Shots: pentagon-night, office-night, map-desk, faces, village, (more in SCENE_SHOTS)
(function (G) {
  const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v)), lerp = (a, b, u) => a + (b - a) * u,
    io = u => { u = clamp(u); return u < .5 ? 4 * u * u * u : 1 - Math.pow(-2 * u + 2, 3) / 2 }, o3 = u => 1 - Math.pow(1 - clamp(u), 3),
    rnd = i => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x) };
  const TYPE = '"Courier Prime", "Courier New", monospace', SERIF = '"Playfair Display", Georgia, serif', BODY = '"Barlow Semi Condensed", Arial, sans-serif';
  const BAR = 132;   // cinema bars (about 2.35:1)
  let OFF = null;
  const off = (W, H, i = 0) => { OFF = OFF || []; if (!OFF[i]) { const c = document.createElement('canvas'); c.width = W; c.height = H; OFF[i] = c } const x = OFF[i].getContext('2d'); x.setTransform(1, 0, 0, 1, 0, 0); x.globalAlpha = 1; x.globalCompositeOperation = 'source-over'; x.filter = 'none'; x.clearRect(0, 0, W, H); return [OFF[i], x] };

  // parts of a shot that don't move are drawn once per shot into a canvas 300 px bigger on every side, then reused
  const CACHE = {};
  function cached(key, W, H, draw) { if (!CACHE[key]) { for (const k in CACHE) delete CACHE[k] && 0; const cv = document.createElement('canvas'); cv.width = W + 600; cv.height = H + 600; const x = cv.getContext('2d'); x.translate(300, 300); draw(x); CACHE[key] = cv } return CACHE[key] }
  // ---------- shared pieces ----------
  function glow(c, x, y, r, col, a) { const g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, `rgba(${col},${a})`); g.addColorStop(.35, `rgba(${col},${a * .35})`); g.addColorStop(1, `rgba(${col},0)`);
    c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = g; c.fillRect(x - r, y - r, 2 * r, 2 * r); c.restore() }
  function rain(c, W, H, t, n = 420, a = .32, slant = .18, lit) {
    c.save(); c.lineCap = 'round';
    for (let i = 0; i < n; i++) {
      const sp = 1500 + rnd(i) * 900, len = 26 + rnd(i + 3) * 40, x0 = rnd(i + 7) * (W + 300) - 150, y = ((rnd(i + 11) * (H + 200) + t * sp) % (H + 200)) - 100, x = x0 + (y + 100) * slant;
      let al = a * (.35 + rnd(i + 5) * .65); if (lit) { const d = Math.hypot(x - lit[0], y - lit[1]); al += Math.max(0, 1 - d / lit[2]) * .7 }
      c.strokeStyle = `rgba(200,215,235,${al})`; c.lineWidth = rnd(i + 9) > .8 ? 2 : 1.2; c.beginPath(); c.moveTo(x, y); c.lineTo(x - len * slant, y - len); c.stroke()
    } c.restore() }
  function smoke(c, x, y, t, h = 320, a = .16, seed = 1) {   // a curling ribbon of cigarette smoke
    c.save(); c.globalCompositeOperation = 'screen';
    for (let k = 0; k < 5; k++) { c.beginPath(); for (let s = 0; s <= 40; s++) { const f = s / 40, yy = y - f * h, w = 6 + f * 60,
        xx = x + Math.sin(f * 7 - t * 1.3 + k * .9 + seed) * w * (.5 + .5 * Math.sin(t * .4 + k)) + Math.sin(f * 2.3 + t * .3) * f * 40;
        s ? c.lineTo(xx, yy) : c.moveTo(xx, yy) }
      c.strokeStyle = `rgba(225,215,200,${a * (1 - k * .15)})`; c.lineWidth = 3 + k * 7; c.globalAlpha = .55; c.stroke() }
    c.restore() }
  function dust(c, cx, cy, rx, ry, t, n = 70, col = '255,225,170') { c.save(); c.globalCompositeOperation = 'lighter';
    for (let i = 0; i < n; i++) { const a = rnd(i) * 6.283 + t * (.05 + rnd(i + 2) * .1), r = Math.sqrt(rnd(i + 4)), x = cx + Math.cos(a) * rx * r + Math.sin(t * .5 + i) * 8, y = cy + Math.sin(a) * ry * r - ((t * 6 + i * 13) % 40);
      c.fillStyle = `rgba(${col},${.25 + .35 * Math.sin(t * 2 + i) ** 2})`; c.beginPath(); c.arc(x, y, .8 + rnd(i + 6) * 1.6, 0, 7); c.fill() } c.restore() }
  // a standing person as a dark shape, lit on one side by a light at (lx, ly). pose: stand | lean | arms | point
  function figure(c, W, H, x, foot, h, o, t, lx, ly, warm = '255,170,90') {
    const [oc, k] = off(W, H, 3), s = h / 1000, br = Math.sin(t * 1.6 + x) * 4 * s, f = o.facing || 1, lean = o.pose === 'lean' ? .22 : 0;
    k.save(); k.translate(x, foot); k.scale(s * f, s); k.fillStyle = '#0b0807';
    const hy = -860 + br + lean * 140, hx = lean * 260;
    // legs
    k.beginPath(); k.moveTo(-95, -470); k.lineTo(-110, 0); k.lineTo(-30, 0); k.lineTo(-5, -380); k.lineTo(25, 0); k.lineTo(105, 0); k.lineTo(95, -470); k.closePath(); k.fill();
    // torso (jacket), leaning forward from the hips
    k.beginPath(); k.moveTo(-120, -460); k.bezierCurveTo(-150, -600, -150 + hx * .6, -720 + br, -135 + hx, -760 + br + lean * 120); k.lineTo(135 + hx, -760 + br + lean * 120);
    k.bezierCurveTo(150 + hx * .6, -720 + br, 150, -600, 120, -460); k.closePath(); k.fill();
    // arms
    const sh = [-135 + hx, -740 + br + lean * 120], sh2 = [135 + hx, -740 + br + lean * 120];
    const limb = (a, b, cc, w) => { k.beginPath(); k.lineCap = 'round'; k.lineJoin = 'round'; k.lineWidth = w; k.strokeStyle = '#0b0807'; k.moveTo(...a); k.lineTo(...b); k.lineTo(...cc); k.stroke() };
    if (o.pose === 'lean') { limb(sh, [-120 + hx * 1.2, -560], [-60 + hx * 1.5, -470], 62); limb(sh2, [190 + hx, -560], [230 + hx, -470], 62) }
    else if (o.pose === 'arms') { limb(sh, [-150, -560], [60, -600], 62); limb(sh2, [150, -560], [-60, -620], 62) }
    else if (o.pose === 'point') { const r = Math.sin(t * .8) * 10; limb(sh, [-160, -580], [-150, -440], 60); limb(sh2, [240 + hx, -700 + r], [360 + hx, -600 + r], 58) }
    else { limb(sh, [-165, -580], [-160, -430], 60); limb(sh2, [165, -580], [160, -430], 60) }
    // neck, head, officer's cap
    k.fillRect(-28 + hx, hy + 70, 56, 70); k.beginPath(); k.ellipse(hx, hy, 66, 82, 0, 0, 7); k.fill();
    if (o.hat === 'wide') { k.beginPath(); k.ellipse(hx, hy - 50, 150, 26, 0, 0, 7); k.fill(); k.beginPath(); k.ellipse(hx, hy - 80, 78, 46, 0, 0, 7); k.fill() }   // settler's hat
    else if (o.cap !== false) { k.beginPath(); k.ellipse(hx + 6, hy - 52, 92, 34, -.06, 0, 7); k.fill(); k.beginPath(); k.moveTo(hx - 70, hy - 50); k.lineTo(hx + 110, hy - 40); k.lineTo(hx + 130, hy - 22); k.lineTo(hx - 40, hy - 30); k.fill() }
    k.restore();
    // rim light from the lamp
    k.save(); k.globalCompositeOperation = 'source-atop'; const g = k.createRadialGradient(lx, ly, 10, lx, ly, h * .75); g.addColorStop(0, `rgba(${warm},.42)`); g.addColorStop(.4, `rgba(${warm},.1)`); g.addColorStop(1, `rgba(${warm},0)`);
    k.fillStyle = g; k.fillRect(0, 0, W, H); k.restore();
    c.drawImage(oc, 0, 0) }
  // camera: slow push and drift for the whole shot, and per-layer parallax
  function cam(S, W, H) { const d = S.dur || 8, k = io(clamp(S.u / d)), z = 1 + (S.push == null ? .07 : S.push) * k, p = S.pan || [0, 0]; return { z, x: p[0] * k, y: p[1] * k, k } }
  function layer(c, C, W, H, depth, fn) { c.save(); const z = 1 + (C.z - 1) * depth; c.translate(W / 2, H / 2); c.scale(z, z); c.translate(-W / 2 - C.x * depth, -H / 2 - C.y * depth); fn(); c.restore() }

  // ---------- shots ----------
  const SH = {};
  SH['pentagon-night'] = (c, W, H, S, t) => {   // exterior at night in the rain: a long low building, rows of lit windows, a car passing
    const C = cam(S, W, H), u = S.u, fl = S.lightning ? Math.max(0, ...[].concat(S.lightning).map(a => (u > a && u < a + .5) ? (1 - (u - a) / .5) * (Math.sin((u - a) * 60) > 0 ? 1 : .4) : 0)) : 0;
    layer(c, C, W, H, .15, () => { const g = c.createLinearGradient(0, 0, 0, H * .62); g.addColorStop(0, '#060b16'); g.addColorStop(1, '#1b2740'); c.fillStyle = g; c.fillRect(-200, -200, W + 400, H + 400);
      for (let i = 0; i < 9; i++) { const x = ((rnd(i) * W * 1.4 + u * 12 * (1 + rnd(i + 1))) % (W * 1.4)) - W * .2, y = 80 + rnd(i + 2) * 360, r = 260 + rnd(i + 3) * 300;
        const g2 = c.createRadialGradient(x, y, 0, x, y, r); g2.addColorStop(0, `rgba(60,75,105,${.35 + fl * .5})`); g2.addColorStop(1, 'rgba(60,75,105,0)'); c.fillStyle = g2; c.fillRect(x - r, y - r, 2 * r, 2 * r) }
      if (fl) { c.fillStyle = `rgba(190,205,255,${fl * .35})`; c.fillRect(-200, -200, W + 400, H + 400) } });
    layer(c, C, W, H, .35, () => { c.fillStyle = '#0a0f19'; c.beginPath(); c.moveTo(-200, H * .6); for (let x = -200; x <= W + 200; x += 30) c.lineTo(x, H * .57 - 18 * (rnd(x * .37) + Math.sin(x * .01) * .5)); c.lineTo(W + 200, H * .62); c.lineTo(-200, H * .62); c.fill() });
    const bld = (refl, c) => {   // the building, two faces meeting at a corner (five storeys)
      const cx = W * .56, top = H * .40, bot = H * .66, Ltop = H * .52, Rtop = H * .515;
      const faces = [[[-260, Ltop], [cx, top], [cx, bot], [-260, bot]], [[cx, top], [W + 260, Rtop], [W + 260, bot], [cx, bot]]];
      faces.forEach((F, fi) => { c.beginPath(); F.forEach((p, i) => i ? c.lineTo(...p) : c.moveTo(...p)); c.closePath(); c.fillStyle = fi ? '#182133' : '#121a2a'; c.fill();
        c.strokeStyle = `rgba(150,170,210,${.25 + fl * .4})`; c.lineWidth = 2; c.beginPath(); c.moveTo(...F[0]); c.lineTo(...F[1]); c.stroke();
        const cols = fi ? 44 : 52;
        for (let j = 0; j < cols; j++) for (let r = 0; r < 5; r++) {
          const a = (j + .2) / cols, b = (j + .75) / cols, ty = v => lerp(F[0][1], F[1][1], v), X = v => lerp(F[0][0], F[1][0], v);
          const y0 = lerp(ty(a), bot, (r + .25) / 5.3), y1 = lerp(ty(a), bot, (r + .78) / 5.3), id = fi * 1000 + j * 7 + r, on = rnd(id) > .62;
          if (!on && !fl) continue; c.fillStyle = on ? `rgba(255,${190 + rnd(id + 4) * 40 | 0},${110 + rnd(id + 5) * 50 | 0},${.55 + rnd(id + 3) * .4})` : `rgba(120,140,190,${fl * .4})`;
          c.fillRect(X(a), y0, X(b) - X(a), y1 - y0) }
        if (!refl) { c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createLinearGradient(0, top, 0, bot); g.addColorStop(0, 'rgba(255,170,90,0)'); g.addColorStop(1, 'rgba(255,170,90,.06)'); c.fillStyle = g; c.beginPath(); F.forEach((p, i) => i ? c.lineTo(...p) : c.moveTo(...p)); c.fill(); c.restore() } }) };
    layer(c, C, W, H, .55, () => { c.drawImage(cached('bld' + S.t + fl.toFixed(1), W, H, x => { bld(0, x);
      // wet forecourt with the building mirrored in it (blurred once, when cached)
      const gy = H * .66; x.save(); x.beginPath(); x.rect(-300, gy, W + 600, H); x.clip(); x.fillStyle = '#05080f'; x.fillRect(-300, gy, W + 600, H);
      x.translate(0, gy * 2); x.scale(1, -1); x.globalAlpha = .28; x.filter = 'blur(5px)'; bld(1, x); x.restore() }), -300, -300);
      c.save(); c.globalCompositeOperation = 'lighter'; for (let i = 0; i < 40; i++) { const y = H * .67 + rnd(i) * H * .3, x = rnd(i + 1) * W; c.strokeStyle = `rgba(255,190,120,${.05 + rnd(i + 2) * .06})`; c.lineWidth = 2; c.beginPath(); c.moveTo(x - 40 - Math.sin(u * 3 + i) * 10, y); c.lineTo(x + 40, y); c.stroke() } c.restore() });
    // a car crossing, headlights through the rain
    if (S.car != null) { const k = clamp((u - S.car) / 5.5); if (k > 0 && k < 1) layer(c, C, W, H, .8, () => { const x = lerp(-300, W + 300, k), y = H * .74;
      c.save(); c.globalCompositeOperation = 'lighter'; const g = c.createLinearGradient(x + 90, y, x + 700, y); g.addColorStop(0, 'rgba(255,240,200,.35)'); g.addColorStop(1, 'rgba(255,240,200,0)'); c.fillStyle = g; c.beginPath(); c.moveTo(x + 90, y - 6); c.lineTo(x + 700, y - 60); c.lineTo(x + 700, y + 60); c.closePath(); c.fill(); c.restore();
      c.fillStyle = '#030406'; c.beginPath(); c.moveTo(x - 120, y + 18); c.lineTo(x - 110, y - 20); c.quadraticCurveTo(x - 60, y - 70, x + 10, y - 66); c.quadraticCurveTo(x + 60, y - 60, x + 80, y - 26); c.lineTo(x + 105, y - 22); c.lineTo(x + 110, y + 18); c.closePath(); c.fill();
      c.beginPath(); c.arc(x - 70, y + 18, 20, 0, 7); c.arc(x + 70, y + 18, 20, 0, 7); c.fill(); glow(c, x + 100, y - 8, 70, '255,235,190', .9); glow(c, x - 115, y - 4, 30, '255,40,30', .6) }) }
    // street lamp in the foreground
    layer(c, C, W, H, 1.25, () => { const lx = W * .14, ly = H * .30; c.fillStyle = '#020305'; c.fillRect(lx - 7, ly, 14, H); c.fillRect(lx - 30, ly - 6, 60, 12); c.beginPath(); c.moveTo(lx - 24, ly - 6); c.lineTo(lx - 14, ly - 46); c.lineTo(lx + 14, ly - 46); c.lineTo(lx + 24, ly - 6); c.fill();
      glow(c, lx, ly - 20, 300, '255,200,130', .55); glow(c, lx, ly - 20, 60, '255,230,180', .9); if (S.rain) rain(c, W, H, u + 3, 140, .0, .16, [lx, ly, 280]); else dust(c, lx, ly + 10, 160, 120, u, 30) });
    if (S.rain) rain(c, W, H, u, 380, .22, .16);
  };

  SH['office-night'] = (c, W, H, S, t) => {   // inside: panelled office, rain on the window, a desk lamp, two officers over a map, a wall clock
    const C = cam(S, W, H), u = S.u, L = [W * .47, H * .56], fl = S.lightning ? Math.max(0, ...[].concat(S.lightning).map(a => (u > a && u < a + .45) ? 1 - (u - a) / .45 : 0)) : 0;
    layer(c, C, W, H, .3, () => {
      const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#120c09'); g.addColorStop(1, '#1d140e'); c.fillStyle = g; c.fillRect(-200, -200, W + 400, H + 400);
      c.strokeStyle = 'rgba(0,0,0,.35)'; c.lineWidth = 3; for (let x = -200; x < W + 200; x += 160) { c.beginPath(); c.moveTo(x, -200); c.lineTo(x, H * .72); c.stroke() }
      c.fillStyle = 'rgba(0,0,0,.25)'; c.fillRect(-200, H * .46, W + 400, 10);
      // window with blinds and rain outside
      const wx = 110, wy = 150, ww = 470, wh = 470; c.save(); c.beginPath(); c.rect(wx, wy, ww, wh); c.clip();
      const sg = c.createLinearGradient(0, wy, 0, wy + wh); sg.addColorStop(0, `rgb(${18 + fl * 140},${30 + fl * 140},${55 + fl * 160})`); sg.addColorStop(1, '#0c1424'); c.fillStyle = sg; c.fillRect(wx, wy, ww, wh);
      for (let i = 0; i < 26; i++) { c.fillStyle = `rgba(255,200,130,${.25 + rnd(i) * .3})`; c.fillRect(wx + rnd(i + 1) * ww, wy + wh * .6 + rnd(i + 2) * wh * .3, 6, 9) }
      if (S.rain) rain(c, W, H, u, 120, .25, .1);
      if (S.rain) for (let i = 0; i < 40; i++) { const x = wx + rnd(i + 20) * ww, y = wy + ((rnd(i + 21) * wh + u * (20 + rnd(i + 22) * 60)) % wh); c.fillStyle = 'rgba(190,210,240,.25)'; c.beginPath(); c.ellipse(x, y, 2.5, 4, 0, 0, 7); c.fill() }
      for (let i = 0; i < 18; i++) { const y = wy + i * (wh / 18); c.fillStyle = '#0f0a07'; c.fillRect(wx, y, ww, wh / 18 * .55); c.fillStyle = 'rgba(255,255,255,.04)'; c.fillRect(wx, y, ww, 2) }
      c.restore(); c.strokeStyle = '#0a0705'; c.lineWidth = 18; c.strokeRect(wx, wy, ww, wh);
      // light through the blinds onto the right wall
      c.save(); c.globalCompositeOperation = 'lighter'; for (let i = 0; i < 9; i++) { c.fillStyle = `rgba(110,140,200,${.03 + fl * .12})`; c.beginPath(); const y = 260 + i * 34; c.moveTo(620, y); c.lineTo(1500, y + 120); c.lineTo(1500, y + 136); c.lineTo(620, y + 14); c.fill() } c.restore();
      // a map of the Pacific pinned to the wall
      c.save(); c.translate(1080, 160); c.rotate(.012); c.fillStyle = '#8e7f62'; c.fillRect(0, 0, 330, 220); c.fillStyle = 'rgba(40,50,60,.5)'; c.fillRect(10, 10, 310, 200);
      c.fillStyle = 'rgba(160,140,100,.7)'; for (let i = 0; i < 9; i++) { c.beginPath(); c.ellipse(40 + rnd(i) * 250, 30 + rnd(i + 1) * 160, 10 + rnd(i + 2) * 40, 6 + rnd(i + 3) * 26, rnd(i) * 3, 0, 7); c.fill() }
      c.fillStyle = '#b3202a'; c.beginPath(); c.arc(80, 70, 5, 0, 7); c.fill(); c.restore();
      // wall clock, second hand moving
      const kx = 1600, ky = 250, R = 74, tm = (S.clock || [11, 20]), sec = (S.clockSec || 0) + u, mins = tm[1] + sec / 60;
      c.fillStyle = '#0a0705'; c.beginPath(); c.arc(kx, ky, R + 10, 0, 7); c.fill(); c.fillStyle = '#d9cdb2'; c.beginPath(); c.arc(kx, ky, R, 0, 7); c.fill();
      c.strokeStyle = '#2a2018'; for (let i = 0; i < 12; i++) { const a = i / 12 * 6.283; c.lineWidth = 4; c.beginPath(); c.moveTo(kx + Math.cos(a) * R * .8, ky + Math.sin(a) * R * .8); c.lineTo(kx + Math.cos(a) * R * .93, ky + Math.sin(a) * R * .93); c.stroke() }
      const hand = (a, l, w, col) => { c.strokeStyle = col; c.lineWidth = w; c.lineCap = 'round'; c.beginPath(); c.moveTo(kx, ky); c.lineTo(kx + Math.sin(a) * l, ky - Math.cos(a) * l); c.stroke() };
      hand((tm[0] % 12 + mins / 60) / 12 * 6.283, R * .5, 7, '#1b120c'); hand(mins / 60 * 6.283, R * .75, 5, '#1b120c'); hand(Math.floor(sec) / 60 * 6.283, R * .82, 2, '#9e1b2a');
      c.fillStyle = 'rgba(0,0,0,.35)'; c.beginPath(); c.arc(kx, ky, R, 0, 7); c.fill();
    });
    // the officers behind the desk
    layer(c, C, W, H, .6, () => { for (const p of (S.people || [{ x: .36, pose: 'arms', facing: 1 }, { x: .6, pose: 'lean', facing: -1 }])) figure(c, W, H, W * p.x, H * 1.05, H * (p.h || .82), p, u + p.x * 10, L[0], L[1] - 60) });
    layer(c, C, W, H, .75, () => {
      // desk
      c.fillStyle = '#2a1a10'; c.beginPath(); c.moveTo(W * .2, H * .67); c.lineTo(W * .8, H * .67); c.lineTo(W * .88, H * .8); c.lineTo(W * .12, H * .8); c.closePath(); c.fill();
      c.fillStyle = '#1a0f09'; c.fillRect(W * .12, H * .8, W * .76, H * .3);
      // papers and the map lying on it
      c.save(); c.translate(W * .56, H * .73); c.transform(1, 0, -.35, .32, 0, 0); c.fillStyle = '#e4d6b0'; c.fillRect(-220, -170, 440, 340); c.strokeStyle = 'rgba(80,60,30,.5)'; c.lineWidth = 3; c.strokeRect(-220, -170, 440, 340);
      c.fillStyle = 'rgba(120,150,160,.6)'; c.fillRect(-200, -150, 400, 300); c.fillStyle = '#d9c99a'; c.beginPath(); c.moveTo(-40, -150); c.quadraticCurveTo(30, -40, -10, 60); c.quadraticCurveTo(20, 130, -30, 150); c.lineTo(-200, 150); c.lineTo(-200, -150); c.fill();
      if (S.line) { c.strokeStyle = '#c4161c'; c.lineWidth = 7; c.beginPath(); c.moveTo(-200, -6); c.lineTo(-200 + 400 * o3(clamp((u - S.line) / 2.5)), -6); c.stroke() } c.restore();
      c.save(); c.translate(W * .33, H * .72); c.transform(1, 0, -.3, .32, 0, 0); c.rotate(.2); c.fillStyle = '#d8ccb0'; c.fillRect(-90, -120, 180, 240); c.fillStyle = 'rgba(40,30,20,.5)'; for (let i = 0; i < 9; i++) c.fillRect(-70, -100 + i * 22, 140 - rnd(i) * 50, 6); c.restore();
      // ashtray and its smoke
      c.fillStyle = '#3a3a3a'; c.beginPath(); c.ellipse(W * .7, H * .725, 44, 13, 0, 0, 7); c.fill(); glow(c, W * .7 + 20, H * .717, 14, '255,120,40', .9);
      // the lamp: brass stem, green shade, a pool of light
      const lx = L[0], ly = L[1];
      c.fillStyle = '#5c4320'; c.beginPath(); c.ellipse(lx, H * .695, 60, 14, 0, 0, 7); c.fill(); c.fillRect(lx - 6, ly, 12, H * .695 - ly);
      c.fillStyle = '#0f4a2c'; c.beginPath(); c.moveTo(lx - 120, ly + 20); c.quadraticCurveTo(lx, ly - 50, lx + 120, ly + 20); c.closePath(); c.fill(); c.fillStyle = '#1d6b40'; c.fillRect(lx - 120, ly + 14, 240, 8);
      c.save(); c.globalCompositeOperation = 'lighter'; const cg = c.createLinearGradient(0, ly + 20, 0, H * .78); cg.addColorStop(0, 'rgba(255,200,120,.32)'); cg.addColorStop(1, 'rgba(255,200,120,0)'); c.fillStyle = cg;
      c.beginPath(); c.moveTo(lx - 115, ly + 22); c.lineTo(lx + 115, ly + 22); c.lineTo(lx + 420, H * .79); c.lineTo(lx - 420, H * .79); c.closePath(); c.fill(); c.restore();
      glow(c, lx, H * .73, 520, '255,180,100', .28); glow(c, lx, ly + 24, 90, '255,230,170', .8);
      dust(c, lx, ly + 160, 300, 130, u);
      smoke(c, W * .7 + 22, H * .715, u, 380, .14, 2);
    });
    // darken the room away from the lamp, cool the shadows
    c.save(); const vg = c.createRadialGradient(L[0], L[1] + 80, 120, L[0], L[1], W * .7); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(2,4,10,.72)'); c.fillStyle = vg; c.fillRect(0, 0, W, H); c.restore();
    if (fl) { c.fillStyle = `rgba(150,175,235,${fl * .12})`; c.fillRect(0, 0, W, H) }
  };

  SH['map-desk'] = (c, W, H, S, t, env) => {   // top-down insert: a 1940s paper map under the lamp, a red pencil drawing the line
    const C = cam(S, W, H), u = S.u, ctr = S.center || [127.6, 38.2], sc = S.scale || 5200, lat = S.lat || 38;
    layer(c, C, W, H, 1, () => {
      c.save(); c.translate(W / 2, H / 2); c.rotate(-.05 + Math.sin(u * .2) * .006); c.translate(-W / 2, -H / 2);
      c.drawImage(cached('map' + S.t, W, H, c => {   // desk, paper and printed map: drawn once per shot
      // wooden desk
      c.fillStyle = '#3b2414'; c.fillRect(-300, -300, W + 600, H + 600); for (let i = 0; i < 90; i++) { c.strokeStyle = `rgba(${rnd(i) > .5 ? '20,10,4' : '90,55,30'},${.15 + rnd(i + 1) * .2})`; c.lineWidth = 1 + rnd(i + 2) * 4; c.beginPath(); const y = -300 + i * 20; c.moveTo(-300, y); for (let x = -300; x < W + 300; x += 80) c.lineTo(x, y + Math.sin(x * .004 + i) * 8); c.stroke() }
      // the paper
      const px = 300, py = 40, pw = 1320, ph = 1000; c.fillStyle = 'rgba(0,0,0,.45)'; c.fillRect(px + 18, py + 22, pw, ph);
      c.save(); c.beginPath(); c.rect(px, py, pw, ph); c.clip();
      const proj = env.d3.geoMercator().center(ctr).scale(sc).translate([W / 2, H / 2]), path = env.d3.geoPath(proj, c);
      c.fillStyle = '#b8cdd0'; c.fillRect(px, py, pw, ph);
      c.beginPath(); path(env.LAND); c.fillStyle = '#efe2bf'; c.fill(); c.strokeStyle = 'rgba(160,90,70,.55)'; c.lineWidth = 9; c.stroke(); c.strokeStyle = '#5a3d22'; c.lineWidth = 1.6; c.stroke();
      // graticule with degree labels
      c.font = `400 22px ${TYPE}`; c.fillStyle = '#4a3a28'; c.textBaseline = 'middle';
      for (let la = 33; la <= 43; la++) { const a = proj([110, la]), b = proj([145, la]); c.strokeStyle = la === lat ? 'rgba(60,40,20,.55)' : 'rgba(60,40,20,.25)'; c.lineWidth = la === lat ? 1.6 : 1; c.beginPath(); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); c.stroke(); c.fillText(la + '°', px + 14, a[1] - 12) }
      for (let lo = 118; lo <= 136; lo += 2) { const a = proj([lo, 30]), b = proj([lo, 46]); c.strokeStyle = 'rgba(60,40,20,.22)'; c.beginPath(); c.moveTo(a[0], a[1]); c.lineTo(b[0], b[1]); c.stroke() }
      // place names, in the style of the time
      const name = (txt, lon, la, f, rot = 0, col = '#3a2a1a') => { const p = proj([lon, la]); c.save(); c.translate(p[0], p[1]); c.rotate(rot); c.font = f; c.fillStyle = col; c.textAlign = 'center'; c.fillText(txt, 0, 0); c.restore() };
      name('K O R E A', 128.3, 40.3, `italic 400 46px ${SERIF}`, -.95); name('(CHŌSEN)', 128.0, 39.8, `400 22px ${TYPE}`, -.95);
      name('M A N C H U R I A', 124.5, 42.2, `italic 400 34px ${SERIF}`, -.08, '#5b4630'); name('JAPAN', 134.2, 35.3, `italic 400 34px ${SERIF}`, -.6, '#5b4630');
      name('YELLOW  SEA', 123.6, 36.4, `italic 400 28px ${SERIF}`, -.2, '#3d5a66'); name('SEA  OF  JAPAN', 131.6, 39.4, `italic 400 28px ${SERIF}`, -.2, '#3d5a66');
      for (const [n, lo, la] of [['Keijō (Seoul)', 126.98, 37.56], ['Heijō (Pyongyang)', 125.75, 39.03], ['Fusan (Busan)', 129.04, 35.1]]) { const p = proj([lo, la]); c.fillStyle = '#2a1a10'; c.beginPath(); c.arc(p[0], p[1], 6, 0, 7); c.fill(); c.font = `700 22px ${TYPE}`; c.textAlign = 'left'; c.fillText(n, p[0] + 12, p[1] + 2) }
      c.restore();
      // paper texture: folds and stains
      c.save(); c.globalCompositeOperation = 'multiply'; c.fillStyle = 'rgba(150,120,80,.18)'; c.fillRect(px + pw / 2 - 2, py, 4, ph); c.fillRect(px, py + ph / 2 - 2, pw, 4);
      for (let i = 0; i < 6; i++) { const g = c.createRadialGradient(px + rnd(i) * pw, py + rnd(i + 1) * ph, 0, px + rnd(i) * pw, py + rnd(i + 1) * ph, 120 + rnd(i + 2) * 200); g.addColorStop(0, 'rgba(160,120,70,.18)'); g.addColorStop(1, 'rgba(160,120,70,0)'); c.fillStyle = g; c.fillRect(px, py, pw, ph) } c.restore();
      }), -300, -300);
      const px = 300, pw = 1320, proj = env.d3.geoMercator().center(ctr).scale(sc).translate([W / 2, H / 2]);
      // the red pencil line along the parallel
      if (S.draw != null) { const k = io(clamp((u - S.draw) / (S.drawDur || 3.2))), a = proj([124.4, lat]), b = proj([129.6, lat]), x = lerp(a[0], b[0], k);
        c.save(); c.strokeStyle = '#c0171d'; c.lineCap = 'round'; c.lineWidth = 9; c.globalAlpha = .9; c.beginPath(); c.moveTo(a[0], a[1]); for (let xx = a[0]; xx <= x; xx += 8) c.lineTo(xx, a[1] + Math.sin(xx * .07) * 1.5); c.stroke();
        c.globalAlpha = .35; c.lineWidth = 3; c.strokeStyle = '#ff6b5b'; c.stroke(); c.restore();
        if (k >= 1) { const g = clamp((u - S.draw - (S.drawDur || 3.2)) / .6); c.save(); c.globalAlpha = g; c.font = `700 40px ${TYPE}`; c.fillStyle = '#c0171d'; c.textAlign = 'left'; c.fillText('38° N', b[0] + 24, b[1] + 4); c.restore() }
        // the pencil itself, with its shadow
        if (k < 1.0 || u < S.draw + (S.drawDur || 3.2) + 1.2) { const lift = k >= 1 ? o3((u - S.draw - (S.drawDur || 3.2)) / 1.2) : 0, X = x + lift * 160, Y = a[1] - lift * 220;
          c.save(); c.translate(X + 26, Y + 30); c.rotate(-.9); c.fillStyle = 'rgba(0,0,0,.18)'; c.fillRect(0, -14, 420, 28); c.fillRect(0, -9, 420, 18); c.restore();
          c.save(); c.translate(X, Y); c.rotate(-.95); c.fillStyle = '#e8c27a'; c.beginPath(); c.moveTo(0, 0); c.lineTo(46, -11); c.lineTo(46, 11); c.closePath(); c.fill(); c.fillStyle = '#c0171d'; c.beginPath(); c.moveTo(0, 0); c.lineTo(14, -3.5); c.lineTo(14, 3.5); c.fill();
          c.fillStyle = '#a3141a'; c.fillRect(46, -11, 380, 22); c.fillStyle = 'rgba(255,255,255,.18)'; c.fillRect(46, -11, 380, 6); c.fillStyle = '#c9b04a'; c.fillRect(426, -11, 26, 22); c.restore() } }
      c.restore();
    });
    // lamp light from the upper left, the rest of the frame falls into shadow
    const vg = c.createRadialGradient(W * .42, H * .38, 200, W * .5, H * .5, W * .75); vg.addColorStop(0, 'rgba(0,0,0,0)'); vg.addColorStop(1, 'rgba(5,3,2,.78)'); c.fillStyle = vg; c.fillRect(0, 0, W, H);
    glow(c, W * .4, H * .32, 900, '255,190,110', .14); dust(c, W * .45, H * .4, 600, 300, u, 50);
  };

  SH['faces'] = (c, W, H, S, t, env) => {   // close-up: the two men in lamp light, names typed underneath
    const C = cam(S, W, H), u = S.u;
    c.fillStyle = '#070504'; c.fillRect(0, 0, W, H);
    layer(c, C, W, H, .3, () => { for (let i = 0; i < 6; i++) glow(c, 200 + rnd(i) * (W - 400), 200 + rnd(i + 1) * 400, 90 + rnd(i + 2) * 120, '255,170,90', .07) });
    layer(c, C, W, H, .8, () => {
      const P = S.people || [{ preset: 'us_officer', x: .3 }, { preset: 'us_officer', x: .7 }];
      P.forEach((p, i) => { const [oc, k] = off(W, H, 4); const spec = Object.assign({}, (env.PRESETS || {})[p.preset] || {}, p.spec || {}, { facing: p.x < .5 ? 1 : -1, mood: p.mood || 'grim' });
        env.drawChar(k, W * p.x, H * 1.02, H * (p.h || .95), spec, u + i * 1.7);
        k.save(); k.globalCompositeOperation = 'source-atop';
        const dk = k.createLinearGradient(0, H * .1, 0, H); dk.addColorStop(0, 'rgba(5,3,2,.78)'); dk.addColorStop(.55, 'rgba(5,3,2,.25)'); dk.addColorStop(1, 'rgba(5,3,2,.55)'); k.fillStyle = dk; k.fillRect(0, 0, W, H);
        const side = k.createLinearGradient(W * p.x - (p.x < .5 ? -1 : 1) * W * .25, 0, W * p.x + (p.x < .5 ? -1 : 1) * W * .15, 0); side.addColorStop(0, 'rgba(255,160,80,.38)'); side.addColorStop(1, 'rgba(255,160,80,0)');
        k.globalCompositeOperation = 'source-atop'; k.fillStyle = side; k.fillRect(0, 0, W, H); k.restore();
        c.drawImage(oc, 0, 0) });
      glow(c, W / 2, H * 1.05, 700, '255,170,90', .3);
      smoke(c, W * .52, H * .95, u, 700, .1, 5);
    });
    // name cards, typed one after the other
    (S.names || []).forEach((n, i) => { const t0 = (S.nameAt || 1) + i * 1.6, k = u - t0; if (k < 0) return; const s = n[0].slice(0, Math.ceil(clamp(k / 1.0) * n[0].length)), x = i ? W * .66 : W * .1;
      c.save(); c.globalAlpha = 1 - clamp((u - (S.dur || 8) + .6) / .6); c.font = `700 34px ${TYPE}`; c.fillStyle = '#f3e7cf'; c.textAlign = 'left'; c.shadowColor = '#000'; c.shadowBlur = 12; c.fillText(s, x, H - BAR - 70);
      if (n[1] && k > 1.1) { c.font = `400 24px ${TYPE}`; c.fillStyle = 'rgba(243,231,207,.75)'; c.fillText(n[1].slice(0, Math.ceil(clamp((k - 1.1) / .8) * n[1].length)), x, H - BAR - 34) } c.restore() });
  };

  SH['village'] = (c, W, H, S, t) => {   // Korea by day: hills, thatched houses, rice fields, a farmer with an A-frame; then the line cuts the frame
    const C = cam(S, W, H), u = S.u, cut = S.cut != null ? clamp((u - S.cut) / 1.1) : 0, split = S.cut != null ? o3(clamp((u - S.cut - 1.1) / 1.4)) : 0;
    const scene = () => {
      layer(c, C, W, H, .1, () => { const g = c.createLinearGradient(0, 0, 0, H * .6); g.addColorStop(0, '#9fb6c2'); g.addColorStop(1, '#efe0c0'); c.fillStyle = g; c.fillRect(-200, -200, W + 400, H + 400); glow(c, W * .72, H * .2, 400, '255,240,200', .5) });
      const ridge = (y, amp, col, seed, d) => layer(c, C, W, H, d, () => { c.fillStyle = col; c.beginPath(); c.moveTo(-300, H + 300); for (let x = -300; x <= W + 300; x += 12) { const v = Math.sin(x * .004 + seed) * .5 + Math.sin(x * .011 + seed * 2) * .3 + Math.sin(x * .027 + seed * 3) * .12; c.lineTo(x, y - amp * v) } c.lineTo(W + 300, H + 300); c.fill() });
      ridge(H * .42, 140, '#a9b5b0', 1, .2); ridge(H * .5, 120, '#8a9a8a', 3, .3);
      layer(c, C, W, H, .35, () => { const g = c.createLinearGradient(0, H * .35, 0, H * .62); g.addColorStop(0, 'rgba(240,230,210,0)'); g.addColorStop(1, 'rgba(240,230,210,.55)'); c.fillStyle = g; c.fillRect(-200, H * .3, W + 400, H * .4) });
      ridge(H * .6, 90, '#5f7552', 5, .45);
      layer(c, C, W, H, .6, () => {   // terraced rice fields
        for (let i = 0; i < 9; i++) { const y = H * .6 + i * 46; c.fillStyle = i % 2 ? '#c8b45a' : '#9fae55'; c.beginPath(); c.moveTo(-300, y); for (let x = -300; x <= W + 300; x += 40) c.lineTo(x, y + Math.sin(x * .003 + i) * 18); c.lineTo(W + 300, y + 60); c.lineTo(-300, y + 60); c.fill();
          c.strokeStyle = 'rgba(70,60,30,.35)'; c.lineWidth = 3; c.beginPath(); c.moveTo(-300, y); for (let x = -300; x <= W + 300; x += 40) c.lineTo(x, y + Math.sin(x * .003 + i) * 18); c.stroke() }
        // thatched houses (choga) with chimney smoke
        for (const [hx, hy, s] of [[W * .2, H * .6, 1], [W * .33, H * .59, .8], [W * .78, H * .61, 1.1], [W * .9, H * .6, .75]]) {
          c.save(); c.translate(hx, hy); c.scale(s, s); c.fillStyle = '#e9e1cf'; c.fillRect(-90, -60, 180, 70); c.fillStyle = '#5a4630'; c.fillRect(-20, -40, 34, 50); c.fillStyle = '#3d2f20'; c.fillRect(-70, -45, 30, 22); c.fillRect(46, -45, 30, 22);
          c.fillStyle = '#b39a62'; c.beginPath(); c.moveTo(-120, -50); c.quadraticCurveTo(-110, -150, 0, -150); c.quadraticCurveTo(110, -150, 120, -50); c.quadraticCurveTo(0, -36, -120, -50); c.fill();
          c.strokeStyle = 'rgba(90,70,40,.5)'; c.lineWidth = 3; for (let j = 0; j < 4; j++) { c.beginPath(); c.moveTo(-110 + j * 8, -60 - j * 22); c.quadraticCurveTo(0, -70 - j * 24, 110 - j * 8, -60 - j * 22); c.stroke() } c.restore();
          smoke(c, hx + 70 * s, hy - 60 * s, u + hx, 260, .12, hx) }
        // a farmer walking with an A-frame carrier
        const fx = lerp(W * .3, W * .55, clamp(u / (S.dur || 10))), fy = H * .82, st = Math.sin(u * 5);
        c.save(); c.translate(fx, fy); c.fillStyle = '#f1ece0'; c.strokeStyle = '#2a2018'; c.lineWidth = 3;
        c.beginPath(); c.moveTo(-14, 0); c.lineTo(-14 + st * 14, 90); c.lineTo(-2 + st * 14, 90); c.lineTo(0, 10); c.lineTo(4 - st * 14, 90); c.lineTo(16 - st * 14, 90); c.lineTo(14, 0); c.fill(); c.stroke();
        c.beginPath(); c.roundRect(-26, -90, 52, 96, 14); c.fill(); c.stroke(); c.fillStyle = '#d9a77a'; c.beginPath(); c.arc(4, -112, 22, 0, 7); c.fill(); c.stroke();
        c.fillStyle = '#2a2018'; c.beginPath(); c.ellipse(4, -128, 26, 9, 0, 0, 7); c.fill();
        c.strokeStyle = '#6b4a2a'; c.lineWidth = 7; c.beginPath(); c.moveTo(-30, -110); c.lineTo(-44, 70); c.moveTo(-10, -110); c.lineTo(-24, 70); c.moveTo(-40, 20); c.lineTo(-20, 20); c.stroke();
        c.fillStyle = '#8c6a3a'; c.fillRect(-60, -150, 44, 60); c.restore();
        // birds
        c.strokeStyle = 'rgba(40,40,40,.6)'; c.lineWidth = 2.5; for (let i = 0; i < 6; i++) { const bx = ((rnd(i) * W + u * 40) % (W + 200)) - 100, by = 160 + rnd(i + 1) * 160 + Math.sin(u * 2 + i) * 8, w = Math.sin(u * 8 + i) * 8; c.beginPath(); c.moveTo(bx - 12, by - w); c.quadraticCurveTo(bx - 4, by - 4, bx, by); c.quadraticCurveTo(bx + 4, by - 4, bx + 12, by - w); c.stroke() }
      });
    };
    if (!split) { scene(); c.save(); c.globalCompositeOperation = 'soft-light'; c.fillStyle = 'rgba(255,200,140,.25)'; c.fillRect(0, 0, W, H); c.restore() }
    else {   // the frame splits along the line: the north half drifts up and cools, the south half drifts down
      const y = H * (S.cutY || .55), gap = split * 26;
      c.save(); c.beginPath(); c.rect(0, 0, W, y); c.clip(); c.translate(0, -gap); scene(); c.fillStyle = `rgba(30,60,140,${split * .22})`; c.fillRect(0, 0, W, H); c.restore();
      c.save(); c.beginPath(); c.rect(0, y, W, H); c.clip(); c.translate(0, gap); scene(); c.fillStyle = `rgba(150,30,20,${split * .18})`; c.fillRect(0, 0, W, H); c.restore();
      c.fillStyle = '#050302'; c.fillRect(0, y - gap, W, gap * 2) }
    if (cut > 0) { const y = H * (S.cutY || .55), x = W * io(cut); c.save(); c.globalCompositeOperation = 'lighter'; c.strokeStyle = '#ff2a1a'; c.lineWidth = 6; c.shadowColor = '#ff3a20'; c.shadowBlur = 30;
      c.beginPath(); c.moveTo(0, y); c.lineTo(x, y); c.stroke(); c.lineWidth = 2; c.strokeStyle = '#fff2e0'; c.stroke(); glow(c, x, y, 120, '255,120,80', .9);
      for (let i = 0; i < 18; i++) { const a = rnd(i + u * 60 | 0) * 6.283, r = rnd(i + 3) * 60; c.fillStyle = 'rgba(255,200,140,.8)'; c.fillRect(x + Math.cos(a) * r, y + Math.sin(a) * r, 3, 3) } c.restore();
      if (cut >= 1) { c.save(); c.globalAlpha = clamp((u - S.cut - 1.1) / .6); c.font = `700 46px ${TYPE}`; c.fillStyle = '#fff'; c.shadowColor = '#000'; c.shadowBlur = 16; c.textAlign = 'right'; c.fillText('38° NORTH', W - 70, y - 40 - 26 * split); c.restore() } }
  };

  // ---------- entry ----------
  G.SCENE_SHOTS = SH;
  G.SCENE_KIT = { clamp, lerp, io, o3, rnd, glow, rain, smoke, dust, figure, cam, layer, off, cached, TYPE, SERIF, BODY, BAR };   // for scenes2.js
  G.SCENE = function (c, W, H, S, t, env) {
    const f = SH[S.shot]; if (!f) return false; c.save();
    // angle cuts (owner, 15 Nov 2026: a cut every 3-4 s, like Paper Billions): inside a longer shot the camera jumps between a wide,
    // a medium and a close framing of the same picture every ~3.6 s. Text shots (doc, card) and dialogue (own cuts) keep one framing.
    const A = G.SCENE_ANGLE(S, W, H); if (A) { c.translate(W / 2 + A.dx, H / 2 + A.dy); c.scale(A.z, A.z); c.translate(-W / 2, -H / 2) }
    f(c, W, H, S, t, env || {}); c.restore();
    // film grade: lift the blacks a touch towards teal, warm the highlights
    c.save(); c.globalCompositeOperation = 'soft-light'; const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, 'rgba(40,80,110,.35)'); g.addColorStop(1, 'rgba(255,170,90,.25)'); c.fillStyle = g; c.fillRect(0, 0, W, H); c.restore();
    // a cut opens on a short fade from black
    const inn = S.fadeIn == null ? .35 : S.fadeIn; if (S.u < inn) { c.fillStyle = `rgba(0,0,0,${1 - S.u / inn})`; c.fillRect(0, 0, W, H) }
    const out = S.fadeOut || 0, d = S.dur || 8; if (out && S.u > d - out) { c.fillStyle = `rgba(0,0,0,${clamp((S.u - d + out) / out)})`; c.fillRect(0, 0, W, H) }
    return true };
  const NOANGLE = { doc: 1, card: 1, talk: 1, off: 1 };
  const ANGLES = [[1.18, -.07, -.04], [1.1, .06, .02], [1.26, .02, -.07], [1.14, -.05, .03], [1.22, .07, -.05]];
  G.SCENE_CUTS = S => { if (NOANGLE[S.shot] || S.angles === false) return []; const d = S.dur || 8, out = []; let a = 0, i = 0;   // where the angle cuts fall
    while (true) { a += 2.6 + rnd((S.t || 0) * 7 + i * 3.1) * 0.9; if (a > d - 1.8) break; out.push(a); i++ } return out };
  G.SCENE_ANGLE = (S, W, H) => { const cuts = G.SCENE_CUTS(S); let k = 0; while (k < cuts.length && S.u >= cuts[k]) k++; if (!k) return null;
    const g = ANGLES[(k - 1 + Math.floor(rnd((S.t || 0) * 13) * 5)) % ANGLES.length]; return { z: g[0], dx: g[1] * W, dy: g[2] * H } };
  // cinema bars and the typed date card, drawn by doc.html above the scene and under the captions
  G.SCENE_BARS = function (c, W, H, a = 1) { c.fillStyle = '#000'; c.fillRect(0, 0, W, BAR * a); c.fillRect(0, H - BAR * a, W, BAR * a) };
  G.SCENE_DATE = function (c, W, H, text, u) {
    const lines = text.split('\n'), per = 20; let n = Math.floor(u * per); c.save(); c.textAlign = 'left'; c.textBaseline = 'alphabetic'; c.shadowColor = 'rgba(0,0,0,.9)'; c.shadowBlur = 14;
    const fade = 1 - clamp((u - 6) / .8); if (fade <= 0) { c.restore(); return } c.globalAlpha = fade;
    lines.forEach((L, i) => { const s = L.slice(0, Math.max(0, n)); n -= L.length + 4; c.font = i ? `400 30px ${TYPE}` : `700 40px ${TYPE}`; c.fillStyle = i ? 'rgba(243,231,207,.85)' : '#f3e7cf';
      const y = BAR + 90 + i * 48; c.fillText(s, 90, y); if (s.length < L.length && s.length > 0 || (i === lines.length - 1 && s.length === L.length && Math.floor(u * 2) % 2 === 0)) { const w = c.measureText(s).width; c.fillRect(90 + w + 4, y - (i ? 24 : 32), i ? 14 : 18, i ? 28 : 36) } });
    c.restore() };
})(typeof window !== 'undefined' ? window : globalThis);
