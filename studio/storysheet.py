"""Storyboard review sheet (owner, 15 Nov 2026: "some scenes were not sync with the script, not related, repeated").
One still per shot, with the exact words spoken while it is on screen, on contact sheets of 20 shots:
    NARRATOR=kokoro python3 studio/storysheet.py <story-id>  -> studio/out/<...>/storyboard-01.jpg, -02.jpg ...
Look at every sheet before rendering: does each picture show what the words say, right when they say it? Is anything repeated?
Fix the storyboard, then look again. Shots marked REPEAT are the same picture used before."""
import sys, os, json, asyncio, io, glob, textwrap
os.environ.setdefault('NARRATOR', 'kokoro'); sid = sys.argv[1]; sys.argv = ['make_doc.py', sid]
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE); os.chdir(HERE)
import make_doc as M
from kokoro_onnx import Kokoro
from PIL import Image, ImageDraw, ImageFont
story = json.load(open(os.path.join(HERE, 'doc', 'stories', sid + '.json')))
tl, clips, cues, moods, chapters, total = M.build(story, Kokoro('tts/kokoro.onnx', 'tts/voices.bin'))
sc = sorted([e for e in tl['events'] if e['k'] == 'scene'], key=lambda e: e['t'])
words = [(x['t'], x['w']) for c in tl['captions'] for x in c['words']]
shots, seen = [], {}
for i, e in enumerate(sc):
    end = sc[i + 1]['t'] if i + 1 < len(sc) else total
    said = ' '.join(w for t, w in words if e['t'] - .05 <= t < end)
    key = json.dumps({k: v for k, v in e.items() if k not in ('t', 'dur', 'k', 'u', 'from', 'text', 'mood', 'name', 'who', 'side')}, sort_keys=True)
    rep = e.get('shot') not in ('talk', 'off', 'card', 'doc') and key in seen
    seen.setdefault(key, i)
    shots.append((e['t'] + min(1.6, (end - e['t']) * .5), e, said, end - e['t'], rep))
frames = asyncio.run(M.render(story['era'], tl, [s[0] for s in shots]))
outdir = sorted(glob.glob(os.path.join(HERE, 'out', '*-doc-' + sid)))[-1] if glob.glob(os.path.join(HERE, 'out', '*-doc-' + sid)) else os.path.join(HERE, 'out', 'storyboard-' + sid)
os.makedirs(outdir, exist_ok=True)
try: font = ImageFont.truetype('DejaVuSans.ttf', 17); bold = ImageFont.truetype('DejaVuSans-Bold.ttf', 18)
except Exception: font = bold = ImageFont.load_default()
W, H, TH = 480, 270, 120; per = 20; cols = 4
for pg in range(0, len(shots), per):
    part = list(zip(shots, frames))[pg:pg + per]; rows = (len(part) + cols - 1) // cols
    sheet = Image.new('RGB', (W * cols, (H + TH) * rows), (18, 16, 14)); d = ImageDraw.Draw(sheet)
    for j, ((t, e, said, dur, rep), fr) in enumerate(part):
        x, y = (j % cols) * W, (j // cols) * (H + TH); sheet.paste(Image.open(io.BytesIO(fr)).resize((W, H)), (x, y))
        what = e.get('shot') + (':' + e['img'] if e.get('img') else '') + (' ' + e.get('who', '') if e.get('shot') == 'talk' else '')
        d.text((x + 6, y + H + 4), '#%d  %d:%02d  %.1fs  %s%s' % (pg + j + 1, int(e['t'] // 60), int(e['t'] % 60), dur, what, '   REPEAT' if rep else ''), fill=(255, 90, 70) if rep else (232, 176, 74), font=bold)
        for k, line in enumerate(textwrap.wrap(said or '(no narration)', 52)[:3]): d.text((x + 6, y + H + 32 + k * 26), line, fill=(235, 228, 210), font=font)
    p = os.path.join(outdir, 'storyboard-%02d.jpg' % (pg // per + 1)); sheet.save(p, quality=80); print(p)
print('%d shots, %d marked REPEAT' % (len(shots), sum(1 for s in shots if s[4])))
