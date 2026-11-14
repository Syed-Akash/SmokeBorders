"""Dot Thinks: makes one deep-thought Short with Dot, the channel's mascot (the only ball without a flag).
usage: python3 make_thought.py [thought-id]     (no id: the next thought that hasn't been used yet)
Scripts live in thoughts/thoughts.json; used ids are kept in thoughts/used.json (updated only on success).
Output: out/<date>-thought-<id>/<id>.mp4, cover.jpg and summary.json.
Everything is free and offline: a blended Kokoro voice with a studio chain (deeper pitch with natural formants, EQ, compression,
hall reverb), a synthesized cinematic score and sound effects, and dot3d.html (Three.js: 3D Dot, scenes, bloom, film grade)
drawn frame by frame in headless Chromium, then ffmpeg."""
import asyncio, base64, datetime, functools, http.server, json, os, re, socketserver, subprocess, sys, threading, time
import numpy as np, soundfile as sf
from playwright.async_api import async_playwright
from browser import launch

HERE = os.path.dirname(os.path.abspath(__file__)); TH = os.path.join(HERE, 'thoughts')
GAME = os.path.join(os.path.dirname(HERE), 'game', 'blast-nations.html')
SR = 24000; FPS = 30; MSR = 48000
VOICE_MIX = [('am_fenrir', 1.0)]   # Dot's voice: rough, deep American (chosen by the owner from 8 samples)

def clean(s):  # what is spoken: no highlight stars, no emoji
    s = s.replace('*', '').replace('…', '...')
    return re.sub(r'[\U0001F000-\U0001FFFF☀-➿️‍]', '', s).strip()

def words(s):
    """Split a line into words; words between *stars* are highlighted (a highlight can span several words)."""
    out, on = [], False
    for w in s.split():
        n = w.count('*'); hl = on or n > 0
        if n % 2: on = not on
        out.append({'w': w.replace('*', ''), 'hl': hl})
    return out

def time_words(ws, a, t0):
    """Word start times: the line is cut into clauses at punctuation, clauses are matched to the longest pauses in the audio,
    and words inside a clause are spread by length."""
    hop = int(.01 * SR); rms = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, len(a) - hop, hop)]); thr = max(rms.max() * .06, 1e-4)
    voiced = np.where(rms > thr)[0]; start, end = (voiced[0], voiced[-1]) if len(voiced) else (0, len(rms) - 1)
    gaps, run = [], None
    for i in range(start, end):
        if rms[i] <= thr: run = run if run is not None else i
        elif run is not None:
            if i - run >= 8: gaps.append((i - run, run, i))
            run = None
    cuts = [i for i, w in enumerate(ws[:-1]) if re.search(r'[,.;:!?…]$', w['w'])]
    use = sorted(sorted(gaps, reverse=True)[:len(cuts)], key=lambda g: g[1]); cuts = cuts[:len(use)]
    spans, prev = [], start
    for g in use: spans.append((prev, g[1])); prev = g[2]
    spans.append((prev, end)); groups, j = [], 0
    for c in cuts: groups.append(ws[j:c + 1]); j = c + 1
    groups.append(ws[j:])
    for grp, (s0, s1) in zip(groups, spans):
        tot = sum(len(w['w']) + 2 for w in grp) or 1; acc = 0
        for w in grp: w['t'] = round(t0 + (s0 + (s1 - s0) * acc / tot) * .01 - .03, 3); acc += len(w['w']) + 2

# ---------- sound ----------
def reverb_ir(sec=2.2, sr=MSR, seed=7):
    rng = np.random.default_rng(seed); n = int(sec * sr); t = np.arange(n) / sr
    ir = rng.standard_normal(n) * np.exp(-t * 3.2); k = 24; ir = np.convolve(ir, np.ones(k) / k, 'same')   # darker tail
    ir[:int(.022 * sr)] = 0; ir[0] = 1.0; return (ir / np.abs(ir).max()).astype(np.float32)

def convolve(x, ir):
    """Reverb by convolution. Block by block (overlap-add): the same result as one huge FFT, which needed ~4 GB for a
    35-minute track and got the render killed on an 8 GB machine."""
    try:
        from scipy.signal import oaconvolve
        return oaconvolve(np.asarray(x, np.float32), np.asarray(ir, np.float32))[:len(x)].astype(np.float32)
    except ImportError:
        n = len(x) + len(ir); N = 1 << (n - 1).bit_length(); return np.fft.irfft(np.fft.rfft(x, N) * np.fft.rfft(ir, N), N)[:len(x)].astype(np.float32)

def score(total, seed, cues):
    """A slow cinematic bed: warm detuned pads (Am-F-C-G), a sub, a sparse piano, all through a hall; plus whooshes on cuts,
    deep booms and a riser into the question."""
    rng = np.random.default_rng(seed); n = int(total * MSR); t = np.arange(n) / MSR; pad = np.zeros(n, np.float32)
    chords = [[110.0, 130.81, 164.81, 220.0], [87.31, 130.81, 174.61, 220.0], [65.41, 130.81, 164.81, 196.0], [98.0, 123.47, 146.83, 196.0]]; L = 6.0
    for ci in range(int(total / L) + 2):
        s0 = ci * L - 1.2; ch = chords[ci % 4]; i0, i1 = max(0, int(s0 * MSR)), min(n, int((s0 + L + 2.4) * MSR))
        if i0 >= i1: continue
        tt = t[i0:i1] - s0; env = np.clip(tt / 2.0, 0, 1) * np.clip((L + 2.4 - tt) / 2.0, 0, 1)
        for f in ch:
            for d in (-.8, 0, .8):
                ph = 2 * np.pi * (f + d) * tt; wave = sum(np.sin(h * ph) / h * (.85 ** h) for h in range(1, 7))   # soft saw
                pad[i0:i1] += wave * env * .022
        pad[i0:i1] += np.sin(2 * np.pi * ch[0] / 2 * tt) * env * .09
    k = 48; pad = np.convolve(pad, np.ones(k) / k, 'same').astype(np.float32)
    piano = np.zeros(n, np.float32); notes = [220.0, 261.63, 293.66, 329.63, 392.0, 440.0, 523.25]; tt0 = 1.4
    while tt0 < total - 2:
        f = notes[rng.integers(len(notes))]; i0 = int(tt0 * MSR); i1 = min(n, i0 + int(3 * MSR)); tt = t[i0:i1] - tt0
        piano[i0:i1] += sum(np.sin(2 * np.pi * f * h * tt) * (.5 ** h) * np.exp(-tt * (1.6 + h * .9)) for h in range(1, 6)) * .16
        tt0 += rng.choice([1.5, 2.25, 3.0])
    music = pad + piano; music = music * .7 + convolve(music, reverb_ir()) * .35
    sfx = np.zeros(n, np.float32)
    for kind, at in cues:
        i0 = int(max(0, at) * MSR)
        if kind == 'whoosh':
            d = int(.7 * MSR); tt = np.arange(d) / MSR; noise = rng.standard_normal(d).astype(np.float32)
            env = np.sin(np.pi * np.clip(tt / .7, 0, 1)) ** 2; sm = int(6 + 40 * (1 - tt[-1] / .7)); x = np.convolve(noise, np.ones(12) / 12, 'same') - np.convolve(noise, np.ones(60) / 60, 'same')
            seg = (x * env * .5).astype(np.float32)
        elif kind == 'boom':
            d = int(2.6 * MSR); tt = np.arange(d) / MSR; f = 48 - 14 * np.clip(tt / 1.5, 0, 1)
            seg = (np.sin(2 * np.pi * np.cumsum(f) / MSR) * np.exp(-tt * 1.6) * .9 + np.convolve(rng.standard_normal(d), np.ones(200) / 200, 'same') * np.exp(-tt * 9) * 2).astype(np.float32)
        else:  # riser
            d = int(1.8 * MSR); tt = np.arange(d) / MSR; i0 = int(max(0, at - 1.8) * MSR); u = tt / 1.8
            x = np.convolve(rng.standard_normal(d), np.ones(8) / 8, 'same') * u ** 2 * .35 + np.sin(2 * np.pi * np.cumsum(200 + 900 * u ** 2) / MSR) * u ** 3 * .08
            seg = x.astype(np.float32)
        j = min(n, i0 + len(seg)); sfx[i0:j] += seg[:j - i0]
    sfx = sfx * .8 + convolve(sfx, reverb_ir(1.6, seed=3)) * .25
    for a in (music, sfx): a /= (np.abs(a).max() or 1)
    return music * .5, sfx * .55

# ---------- picture ----------
def build_page():
    g = open(GAME).read()
    wm = re.search(r'const WORLD_MAP=".*?";', g, re.S).group(0); fn = re.search(r'function worldMap\(\)\{.*?\n  return WMAP\}', g, re.S).group(0)
    dst = os.path.join(TH, '_build3d.html'); open(dst, 'w').write(open(os.path.join(TH, 'dot3d.html')).read().replace('/*WORLD_MAP*/', 'let WMAP=null;\n' + wm + '\n' + fn)); return dst

class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass

async def render(data, out_mp4):
    build_page()
    srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(_Quiet, directory=HERE)); port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    tmp = out_mp4[:-4] + '.tmp.mp4'; nfr = int(data['total'] * FPS); errs = []
    enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                            '-c:v', 'libx264', '-preset', 'medium', '-crf', '21', '-pix_fmt', 'yuv420p', '-r', str(FPS), tmp], stdin=subprocess.PIPE)
    try:
        async with async_playwright() as p:
            b = await launch(p, args=['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'])
            pg = await b.new_page(viewport={'width': 1080, 'height': 1920}); pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('http://127.0.0.1:%d/thoughts/_build3d.html' % port); await pg.wait_for_function('window.__ok', timeout=120000)
            await pg.evaluate('ready()'); await pg.evaluate('d=>init(d)', data); t0 = time.time()
            for i in range(0, nfr, 3):
                urls = await pg.evaluate("([a,b])=>{const o=[];for(let i=a;i<b;i++){frame(i/30);o.push(document.getElementById('out').toDataURL('image/jpeg',.93))}return o}", [i, min(nfr, i + 3)])
                for u in urls: enc.stdin.write(base64.b64decode(u.split(',', 1)[1]))
                if i % 150 == 0: print('frame %d/%d (%.0fs)' % (i, nfr, time.time() - t0), flush=True)
            await b.close()
    finally:
        enc.stdin.close(); enc.wait(); srv.shutdown()
    if enc.returncode or errs: raise RuntimeError('render failed: %s %s' % (enc.returncode, errs[:3]))
    os.replace(tmp, out_mp4)

def main():
    data = json.load(open(os.path.join(TH, 'thoughts.json')))['thoughts']; usedf = os.path.join(TH, 'used.json')
    used = json.load(open(usedf)) if os.path.exists(usedf) else []
    if len(sys.argv) > 1: th = next(x for x in data if x['id'] == sys.argv[1])
    else:
        fresh = [x for x in data if x['id'] not in used]
        if not fresh: sys.exit('NO UNUSED THOUGHTS: write new ones in studio/thoughts/thoughts.json first')
        th = fresh[0]
    t0 = time.time(); day = datetime.date.today().isoformat(); outdir = os.path.join(HERE, 'out', '%s-thought-%s' % (day, th['id'])); os.makedirs(outdir, exist_ok=True)
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(HERE, 'tts/kokoro.onnx'), os.path.join(HERE, 'tts/voices.bin'))
    style = sum(k.get_voice_style(v) * w for v, w in VOICE_MIX)
    say = lambda text, sp: k.create(text, voice=style, speed=sp, lang='en-us')[0].astype(np.float32)
    # 1) voice and timeline (a breath of silence before key lines, longer before a new scene)
    clips = []; t = 1.0; lines = []; segs = []; cues = [('boom', .15)]
    for i, L in enumerate(th['lines']):
        a = say(clean(L['say']), .9); d = len(a) / SR; ws = words(L['say']); time_words(ws, a, t)
        lines.append({'scene': L['scene'], 'start': round(t, 3), 'end': round(t + d + .3, 3), 'words': ws}); clips.append((t, a))
        if not segs or segs[-1]['scene'] != L['scene']:
            segs.append({'scene': L['scene'], 'start': round(max(0, t - .35), 3)})
            if i: cues.append(('whoosh', t - .55))
        nxt = th['lines'][i + 1]['scene'] if i + 1 < len(th['lines']) else 'question'
        t += d + (.9 if nxt != L['scene'] else .5)
    t += .5; qa = say(clean(th['question']), .86); qd = len(qa) / SR; qw = words(th['question']); time_words(qw, qa, t)
    question = {'start': round(t, 3), 'words': qw}; clips.append((t, qa)); segs.append({'scene': 'question', 'start': round(t - .4, 3)})
    cues += [('riser', t - .35), ('boom', t - .3)]
    total = round(t + qd + 3.6, 2)
    vo = np.zeros(int((total + 1) * SR), np.float32)
    for s0, a in clips: i = int(s0 * SR); vo[i:i + len(a)] += a
    vraw = os.path.join(outdir, 'voice_raw.wav'); sf.write(vraw, vo, SR)
    hop = SR // FPS; rms = np.array([np.sqrt(np.mean(vo[j * hop:(j + 1) * hop] ** 2)) for j in range(int(total * FPS) + 1)])
    ref = np.percentile(rms[rms > .005], 90) if (rms > .005).any() else 1; mouth = np.convolve(np.clip(rms / ref, 0, 1), [.2, .3, .3, .2], 'same')
    page_data = {'lines': lines, 'segs': segs, 'question': question, 'total': total, 'mouth': [round(float(x), 3) for x in mouth]}
    # 2) picture
    vid = os.path.join(outdir, 'video.mp4'); asyncio.run(render(page_data, vid))
    # 3) sound
    music, sfx = score(total + 1, sum(map(ord, th['id'])), cues)
    mw, xw, irw = (os.path.join(outdir, n) for n in ('music.wav', 'sfx.wav', 'ir.wav')); sf.write(mw, music, MSR); sf.write(xw, sfx, MSR); sf.write(irw, reverb_ir(1.8, seed=11), MSR)
    final = os.path.join(outdir, th['id'] + '.mp4'); tmp = final[:-4] + '.tmp.mp4'
    flt = ('[1:a]aresample=48000,rubberband=pitch=0.92:formant=preserved,highpass=f=70,lowshelf=g=3.5:f=170,equalizer=f=420:t=q:w=1:g=-2.5,'
           'equalizer=f=3300:t=q:w=1.2:g=2,deesser=i=0.4,acompressor=threshold=0.08:ratio=3:attack=8:release=150:makeup=2,asplit=3[dry][wet0][sc];'
           '[wet0][4:a]afir=dry=0:wet=1,volume=0.28[wet];[dry][wet]amix=inputs=2:normalize=0[v];'
           '[2:a]volume=0.6[m];[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=25:release=600[md];'
           '[3:a]volume=0.9[x];[md][x][v]amix=inputs=3:duration=first:normalize=0,loudnorm=I=-14:TP=-2:LRA=10,alimiter=limit=0.84:level=false[a]')
    r = subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', vid, '-i', vraw, '-i', mw, '-i', xw, '-i', irw, '-filter_complex', flt, '-map', '0:v', '-map', '[a]',
                        '-c:v', 'copy', '-c:a', 'aac', '-b:a', '256k', '-shortest', '-movflags', '+faststart', tmp], capture_output=True, text=True)
    if r.returncode: sys.exit('mux failed: ' + r.stderr[-800:])
    os.replace(tmp, final)
    for f in (vid, vraw, mw, xw, irw): os.remove(f)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(question['start'] + 1.6), '-i', final, '-frames:v', '1', '-q:v', '2', os.path.join(outdir, 'cover.jpg')], check=True)
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', final]).decode().strip())
    ok = dur <= 59
    summ = {'id': th['id'], 'title': th['title'], 'question': clean(th['question']), 'script': [clean(L['say']) for L in th['lines']], 'sources': th.get('sources', []),
            'duration': round(dur, 1), 'ok': ok, 'build_seconds': round(time.time() - t0), 'playlists': ['thoughts'], 'file': final}
    json.dump(summ, open(os.path.join(outdir, 'summary.json'), 'w'), indent=1)
    if ok and th['id'] not in used: used.append(th['id']); json.dump(used, open(usedf, 'w'), indent=1)
    print(json.dumps({k: summ[k] for k in ('id', 'title', 'duration', 'ok', 'build_seconds')}))

if __name__ == '__main__':
    main()
