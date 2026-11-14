"""Realistic portraits for thumbnails, in the Smoke & Borders look (owner, 11 Nov 2026: realistic like the big history channels,
but with our own flavour). The person is a real public-domain or free-licensed painting/photo from Wikimedia Commons, cut out
of its background, given a high-contrast grade, a thick white sticker outline and an ember-orange rim light, then saved as a PNG
with transparency that thumb2.html places like a character ({"portrait": "smoke/portraits/<name>.png"}).

usage: python3 smoke/portrait.py <name> "<Commons file title or search words>" [--flip]
  e.g. python3 smoke/portrait.py washington "File:Gilbert Stuart Williamstown Portrait of George Washington.jpg"
Writes smoke/portraits/<name>.png and adds the credit to smoke/portraits/credits.json (put CC BY / CC BY-SA credits in the
video description). Refuses anything whose licence isn't public domain, CC0, CC BY or CC BY-SA.
Needs: commons.wikimedia.org + upload.wikimedia.org reachable, pip rembg + onnxruntime (u2net models come from GitHub releases)."""
import io, json, os, re, sys, urllib.error, urllib.parse, urllib.request
import numpy as np
from PIL import Image, ImageFilter, ImageEnhance, ImageOps

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'portraits'); os.makedirs(OUT, exist_ok=True)
UA = {'User-Agent': 'SmokeBordersThumbnails/1.0 (https://github.com/Syed-Akash/Flagbomb; history thumbnails) python-urllib'}   # Wikimedia asks for a contact URL
OK = re.compile(r'^(public domain|pd\b|pd-|cc0|cc by(-sa)? ?[1-4]\.\d|cc-by(-sa)?-[1-4]\.\d|no restrictions)', re.I)

def api(**q):
    import time; time.sleep(1.2)   # be polite: Wikimedia answers 429 to fast clients
    q.update(format='json'); return json.load(io.BytesIO(fetch('https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode(q))))

def fetch(url, tries=6):
    """GET with back-off: Wikimedia answers 429 when the shared address is busy; wait 15, 30, 60... seconds and retry."""
    import time
    for k in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r: return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429 or k == tries - 1: raise
            time.sleep(15 * 2 ** k)

def find(query):
    """A Commons file title, given one or by searching the File namespace."""
    if query.lower().startswith('file:'): return query
    hits = api(action='query', list='search', srsearch=query + ' portrait', srnamespace=6, srlimit=8)['query']['search']
    hits = [h for h in hits if h['title'].lower().endswith(('.jpg', '.jpeg', '.png'))]   # photos only: no PDF pages or scans of whole books
    if not hits: sys.exit('nothing found on Commons for: ' + query)
    return hits[0]['title']

def info(title):
    w0 = next(iter(api(action='query', titles=title, prop='imageinfo', iiprop='size')['query']['pages'].values()))['imageinfo'][0]['width']
    sw = max([x for x in (330, 500, 960, 1280) if x < w0] or [330])   # a standard thumbnail size SMALLER than the original, or Wikimedia serves the original (429)
    p = next(iter(api(action='query', titles=title, prop='imageinfo', iiprop='url|size|extmetadata', iiurlwidth=sw)['query']['pages'].values()))
    ii = p['imageinfo'][0]; md = ii.get('extmetadata', {}); g = lambda k: re.sub('<[^>]+>', '', md.get(k, {}).get('value', '')).strip()
    src = ii.get('thumburl') or ii['url']   # Wikimedia asks for standard thumbnail sizes (1280 is one); originals get 429 from shared addresses
    url = re.sub(r'\?.*$', '', src.replace('thumb.wikimedia.org', 'upload.wikimedia.org'))   # only upload.* is allowed
    return {'title': title, 'url': url, 'page': ii.get('descriptionurl'), 'license': g('LicenseShortName'),
            'artist': g('Artist')[:200], 'credit': g('Credit')[:200]}

def cutout(img):
    from rembg import remove, new_session
    out = remove(img, session=new_session(os.environ.get('REMBG_MODEL', 'isnet-general-use')))
    a = np.asarray(out.getchannel('A'))
    if (a > 128).mean() > .45:   # it kept the whole print or frame (engravings, framed paintings): try the person-only model
        out = remove(img, session=new_session('u2net_human_seg'))
    return out

def style(rgba, flip=False):
    """Our look: punchy grade, warm shadows, white sticker outline, ember rim light on one side, a little grain."""
    if flip: rgba = ImageOps.mirror(rgba)   # careful: mirrors badges and text (use only for paintings without writing)
    a = np.asarray(rgba.getchannel('A')).copy(); h_, w_ = a.shape; b = max(4, int(min(h_, w_) * .02))
    a[:, :b] = 0; a[:, -b:] = 0; a[:b, :] = 0                       # scan borders and frame edges are never the person
    try:   # keep only the biggest piece (drops stray specks the cut-out left behind)
        from scipy import ndimage
        lab, n = ndimage.label(a > 40)
        if n > 1: keep = 1 + int(np.argmax(ndimage.sum(np.ones_like(lab), lab, range(1, n + 1)))); a[(lab != keep) & (lab > 0)] = 0
    except ImportError: pass
    a = Image.fromarray(a); rgb = rgba.convert('RGB')
    rgb = ImageEnhance.Contrast(rgb).enhance(1.25); rgb = ImageEnhance.Color(rgb).enhance(1.15); rgb = ImageEnhance.Sharpness(rgb).enhance(1.6)
    arr = np.asarray(rgb).astype(np.float32); lum = arr.mean(axis=2, keepdims=True) / 255
    arr = arr * (0.92 + 0.08 * lum) + np.array([18, 6, -6]) * (1 - lum)          # warm the shadows
    # ember rim light: brighten the edge facing left (towards the map), orange
    m = np.asarray(a).astype(np.float32) / 255; inner = np.asarray(a.filter(ImageFilter.MinFilter(15))).astype(np.float32) / 255
    rim = np.clip(m - inner, 0, 1); xs = np.linspace(1, 0, m.shape[1])[None, :]; rim = rim * (0.35 + 0.65 * xs)
    arr = arr + rim[..., None] * np.array([255, 120, 30]) * 0.85
    arr = arr + np.random.default_rng(1).normal(0, 5, arr.shape)                     # film grain
    body = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)); body.putalpha(a)
    # white sticker outline (dilated alpha) with a soft dark shadow under it
    pad = 40; W, H = rgba.size; canvas = Image.new('RGBA', (W + 2 * pad, H + 2 * pad), (0, 0, 0, 0))
    big = Image.new('L', canvas.size, 0); big.paste(a, (pad, pad)); ring = big.filter(ImageFilter.MaxFilter(19))
    shadow = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); shadow.putalpha(ring.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * .6)))
    canvas = Image.alpha_composite(canvas, shadow); white = Image.new('RGBA', canvas.size, (255, 255, 255, 0)); white.putalpha(ring)
    canvas = Image.alpha_composite(canvas, white); canvas.alpha_composite(body, (pad, pad))
    out = canvas.crop(canvas.getbbox())
    if out.height > 1200: out = out.resize((round(out.width * 1200 / out.height), 1200), Image.LANCZOS)   # thumbnails never need more
    return out

def main():
    name, query = sys.argv[1], sys.argv[2]; meta = info(find(query))
    if not OK.match(meta['license'] or ''): sys.exit('refused: licence "%s" is not public domain / CC0 / CC BY / CC BY-SA (%s)' % (meta['license'], meta['page']))
    img = Image.open(io.BytesIO(fetch(meta['url']))).convert('RGB')
    if img.height < 1000: img = img.resize((round(img.width * 1000 / img.height), 1000), Image.LANCZOS)   # small sources: enlarge before the cut-out
    out = style(cutout(img), '--flip' in sys.argv); p = os.path.join(OUT, name + '.png'); out.save(p)
    cp = os.path.join(OUT, 'credits.json'); cr = json.load(open(cp)) if os.path.exists(cp) else {}; cr[name] = meta; json.dump(cr, open(cp, 'w'), indent=1, ensure_ascii=False)
    print(p, '|', meta['license'], '|', meta['artist'] or meta['credit'], '|', meta['page'])

if __name__ == '__main__':
    main()
