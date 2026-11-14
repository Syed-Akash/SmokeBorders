"""Render the 5 branding concepts and a channel-page mock-up of each to smoke/brand/concepts/.
usage: python3 smoke/brand/concepts.py [concept numbers...]"""
import functools, http.server, os, sys, threading
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(HERE, '..', '..')); OUT = os.path.join(HERE, 'concepts')
NAMES = {1: 'Split Ball', 2: 'Torn Globe', 3: 'Two Faces', 4: 'Burning Pin', 5: 'Passport Stamp',
         6: 'Globe of Eras', 7: 'Hourglass of Empires', 8: 'Then and Now', 9: 'Layers of Time', 10: 'The Era Dial'}
os.makedirs(OUT, exist_ok=True)
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT))
srv.RequestHandlerClass.log_message = lambda *a: None
threading.Thread(target=srv.serve_forever, daemon=True).start()

def circle(im, d):
    im = im.resize((d, d), Image.LANCZOS); m = Image.new('L', (d * 4, d * 4), 0); ImageDraw.Draw(m).ellipse((0, 0, d * 4 - 1, d * 4 - 1), fill=255)
    out = Image.new('RGBA', (d, d)); out.paste(im, (0, 0), m.resize((d, d), Image.LANCZOS)); return out

def mockup(n):
    """How the channel page looks: desktop banner strip + avatar + name, the phone crop, and the avatar at comment/feed sizes."""
    ban = Image.open(os.path.join(OUT, '%d-banner.png' % n)).convert('RGB'); av = Image.open(os.path.join(OUT, '%d-avatar.png' % n)).convert('RGB')
    Wm = 1600; sheet = Image.new('RGB', (Wm, 1180), (15, 15, 15)); d = ImageDraw.Draw(sheet)
    f = lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', s); g = lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf', s)
    d.text((40, 26), 'Concept %d: %s' % (n - 5 if n > 5 else n, NAMES[n]), font=f(40), fill=(255, 255, 255))
    d.text((40, 90), 'DESKTOP', font=f(20), fill=(150, 150, 150))
    strip = ban.crop((0, 508, 2560, 931)).resize((Wm - 80, int((Wm - 80) * 423 / 2560)), Image.LANCZOS); sheet.paste(strip, (40, 120))
    y = 120 + strip.height + 24; sheet.paste(circle(av, 160), (40, y), circle(av, 160))
    d.text((230, y + 30), 'Smoke & Borders', font=f(44), fill=(255, 255, 255)); d.text((232, y + 92), '@SmokeAndBorders · Every border has two sides. We tell both.', font=g(24), fill=(170, 170, 170))
    y2 = y + 200; d.text((40, y2), 'PHONE', font=f(20), fill=(150, 150, 150))
    ph = ban.crop((507, 508, 2053, 931)).resize((560, int(560 * 423 / 1546)), Image.LANCZOS); sheet.paste(ph, (40, y2 + 30))
    d.text((640, y2), 'IN THE FEED AND COMMENTS', font=f(20), fill=(150, 150, 150))
    xx = 640
    for s in (120, 72, 48, 36):
        sheet.paste(circle(av, s), (xx, y2 + 40), circle(av, s)); xx += s + 40
    d.text((640, y2 + 190), 'History title of the next video goes here', font=f(26), fill=(255, 255, 255))
    sheet.paste(circle(av, 36), (640, y2 + 232), circle(av, 36)); d.text((686, y2 + 238), 'Smoke & Borders · 1.2M views', font=g(22), fill=(170, 170, 170))
    sheet.save(os.path.join(OUT, '%d-mockup.jpg' % n), quality=90)

with sync_playwright() as p:
    b = p.chromium.launch(); todo = [int(a) for a in sys.argv[1:]] or [1, 2, 3, 4, 5]
    for n in todo:
        for k, w, h in (('banner', 2560, 1440), ('avatar', 800, 800)):
            pg = b.new_page(viewport={'width': w, 'height': h}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            pg.goto('http://127.0.0.1:%d/smoke/brand/%s?c=%d&k=%s' % (srv.server_port, 'concepts.html' if n <= 5 else 'concepts2.html', n, k))
            try: pg.wait_for_function('window.done', timeout=180000)
            except Exception: print('FAILED', n, k, errs); continue
            pg.screenshot(path=os.path.join(OUT, '%d-%s.png' % (n, k)))
        mockup(n); print('concept', n, 'done')
    b.close()
