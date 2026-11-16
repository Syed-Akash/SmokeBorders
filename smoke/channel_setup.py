"""One-time channel fixes for @SmokeAndBorders (16 Nov 2026), run by the daily run (it has the upload token):
    cd studio && YT_CHANNEL=smoke python3 ../smoke/channel_setup.py [--captions <videoId> <file.srt>]...
- channel description: what the channel is now (film-style, both sides, a new episode every 3 days)
- channel keywords: clean (no other channels' names, no stray words: those read as spam to YouTube)
- every uploaded long video: category Education (27)
- captions: uploads an .srt to a video that has none
Then sets smoke/channel_setup.json {"done": true}."""
import sys, os, json, urllib.request, urllib.error, uuid
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'studio'))
import upload as U
DESC = """Animated history, told like a film and from both sides of the border.

Every border on the map was drawn by someone, fought over by someone, and lived with by millions. Smoke & Borders tells those stories minute by minute: the people in the room, the mistakes, the turn nobody saw coming, and the hidden person history forgot.

In every episode:
• The real story, acted out: animated characters, archival photos, letters and maps
• Both sides, so you decide who was right
• Real sources, pinned in the comments
• Dark humour where history earns it, and silence where it doesn't

A new full episode every three days, and short stories in between.

Every border has two sides. We tell both."""
KEYWORDS = ['history', 'animated history', 'history documentary', 'history explained', 'borders', 'both sides', 'minute by minute',
            'empires', 'world history', 'war history', 'geopolitics', 'maps', 'untold history', 'history stories']
def kw(lst): return ' '.join('"%s"' % k if ' ' in k else k for k in lst)
def captions(tok, vid, srt):
    have = U.api(tok, 'GET', 'captions?part=snippet&videoId=' + vid).get('items', [])
    if any(c['snippet'].get('language') == 'en' and c['snippet'].get('trackKind') != 'asr' for c in have): return 'captions already there'
    b = uuid.uuid4().hex; meta = json.dumps({'snippet': {'videoId': vid, 'language': 'en', 'name': 'English', 'isDraft': False}})
    body = ('--%s\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n%s\r\n--%s\r\nContent-Type: application/octet-stream\r\n\r\n' % (b, meta, b)).encode() + open(srt, 'rb').read() + ('\r\n--%s--\r\n' % b).encode()
    req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/captions?part=snippet&uploadType=multipart', data=body, method='POST',
                                 headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'multipart/related; boundary=' + b})
    with urllib.request.urlopen(req) as r: return 'captions added (%s)' % json.load(r)['id']
if __name__ == '__main__':
    tok = U.token(); U.check_channel(tok); log = []
    ch = U.api(tok, 'GET', 'channels?part=brandingSettings&mine=true')['items'][0]; bs = ch['brandingSettings']
    bs.setdefault('channel', {}).update({'description': DESC, 'keywords': kw(KEYWORDS)})
    U.api(tok, 'PUT', 'channels?part=brandingSettings', {'id': ch['id'], 'brandingSettings': bs}); log.append('channel description and keywords set')
    for it in U.recent(tok, 50):
        vid = it[0]
        v = U.api(tok, 'GET', 'videos?part=snippet,contentDetails&id=' + vid)['items']
        if not v: continue
        sn = v[0]['snippet']
        if sn.get('categoryId') != '27':
            sn['categoryId'] = '27'; sn.pop('thumbnails', None); sn.pop('localized', None)
            U.api(tok, 'PUT', 'videos?part=snippet', {'id': vid, 'snippet': sn}); log.append('%s: category Education' % vid)
    a = sys.argv[1:]
    while len(a) >= 3 and a[0] == '--captions':
        try: log.append('%s: %s' % (a[1], captions(tok, a[1], a[2])))
        except urllib.error.HTTPError as e: log.append('%s: captions error %s %s' % (a[1], e.code, e.read().decode(errors='replace')[:200]))
        a = a[3:]
    json.dump({'done': True, 'log': log}, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'channel_setup.json'), 'w'), indent=1)
    print('\n'.join(log))
