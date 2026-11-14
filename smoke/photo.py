"""Archival photos for the film-style episodes (owner, 14 Nov 2026: "think like actual documentaries... unique scenes").
A real public-domain / free-licensed photo from Wikimedia Commons becomes a 2.5-D shot: the subject is cut out (rembg) into a
foreground layer, the hole it leaves is filled (OpenCV inpaint) to make the background layer, and scenes.js's `photo` shot drifts
the camera through the two layers with grain, grade, smoke and light. Landscapes without a clear subject use --flat (one layer).

usage: python3 smoke/photo.py <story-id> <name> "<File:... or search words>" [--flat]
writes studio/doc/photos/<story-id>/<name>.jpg (background), <name>-fg.png (subject, unless --flat or none found),
and the credit in studio/doc/photos/<story-id>/credits.json (CC BY / CC BY-SA credits go in the video description).
In a story beat: {"scene": {"shot": "photo", "img": "<name>", "caption": "Royal Marines at English Camp, 1860s"}}"""
import io, json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import portrait as P

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def main():
    sid, name, query = sys.argv[1], sys.argv[2], sys.argv[3]; flat = '--flat' in sys.argv
    out = os.path.join(ROOT, 'studio', 'doc', 'photos', sid); os.makedirs(out, exist_ok=True)
    meta = P.info(P.find(query) if query.lower().startswith('file:') else find_any(query))
    if not P.OK.match(meta['license'] or ''): sys.exit('refused: licence "%s" (%s)' % (meta['license'], meta['page']))
    img = Image.open(io.BytesIO(P.fetch(meta['url']))).convert('RGB')
    if img.width < 1600: img = img.resize((1600, round(img.height * 1600 / img.width)), Image.LANCZOS)
    if img.width > 2200: img = img.resize((2200, round(img.height * 2200 / img.width)), Image.LANCZOS)
    bg = img
    if not flat:
        from rembg import remove, new_session
        cut = remove(img, session=new_session(os.environ.get('REMBG_MODEL', 'isnet-general-use')))
        a = np.asarray(cut.getchannel('A'))
        share = (a > 128).mean()
        if 0.04 < share < 0.6:   # a real subject: not a speck, not the whole frame
            import cv2
            mask = cv2.dilate((a > 30).astype(np.uint8) * 255, np.ones((25, 25), np.uint8))
            bg = Image.fromarray(cv2.inpaint(np.asarray(img), mask, 9, cv2.INPAINT_TELEA))
            cut.save(os.path.join(out, name + '-fg.png'))
        else:
            print('no clear subject (%.0f%% of the frame): one layer only' % (share * 100))
    bg.save(os.path.join(out, name + '.jpg'), quality=88)
    cp = os.path.join(out, 'credits.json'); cr = json.load(open(cp)) if os.path.exists(cp) else {}; cr[name] = meta
    json.dump(cr, open(cp, 'w'), indent=1, ensure_ascii=False)
    print(name, '|', meta['license'], '|', meta['title'], '|', meta['page'])

def find_any(query):
    """Like portrait.find, without adding 'portrait' to the search."""
    hits = P.api(action='query', list='search', srsearch=query, srnamespace=6, srlimit=10)['query']['search']
    hits = [h for h in hits if h['title'].lower().endswith(('.jpg', '.jpeg', '.png', '.tif', '.tiff'))]
    if not hits: sys.exit('nothing found on Commons for: ' + query)
    return hits[0]['title']

if __name__ == '__main__':
    main()
