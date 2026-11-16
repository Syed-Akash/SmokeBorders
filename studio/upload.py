"""Upload a video to the @PlayFlagbomb channel with the YouTube Data API.
usage: python3 upload.py video.mp4 meta.json    |    python3 upload.py --comments  (posts queued first comments on videos that are now live, and adds queued videos to playlists)
meta.json: {"title","description","tags":[...],"categoryId":"24","privacy":"private|unlisted|public",
            "publishAt":"2026-10-28T13:30:00Z" (optional, needs privacy "private"), "thumbnail":"cover.jpg" (optional), "comment":"first comment text" (optional), "playlists":["rivalries","conquest:1",...] (optional, see PLAYLISTS),
            "captions":"episode.srt" (optional, English subtitles), "long":true (long video: watch link instead of a Shorts link),
            "localizations":{"hi":{"title","description"},"ur":{...},"es":{...},"pt":{...},"id":{...}} (optional, translated title + description)}
Needs the environment variables YT_CLIENT_ID, YT_CLIENT_SECRET and YT_REFRESH_TOKEN (OAuth, scopes youtube.upload and, for the first comment, youtube.force-ssl).
Second channel: YT_CHANNEL=smoke uploads to Smoke & Borders with YT_REFRESH_TOKEN_SMOKE (same client), keeps its own queue
(pending_youtube_smoke.json), and refuses to upload unless the signed-in channel really is Smoke & Borders.
python3 upload.py --whoami   prints the channel the current token belongs to.
Only the Python standard library is used."""
import json, os, sys, urllib.request, urllib.parse, urllib.error

CHANNEL = os.environ.get('YT_CHANNEL', 'smoke')   # this repo is Smoke & Borders only
TOKEN_VAR = {'flagbomb': 'YT_REFRESH_TOKEN', 'smoke': 'YT_REFRESH_TOKEN_SMOKE'}[CHANNEL]
EXPECT = os.environ.get('YT_EXPECT_TITLE') or {'flagbomb': None, 'smoke': 'Smoke & Borders'}[CHANNEL]   # the channel title an upload must land on
# the old and the new channel share the title, so the handle decides (owner, 14 Nov 2026: new channel @SmokeAndBorders)
EXPECT_HANDLE = (os.environ.get('YT_EXPECT_HANDLE') or {'flagbomb': '', 'smoke': '@SmokeAndBorders'}[CHANNEL]).lower()

def token():
    data = urllib.parse.urlencode({'client_id': os.environ['YT_CLIENT_ID'], 'client_secret': os.environ['YT_CLIENT_SECRET'],
                                   'refresh_token': os.environ[TOKEN_VAR], 'grant_type': 'refresh_token'}).encode()
    with urllib.request.urlopen(urllib.request.Request('https://oauth2.googleapis.com/token', data=data)) as r:
        return json.load(r)['access_token']

def call(req):
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, r.headers, r.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors='replace')
        sys.exit('YouTube API error %s: %s' % (e.code, body[:1500]))

def recent(tok, n=50):
    """The channel's latest uploads (scheduled and private ones too): [(videoId, title, publishAt or published)]."""
    ch = api(tok, 'GET', 'channels?part=contentDetails&mine=true')['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    items = api(tok, 'GET', 'playlistItems?part=snippet,contentDetails&maxResults=%d&playlistId=%s' % (n, ch)).get('items', [])
    return [(i['contentDetails']['videoId'], i['snippet']['title'], i['contentDetails'].get('videoPublishedAt', '')) for i in items]

def upload(video, meta):
    tok = token(); check_channel(tok); size = os.path.getsize(video)
    # never upload the same video twice (a run that died before committing its records made the next run repeat it, 4-5 Nov 2026)
    try: dup = next((v for v in recent(tok) if v[1].strip().lower() == meta['title'][:100].strip().lower()), None)
    except Exception as e: dup = None; print('duplicate check failed:', e, file=sys.stderr)
    if dup and not meta.get('allowDuplicate'):
        return {'id': dup[0], 'skipped': 'DUPLICATE: a video with this exact title is already on the channel; nothing uploaded', 'url': 'https://youtu.be/' + dup[0]}
    status = {'privacyStatus': meta.get('privacy', 'private'), 'selfDeclaredMadeForKids': False}
    if meta.get('publishAt'):
        # a render that finished after its slot: YouTube refuses a past publishAt, so go out 15 minutes from now (6 Nov 2026)
        import datetime as _dt
        soon = _dt.datetime.now(_dt.timezone.utc) + _dt.timedelta(minutes=15)
        try:
            if _dt.datetime.fromisoformat(meta['publishAt'].replace('Z', '+00:00')) < soon:
                meta['publishAt'] = soon.strftime('%Y-%m-%dT%H:%M:00Z'); print('publish time already passed; scheduled for', meta['publishAt'], file=sys.stderr)
        except ValueError: pass
        status.update(privacyStatus='private', publishAt=meta['publishAt'])
    if meta.get('long') or meta.get('linkPlaylists'):   # owner, 9 Nov 2026: long videos link their playlists in the description
        try: meta['description'] = with_playlist_links(tok, meta.get('description', ''), (meta.get('playlists') or []) + (meta.get('linkPlaylists') or []))
        except Exception as e: print('playlist links skipped:', e, file=sys.stderr)
    body = {'snippet': {'title': meta['title'][:100], 'description': meta.get('description', '')[:5000], 'tags': meta.get('tags', []),
                        'categoryId': '27', 'defaultLanguage': 'en', 'defaultAudioLanguage': 'en'},
            'status': status}
    loc = {k: {'title': v['title'][:100], 'description': v.get('description', '')[:5000]} for k, v in (meta.get('localizations') or {}).items() if v.get('title')}
    if loc: body['localizations'] = loc   # translated titles/descriptions: the same video shows in the viewer's language
    req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status' + (',localizations' if loc else ''),
                                 data=json.dumps(body).encode(), method='POST',
                                 headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8',
                                          'X-Upload-Content-Type': 'video/mp4', 'X-Upload-Content-Length': str(size)})
    _, h, _ = call(req); loc = h['Location']
    with open(video, 'rb') as f:
        req = urllib.request.Request(loc, data=f.read(), method='PUT', headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'video/mp4'})
    _, _, out = call(req); vid = json.loads(out)
    res = {'id': vid['id'], 'url': 'https://youtube.com/shorts/' + vid['id'], 'status': vid.get('status')}
    if meta.get('long'): res['url'] = 'https://youtu.be/' + vid['id']
    cap = meta.get('captions')   # an .srt next to the video (needs youtube.force-ssl)
    if cap and os.path.exists(cap):
        bd = 'fbcap7x'; part = json.dumps({'snippet': {'videoId': vid['id'], 'language': 'en', 'name': 'English', 'isDraft': False}})
        data = ('--%s\r\nContent-Type: application/json; charset=UTF-8\r\n\r\n%s\r\n--%s\r\nContent-Type: application/octet-stream\r\n\r\n' % (bd, part, bd)).encode() + open(cap, 'rb').read() + ('\r\n--%s--' % bd).encode()
        req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/captions?uploadType=multipart&part=snippet', data=data, method='POST',
                                     headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'multipart/related; boundary=' + bd})
        try:
            with urllib.request.urlopen(req) as r: res['captions'] = 'added'
        except urllib.error.HTTPError as e: res['captions'] = 'not added (%s): %s' % (e.code, e.read().decode(errors='replace')[:300])
    th = meta.get('thumbnail')
    if th and os.path.exists(th):
        with open(th, 'rb') as f:
            req = urllib.request.Request('https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=' + vid['id'], data=f.read(), method='POST',
                                         headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'image/jpeg'})
        try:
            with urllib.request.urlopen(req) as r: res['thumbnail'] = 'set'
        except urllib.error.HTTPError as e: res['thumbnail'] = 'not set (%s): %s' % (e.code, e.read().decode(errors='replace')[:300])
    if meta.get('playlists'):
        q = json.load(open(PENDING)) if os.path.exists(PENDING) else []
        for k in meta['playlists']: q.append({'type': 'playlist', 'videoId': vid['id'], 'playlist': k})
        json.dump(q, open(PENDING, 'w'), indent=1); res['playlists'] = add_pending_playlists(tok)
    if meta.get('comment'):   # scheduled videos are private until they go live, so the comment waits for the next run
        q = json.load(open(PENDING)) if os.path.exists(PENDING) else []
        q.append({'type': 'comment', 'videoId': vid['id'], 'text': meta['comment'][:1000], 'after': meta.get('publishAt')}); json.dump(q, open(PENDING, 'w'), indent=1)
        res['comment'] = 'queued: posted by the next run after the video is live (upload.py --comments)'
    return res

PENDING = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'pending_youtube.json' if CHANNEL == 'flagbomb' else 'pending_youtube_%s.json' % CHANNEL)

def whoami(tok):
    it = api(tok, 'GET', 'channels?part=snippet&mine=true').get('items', [])
    return (it[0]['id'], it[0]['snippet']['title'], (it[0]['snippet'].get('customUrl') or '').lower()) if it else (None, None, '')

def check_channel(tok):
    cid, title, handle = whoami(tok)
    if EXPECT and title != EXPECT: sys.exit('wrong channel: this token belongs to %r, not %r; nothing uploaded' % (title, EXPECT))
    if EXPECT_HANDLE and handle != EXPECT_HANDLE:
        sys.exit('wrong channel: this token belongs to %s (%s), not %s; nothing uploaded' % (handle or '?', cid, EXPECT_HANDLE))

def comment(tok, video_id, text):
    """First comment from the channel. Needs the youtube.force-ssl scope; pinning is done by hand in the app."""
    req = urllib.request.Request('https://www.googleapis.com/youtube/v3/commentThreads?part=snippet', method='POST',
                                 data=json.dumps({'snippet': {'videoId': video_id, 'topLevelComment': {'snippet': {'textOriginal': text}}}}).encode(),
                                 headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8'})
    try:
        with urllib.request.urlopen(req) as r: return True, 'posted ' + json.load(r)['id']
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors='replace')
        if e.code == 403 and 'insufficient' in body.lower():   # also what YouTube answers for a video that isn't public yet (or was removed)
            return False, 'refused (403): the video is not public yet, was removed, or the sign-in lacks youtube.force-ssl; kept in the queue'
        return False, 'not posted (%s): %s' % (e.code, body[:300])

# playlists: key -> (title, description). "conquest:N" is World Conquest season N.
PLAYLISTS = {
    'rivalries': ('Country Rivalries ⚔️ 1v1 Bomb Battles', 'Pakistan vs India, USA vs China, Brazil vs Argentina and more: two nations, one arena, only one walks out.'),
    '8nations': ('8 Nations, Only 1 Survives 💣', 'Eight countries drop into the arena. Find yours and see if it survives.'),
    'chaos': ('Chaos Mode 💥', 'Everything at once: more bombs, more powers, less time.'),
    'football': ('Bomb Football ⚽💣', 'Countries play football, but the ball explodes.'),
    'modes': ('Boss Battles, King of the Hill & Continent Wars', 'The special FlagBomb modes.'),
    'requests': ('Your Requests 👇', 'Fights picked by the top comment. Comment two countries and yours could be next.'),
    'war': ('War Mode 🗺️ Full Country Wars', 'Full-length wars on the world map: cities, capitals, commanders and one winner.'),
    'worldcup': ('Bomb World Cup 🏆', '32 nations, one trophy.'),
    'long': ('Full Episodes 🎬', 'The long FlagBomb episodes: wars, world cups and the stories between nations.'),
    'planets': ('Planet Battles 🌍', 'Earth vs the universe.'),
    'history-docs': ('FlagBomb History: Full Documentaries 🎬', 'Real history explained on the map: how wars started, who decided, who paid the price, and what it changed.'),
    'history': ('History in a Nutshell 🕰️ #countryballs', 'Real history told by countryballs on the map, a new story every day. Tell us what we missed.'),
    'thoughts': ('Dot Thinks… 🌍 Deep Questions', 'Dot is the only ball without a flag. Short thoughts about borders, peace, rights, animals, time and why we are here. Tell Dot what you think.'),
    'sb-episodes': ('Every Episode, In Order', 'Every Smoke & Borders story, oldest first.'),
    'sb-shorts': ('Smoke & Borders in 60 Seconds', 'True stories in a minute: the people and details history forgot. The full episodes are on the channel.'),
    'underdog': ('Can Vatican City Win ONE Fight? ⛪ Every Attempt', 'The smallest country on Earth against 7 nations, again and again, until it finally wins. Watch in order.'),
}
def playlist_title(k):
    if k.startswith('conquest:'):
        n = k.split(':')[1]
        return ('World Conquest · Season %s 🌍' % n, 'One world map, one battle a day. The winner takes the loser\'s land, until one empire rules the world. Watch in order from Day 1.')
    return PLAYLISTS.get(k, (k, ''))

def api(tok, method, path, body=None):
    req = urllib.request.Request('https://www.googleapis.com/youtube/v3/' + path, method=method, data=json.dumps(body).encode() if body is not None else None,
                                 headers={'Authorization': 'Bearer ' + tok, 'Content-Type': 'application/json; charset=UTF-8'})
    with urllib.request.urlopen(req) as r: return json.load(r)

def my_playlists(tok):
    out, page = {}, ''
    while True:
        d = api(tok, 'GET', 'playlists?part=snippet&mine=true&maxResults=50' + ('&pageToken=' + page if page else ''))
        for it in d.get('items', []): out[it['snippet']['title']] = it['id']
        page = d.get('nextPageToken')
        if not page: return out

def with_playlist_links(tok, desc, keys):
    """Adds a "Watch more" block with each playlist's link (creating a playlist that doesn't exist yet), above the hashtags."""
    keys = list(dict.fromkeys(k for k in keys if k)); have = my_playlists(tok); lines = []
    for k in keys:
        title, pdesc = playlist_title(k)
        if title not in have:
            have[title] = api(tok, 'POST', 'playlists?part=snippet,status', {'snippet': {'title': title, 'description': pdesc}, 'status': {'privacyStatus': 'public'}})['id']
        lines.append('%s: https://www.youtube.com/playlist?list=%s' % (title, have[title]))
    if not lines or 'youtube.com/playlist?list=' in desc: return desc
    block = '▶ Watch more\n' + '\n'.join(lines)
    parts = desc.rstrip().split('\n')
    if parts and parts[-1].startswith('#'): return '\n'.join(parts[:-1]).rstrip() + '\n\n' + block + '\n\n' + parts[-1]
    return desc.rstrip() + '\n\n' + block

def add_pending_playlists(tok):
    """Adds queued videos to their playlists (creating a playlist the first time). Needs the youtube.force-ssl scope."""
    q = json.load(open(PENDING)) if os.path.exists(PENDING) else []; todo = [c for c in q if c.get('type') == 'playlist']
    if not todo: return []
    log = []
    import time
    try: have = my_playlists(tok)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors='replace'); json.dump(q, open(PENDING, 'w'), indent=1)
        return ['needs the youtube.force-ssl permission: renew the YouTube sign-in with both scopes' if e.code == 403 and 'insufficient' in body.lower() else 'playlist error (%s): %s' % (e.code, body[:300])]
    for c in todo:   # one at a time with a short pause: YouTube answers 409 when a playlist gets several additions at once
        title, desc = playlist_title(c['playlist'])
        for attempt in range(3):
            try:
                if title not in have:
                    have[title] = api(tok, 'POST', 'playlists?part=snippet,status', {'snippet': {'title': title, 'description': desc}, 'status': {'privacyStatus': 'public'}})['id']
                api(tok, 'POST', 'playlistItems?part=snippet', {'snippet': {'playlistId': have[title], 'resourceId': {'kind': 'youtube#video', 'videoId': c['videoId']}}})
                q.remove(c); log.append('%s -> %s' % (c['videoId'], title)); break
            except urllib.error.HTTPError as e:
                body = e.read().decode(errors='replace')
                if e.code == 409 and attempt < 2: time.sleep(4 * (attempt + 1)); continue
                c['tries'] = c.get('tries', 0) + 1; log.append('%s: playlist error (%s) %s' % (c['videoId'], e.code, body[:160]))
                if c['tries'] >= 5: q.remove(c); log.append('%s: gave up after 5 runs' % c['videoId'])
                break
        time.sleep(1.2)
    json.dump(q, open(PENDING, 'w'), indent=1); return log

def post_pending():
    import datetime
    q = json.load(open(PENDING)) if os.path.exists(PENDING) else []; now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    tok = token() if q else None; keep = []; log = []
    for c in q:
        if c.get('type') == 'playlist': keep.append(c); continue
        if c.get('after') and c['after'] > now: keep.append(c); continue
        ok, msg = comment(tok, c['videoId'], c['text']); log.append({'videoId': c['videoId'], 'result': msg})
        if not ok and 'permission' not in msg: c['tries'] = c.get('tries', 0) + 1
        if not ok and c.get('tries', 0) < 4: keep.append(c)
    json.dump(keep, open(PENDING, 'w'), indent=1)
    if any(c.get('type') == 'playlist' for c in keep): log += add_pending_playlists(tok or token())
    return log

def replace(tok, old, new):
    """Delete a scheduled upload that a re-render replaces (owner, 12 Nov 2026: Korea re-rendered in the new style).
    Refuses unless `old` is still private (never deletes anything people could have seen), and moves its queued comments to `new`."""
    v = api(tok, 'GET', 'videos?part=status,snippet&id=' + old).get('items', [])
    if not v: return 'nothing to delete: %s is already gone' % old
    st = v[0]['status']
    if st.get('privacyStatus') != 'private': sys.exit('refused: %s is %s, not private; delete it by hand if you really mean to' % (old, st.get('privacyStatus')))
    if not api(tok, 'GET', 'videos?part=status&id=' + new).get('items'): sys.exit('refused: the new video %s was not found on the channel' % new)
    req = urllib.request.Request('https://www.googleapis.com/youtube/v3/videos?id=' + old, method='DELETE', headers={'Authorization': 'Bearer ' + tok}); call(req)
    q = json.load(open(PENDING)) if os.path.exists(PENDING) else []
    for c in q:
        if c.get('videoId') == old: c['videoId'] = new
    json.dump(q, open(PENDING, 'w'), indent=1)
    return 'deleted the scheduled upload %s ("%s"); its queued comments now point at %s' % (old, v[0]['snippet']['title'], new)

if __name__ == '__main__':
    if sys.argv[1:2] == ['--replace']: print(replace(token(), sys.argv[2], sys.argv[3])); sys.exit()
    if sys.argv[1:] == ['--comments']: print(json.dumps(post_pending(), indent=1)); sys.exit()
    if sys.argv[1:] == ['--whoami']: print(*whoami(token()), sep='  |  '); sys.exit()
    if sys.argv[1:] == ['--recent']: [print(*v, sep='  |  ') for v in recent(token())]; sys.exit()
    res = upload(sys.argv[1], json.load(open(sys.argv[2])))
    srt = os.path.splitext(sys.argv[1])[0] + '.srt'   # captions with every upload (16 Nov 2026: search and accessibility)
    if os.path.exists(srt) and isinstance(res, dict) and res.get('id'):
        try:
            sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'smoke')); import channel_setup
            res['captions'] = channel_setup.captions(token(), res['id'], srt)
        except Exception as e: res['captions'] = 'captions error: %s' % e
    json.dump(res, open(os.path.splitext(sys.argv[2])[0] + '.result.json', 'w'), indent=1)   # keep the link even if the log is lost
    print(json.dumps(res, indent=1))
