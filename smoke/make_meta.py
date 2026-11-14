"""Build the upload meta.json for a finished Smoke & Borders episode (or one of its Shorts).
usage: python3 smoke/make_meta.py <story-id> <publishAt UTC, e.g. 2026-11-14T16:00:00Z>      -> out/<...>/meta.json
       python3 smoke/make_meta.py <story-id> <publishAt> --short <n> [title]              -> out/<...>/short-<n>.meta.json
The story may carry "hook" (first description line), "about" (2-3 sentence summary with the search words), "tags" and
"localizations" ({lang: {title, description}}), written when the script is written. Nothing here mentions AI or automation."""
import glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); STUDIO = os.path.join(HERE, '..', 'studio')
BASE_TAGS = ['history', 'animated history', 'history documentary', 'world history', 'history explained', 'history maps', 'animated map', 'borders', 'empires', 'war history', 'smoke and borders']

def main():
    sid, when = sys.argv[1], sys.argv[2]; story = json.load(open(os.path.join(STUDIO, 'doc', 'stories', sid + '.json')))
    outdir = sorted(glob.glob(os.path.join(STUDIO, 'out', '*-doc-' + sid)))[-1]; summ = json.load(open(os.path.join(outdir, 'summary.json')))
    src = '\n'.join('• ' + s for s in story.get('sources', []))
    if '--short' in sys.argv:
        n = sys.argv[sys.argv.index('--short') + 1]; i = sys.argv.index('--short') + 2
        # a Short cut from the episode (owner, 11 Nov 2026) takes its title from summary.json shortCuts unless one is given
        title = sys.argv[i] if len(sys.argv) > i else next((c['title'] for c in summ.get('shortCuts', []) if str(c['n']) == n), '')
        if not title: sys.exit('no title for Short %s: give one, or add "title" to the story\'s "shorts"' % n)
        # a Short is its own story file (<episode>-short<n>.json); its description points to the full episode, with the link once it's up
        pid = sid.rsplit('-short', 1)[0]; parent = json.load(open(os.path.join(STUDIO, 'doc', 'stories', pid + '.json')))
        ep = next((e for e in json.load(open(os.path.join(HERE, 'plan.json')))['episodes'] if e['id'] == pid), {})
        first = story.get('hook') or (story.get('intro') or {}).get('beats', [{}])[0].get('say', '')
        full = 'The full story, from both sides: "%s"%s' % ((parent.get('abTest') or [{'title': parent['title']}])[0]['title'], (' https://youtu.be/' + ep['videoId']) if ep.get('videoId') else ' on Smoke & Borders.')
        meta = {'title': title[:100], 'description': '%s\n\n%s\n\n📚 Source:\n%s\n\n#history #shorts #documentary' % (first, full, src),
                'tags': BASE_TAGS + parent.get('tags', []), 'categoryId': '24', 'privacy': 'private', 'publishAt': when, 'playlists': ['sb-shorts'], 'linkPlaylists': ['sb-episodes'], 'comment': ('Would you have done the same? 👇\n\n' + full)}
        f = os.path.join(outdir, 'short-%s.meta.json' % n)
    else:
        desc = '\n'.join([story.get('hook', ''), '', story.get('about', ''), '', '⏱️ Chapters', *summ['chapters'], '',
                          '📚 Sources: the full list is pinned in the comments.' + ('\n' + story['talkNote'] if story.get('talkNote') else ''), '', 'Smoke & Borders: every border has two sides. We tell both.',
                          '#history #animatedhistory #documentary'])
        # titles may say "{min}" (owner, 11 Nov 2026: "The Korean War Explained in 37 Minutes"); it becomes the real length
        mins = str(max(1, round(float(summ.get('duration') or summ.get('total') or 0) / 60)))
        for v in story.get('abTest') or []: v['title'] = v.get('title', '').replace('{min}', mins)
        story['title'] = story['title'].replace('{min}', mins)
        meta = {'title': (story.get('abTest') or [{'title': story['title']}])[0]['title'][:100], 'description': desc[:4900], 'tags': (BASE_TAGS + story.get('tags', []))[:30], 'categoryId': '24',
                'privacy': 'private', 'publishAt': when, 'thumbnail': os.path.join(outdir, 'thumb.jpg'), 'captions': summ['srt'], 'long': True, 'linkPlaylists': ['sb-shorts'],
                'playlists': summ.get('playlists', ['sb-episodes']), 'comment': '📚 Sources for this episode:\n' + src + '\n\nSpotted a mistake? Tell us below and we will pin the correction.',
                'localizations': story.get('localizations', {})}
        f = os.path.join(outdir, 'meta.json')
    json.dump(meta, open(f, 'w'), indent=1, ensure_ascii=False); print(f)

if __name__ == '__main__':
    main()
