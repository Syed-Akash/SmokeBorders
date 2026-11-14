"""Smoke & Borders channel numbers for the weekly review (YouTube Data + Analytics API, token YT_REFRESH_TOKEN_SMOKE).
usage: python3 smoke/stats.py            -> smoke/stats/<date>.json and a short printed summary
Per video: views, likes, comments, average % viewed, average view duration, subscribers gained, the retention curve
(share of viewers still watching at each 5% of the video) and where views came from (traffic sources).
Needs the yt-analytics.readonly scope on the token; without it, only the public counts are collected."""
import datetime, json, os, sys, urllib.error, urllib.parse, urllib.request
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(HERE, '..', 'studio'))
os.environ.setdefault('YT_CHANNEL', 'smoke')
import upload

def analytics(tok, **q):
    url = 'https://youtubeanalytics.googleapis.com/v2/reports?' + urllib.parse.urlencode({'ids': 'channel==MINE', **q})
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'Authorization': 'Bearer ' + tok})) as r: return json.load(r)
    except urllib.error.HTTPError as e: return {'error': e.code, 'body': e.read().decode(errors='replace')[:300]}

def main():
    tok = upload.token(); cid, title = upload.whoami(tok)[:2]
    if upload.EXPECT and title != upload.EXPECT: sys.exit('token belongs to %r, not %r' % (title, upload.EXPECT))
    vids = upload.recent(tok, 50); ids = [v[0] for v in vids]; today = datetime.date.today(); out = {'date': today.isoformat(), 'channel': title, 'videos': []}
    pub = {}
    for i in range(0, len(ids), 50):
        r = upload.api(tok, 'GET', 'videos?part=statistics,contentDetails,snippet&id=' + ','.join(ids[i:i + 50]))
        for it in r.get('items', []): pub[it['id']] = it
    start = '2026-11-01'; end = today.isoformat()
    for vid, name, published in vids:
        it = pub.get(vid, {}); st = it.get('statistics', {})
        row = {'id': vid, 'title': name, 'published': published, 'duration': it.get('contentDetails', {}).get('duration'),
               'views': int(st.get('viewCount', 0)), 'likes': int(st.get('likeCount', 0)), 'comments': int(st.get('commentCount', 0))}
        a = analytics(tok, startDate=start, endDate=end, metrics='averageViewPercentage,averageViewDuration,subscribersGained,estimatedMinutesWatched', filters='video==' + vid)
        if 'rows' in a and a['rows']: row.update(dict(zip([h['name'] for h in a['columnHeaders']], a['rows'][0])))
        elif 'error' in a: row['analytics'] = 'unavailable (%s)' % a['error']
        c = analytics(tok, startDate=start, endDate=end, metrics='audienceWatchRatio', dimensions='elapsedVideoTimeRatio', filters='video==' + vid)
        if c.get('rows'): row['retention'] = [[round(x, 2), round(y, 3)] for x, y in c['rows'] if round(x * 100) % 5 == 0]
        s = analytics(tok, startDate=start, endDate=end, metrics='views', dimensions='insightTrafficSourceType', filters='video==' + vid, sort='-views')
        if s.get('rows'): row['traffic'] = {k: v for k, v in s['rows']}
        out['videos'].append(row)
    d = os.path.join(HERE, 'stats'); os.makedirs(d, exist_ok=True); f = os.path.join(d, today.isoformat() + '.json'); json.dump(out, open(f, 'w'), indent=1)
    for v in out['videos']:
        print('%-60s %7d views  %s%% viewed  %s subs' % (v['title'][:60], v['views'], v.get('averageViewPercentage', '?'), v.get('subscribersGained', '?')))
    print(f)

if __name__ == '__main__':
    main()
