"""photo shot from a saved cut-out portrait: a dark, blurred, sepia backdrop of the same picture + the cut-out as the 2.5-D layer."""
import sys, os, json
from PIL import Image, ImageFilter, ImageEnhance
sid, name, src = sys.argv[1:4]
out = '/home/claude/smokeborders/studio/doc/photos/%s' % sid; os.makedirs(out, exist_ok=True)
p = Image.open(src).convert('RGBA'); W, H = 1600, 1000
s = H * .92 / p.height; p = p.resize((round(p.width * s), round(p.height * s)), Image.LANCZOS)
x, y = (W - p.width) // 2 + int(W * float(sys.argv[4]) if len(sys.argv) > 4 else 0), H - p.height
bg = Image.new('RGB', (W, H), (24, 18, 13))
big = p.resize((W, round(p.height * W / p.width)), Image.LANCZOS).filter(ImageFilter.GaussianBlur(40))
bg.paste(ImageEnhance.Brightness(big.convert('RGB')).enhance(.35), (0, (H - big.height) // 2), big)
bg.save(os.path.join(out, name + '.jpg'), quality=92)
fg = Image.new('RGBA', (W, H)); fg.paste(p, (x, y), p); fg.save(os.path.join(out, name + '-fg.png'))
cr = os.path.join(out, 'credits.json'); c = json.load(open(cr)) if os.path.exists(cr) else {}
pc = json.load(open(os.path.join(os.path.dirname(src), 'credits.json'))) if os.path.exists(os.path.join(os.path.dirname(src), 'credits.json')) else {}
c[name] = pc.get(os.path.basename(src)[:-4]) or pc.get(os.path.basename(src)) or {'from': os.path.basename(src)}
json.dump(c, open(cr, 'w'), indent=1); print('made', name)
