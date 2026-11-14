"""Competitor packaging scout: what titles and thumbnails are working right now in our niche.
For every channel in smoke/competitors.json it reads the latest long videos (YouTube Data API, the same sign-in as the uploader,
read-only calls, about 3 quota units per channel), scores each video against that channel's median views (outlier score), downloads
the thumbnails of the best ones and lays them out as labelled contact sheets you can look at.

usage: YT_CHANNEL=smoke python3 smoke/scout.py [--top 24] [--per 50]
       python3 smoke/scout.py --list studio/competitors.json      (FlagBomb: writes studio/watch/<date>/)
writes <the list's folder>/watch/<date>/packaging.json, sheet-1.jpg, sheet-2.jpg ... and title-patterns.md
If the API can't be reached it falls back to scrapetube (MIT, pip install scrapetube) for the titles and views.
Look at every sheet (Read the jpg) and write what the outliers share into LEARNINGS.md (RUNBOOK step 6)."""
import datetime, io, json, os, re, statistics, sys, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'studio'))

def api(tok, path, **q):
    req = urllib.request.Request('https://www.googleapis.com/youtube/v3/' + path + '?' + urllib.parse.urlencode(q), headers={'Authorization': 'Bearer ' + tok})
    with urllib.request.urlopen(req, timeout=30) as r: return json.load(r)

def secs(iso):
    m = re.match(r'P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', iso or ''); d, h, mi, s = (int(x or 0) for x in m.groups()) if m else (0, 0, 0, 0)
    return d * 86400 + h * 3600 + mi * 60 + s

def via_api(cid, per):
    import upload
    tok = via_api.tok = getattr(via_api, 'tok', None) or upload.token()
    up = api(tok, 'channels', part='contentDetails,snippet', id=cid)['items'][0]
    ids = [i['contentDetails']['videoId'] for i in api(tok, 'playlistItems', part='contentDetails', playlistId=up['contentDetails']['relatedPlaylists']['uploads'], maxResults=per)['items']]
    out = []
    for v in api(tok, 'videos', part='snippet,statistics,contentDetails', id=','.join(ids))['items']:
        th = v['snippet']['thumbnails']; best = (th.get('maxres') or th.get('standard') or th.get('high') or {}).get('url')
        out.append({'id': v['id'], 'title': v['snippet']['title'], 'views': int(v['statistics'].get('viewCount', 0)), 'secs': secs(v['contentDetails']['duration']),
                    'published': v['snippet']['publishedAt'][:10], 'thumb': best})
    return up['snippet']['title'], out

def via_scrapetube(cid, per):
    import scrapetube
    out = []
    for v in scrapetube.get_channel(cid, limit=per, content_type='videos'):
        t = ''.join(r.get('text', '') for r in v.get('title', {}).get('runs', [])); vt = v.get('viewCountText', {}).get('simpleText', '0')
        L = v.get('lengthText', {}).get('simpleText', '0:00').split(':'); s = 0
        for x in L: s = s * 60 + int(x or 0)
        out.append({'id': v['videoId'], 'title': t, 'views': int(re.sub(r'\D', '', vt) or 0), 'secs': s, 'published': v.get('publishedTimeText', {}).get('simpleText', ''),
                    'thumb': 'https://i.ytimg.com/vi/%s/hqdefault.jpg' % v['videoId']})
    return cid, out

def patterns(title):
    w = title.split()
    return {'words': len(w), 'chars': len(title), 'number': bool(re.search(r'\d', title)), 'caps_word': any(len(x) > 2 and x.isupper() for x in w),
            'question': '?' in title, 'brackets': bool(re.search(r'[\[\(]', title)), 'entire': 'ENTIRE' in title.upper(), 'vs': ' vs' in title.lower(),
            'pov_your_life': bool(re.search(r'POV|Your Life', title, re.I)), 'years_in_minutes': bool(re.search(r'Years.*in \d+ Minutes', title, re.I))}

def sheet(items, path, cols=4, w=480):
    from PIL import Image, ImageDraw, ImageFont
    h = w * 9 // 16; cap = 64; rows = -(-len(items) // cols); img = Image.new('RGB', (cols * w, rows * (h + cap)), '#111')
    font = None
    for f in ['/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf']:
        try: font = ImageFont.truetype(f, 17); break
        except Exception: pass
    font = font or ImageFont.load_default()
    d = ImageDraw.Draw(img)
    for i, it in enumerate(items):
        x, y = i % cols * w, i // cols * (h + cap)
        try:
            with urllib.request.urlopen(it['thumb'], timeout=20) as r: im = Image.open(io.BytesIO(r.read())).convert('RGB').resize((w, h))
            img.paste(im, (x, y))
        except Exception as e: d.text((x + 10, y + h // 2), 'thumbnail not reachable', fill='#f55', font=font)
        d.text((x + 6, y + h + 4), '%.1fx  %s views  %d min  %s' % (it['outlier'], f"{it['views']:,}", it['secs'] // 60, it['channel'][:22]), fill='#ffb347', font=font)
        d.text((x + 6, y + h + 26), it['title'][:52], fill='#fff', font=font)
    img.save(path, quality=88)

def main():
    top = int(sys.argv[sys.argv.index('--top') + 1]) if '--top' in sys.argv else 24; per = int(sys.argv[sys.argv.index('--per') + 1]) if '--per' in sys.argv else 50
    lst = sys.argv[sys.argv.index('--list') + 1] if '--list' in sys.argv else os.path.join(HERE, 'competitors.json')
    comp = json.load(open(lst))['channels']; day = datetime.date.today().isoformat()
    out = os.path.join(os.path.dirname(os.path.abspath(lst)), 'watch', day); os.makedirs(out, exist_ok=True); allv = []
    for c in comp:
        try: name, vids = via_api(c['id'], per)
        except Exception as e:
            print('API failed for %s (%s); trying scrapetube' % (c['name'], e), file=sys.stderr)
            try: name, vids = via_scrapetube(c['id'], per)
            except Exception as e2: print('  scrapetube failed too: %s' % e2, file=sys.stderr); continue
        longv = [v for v in vids if v['secs'] > 180]
        if not longv: continue
        med = statistics.median(v['views'] for v in longv) or 1
        for v in longv: v.update(channel=c['name'], outlier=round(v['views'] / med, 2), **patterns(v['title']))
        allv += longv; print('%-24s %3d long videos, median %s views' % (c['name'], len(longv), f'{int(med):,}'))
    allv.sort(key=lambda v: -v['outlier']); json.dump(allv, open(os.path.join(out, 'packaging.json'), 'w'), indent=1)
    best = allv[:top]
    for i in range(0, len(best), 12): sheet(best[i:i + 12], os.path.join(out, 'sheet-%d.jpg' % (i // 12 + 1)))
    # what the winners' titles share, compared with everyone else's
    hi = [v for v in allv if v['outlier'] >= 1.5]; lo = [v for v in allv if v['outlier'] < 1]
    keys = ['number', 'caps_word', 'question', 'brackets', 'entire', 'vs', 'pov_your_life', 'years_in_minutes']
    lines = ['# Title patterns, %s' % day, '', 'Outliers (1.5x or more of their channel median): %d videos. Under the median: %d.' % (len(hi), len(lo)), '',
             '| pattern | share of outliers | share of under-median |', '|---|---|---|']
    pct = lambda vs, k: '%d%%' % (100 * sum(v[k] for v in vs) / max(1, len(vs)))
    lines += ['| %s | %s | %s |' % (k, pct(hi, k), pct(lo, k)) for k in keys]
    if hi: lines += ['', 'Median title length: outliers %d words / %d characters, under-median %d / %d.' % (
        statistics.median(v['words'] for v in hi), statistics.median(v['chars'] for v in hi), statistics.median(v['words'] for v in lo or hi), statistics.median(v['chars'] for v in lo or hi))]
    lines += ['', '## Top outliers'] + ['- %.1fx  %s  (%s, %s views, %d min)' % (v['outlier'], v['title'], v['channel'], f"{v['views']:,}", v['secs'] // 60) for v in best]
    open(os.path.join(out, 'title-patterns.md'), 'w').write('\n'.join(lines)); print('\n'.join(lines[:16])); print('sheets and packaging.json in', out)

if __name__ == '__main__':
    main()
