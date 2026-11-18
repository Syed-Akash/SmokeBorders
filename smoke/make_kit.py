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
    # the chat can only send files up to 400 MB (18 Nov 2026: the 35-minute WW2 episode was 1.1 GB): a smaller copy to send
    epk = os.path.join(kit, 'episode.mp4')
    if os.path.exists(epk) and os.path.getsize(epk) > 380e6:
        import subprocess
        dur = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', epk], capture_output=True, text=True).stdout or 1800)
        vk = int(min(4000, max(800, 360e6 * 8 / dur / 1000 - 140)))   # about 360 MB in all
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', epk, '-c:v', 'libx264', '-preset', 'medium', '-b:v', '%dk' % vk, '-maxrate', '%dk' % (vk * 1.6),
                        '-bufsize', '%dk' % (vk * 3), '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', os.path.join(kit, 'episode-send.mp4')], check=True)
        print('episode over 380 MB: episode-send.mp4 is the copy to send (episode.mp4 stays the full-quality file)')
    parts.append(block('1. The episode', m, 'episode.mp4', '**Thumbnail:** `thumbnail.jpg` · **Subtitles:** upload `captions.srt` (Subtitles → Add language → English → Upload file)\n'
                       '**End screen:** Editor → End screen → Import from video (the previous episode).'))
    for n in (1, 2):
        od = (sorted(glob.glob(os.path.join(STUDIO, 'out', '*-doc-%s-short%d' % (sid, n)))) or [out])[-1]   # "Do you know" Shorts are their own stories (18 Nov 2026)
        mp, v = os.path.join(od, 'short-%d.meta.json' % n), os.path.join(od, 'short-1.mp4' if od != out else 'short-%d.mp4' % n)
        if od != out and not os.path.exists(mp): mp = os.path.join(od, 'short-1.meta.json')
        if os.path.exists(mp) and os.path.exists(v):
            shutil.copy(v, os.path.join(kit, 'short-%d.mp4' % n)); parts.append(block('%d. Short %d' % (n + 1, n), json.load(open(mp)), 'short-%d.mp4' % n, '**Related video:** after the episode is up, set it here (Short → Details → Related video → the episode). This is how Short viewers reach the episode.'))
    ab = os.path.join(HERE, 'ab', sid, 'ab.md')
    if os.path.exists(ab): parts += ['## A/B test (after the episode is up)', '', open(ab).read()]
    md = '\n'.join(parts); open(os.path.join(kit, 'KIT.md'), 'w').write(md)
    os.makedirs(os.path.join(HERE, 'kits'), exist_ok=True); open(os.path.join(HERE, 'kits', sid + '.md'), 'w').write(md)
    print(kit); [print(' ', f, '%.0f MB' % (os.path.getsize(os.path.join(kit, f)) / 1e6)) for f in sorted(os.listdir(kit))]
if __name__ == '__main__': main(sys.argv[1])
