"""Upload kit for the owner (17 Nov 2026): videos uploaded through the API got 0 impressions on the new channel, a hand
upload got views within the hour, so the owner uploads by hand. After make_meta.py (episode and both Shorts):
    python3 smoke/make_kit.py <id>
collects into studio/out/kit-<id>/: the episode, thumbnail, captions, both Shorts, and KIT.md (what to paste, when);
KIT.md is also copied to smoke/kits/<id>.md (committed, readable on GitHub). The run then sends every file with
SendUserFile and the KIT.md text with SendUserMessage."""
import sys, os, json, glob, shutil, datetime
HERE = os.path.dirname(os.path.abspath(__file__)); STUDIO = os.path.join(HERE, '..', 'studio')
PKT = datetime.timezone(datetime.timedelta(hours=5))
def when(iso):
    if not iso: return 'any time'
    d = datetime.datetime.fromisoformat(iso.replace('Z', '+00:00')).astimezone(PKT); return d.strftime('%a %d %b, %I:%M %p Pakistan time').replace(' 0', ' ')
def block(name, m, video, extra=''):
    return '\n'.join(['## %s' % name, '', '**File:** `%s`  ' % os.path.basename(video), '**Post:** %s (in Studio: Visibility → Schedule)' % when(m.get('publishAt')), extra, '',
                      '**Title**', '```', m['title'], '```', '**Description**', '```', m['description'], '```', '**Tags**', '```', ', '.join(m.get('tags', [])), '```',
                      '**Pinned comment** (post it, then ⋮ → Pin)', '```', m.get('comment', ''), '```',
                      '**Settings:** No, it\'s not made for kids · Category: Education · Playlist: %s' % ('Every Episode, In Order' if m.get('long') else 'Smoke & Borders in 60 Seconds'), ''])
def main(sid):
    out = sorted(glob.glob(os.path.join(STUDIO, 'out', '*-doc-' + sid)))[-1]; kit = os.path.join(STUDIO, 'out', 'kit-' + sid); os.makedirs(kit, exist_ok=True)
    parts = ['# Upload kit: %s' % sid, '', 'Upload by hand from YouTube Studio (not through any other app). Upload the episode first; '
             'after it is up, put its link into both Shorts\' descriptions where it says "on Smoke & Borders".', '']
    m = json.load(open(os.path.join(out, 'meta.json'))); ep = os.path.join(out, sid + '.mp4')
    for src, dst in ((ep, 'episode.mp4'), (m.get('thumbnail', ''), 'thumbnail.jpg'), (m.get('captions', ''), 'captions.srt')):
        if src and os.path.exists(src): shutil.copy(src, os.path.join(kit, dst))
    parts.append(block('1. The episode', m, 'episode.mp4', '**Thumbnail:** `thumbnail.jpg` · **Subtitles:** upload `captions.srt` (Subtitles → Add language → English → Upload file)\n'
                       '**End screen:** Editor → End screen → Import from video (the previous episode).'))
    for n in (1, 2):
        mp, v = os.path.join(out, 'short-%d.meta.json' % n), os.path.join(out, 'short-%d.mp4' % n)
        if os.path.exists(mp) and os.path.exists(v):
            shutil.copy(v, os.path.join(kit, 'short-%d.mp4' % n)); parts.append(block('%d. Short %d' % (n + 1, n), json.load(open(mp)), 'short-%d.mp4' % n))
    ab = os.path.join(HERE, 'ab', sid, 'ab.md')
    if os.path.exists(ab): parts += ['## A/B test (after the episode is up)', '', open(ab).read()]
    md = '\n'.join(parts); open(os.path.join(kit, 'KIT.md'), 'w').write(md)
    os.makedirs(os.path.join(HERE, 'kits'), exist_ok=True); open(os.path.join(HERE, 'kits', sid + '.md'), 'w').write(md)
    print(kit); [print(' ', f, '%.0f MB' % (os.path.getsize(os.path.join(kit, f)) / 1e6)) for f in sorted(os.listdir(kit))]
if __name__ == '__main__': main(sys.argv[1])
