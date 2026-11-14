"""Render the Smoke & Borders avatar and banner to smoke/brand/out/. usage: python3 smoke/brand/render.py"""
import functools, http.server, os, threading
from playwright.sync_api import sync_playwright

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')); OUT = os.path.join(os.path.dirname(__file__), 'out')
os.makedirs(OUT, exist_ok=True)
srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT))
srv.RequestHandlerClass.log_message = lambda *a: None
threading.Thread(target=srv.serve_forever, daemon=True).start()
with sync_playwright() as p:
    b = p.chromium.launch()
    for k, w, h in (('banner', 2560, 1440), ('avatar', 800, 800)):
        pg = b.new_page(viewport={'width': w, 'height': h})
        pg.goto('http://127.0.0.1:%d/smoke/brand/brand.html?k=%s' % (srv.server_port, k)); pg.wait_for_function('window.done', timeout=60000)
        pg.screenshot(path=os.path.join(OUT, k + '.png')); print(os.path.join(OUT, k + '.png'))
    b.close()
