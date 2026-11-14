"""Smoke & Borders thumbnails (1280x720), in the layout the top channel in the niche (Animated History) proves works, with our own twist:
the old world on parchment on the left, today's world in colour on the right, split by a burning border; one big illustrated
character for each side (smoke/brand/chars.js, never countryballs); two black year boxes at the top; one huge word at the bottom;
an ember "BOTH SIDES" ribbon in the corner.
usage: python3 smoke/make_thumb_sb.py <story-id> [out.jpg]
       python3 smoke/make_thumb_sb.py <story-id> --ab   -> smoke/ab/<id>/a.jpg, b.jpg, c.jpg + ab.md from the story's "abTest"
  "abTest": [{"title": "...", "thumb": {overrides of "thumb", e.g. kicker/word}}, x3]; A is what gets uploaded,
  B and C are for YouTube Studio's Test & Compare, which the owner switches on (the API can't).
The story's "thumb" block:
  {"then": "1715", "now": "1783", "center": [lon, lat], "scale": 700,
   "hlThen": [{"names": [...], "color": "#c8102e"}], "hlNow": [...],
   "left":  {"preset": "king_george", "mood": "angry"},     (any chars.js preset + overrides; optional x, h)
   "right": {"preset": "washington",  "mood": "smug"},
   "years": ["1763", "1783"], "word": "LOST?"}"""
# v2 layouts (owner review 9 Nov 2026), used when the thumb block has "layout": spotlight | circled | versus | dossier | mapperson,
#   with scene (fire | sea | map), topic (the bar people recognise), hook [line1, line2], hi (word in yellow), hidden {preset...}, anchor {preset...}
import functools, http.server, json, os, sys, threading
from playwright.sync_api import sync_playwright
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..'))

def make(sid, out=None, spec=None):
    story = json.load(open(os.path.join(ROOT, 'studio', 'doc', 'stories', sid + '.json'))) if spec is None else {}
    spec = spec or dict(story['thumb'], **((story.get('abTest') or [{}])[0].get('thumb', {})));   # the uploaded thumbnail is pair A
    out = out or os.path.join(ROOT, 'studio', 'out', 'thumb-%s.jpg' % sid)
    # STYLE.md 4: real photo portraits only, never cartoon characters (owner, repeated). Refuse instead of drawing a stand-in.
    people = {k: spec[k] for k in ('hidden', 'anchor', 'left', 'right', 'hero') if isinstance(spec.get(k), dict) and not spec[k].get('flag')}
    bad = [k for k, v in people.items() if not v.get('portrait') or not os.path.exists(os.path.join(ROOT, v['portrait']))]
    if bad: sys.exit('thumbnail refused: %s needs a real portrait PNG (smoke/portrait.py), not a cartoon character: %s' % (sid, ', '.join('%s=%s' % (k, people[k].get('portrait') or people[k].get('preset')) for k in bad)))
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT))
    srv.RequestHandlerClass.log_message = lambda *a: None; threading.Thread(target=srv.serve_forever, daemon=True).start()
    with sync_playwright() as p:
        _ch = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'studio', '.chromium'); b = p.chromium.launch(executable_path=open(_ch).read().strip()) if os.path.exists(_ch) else p.chromium.launch(); pg = b.new_page(viewport={'width': 1280, 'height': 720}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto('http://127.0.0.1:%d/smoke/%s' % (srv.server_port, 'thumb2.html' if spec.get('layout') else 'thumb.html')); pg.evaluate('s => { window.SPEC = s; return window.draw() }', spec)
        pg.wait_for_function('window.done', timeout=180000)
        if pg.evaluate('window.OVERLAP || 0'): print('WARNING: text still covers a person after shrinking; change the layout or the hook length')
        pg.screenshot(path=out, type='jpeg', quality=92); b.close()
    if errs: print('page errors:', errs)
    srv.shutdown(); print(out); return out

def ab(sid):
    story = json.load(open(os.path.join(ROOT, 'studio', 'doc', 'stories', sid + '.json'))); d = os.path.join(HERE, 'ab', sid); os.makedirs(d, exist_ok=True)
    raw = 'https://raw.githubusercontent.com/Syed-Akash/Flagbomb/main/smoke/ab/%s/' % sid; lines = ['# Test & Compare: %s' % sid, '',
        'In YouTube Studio: Content > the video > Details > A/B Testing. If all three titles below are the same, choose **Thumbnail** only and upload the three images; otherwise choose Title and thumbnail. A is already uploaded.', '']
    import glob; sm = sorted(glob.glob(os.path.join(ROOT, 'studio', 'out', '*-doc-%s' % sid, 'summary.json')))   # {min} = the real length, once rendered
    mins = str(round(json.load(open(sm[-1]))['duration'] / 60)) if sm else 'N'
    for k, v in zip('abc', story['abTest']):
        make(None, os.path.join(d, k + '.jpg'), dict(story['thumb'], **v.get('thumb', {})))
        lines += ['**%s.** %s' % (k.upper(), (v.get('title') or story['abTest'][0]['title']).replace('{min}', mins)), '   thumbnail (%s): %s%s.jpg' % (dict(story['thumb'], **v.get('thumb', {})).get('layout', 'split'), raw, k), '']
    open(os.path.join(d, 'ab.md'), 'w').write('\n'.join(lines)); print('\n'.join(lines))

if __name__ == '__main__':
    if '--ab' in sys.argv: ab(sys.argv[1])
    else: make(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
