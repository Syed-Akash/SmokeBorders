// Smoke & Borders characters: bold-outlined cartoon busts (no countryballs).
// drawChar(ctx, x, y, H, spec, t)  draws a bust whose bottom centre is (x, y) and height is H.
// spec: {coat, coat2 (lapels/facings), skin, hair, hairStyle (bald|short|wig|franklin|long|none), hat (none|tricorn|bicorne|crown|helmet|roman|tophat|kepi|fur|mitre|turban),
//        hatCol, trim, beard (none|mustache|full|stubble), glasses, mood (neutral|angry|shock|sad|smug|happy|grim), facing (-1 left, 1 right), medal, sash, epaulettes}
(function (G) {
  const INK = '#1b120c';
  const shade = (hex, k) => { const n = parseInt(hex.slice(1), 16); let r = n >> 16, g = (n >> 8) & 255, b = n & 255;
    const f = v => Math.max(0, Math.min(255, Math.round(k < 0 ? v * (1 + k) : v + (255 - v) * k))); return '#' + [f(r), f(g), f(b)].map(v => v.toString(16).padStart(2, '0')).join('') };
  function outline(c, w) { c.lineJoin = 'round'; c.lineCap = 'round'; c.strokeStyle = INK; c.lineWidth = w; c.stroke() }
  function ell(c, x, y, rx, ry, r = 0) { c.beginPath(); c.ellipse(x, y, rx, ry, r, 0, Math.PI * 2) }
  G.drawChar = function (c, x, y, H, s, t = 0) {
    s = Object.assign({ coat: '#2f4a7a', coat2: '#e9e2d0', skin: '#f2c9a0', hair: '#6b4a2b', hairStyle: 'short', hat: 'none', hatCol: '#1c1c1c', trim: '#d4a72c',
      beard: 'none', mood: 'neutral', facing: 1 }, s || {});
    const R = H * 0.235, hx = x + s.facing * R * 0.05, hy = y - H * 0.6, lw = Math.max(2, R * 0.085), f = s.facing;
    c.save();
    // ---------- coat / bust ----------
    const sw = H * 0.5, top = y - H * 0.33;
    c.beginPath(); c.moveTo(x - sw, y); c.bezierCurveTo(x - sw, top + H * .05, x - sw * .7, top - H * .02, x - R * .55, top - H * .03);
    c.lineTo(x + R * .55, top - H * .03); c.bezierCurveTo(x + sw * .7, top - H * .02, x + sw, top + H * .05, x + sw, y); c.closePath();
    c.fillStyle = s.coat; c.fill();
    const coatPath = () => { c.beginPath(); c.moveTo(x - sw, y); c.bezierCurveTo(x - sw, top + H * .05, x - sw * .7, top - H * .02, x - R * .55, top - H * .03);
      c.lineTo(x + R * .55, top - H * .03); c.bezierCurveTo(x + sw * .7, top - H * .02, x + sw, top + H * .05, x + sw, y); c.closePath() };
    c.save(); coatPath(); c.clip(); c.fillStyle = shade(s.coat, -.28); c.beginPath(); c.moveTo(x + f * R * .1, top - H * .1); c.lineTo(x + f * sw * 1.1, top); c.lineTo(x + f * sw * 1.1, y + 5); c.lineTo(x + f * R * .4, y + 5); c.fill(); c.restore();
    coatPath(); outline(c, lw);
    // facings / lapels
    c.fillStyle = s.coat2; c.beginPath(); c.moveTo(x - R * .55, top - H * .03); c.lineTo(x - R * .05, y); c.lineTo(x - R * .95, y); c.lineTo(x - R * 1.0, top + H * .06); c.closePath(); c.fill(); outline(c, lw * .7);
    c.beginPath(); c.moveTo(x + R * .55, top - H * .03); c.lineTo(x + R * .05, y); c.lineTo(x + R * .95, y); c.lineTo(x + R * 1.0, top + H * .06); c.closePath(); c.fill(); outline(c, lw * .7);
    // cravat / shirt
    c.fillStyle = '#fbf6ea'; c.beginPath(); c.moveTo(x - R * .42, top - H * .03); c.quadraticCurveTo(x, top + H * .16, x + R * .42, top - H * .03); c.quadraticCurveTo(x, top + H * .05, x - R * .42, top - H * .03); c.fill(); outline(c, lw * .6);
    if (s.sash) { c.save(); c.beginPath(); c.moveTo(x - sw * .8, top + H * .05); c.lineTo(x - sw * .6, top - H * .0); c.lineTo(x + sw * .9, y); c.lineTo(x + sw * .55, y); c.closePath(); c.fillStyle = s.sash; c.fill(); outline(c, lw * .6); c.restore() }
    if (s.epaulettes) for (const k of [-1, 1]) { ell(c, x + k * sw * .72, top + H * .03, R * .42, R * .16, k * .25); c.fillStyle = s.trim; c.fill(); outline(c, lw * .6) }
    if (s.medal) { ell(c, x - f * R * .9, top + H * .17, R * .13, R * .13); c.fillStyle = s.trim; c.fill(); outline(c, lw * .5) }
    // buttons
    c.fillStyle = s.trim; for (let i = 0; i < 3; i++) { ell(c, x + R * .78 * (i % 2 ? 1 : -1) * 0 - R * .72, top + H * (.12 + i * .07), R * .055, R * .055); c.fill(); ell(c, x + R * .72, top + H * (.12 + i * .07), R * .055, R * .055); c.fill() }
    // ---------- neck ----------
    c.fillStyle = shade(s.skin, -.12); c.fillRect(hx - R * .32, hy + R * .6, R * .64, R * .55);
    // ---------- hair behind the head ----------
    const hairCol = s.hair;
    if (s.hairStyle === 'wig') { for (const k of [-1, 1]) { ell(c, hx + k * R * 1.0, hy + R * .25, R * .32, R * .5); c.fillStyle = hairCol; c.fill(); outline(c, lw * .8) } ell(c, hx - f * R * .8, hy + R * .55, R * .22, R * .35); c.fillStyle = hairCol; c.fill(); outline(c, lw * .7) }
    if (s.hairStyle === 'franklin' || s.hairStyle === 'long') { c.beginPath(); c.moveTo(hx - R * 1.02, hy - R * .1); c.quadraticCurveTo(hx - R * 1.25, hy + R * 1.0, hx - R * .7, hy + R * 1.15); c.lineTo(hx + R * .7, hy + R * 1.15); c.quadraticCurveTo(hx + R * 1.25, hy + R * 1.0, hx + R * 1.02, hy - R * .1); c.closePath(); c.fillStyle = hairCol; c.fill(); outline(c, lw * .8) }
    if (s.hairStyle === 'flowing') {   // long hair falling past the shoulders (women)
      c.beginPath(); c.moveTo(hx - R * 1.05, hy - R * .3); c.bezierCurveTo(hx - R * 1.45, hy + R * .6, hx - R * 1.35, hy + R * 1.6, hx - R * 1.05, hy + R * 1.95);
      c.lineTo(hx + R * 1.05, hy + R * 1.95); c.bezierCurveTo(hx + R * 1.35, hy + R * 1.6, hx + R * 1.45, hy + R * .6, hx + R * 1.05, hy - R * .3); c.closePath();
      c.fillStyle = hairCol; c.fill(); outline(c, lw * .8) }
    // ---------- head ----------
    if (s.hairStyle !== 'flowing') {
    ell(c, hx - R * 1.0, hy + R * .1, R * .17, R * .24); c.fillStyle = s.skin; c.fill(); outline(c, lw * .7);
    ell(c, hx + R * 1.0, hy + R * .1, R * .17, R * .24); c.fill(); outline(c, lw * .7); }
    c.beginPath(); c.moveTo(hx - R * .98, hy - R * .25); c.bezierCurveTo(hx - R * 1.02, hy - R * 1.15, hx + R * 1.02, hy - R * 1.15, hx + R * .98, hy - R * .25);
    c.bezierCurveTo(hx + R * .98, hy + R * .55, hx + R * .55, hy + R * 1.0, hx, hy + R * 1.02); c.bezierCurveTo(hx - R * .55, hy + R * 1.0, hx - R * .98, hy + R * .55, hx - R * .98, hy - R * .25); c.closePath();
    c.fillStyle = s.skin; c.fill(); c.save(); c.clip(); c.fillStyle = shade(s.skin, -.13); ell(c, hx + f * R * .95, hy + R * .2, R * .45, R * 1.3); c.fill();
    c.fillStyle = 'rgba(255,120,110,.18)'; ell(c, hx - R * .5, hy + R * .38, R * .2, R * .12); c.fill(); ell(c, hx + R * .5, hy + R * .38, R * .2, R * .12); c.fill(); c.restore();
    c.beginPath(); c.moveTo(hx - R * .98, hy - R * .25); c.bezierCurveTo(hx - R * 1.02, hy - R * 1.15, hx + R * 1.02, hy - R * 1.15, hx + R * .98, hy - R * .25);
    c.bezierCurveTo(hx + R * .98, hy + R * .55, hx + R * .55, hy + R * 1.0, hx, hy + R * 1.02); c.bezierCurveTo(hx - R * .55, hy + R * 1.0, hx - R * .98, hy + R * .55, hx - R * .98, hy - R * .25); outline(c, lw);
    // ---------- face ----------
    const m = s.mood, ey = hy + R * .02, ex = R * .38, blink = ((t * 1.0 + x * .001) % 4.2) < .1;
    for (const k of [-1, 1]) {
      const cx = hx + k * ex + f * R * .06, wide = m === 'shock' ? 1.25 : 1, lid = m === 'smug' ? .5 : m === 'grim' ? .7 : 1;
      ell(c, cx, ey, R * .17 * wide, R * .2 * wide * (blink ? .12 : lid)); c.fillStyle = '#fff'; c.fill(); outline(c, lw * .55);
      if (!blink) { ell(c, cx + f * R * .05, ey + R * .02, R * (m === 'shock' ? .06 : .085), R * (m === 'shock' ? .06 : .1) * lid); c.fillStyle = INK; c.fill() }
      if (m === 'smug' || m === 'grim') { c.beginPath(); c.moveTo(cx - R * .19, ey - R * .2 * lid + R * .02); c.lineTo(cx + R * .19, ey - R * .2 * lid + R * .02); outline(c, lw * .6) }
      // brows
      c.beginPath(); const by = ey - R * .32;
      if (m === 'angry' || m === 'grim') { c.moveTo(cx + k * R * .2, by - R * .1); c.lineTo(cx - k * R * .16, by + R * .07) }
      else if (m === 'sad') { c.moveTo(cx + k * R * .2, by + R * .05); c.lineTo(cx - k * R * .16, by - R * .1) }
      else if (m === 'shock') { c.moveTo(cx - R * .18, by - R * .1); c.quadraticCurveTo(cx, by - R * .22, cx + R * .18, by - R * .1) }
      else if (m === 'smug' && k === f) { c.moveTo(cx - R * .18, by - R * .14); c.quadraticCurveTo(cx, by - R * .26, cx + R * .18, by - R * .12) }
      else { c.moveTo(cx - R * .18, by - R * .02); c.quadraticCurveTo(cx, by - R * .1, cx + R * .18, by - R * .02) }
      c.lineWidth = R * .1; c.strokeStyle = s.hairStyle === 'wig' || s.hair === '#efeae0' ? '#6d665d' : shade(hairCol, -.35); c.lineCap = 'round'; c.stroke()
    }
    if (s.glasses) for (const k of [-1, 1]) { ell(c, hx + k * ex + f * R * .06, ey, R * .21, R * .17); c.strokeStyle = INK; c.lineWidth = lw * .5; c.stroke() }
    // nose
    c.beginPath(); c.moveTo(hx + f * R * .1, ey + R * .05); c.quadraticCurveTo(hx + f * R * .28, ey + R * .32, hx + f * R * .02, ey + R * .36); outline(c, lw * .6);
    // mouth
    const my = hy + R * .62; c.beginPath();
    if (m === 'shock') { ell(c, hx, my + R * .02, R * .13, R * .17); c.fillStyle = '#5a1d14'; c.fill(); outline(c, lw * .6) }
    else if (m === 'happy') { c.moveTo(hx - R * .25, my - R * .04); c.quadraticCurveTo(hx, my + R * .2, hx + R * .25, my - R * .04); c.closePath(); c.fillStyle = '#5a1d14'; c.fill(); outline(c, lw * .6) }
    else if (m === 'smug') { c.moveTo(hx - R * .18, my + R * .02); c.quadraticCurveTo(hx + R * .05, my + R * .06, hx + f * R * .26, my - R * .08); outline(c, lw * .65) }
    else if (m === 'angry') { c.moveTo(hx - R * .24, my + R * .08); c.quadraticCurveTo(hx, my - R * .08, hx + R * .24, my + R * .08); outline(c, lw * .7) }
    else if (m === 'sad') { c.moveTo(hx - R * .2, my + R * .08); c.quadraticCurveTo(hx, my - R * .04, hx + R * .2, my + R * .08); outline(c, lw * .6);
      c.beginPath(); c.moveTo(hx - ex, ey + R * .22); c.quadraticCurveTo(hx - ex - R * .06, ey + R * .38, hx - ex, ey + R * .42); c.quadraticCurveTo(hx - ex + R * .06, ey + R * .38, hx - ex, ey + R * .22); c.fillStyle = '#7fd3ff'; c.fill() }
    else { c.moveTo(hx - R * .18, my); c.lineTo(hx + R * .18, my); outline(c, lw * .6) }
    // facial hair
    if (s.beard === 'toothbrush') { c.fillStyle = s.hair; c.fillRect(hx + f * R * .06 - R * .13, my - R * .2, R * .26, R * .13); outline(c, lw * .35) }
    if (s.beard === 'mustache' || s.beard === 'full') { c.beginPath(); c.moveTo(hx, my - R * .14); c.quadraticCurveTo(hx - R * .3, my - R * .2, hx - R * .36, my - R * .02); c.quadraticCurveTo(hx - R * .15, my - R * .08, hx, my - R * .07);
      c.quadraticCurveTo(hx + R * .15, my - R * .08, hx + R * .36, my - R * .02); c.quadraticCurveTo(hx + R * .3, my - R * .2, hx, my - R * .14); c.fillStyle = hairCol; c.fill(); outline(c, lw * .5) }
    if (s.beard === 'full') { c.beginPath(); c.moveTo(hx - R * .9, hy + R * .1); c.quadraticCurveTo(hx - R * .9, hy + R * 1.35, hx, hy + R * 1.45); c.quadraticCurveTo(hx + R * .9, hy + R * 1.35, hx + R * .9, hy + R * .1);
      c.quadraticCurveTo(hx + R * .6, hy + R * .8, hx + R * .3, my + R * .12); c.lineTo(hx - R * .3, my + R * .12); c.quadraticCurveTo(hx - R * .6, hy + R * .8, hx - R * .9, hy + R * .1); c.fillStyle = hairCol; c.fill(); outline(c, lw * .7) }
    // ---------- hair on top ----------
    if (s.hairStyle === 'flowing') {   // centre-parted fringe framing the face
      for (const k of [-1, 1]) { c.beginPath(); c.moveTo(hx, hy - R * 1.02); c.bezierCurveTo(hx + k * R * .7, hy - R * 1.1, hx + k * R * 1.12, hy - R * .7, hx + k * R * 1.02, hy + R * .25);
        c.quadraticCurveTo(hx + k * R * .92, hy - R * .45, hx + k * R * .25, hy - R * .72); c.closePath(); c.fillStyle = hairCol; c.fill(); outline(c, lw * .7) } }
    if (s.female) {
      for (const k of [-1, 1]) { const cx = hx + k * R * .38 + f * R * .06; c.beginPath(); c.moveTo(cx + k * R * .14, ey - R * .12); c.lineTo(cx + k * R * .27, ey - R * .22); c.lineWidth = lw * .5; c.strokeStyle = INK; c.lineCap = 'round'; c.stroke();
        ell(c, hx + k * R * 1.0, hy + R * .48, R * .07, R * .07); c.fillStyle = s.trim; c.fill(); outline(c, lw * .35) } }
    if (s.hat === 'sailor') { c.beginPath(); c.moveTo(hx - R * .95, hy - R * .55); c.quadraticCurveTo(hx, hy - R * 1.55, hx + R * .95, hy - R * .55); c.closePath(); c.fillStyle = '#f7f7f2'; c.fill(); outline(c, lw * .7);
      ell(c, hx, hy - R * .55, R * 1.08, R * .2); c.fillStyle = '#f7f7f2'; c.fill(); outline(c, lw * .7) }
    if (s.hat === 'diadem') { c.beginPath(); c.moveTo(hx - R * .9, hy - R * .62); c.quadraticCurveTo(hx, hy - R * 1.02, hx + R * .9, hy - R * .62); c.lineWidth = R * .13; c.strokeStyle = s.hatCol; c.lineCap = 'round'; c.stroke();
      ell(c, hx, hy - R * .84, R * .1, R * .12); c.fillStyle = s.trim2 || '#c0392b'; c.fill(); outline(c, lw * .45) }
    if (s.hairStyle === 'short') { c.beginPath(); c.moveTo(hx - R * .99, hy - R * .1); c.bezierCurveTo(hx - R * 1.05, hy - R * 1.25, hx + R * 1.05, hy - R * 1.25, hx + R * .99, hy - R * .1); c.quadraticCurveTo(hx + R * .7, hy - R * .6, hx + R * .1, hy - R * .55); c.quadraticCurveTo(hx - R * .6, hy - R * .55, hx - R * .99, hy - R * .1); c.fillStyle = hairCol; c.fill(); outline(c, lw * .8) }
    if (s.hairStyle === 'wig') { c.beginPath(); c.moveTo(hx - R * .99, hy - R * .05); c.bezierCurveTo(hx - R * 1.1, hy - R * 1.3, hx + R * 1.1, hy - R * 1.3, hx + R * .99, hy - R * .05); c.quadraticCurveTo(hx + R * .8, hy - R * .55, hx, hy - R * .62); c.quadraticCurveTo(hx - R * .8, hy - R * .55, hx - R * .99, hy - R * .05); c.fillStyle = hairCol; c.fill(); outline(c, lw * .8);
      for (const k of [-1, 1]) for (let i = 0; i < 2; i++) { ell(c, hx + k * R * .98, hy - R * .05 + i * R * .32, R * .2, R * .14); c.fillStyle = hairCol; c.fill(); outline(c, lw * .55) } }
    if (s.hairStyle === 'franklin') { c.beginPath(); c.moveTo(hx - R * 1.0, hy - R * .15); c.quadraticCurveTo(hx - R * .95, hy - R * .55, hx - R * .6, hy - R * .6); c.quadraticCurveTo(hx - R * .7, hy - R * .25, hx - R * .82, hy + R * .2); c.closePath(); c.fillStyle = hairCol; c.fill(); outline(c, lw * .6);
      c.beginPath(); c.moveTo(hx + R * 1.0, hy - R * .15); c.quadraticCurveTo(hx + R * .95, hy - R * .55, hx + R * .6, hy - R * .6); c.quadraticCurveTo(hx + R * .7, hy - R * .25, hx + R * .82, hy + R * .2); c.closePath(); c.fill(); outline(c, lw * .6) }
    // ---------- hats ----------
    const hc = s.hatCol, ht = hy - R * .72;
    if (s.hat === 'tricorn') { c.beginPath(); c.moveTo(hx - R * 1.45, ht + R * .05); c.quadraticCurveTo(hx - R * .9, ht - R * .75, hx, ht - R * .55); c.quadraticCurveTo(hx + R * .9, ht - R * .75, hx + R * 1.45, ht + R * .05); c.quadraticCurveTo(hx, ht + R * .3, hx - R * 1.45, ht + R * .05); c.fillStyle = hc; c.fill(); outline(c, lw);
      c.beginPath(); c.moveTo(hx - R * 1.38, ht + R * .02); c.quadraticCurveTo(hx, ht + R * .24, hx + R * 1.38, ht + R * .02); c.strokeStyle = s.trim; c.lineWidth = R * .08; c.stroke() }
    if (s.hat === 'bicorne') { c.beginPath(); c.moveTo(hx - R * 1.55, ht + R * .1); c.quadraticCurveTo(hx, ht - R * 1.05, hx + R * 1.55, ht + R * .1); c.quadraticCurveTo(hx, ht + R * .1, hx - R * 1.55, ht + R * .1); c.fillStyle = hc; c.fill(); outline(c, lw); ell(c, hx, ht - R * .3, R * .14, R * .14); c.fillStyle = s.trim; c.fill(); outline(c, lw * .5) }
    if (s.hat === 'crown') { c.beginPath(); c.moveTo(hx - R * .78, ht + R * .12); c.lineTo(hx - R * .85, ht - R * .5); c.lineTo(hx - R * .42, ht - R * .15); c.lineTo(hx, ht - R * .65); c.lineTo(hx + R * .42, ht - R * .15); c.lineTo(hx + R * .85, ht - R * .5); c.lineTo(hx + R * .78, ht + R * .12); c.closePath();
      c.fillStyle = '#e8b931'; c.fill(); outline(c, lw); for (const k of [-.5, 0, .5]) { ell(c, hx + k * R, ht - R * .0, R * .09, R * .09); c.fillStyle = k ? '#c8102e' : '#1f4fa8'; c.fill() } c.fillStyle = '#8b1020'; c.fillRect(hx - R * .78, ht + R * .02, R * 1.56, R * .12) }
    if (s.hat === 'helmet') { c.beginPath(); c.moveTo(hx - R * 1.2, ht + R * .55); c.bezierCurveTo(hx - R * 1.15, ht - R * .75, hx + R * 1.15, ht - R * .75, hx + R * 1.2, ht + R * .55); c.lineTo(hx + R * .95, ht + R * .45); c.lineTo(hx - R * .95, ht + R * .45); c.closePath(); c.fillStyle = hc; c.fill(); outline(c, lw) }
    if (s.hat === 'roman') { c.beginPath(); c.moveTo(hx - R * 1.05, ht + R * .55); c.bezierCurveTo(hx - R * 1.1, ht - R * .7, hx + R * 1.1, ht - R * .7, hx + R * 1.05, ht + R * .55); c.closePath(); c.fillStyle = '#c9a85a'; c.fill(); outline(c, lw);
      c.beginPath(); c.moveTo(hx - R * .85, ht - R * .05); c.quadraticCurveTo(hx, ht - R * 1.15, hx + R * .85, ht - R * .05); c.quadraticCurveTo(hx, ht - R * .45, hx - R * .85, ht - R * .05); c.fillStyle = s.trim === '#d4a72c' ? '#c8102e' : s.trim; c.fill(); outline(c, lw * .8) }
    if (s.hat === 'tophat') { c.fillStyle = hc; c.beginPath(); c.roundRect(hx - R * .7, ht - R * 1.1, R * 1.4, R * 1.15, R * .1); c.fill(); outline(c, lw); ell(c, hx, ht + R * .08, R * 1.15, R * .2); c.fill(); outline(c, lw) }
    if (s.hat === 'kepi') { c.fillStyle = hc; c.beginPath(); c.moveTo(hx - R * .85, ht + R * .25); c.lineTo(hx - R * .75, ht - R * .55); c.lineTo(hx + R * .75, ht - R * .55); c.lineTo(hx + R * .85, ht + R * .25); c.closePath(); c.fill(); outline(c, lw); c.fillStyle = INK; c.beginPath(); c.ellipse(hx + f * R * .4, ht + R * .3, R * .7, R * .14, 0, 0, Math.PI * 2); c.fill() }
    if (s.hat === 'fur') { c.fillStyle = hc; c.beginPath(); c.roundRect(hx - R * 1.0, ht - R * .75, R * 2.0, R * 1.05, R * .4); c.fill(); outline(c, lw) }
    if (s.hat === 'mitre') { c.beginPath(); c.moveTo(hx - R * .85, ht + R * .3); c.lineTo(hx - R * .5, ht - R * 1.2); c.quadraticCurveTo(hx, ht - R * 1.45, hx + R * .5, ht - R * 1.2); c.lineTo(hx + R * .85, ht + R * .3); c.closePath(); c.fillStyle = hc; c.fill(); outline(c, lw);
      c.beginPath(); c.moveTo(hx - R * .5, ht - R * .1); c.lineTo(hx, ht - R * 1.05); c.lineTo(hx + R * .5, ht - R * .1); c.closePath(); c.fillStyle = s.trim; c.fill(); outline(c, lw * .6) }
    if (s.hat === 'turban') { for (let i = 0; i < 3; i++) { ell(c, hx, ht + R * .05 - i * R * .3, R * (1.1 - i * .12), R * .4); c.fillStyle = i % 2 ? shade(hc, .15) : hc; c.fill(); outline(c, lw * .7) } }
    c.restore();
  };
  G.CHAR_PRESETS = {
    redcoat: { coat: '#b3202a', coat2: '#f1e6c8', hat: 'tricorn', hatCol: '#1c1a1a', trim: '#e9e2d0', hairStyle: 'wig', hair: '#efeae0' },
    continental: { coat: '#24407a', coat2: '#e7d7a8', hat: 'tricorn', hatCol: '#1c1a1a', trim: '#d4a72c', hairStyle: 'short', hair: '#5a3b22' },
    king_george: { coat: '#9e1b2a', coat2: '#e9d9a6', hat: 'crown', hairStyle: 'wig', hair: '#efeae0', sash: '#1f4fa8', medal: 1, epaulettes: 1 },
    franklin: { coat: '#6b4f33', coat2: '#8a6a47', hairStyle: 'franklin', hair: '#d8d3cb', glasses: 1, skin: '#efc49c' },
    governor: { coat: '#2a3f6b', coat2: '#e9e2d0', hairStyle: 'wig', hair: '#efeae0', trim: '#d4a72c' },
    washington: { coat: '#24407a', coat2: '#e7d7a8', hairStyle: 'wig', hair: '#efeae0', epaulettes: 1, trim: '#d4a72c' },
    hessian: { coat: '#1f3f7a', coat2: '#d21034', hat: 'mitre', hatCol: '#c9a227', trim: '#d21034', hairStyle: 'short', hair: '#3b2a1a', beard: 'mustache' },
    french_officer: { coat: '#eeeadf', coat2: '#1f3f8a', hat: 'tricorn', hatCol: '#1c1a1a', trim: '#d4a72c', hairStyle: 'wig', hair: '#efeae0' },
    lord_north: { coat: '#3a3a3a', coat2: '#d8d1c0', hairStyle: 'wig', hair: '#efeae0', medal: 1, sash: '#1f4fa8' },
    roman: { coat: '#9e1b2a', coat2: '#c9a85a', hat: 'roman', trim: '#c8102e', hairStyle: 'short', hair: '#3b2a1a' },
    hitler: { coat: '#7a6a45', coat2: '#5f5235', trim: '#3a3226', hairStyle: 'short', hair: '#2a1d12', beard: 'toothbrush', skin: '#efc6a0', sash: '#b3202a' },
    us_sailor: { coat: '#1d2f5a', coat2: '#f7f7f2', hat: 'sailor', trim: '#f7f7f2', hairStyle: 'short', hair: '#3b2a1a', skin: '#efc6a0' },
    carthaginian_woman: { coat: '#5b2a6e', coat2: '#d4a72c', hat: 'diadem', hatCol: '#d4a72c', trim: '#e8c35a', trim2: '#b3202a', hairStyle: 'flowing', hair: '#1f140c', skin: '#c99068', female: 1 },
    scipio: { coat: '#9e1b2a', coat2: '#e9d9a6', hat: 'roman', hatCol: '#b8b8b8', trim: '#d4a72c', hairStyle: 'short', hair: '#3b2a1a', skin: '#e8b98f' },
    carthaginian: { coat: '#5b2a6e', coat2: '#d4a72c', hat: 'helmet', hatCol: '#a9883e', hairStyle: 'short', hair: '#2b1d12', beard: 'full', skin: '#c99068' },
    us_officer: { coat: '#8a7d4a', coat2: '#6f6438', hat: 'kepi', hatCol: '#6f6438', trim: '#d4a72c', hairStyle: 'short', hair: '#5a3b22', medal: 1 },
    soviet_officer: { coat: '#5a6b3a', coat2: '#3f4c28', hat: 'kepi', hatCol: '#4a5a2e', trim: '#c8102e', hairStyle: 'short', hair: '#3b2a1a', epaulettes: 1, medal: 1 },
    // 1859 Pig War (Smoke & Borders): US Army in dark blue with kepis, Royal Navy in navy and gold, settler, HBC trader, governor
    us_army_1859: { coat: '#1f2f5a', coat2: '#2c3f73', hat: 'kepi', hatCol: '#1a2647', trim: '#d4a72c', hairStyle: 'short', hair: '#5a3b22', beard: 'mustache' },
    pickett: { coat: '#1f2f5a', coat2: '#2c3f73', hat: 'kepi', hatCol: '#1a2647', trim: '#d4a72c', hairStyle: 'long', hair: '#6b4a2a', beard: 'mustache', epaulettes: 1 },
    rn_officer: { coat: '#141c3a', coat2: '#f1ede2', hat: 'bicorne', hatCol: '#111', trim: '#d4a72c', hairStyle: 'short', hair: '#3b2a1a', epaulettes: 1 },
    settler: { coat: '#6b4f33', coat2: '#c9b58a', hat: 'tophat', hatCol: '#4a3a2a', trim: '#8a6a47', hairStyle: 'short', hair: '#7a5230', beard: 'full' },
    hbc_man: { coat: '#2f4a3a', coat2: '#d8d1c0', hat: 'tophat', hatCol: '#222', trim: '#b3202a', hairStyle: 'short', hair: '#a0522d', beard: 'mustache' },
    douglas: { coat: '#2a2a33', coat2: '#e9e2d0', hairStyle: 'short', hair: '#d8d3cb', skin: '#c99068', medal: 1 },
    korean: { coat: '#f1ede2', coat2: '#c8102e', hairStyle: 'short', hair: '#1c1a1a', skin: '#efc49c' },
    rhee: { coat: '#2b2b33', coat2: '#e9e2d0', hairStyle: 'short', hair: '#d8d3cb', glasses: 1, skin: '#efc49c' },
    kim: { coat: '#4a4a52', coat2: '#d8d1c0', hairStyle: 'short', hair: '#1c1a1a', skin: '#efc49c', hat: 'none' }
  };
})(typeof window !== 'undefined' ? window : globalThis);
