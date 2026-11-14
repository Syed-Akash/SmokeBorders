"""FlagBomb History documentaries (16:9, 1920x1080): narrated stories on real historical maps with countryballs.
usage: python3 make_doc.py <story-id> [--stills 10,40,90]  (story: doc/stories/<id>.json; format in doc/DOC-FORMAT.md)
Output: out/<date>-doc-<id>/<id>.mp4, <id>.srt (subtitles), cover.jpg, summary.json (chapters, sources).
Narration: Kokoro voice with a studio chain; every visual action fires on a spoken word. Music is composed per chapter mood
(uneasy, tension, clock, war, grief, hope); sound effects and per-country typing blips are synthesized. All free and offline."""
import glob
import asyncio, base64, datetime, functools, http.server, json, os, re, socketserver, subprocess, sys, threading, time
import numpy as np, soundfile as sf
from playwright.async_api import async_playwright
from browser import launch
from make_thought import clean, words, time_words, reverb_ir, convolve

HERE = os.path.dirname(os.path.abspath(__file__)); DOC = os.path.join(HERE, 'doc'); SR = 24000; MSR = 48000; FPS = 30
VOICE = [('am_fenrir', 1.0)]

# ---------- timeline ----------
AUTO = [(r'^(shots?|shooting|gunfire|rifles?|bullets?|fired)$', 'gunfire'), (r'^(bombs?|explo\w*|blasts?|shells?|shelling)$', 'boom'), (r'^(artillery|cannons?|guns)$', 'cannon'),
        (r'^(march\w*|soldiers|troops|armies|army)$', 'boots'), (r'^(telegrams?|telegraph\w*|cables?|wrote|letters)$', 'morse'), (r'^(typewriter|typed)$', 'typewriter'),
        (r'^(crowds?|cheer\w*|celebrat\w*|parade)$', 'crowd'), (r'^(trains?|railway|carriage)$', 'train'), (r'^(car|driver)$', 'car'), (r'^(bells?|church)$', 'bells'),
        (r'^(ships?|navy|fleet|sea|ocean)$', 'waves'), (r'^gas$', 'hiss'), (r'^(winter|snow|christmas|frozen)$', 'wind'), (r'^(clock|hours|minutes|deadline)$', 'tick4'),
        (r'^(treaty|signed|sign|signature)$', 'pen'), (r'^(heart|heartbeat)$', 'heart')]
def norm(w): return re.sub(r"[^a-z0-9']", '', w.lower())
def voiced(a, hop=240):
    """(start, end, pauses) of a voice clip in seconds; pauses are silent runs of at least 90 ms inside the voiced part."""
    r = np.array([np.sqrt(np.mean(a[i:i + hop] ** 2)) for i in range(0, max(1, len(a) - hop), hop)]); thr = max(r.max() * .06, 1e-4)
    v = np.where(r > thr)[0]
    if not len(v): return 0, len(a) / SR, []
    st, en = v[0], v[-1] + 1; gaps, run = [], None
    for i in range(st, en):
        if r[i] <= thr: run = i if run is None else run
        elif run is not None:
            if i - run >= 9: gaps.append((run * hop / SR, i * hop / SR))
            run = None
    return st * hop / SR, en * hop / SR, gaps

TAGRE = re.compile(r'^\[(chuckle|laugh|cough|sigh|gasp|groan|sniff|clear throat)\]$', re.I)
def strip_tags(t): return re.sub(r'\[(chuckle|laugh|cough|sigh|gasp|groan|sniff|clear throat)\]\s*', '', t, flags=re.I).strip()

def build(story, k):
    # brand "smoke" = Smoke & Borders: own narrator, spoken chapter titles, voiced dialogue, logo sting, end card (no Dot)
    brand = story.get('brand', 'flagbomb'); SMOKE = brand == 'smoke'
    narr = story.get('narrator', 'bm_george' if SMOKE else None)
    style = k.get_voice_style(narr) if narr else sum(k.get_voice_style(v) * w for v, w in VOICE)
    lang = 'en-gb' if (narr or '').startswith('b') else 'en-us'
    SPK = story.get('narratorSpeed', 1.05 if SMOKE else 1.0)   # Smoke & Borders: about 145 words a minute (documentary range 135-150)
    # voice clips are cached on disk (tts/cache) so a resumed run doesn't redo minutes of synthesis
    import hashlib
    cdir = os.path.join(HERE, 'tts', 'cache'); os.makedirs(cdir, exist_ok=True)
    def cached(key, fn):
        f = os.path.join(cdir, hashlib.sha1(repr(key).encode()).hexdigest() + '.npy')
        if os.path.exists(f): return np.load(f)
        a = fn(); np.save(f + '.tmp.npy', a); os.replace(f + '.tmp.npy', f); return a
    # Kokoro is always loaded: it measures phrase lengths for the captions, and it is the fallback voice
    measure = lambda text, sp=.95: cached((narr, VOICE if not narr else 0, strip_tags(clean(text)), sp * SPK, lang), lambda: k.create(strip_tags(clean(text)), voice=style, speed=sp * SPK, lang=lang)[0].astype(np.float32))
    def kok_as(v, text): return cached((v, strip_tags(clean(text)), 1.0), lambda: k.create(strip_tags(clean(text)), voice=k.get_voice_style(v), speed=1.0, lang='en-gb' if v.startswith('b') else 'en-us')[0].astype(np.float32))
    # the narrator: Chatterbox Turbo in the timbre of our Kokoro voice (owner's pick, 7 Nov 2026), Kokoro if Turbo can't run
    engine = os.environ.get('NARRATOR') or story.get('tts', 'turbo'); refs = {}   # NARRATOR=kokoro forces the old voice
    if engine == 'turbo':
        try:
            import turbo; turbo.model(); refs[None] = turbo.ref(k, narr or 'flagbomb', style, lang, SR); turbo.speak('A short test. [chuckle] It works.', refs[None], SR)   # fail here, not mid-episode
            open(os.path.join(HERE, 'tts', 'engine.txt'), 'w').write('turbo\n')
        except Exception as e:
            engine = 'kokoro'; open(os.path.join(HERE, 'tts', 'engine.txt'), 'w').write('kokoro (Turbo failed: %s)\n' % str(e)[:300])
            print('Chatterbox Turbo unavailable, narrating with Kokoro:', e, file=sys.stderr)
    def say(text, sp=.95):
        if engine != 'turbo': return measure(text, sp)
        return cached(('turbo', narr or 'flagbomb', clean(text)), lambda: turbo.speak(clean(text), refs[None], SR))
    def say_as(who, text):
        v = story.get('voices', {}).get(who, 'am_michael')
        if engine != 'turbo': return kok_as(v, text)
        if v not in refs: refs[v] = turbo.ref(k, v, k.get_voice_style(v), 'en-gb' if v.startswith('b') else 'en-us', SR)
        return cached(('turbo', v, clean(text)), lambda: turbo.speak(clean(text), refs[v], SR))
    ev, clips, caps, cues, moods, chapters = [], [], [], [], [], []
    beatlog = []   # (start time, narration) of every spoken beat: Shorts are cut from these (shortCuts in summary.json)
    t = 1.0; balls = story['balls']; places = story.get('places', {})
    def E(**kw): ev.append(kw)
    def act(a, at, words_):
        T0 = at + a.get('delay', 0)
        if 'show' in a:
            for i, b in enumerate(a['show']): E(k='show', id=b, t=T0 + i * .18); cues.append(('pop', T0 + i * .18))
        if 'link' in a: E(k='link', a=a['link'][0], b=a['link'][1], color=a.get('color', '#fff'), t=T0)
        if 'hl' in a: E(k='hl', names=a['hl'], color=a.get('color', '#c33'), t=T0)
        if 'label' in a: E(k='label', t=T0, **a['label'])
        if 'mood' in a: E(k='mood', id=a['mood'][0], mood=a['mood'][1], t=T0)
        if 'happy' in a:
            for b_ in a['happy']: E(k='mood', id=b_, mood='happy', t=T0)
        if 'hide' in a:
            for b_ in ([a['hide']] if isinstance(a['hide'], str) else a['hide']): E(k='hide', id=b_, t=T0, dur=.5)
        if 'unlink' in a: E(k='unlink', a=a['unlink'][0], b=a['unlink'][1], t=T0)
        if 'unwar' in a: E(k='unlink', a=a['unwar'][0], b=a['unwar'][1], t=T0) if a['unwar'] != 'all' else E(k='unlink', all=1, t=T0)
        if 'line' in a: E(k='arrow', pts=a['line'], color=a.get('color', '#a9784a'), nohead=1, hold=a.get('hold', 45), t=T0, dur=2.2); cues.append(('whoosh', T0))
        if 'angry' in a:
            for b in a['angry']: E(k='mood', id=b, mood='angry', t=T0)
        if 'pin' in a: lon, lat = places[a['pin']]; E(k='pin', name=a['pin'], lon=lon, lat=lat, t=T0); cues.append(('pop', T0))
        if 'move' in a: E(k='move', id=a['move'][0], lon=a['move'][1], lat=a['move'][2], t=T0, dur=1.3)
        if 'card' in a:
            c = dict(a['card']); E(k='card', t=T0, **c); cues.append(({'doc': 'paper', 'stamp': 'stamp', 'quote': 'hit', 'big': 'hit', 'stat': 'hit'}.get(c['kind'], 'whoosh'), T0))
            if c['kind'] == 'doc':
                for j in range(len(c.get('lines', []))): cues.append(('type', T0 + .4 + j * .25))
        if 'shake' in a: E(k='fx', shake=a['shake'], t=T0)
        if 'boom' in a: cues.append(('boom', T0, a['boom']))
        if 'shot' in a: cues.append(('shot', T0)); E(k='fx', flash=.22, shake=.3, t=T0)
        if 'flash' in a: E(k='fx', flash=a['flash'], t=T0)
        if 'dim' in a: E(k='dim', v=a['dim'], dur=a.get('dimdur', 3), t=T0)
        if 'zoomhit' in a: E(k='fx', zoomhit=1, t=T0); cues.append(('hit', T0))
        if 'arrow' in a: E(k='arrow', pts=a['arrow'], color=a.get('color', '#ff5a4e'), big=a.get('big', 0), t=T0, dur=1.7); cues.append(('whoosh', T0))
        if 'clock' in a:
            E(k='clock', hours=a['clock'], t=T0, dur=5)
            for j in range(10): cues.append(('tick', T0 + j * .5))
        if 'war' in a:
            x, y = a['war']; E(k='link', a=x, b=y, war=1, t=T0); E(k='mood', id=x, mood='angry', t=T0); E(k='mood', id=y, mood='angry', t=T0); cues.append(('boom', T0, .8))
        if 'troops' in a: E(k='troops', **{'from': a['troops'][0]}, lon=a['troops'][1], lat=a['troops'][2], t=T0); cues.append(('boots', T0, 4))
        if 'cam' in a: E(k='cam', t=T0, dur=a.get('camdur', 2), **a['cam']); cues.append(('whoosh', T0))
        if 'date' in a: E(k='date', text=a['date'], t=T0); cues.append(('typewriter', T0) if '\n' in a['date'] else ('date', T0))
        if 'scene' in a: E(k='scene', t=T0, **a['scene'])   # a cut to a cinematic shot (doc/scenes.js)
        if 'cue' in a:   # times a moment inside the current shot to a word, e.g. {"on": "pencil", "cue": "draw"} (scenes.js reads S.draw)
            for x in ([a['cue']] if isinstance(a['cue'], str) else a['cue']): E(k='scenecue', key=x, t=T0)
        if 'snow' in a: E(k='snow', t=T0, off=0 if a['snow'] else 1)
        if 'say' in a: E(k='say', who=a['say'][0], text=a['say'][1], t=T0, dur=2.8)
        def where(v):
            if isinstance(v, str) and v in places: return places[v]
            if isinstance(v, str) and v in balls: return balls[v]['at']
            return v
        for kind, snd in (('explode', 'boom'), ('fire', 'fire'), ('smoke', None), ('gas', 'hiss'), ('guns', 'gunfire')):
            if kind in a:
                v = a[kind]; spec = v if isinstance(v, dict) else {'at': v}; lon, lat = where(spec['at'])
                E(k=kind, lon=lon, lat=lat, t=T0, dur=spec.get('dur', {'explode': 5, 'fire': 7, 'smoke': 7, 'gas': 7, 'guns': 4}[kind]), size=spec.get('size', 1))
                if snd: cues.append((snd, T0, spec.get('dur', 4)))
                if kind == 'explode': E(k='fx', shake=.6, t=T0)
        if 'cannon' in a: lon, lat = where(a['cannon']); E(k='guns', lon=lon, lat=lat, t=T0, dur=4, size=1.4); cues.append(('cannon', T0, 4))
        if 'telegraph' in a: E(k='telegraph', a=a['telegraph'][0], b=a['telegraph'][1], t=T0, dur=3.2); cues.append(('morse', T0, 3))
        if 'car' in a: E(k='car', pts=[where(x) for x in a['car']], t=T0, dur=a.get('cardur', 4)); cues.append(('car', T0, a.get('cardur', 4)))
        if 'news' in a: E(k='card', kind='news', t=T0, dur=a['news'].get('dur', 4.5), **{k_: v_ for k_, v_ in a['news'].items() if k_ != 'dur'}); cues.append(('press', T0)); cues.append(('whoosh', T0))
        if 'era' in a: E(k='era', era=a['era'], t=T0); cues.append(('whoosh', T0))
        if 'logo' in a: E(k='card', kind='logo', t=T0, dur=a.get('dur', 3.4)); cues.append(('chapter', T0)); cues.append(('whoosh', T0 + .2))
        if 'sfx' in a:
            for x in ([a['sfx']] if isinstance(a['sfx'], str) else a['sfx']): cues.append((x, T0, a['sfx'][x] if isinstance(a['sfx'], dict) else 3))   # {"rain": 12} sets a length
    n = 0
    for ch in ([dict(story['intro'], title='Intro', nocard=1)] if story.get('intro') else []) + story['chapters']:
        if ch.get('nocard'): chapters.append((0, 'Intro')); moods.append((t, ch.get('mood', 'tension'))); first = True; t += .2
        else:
            n += 1; dur = 3.2
            if SMOKE:   # say the chapter title, so listeners know where they are
                words_n = ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']
                a = say('Chapter %s. %s.' % (words_n[n - 1] if n <= 12 else n, ch['title']), .92); clips.append((t + .6, a)); dur = max(3.2, .6 + len(a) / SR + .9)
            E(k='chapter', n=n, title=ch['title'], years=ch['years'], t=t, dur=dur); cues.append(('chapter', t)); chapters.append((t, ch['title'])); moods.append((t, ch['mood']))
            first = True; t += dur + .2
            # owner (7 Nov 2026): a subscribe / bell / like reminder once in the middle, after the viewer has had real value
            # (start of chapter 3 by default, about a quarter in); no voice, so the story keeps moving underneath
            if n == story.get('subChapter', 3) and not story.get('noSub'):
                st_ = t + 5; E(k='sub', t=st_, dur=6.2, sub=story.get('subLine', 'Both sides, every week' if SMOKE else 'New history every week'))
                for c_ in (.5, 1.55, 2.65, 3.75): cues.append(('pop', st_ + c_))
        for bi, b in enumerate(ch['beats']):
            if 'cam' in b:
                if first: E(k='cam', t=max(0, t - 2.6), dur=2.4 if t > 3 else .01, **b['cam'])
                else: E(k='cam', t=t, dur=1.8, **b['cam']); cues.append(('whoosh', t)); t += .5
            if 'scene' in b: E(k='scene', t=t, **b['scene'])   # a cut to a cinematic shot (doc/scenes.js); {"shot": "off"} returns to the map
            if 'date' in b: E(k='date', text=b['date'], t=t); cues.append(('typewriter', t) if '\n' in b['date'] else ('date', t))
            first = False
            if 'say' in b:
                beatlog.append((round(t, 2), b['say']))
                # narration is synthesized a whole sentence at a time (natural flow across caption breaks);
                # captions come from phrase timings: each phrase is also voiced alone just to measure its length,
                # those lengths are fitted to the sentence audio and every boundary is snapped to the pause nearest to it
                ws, pend = [], None   # a cue such as [chuckle] is spoken by Turbo but never shown in the captions: it rides on the next word
                for x in words(b['say']):
                    if TAGRE.match(x['w']): pend = x['w']; continue
                    if pend: x['pre'] = pend; pend = None
                    ws.append(x)
                sents, cur = [], []
                for w in ws:
                    cur.append(w)
                    if re.search(r'[.?!…]["\u201d]?$', w['w']): sents.append(cur); cur = []
                if cur: sents.append(cur)
                pt = t
                for sw in sents:
                    a = say(' '.join((x.get('pre', '') + ' ' + x['w']).strip() for x in sw)); clips.append((pt, a))
                    phrases, cur = [], []
                    P_ = lambda w: re.search(r'[,;:\u2014]["\u201d]?$', w['w'])
                    for wi, w in enumerate(sw):
                        cur.append(w)
                        if P_(w) and len(cur) >= 3: phrases.append(cur); cur = []
                    if cur: phrases.append(cur)
                    even = []   # a long clause is cut into even pieces of at most 8 words
                    for ph in phrases:
                        m = -(-len(ph) // 8); q = len(ph) / m; even += [ph[round(i * q):round((i + 1) * q)] for i in range(m)]
                    phrases = even
                    v0, v1, gaps = voiced(a)
                    if len(phrases) > 1:
                        lens = [max(.05, np.subtract(*voiced(measure(' '.join(x['w'] for x in ph)))[1::-1])) for ph in phrases]
                        bounds, acc = [], 0
                        for L in lens[:-1]:
                            acc += L; e = v0 + (v1 - v0) * acc / sum(lens)
                            near = min(gaps, key=lambda g: abs((g[0] + g[1]) / 2 - e), default=None)
                            bounds.append(near if near and abs((near[0] + near[1]) / 2 - e) < .45 else (e, e))
                    else: bounds = []
                    edges = [v0] + [x for g in bounds for x in g] + [v1]
                    for k_, ph in enumerate(phrases):
                        s0, s1 = edges[2 * k_], edges[2 * k_ + 1]; s1 = max(s1, s0 + .2)
                        tot = sum(len(x['w']) + 2 for x in ph); acc = 0
                        for x in ph: x['t'] = round(pt + s0 + (s1 - s0) * acc / tot, 3); acc += len(x['w']) + 2
                        caps.append({'t0': pt + max(0, s0 - .08), 't1': pt + s1 + .12, 'words': [{'w': x['w'], 't': x['t']} for x in ph]})
                    last = sw[-1]['w']; pt += len(a) / SR + (.30 if re.search(r'[.?!]["\u201d]?$', last) else .22)
                d = pt - t
                # a caption stays up until the next one starts (no flicker in short gaps), and never overlaps it
                for c0, c1 in zip(caps, caps[1:]):
                    c0['t1'] = min(c0['t1'], c1['t0'])
                    if 0 < c1['t0'] - c0['t1'] < .45: c0['t1'] = c1['t0']
                done = set()
                for w in ws:
                    nw = norm(w['w'])
                    for rx, snd in AUTO:
                        if snd not in done and re.match(rx, nw) and not any(c[0] == snd and abs(c[1] - w['t']) < 1.5 for c in cues): cues.append((snd, w['t'], 3)); done.add(snd)
                for a_ in b.get('do', []):
                    key = norm(a_.get('on', '')); at = next((w['t'] for w in ws if key and norm(w['w']).startswith(key)), t)
                    act(a_, at, ws)
                nxt = ch['beats'][bi + 1] if bi + 1 < len(ch['beats']) else None
                t += d + (.75 if nxt and 'talk' in nxt else .5)
            elif 'talk' in b:
                order = []
                for line in b['talk']:
                    if line['who'] not in order: order.append(line['who'])
                for line in b['talk']:
                    if SMOKE:   # dialogue is spoken in each side's own voice
                        a = say_as(line['who'], line['text']); clips.append((t + .15, a)); dur = len(a) / SR + .55
                        if story.get('film'):   # owner, 15 Nov 2026: acted dialogue, shot / reverse shot, one cut per line
                            cast = story.get('cast', {}); me = cast.get(line['who'], {}); oth = next((w for w in order if w != line['who']), None)
                            E(k='scene', t=t, shot='talk', who=line['who'], name=line.get('name') or me.get('name', line['who']), preset=me.get('preset'), spec=me.get('spec'),
                              side='l' if order.index(line['who']) == 0 else 'r', text=line['text'], mood=line.get('mood', me.get('mood', 'neutral')),
                              other={'preset': cast.get(oth, {}).get('preset'), 'spec': cast.get(oth, {}).get('spec')} if oth else None,
                              bg=b.get('bg') or me.get('bg') or story.get('talkBg'))
                        else: E(k='say', who=line['who'], text=line['text'], t=t, dur=dur + .3)
                        t += dur + .15; continue
                    dur = min(4.6, max(2.2, 1.3 + len(line['text']) * .045)); E(k='say', who=line['who'], text=line['text'], t=t, dur=dur)
                    for j in range(int(len(line['text']) / 38 / .07)): cues.append(('blip', t + j * .07, line['who']))
                    t += dur * .9 + .1
                t += .3
                for a_ in b.get('do', []): act(a_, t, [])
            else:
                for a_ in b.get('do', []): act(a_, t, [])
                t += b.get('pause', 0)   # a beat with no words that still takes time (logo sting, a silent map move)
        t += .4
    sc = sorted([e for e in ev if e['k'] == 'scene'], key=lambda e: e['t'])   # each shot lasts until the next cut (its camera move spans the shot)
    for i, e in enumerate(sc):
        if 'dur' not in e: e['dur'] = round(((sc[i + 1]['t'] if i + 1 < len(sc) else t) - e['t']), 2)
    if story.get('film'): film_sound(sc, cues)
    if story.get('short') or story.get('demo'):   # a standalone Short (or a style demo): just the story, no outro, reminder or end card (cut_shorts.py makes it vertical)
        start = next(b['cam'] for c in ([story['intro']] if story.get('intro') else []) + story['chapters'] for b in c['beats'] if 'cam' in b)
        total = t + 1.0
        return {'events': ev, 'captions': caps, 'balls': balls, 'start': start, 'total': round(total, 2), 'brand': brand, 'beats': beatlog, 'story': story.get('photosFrom', story['id']), **({'short': 1} if story.get('short') else {})}, clips, cues, moods, chapters, total
    O = story['outro']; t += .3
    if SMOKE:   # end card: the closing line and the question are both spoken; then the next story
        a = say(O['text'] + ' ' + O['question'], .9); d = len(a) / SR; clips.append((t + .8, a)); moods.append((t - .5, 'hope'))
        E(k='outro', t=t, text=O['text'], question=O['question'], next=O.get('next', ''), talkEnd=.8 + d, qAt=.8 + d * .75, brand='smoke', cta=1); cues.append(('chapter', t))
        total = t + d + 1.2
    else:   # outro: Dot
        a = say(O['dot'], .9); d = len(a) / SR; clips.append((t + .8, a)); moods.append((t - .5, 'hope'))
        E(k='outro', t=t, text=O['dot'], question=O['question'], talkEnd=.8 + d, qAt=1.2 + d); cues.append(('chapter', t))
        total = t + d + 1.6
    # the warm close (owner, 7 Nov 2026): one friendly spoken line with the subscribe / bell / like animation, then 20 seconds of
    # end card so YouTube's end screen (subscribe button + next video) has room. Never begging, never before the story's close.
    cta = O.get('cta') or ("If you enjoyed this story, subscribe to stay connected, and tap the bell so you never miss the next one." if SMOKE
                           else "If you enjoyed this one, subscribe to stay connected, and hit the bell so you never miss the next story.")
    a = say(cta, .93); dc = len(a) / SR; clips.append((total, a))
    E(k='sub', t=total - .3, dur=max(6.2, dc + 1.2), sub=story.get('subLine', 'Both sides, every week' if SMOKE else 'New history every week'), cx=1, top=int(1080 * .6 - 40) if SMOKE else 70)
    for c_ in (.5, 1.55, 2.65, 3.75): cues.append(('pop', total - .3 + c_))
    total += dc + 20
    start = next(b['cam'] for c in ([story['intro']] if story.get('intro') else []) + story['chapters'] for b in c['beats'] if 'cam' in b)
    return {'events': ev, 'captions': caps, 'balls': balls, 'start': start, 'total': round(total, 2), 'brand': brand, 'beats': beatlog, 'story': story.get('photosFrom', story['id'])}, clips, cues, moods, chapters, total

# ---------- music & sound ----------
def env(n, a, d): x = np.arange(n) / MSR; return np.clip(x / max(a, 1e-4), 0, 1) * np.exp(-x / max(d, 1e-4))
def saw(f, x, n=6): return sum(np.sin(2 * np.pi * f * h * x) / h * (.85 ** h) for h in range(1, n + 1))
def lp(x, k): return np.convolve(x, np.ones(k) / k, 'same')
NOTE = lambda s: 440 * 2 ** ((s - 69) / 12)
def mood_music(mood, dur, rng):
    n = int(dur * MSR); x = np.arange(n) / MSR; out = np.zeros(n)
    def pad(chords, L, gain=.02, oct_=0):
        for ci in range(int(dur / L) + 2):
            s0 = ci * L - .8; i0, i1 = max(0, int(s0 * MSR)), min(n, int((s0 + L + 1.6) * MSR))
            if i0 >= i1: continue
            tt = x[i0:i1] - s0; e = np.clip(tt / 1.6, 0, 1) * np.clip((L + 1.6 - tt) / 1.6, 0, 1)
            for m in chords[ci % len(chords)]:
                for dt in (-.7, .7): out[i0:i1] += saw(NOTE(m + oct_) + dt, tt) * e * gain
    def piano(scale, every, gain=.12, lo=0):
        tt0 = .6
        while tt0 < dur - 1:
            f = NOTE(scale[rng.integers(len(scale))] + lo); i0 = int(tt0 * MSR); i1 = min(n, i0 + int(3.5 * MSR)); tt = x[i0:i1] - tt0
            out[i0:i1] += sum(np.sin(2 * np.pi * f * h * tt) * (.5 ** h) * np.exp(-tt * (1.4 + h * .8)) for h in range(1, 6)) * gain; tt0 += rng.choice(every)
    def drone(fs, gain=.18):
        for f in fs: out[:] += np.sin(2 * np.pi * f * x) * (0.6 + 0.4 * np.sin(2 * np.pi * .07 * x)) * gain
    def beats(times, f0=60, gain=.5, dec=.12):
        for b in times:
            L = int(.4 * MSR); i0 = int(b * MSR)
            if i0 >= n: break
            seg = np.sin(2 * np.pi * np.cumsum(np.linspace(f0 * 2.2, f0, L)) / MSR) * env(L, .002, dec) * gain; j = min(n, i0 + L); out[i0:j] += seg[:j - i0]
    if mood == 'uneasy': pad([[50, 57, 62, 65], [46, 53, 62, 65], [53, 57, 60, 65], [45, 52, 61, 64]], 5.0, .016); piano([74, 77, 79, 81, 84, 86], [1.5, 2.25, 3.0], .09)
    elif mood in ('tension', 'clock'):
        drone([36.71, 55.0, 73.42], .12); out[:] += (np.sin(2 * np.pi * 587.33 * x) + np.sin(2 * np.pi * 622.25 * x)) * .012 * (0.5 + 0.5 * np.sin(2 * np.pi * .1 * x))
        beats([i * 1.15 for i in range(int(dur / 1.15) + 1)] + [i * 1.15 + .28 for i in range(int(dur / 1.15) + 1)], 55, .45)
    elif mood == 'war':
        bt = 60 / 96; beats([i * bt for i in range(int(dur / bt) + 1)], 58, .55); beats([i * bt * 2 + bt for i in range(int(dur / bt / 2) + 1)], 110, .3, .08)
        for i in range(int(dur / (bt / 2))):
            i0 = int(i * bt / 2 * MSR); L = int(bt / 2 * MSR); j = min(n, i0 + L)
            if i0 < n: out[i0:j] += (saw(73.42, x[:j - i0], 4) * env(L, .005, .15)[:j - i0]) * .12
        pad([[38, 45, 50], [41, 48, 53]], 4.0, .018)
    elif mood == 'grief': pad([[45, 52, 57, 60], [41, 48, 57, 60], [48, 55, 60, 64], [43, 50, 59, 62]], 5.5, .012); piano([57, 60, 64, 69, 72, 76], [1.0, 1.5], .11, -12)
    else: pad([[48, 55, 60, 64], [43, 50, 59, 62], [45, 52, 57, 60], [41, 48, 57, 60]], 4.5, .015); piano([72, 74, 76, 79, 81, 84], [1.0, 1.5, 2.0], .1)
    out = lp(out, 16); return out / (np.abs(out).max() or 1)

# ---------- the sound library (studio/sfx/<kind>/NN.flac, 48 kHz mono, picked from the owner's pack; see sfx/sources.json) ----------
SFXDIR = os.path.join(HERE, 'sfx'); _LIB = {}; _LAST = {}
def lib(kind):
    if kind not in _LIB: _LIB[kind] = [sf.read(f, dtype='float32')[0] for f in sorted(glob.glob(os.path.join(SFXDIR, kind, '*.flac')))]
    return _LIB[kind]
def lib_pick(kind, rng):
    L = lib(kind)
    if not L: return None
    i = int(rng.integers(len(L)))
    if len(L) > 1 and i == _LAST.get(kind): i = (i + 1) % len(L)   # never the same sound twice in a row
    _LAST[kind] = i; return L[i]
def fit(s, dur, fin=.5, fout=.8):
    """Loops (with a half-second crossfade) or trims a sound to dur seconds, with a fade in and out: background beds under a shot."""
    n = int(dur * MSR); xf = int(.5 * MSR)
    if len(s) < n:
        out = np.zeros(n + len(s), np.float32); pos = 0; ramp = np.linspace(0, 1, xf, dtype=np.float32)
        while pos < n:
            seg = s.copy()
            if pos: seg[:xf] *= ramp
            seg[-xf:] *= ramp[::-1]
            out[pos:pos + len(seg)] += seg; pos += len(s) - xf
        s = out
    s = s[:n].copy(); a, b = int(fin * MSR), int(fout * MSR)
    if a: s[:a] *= np.linspace(0, 1, a)
    if b and len(s) > b: s[-b:] *= np.linspace(1, 0, b)
    return s

OUTDOOR = {'hills', 'land', 'forest', 'farm', 'camp', 'fort', 'flagpole', 'animal', 'soldiers', 'cannons'}
def film_sound(sc, cues):
    """Owner, 14 Nov 2026 ("the videos don't have enough sound effects"): every film shot gets its own sound.
    A soft whoosh on each cut (not where a chapter card or a boom already hits), a quiet background bed under the shot
    (sea and ships: waves; fire: fire; outdoors: wind; rain: rain; towns and crowds: crowd; archival photos: the film
    projector; time cards: a ticking clock) and a paper rustle when a document comes up. Beds are ducked under the voice."""
    loud = [c[1] for c in cues if c[0] in ('chapter', 'boom', 'hit', 'stamp', 'shot')]
    for i, e in enumerate(sc):
        k = e.get('shot')
        if k == 'off': continue
        t0, d = e['t'], max(1.0, e.get('dur', 6))
        if k == 'talk':   # dialogue: one soft whoosh into the exchange, none between its lines
            if i and sc[i - 1].get('shot') != 'talk': cues.append(('cut', t0))
            continue
        if i and not any(abs(x - t0) < 1.2 for x in loud): cues.append(('cut', t0))
        if k == 'photo': cues.append(('bed', t0, d, 'projector', .16))
        elif k == 'card': cues.append(('bed', t0, min(d, 7), 'clock', .45))
        elif k == 'doc': cues.append(('paper', t0 + .15))
        elif k == 'set':
            types = {p.get('type') for p in e.get('parts', []) if isinstance(p, dict)}
            fx = set([e['fx']] if isinstance(e.get('fx'), str) else e.get('fx') or []) | ({e['weather']} if e.get('weather') else set())
            wet = types & {'sea', 'coast', 'ships'}
            if wet: cues.append(('bed', t0, d, 'waves', .32))
            if 'fire' in types or 'embers' in fx: cues.append(('bed', t0, d, 'fire', .34))
            if fx & {'rain', 'storm'}: cues.append(('rain', t0, d))
            if types & {'town', 'crowd'}: cues.append(('crowd', t0 + .3))
            if (types & OUTDOOR or 'fog' in fx) and not wet: cues.append(('bed', t0, d, 'wind', .26))

LIBMAP = {'whoosh': ('whoosh', .55), 'cut': ('whoosh', .3), 'hit': ('subdrop', .9), 'shot': ('shot', .9), 'bells': ('bells', .8),
          'thunder': ('thunder', 1.0), 'braam': ('braam', .9), 'tension': ('tension', .7), 'riser': ('riser', .6), 'impact': ('impact', .9)}
LOOPS = {'fire': ('fire', .7), 'waves': ('waves', .7), 'wind': ('wind', .6), 'train': ('train', .7), 'clock': ('clock', .6), 'projector': ('projector', .5)}

SPEAK = {}
def sfx_track(cues, total, rng, beds=False):
    """The effects track. beds=True returns only the background beds (quiet, not normalised: ducked under the voice in the mix).
    Every kind uses a real recording from studio/sfx when there is one, and falls back to the sound made here."""
    n = int((total + 1) * MSR); out = np.zeros(n, np.float32)   # 35 minutes at 48 kHz is 400 MB even in float32: keep every full-length track float32
    def add(at, s, g=1.0):
        i = int(max(0, at) * MSR); j = min(n, i + len(s))
        if i < n: out[i:j] += s[:j - i] * g
    if beds:
        for c in cues:
            if c[0] == 'bed':
                s = lib_pick(c[3], rng)
                if s is not None: add(c[1], fit(s, c[2]), c[4])
        return np.clip(out, -.95, .95, out=out)
    for c in cues:
        kind, at = c[0], c[1]
        if kind == 'bed': continue
        if kind in LIBMAP:   # a one-shot from the library
            s = lib_pick(LIBMAP[kind][0], rng)
            if s is not None: add(at - (.25 if kind in ('whoosh', 'cut') else 0), s, LIBMAP[kind][1]); continue
        if kind == 'boom':
            s = lib_pick('impact', rng)
            if s is not None: add(at, s, c[2] if len(c) > 2 else 1); continue
        if kind == 'chapter':   # a riser that lands on the chapter card, then a sub drop
            r, d = lib_pick('riser', rng), lib_pick('subdrop', rng)
            if r is not None and d is not None:
                r = r[:int(min(len(r) / MSR, 3.0) * MSR)].copy(); r[:int(.8 * MSR)] *= np.linspace(0, 1, int(.8 * MSR)); add(at - len(r) / MSR, r, .4); add(at, d, 1.0); continue
        if kind in LOOPS or kind == 'tick':
            k_, g_ = LOOPS.get(kind, ('clock', .6)); s = lib_pick(k_, rng)
            if s is not None: add(at, fit(s, c[2] if len(c) > 2 else (5 if kind == 'tick' else 4), .2, .6), g_); continue
        if kind == 'boom':
            L = int(2.8 * MSR); x = np.arange(L) / MSR; add(at, (np.sin(2 * np.pi * np.cumsum(46 - 14 * np.clip(x / 1.5, 0, 1)) / MSR) * np.exp(-x * 1.5) + lp(rng.standard_normal(L), 160) * np.exp(-x * 7) * 3) * .9, c[2] if len(c) > 2 else 1)
        elif kind == 'shot':
            L = int(1.2 * MSR); x = np.arange(L) / MSR; add(at, rng.standard_normal(L) * np.exp(-x * 38) * 1.4 + np.sin(2 * np.pi * 70 * x) * np.exp(-x * 9) * .9 + lp(rng.standard_normal(L), 30) * np.exp(-x * 3) * .4)
        elif kind == 'whoosh':
            L = int(.9 * MSR); x = np.arange(L) / MSR; nz = lp(rng.standard_normal(L), 24) - lp(rng.standard_normal(L), 120); add(at - .2, nz * np.sin(np.pi * x / .9) ** 2 * .8)
        elif kind in ('paper', 'type'):
            L = int((.25 if kind == 'paper' else .04) * MSR); x = np.arange(L) / MSR; add(at, np.diff(rng.standard_normal(L + 1)) * np.exp(-x * (12 if kind == 'paper' else 120)) * (.5 if kind == 'paper' else .35))
        elif kind == 'stamp':
            L = int(.6 * MSR); x = np.arange(L) / MSR; add(at + .2, np.sin(2 * np.pi * 90 * x) * np.exp(-x * 14) * 1.2 + rng.standard_normal(L) * np.exp(-x * 40) * .6)
        elif kind == 'hit':
            L = int(2.0 * MSR); x = np.arange(L) / MSR; add(at, np.sin(2 * np.pi * 55 * x) * np.exp(-x * 2.2) * .8 + rng.standard_normal(L) * np.exp(-x * 30) * .3)
        elif kind == 'chapter':
            L = int(3.0 * MSR); x = np.arange(L) / MSR; swell = lp(rng.standard_normal(L), 60) * np.clip(x / 1.2, 0, 1) ** 2 * (x < 1.2); add(at - 1.2, swell * .5); add(at, np.sin(2 * np.pi * 41 * x) * np.exp(-x * 1.4) * 1.0)
        elif kind == 'tick':
            L = int(.05 * MSR); x = np.arange(L) / MSR; add(at, np.sin(2 * np.pi * 2400 * x) * np.exp(-x * 160) * .5)
        elif kind == 'date':
            L = int(.5 * MSR); x = np.arange(L) / MSR; add(at, np.sin(2 * np.pi * 880 * x) * np.exp(-x * 9) * .15)
        elif kind == 'pop':
            L = int(.14 * MSR); x = np.arange(L) / MSR; add(at, np.sin(2 * np.pi * (380 + 1400 * x / .14) * x) * env(L, .002, .05) * .35)
        elif kind == 'gunfire':
            for j in range(int(rng.integers(5, 9))):
                L = int(.9 * MSR); x = np.arange(L) / MSR; add(at + j * rng.uniform(.12, .45), (rng.standard_normal(L) * np.exp(-x * 45) * 1.2 + lp(rng.standard_normal(L), 40) * np.exp(-x * 6) * .5) * rng.uniform(.4, .9))
        elif kind == 'cannon':
            for j in range(4):
                L = int(2.5 * MSR); x = np.arange(L) / MSR; add(at + j * rng.uniform(.6, 1.1), (np.sin(2 * np.pi * np.cumsum(70 - 30 * np.clip(x / .8, 0, 1)) / MSR) * np.exp(-x * 2.4) + lp(rng.standard_normal(L), 90) * np.exp(-x * 2) * 1.6 + rng.standard_normal(L) * np.exp(-x * 60) * .7) * .8)
        elif kind == 'boots':
            for j in range(int(c[2] * 2.2) if len(c) > 2 else 8):
                L = int(.18 * MSR); x = np.arange(L) / MSR; add(at + j * .45 + rng.uniform(-.02, .02), (np.sin(2 * np.pi * 80 * x) * np.exp(-x * 30) + lp(rng.standard_normal(L), 6) * np.exp(-x * 25) * .8) * .45)
        elif kind == 'morse':
            tt = at; pat = '.-.. --- -.-- .- .-..'
            for ch in pat:
                L = int((.07 if ch == '.' else .21 if ch == '-' else .14) * MSR); x = np.arange(L) / MSR
                if ch != ' ': add(tt, np.sin(2 * np.pi * 760 * x) * .22 * np.clip(x / .004, 0, 1) * np.clip((L / MSR - x) / .004, 0, 1))
                tt += L / MSR + .06
        elif kind == 'typewriter':
            for j in range(18):
                L = int(.03 * MSR); x = np.arange(L) / MSR; add(at + j * rng.uniform(.07, .16), np.diff(rng.standard_normal(L + 1)) * np.exp(-x * 140) * .5)
            L = int(.6 * MSR); x = np.arange(L) / MSR; add(at + 2.4, np.sin(2 * np.pi * 2100 * x) * np.exp(-x * 7) * .25)
        elif kind == 'crowd':
            L = int(4 * MSR); x = np.arange(L) / MSR; base = lp(rng.standard_normal(L), 10) - lp(rng.standard_normal(L), 60); add(at, base * (0.5 + 0.5 * np.sin(2 * np.pi * 3.3 * x + rng.uniform(0, 6))) * np.sin(np.pi * x / 4) * 1.2)
            for j in range(40): Lc = int(.025 * MSR); add(at + rng.uniform(.3, 3.6), rng.standard_normal(Lc) * .4)
        elif kind == 'train':
            for j in range(16):
                L = int(.22 * MSR); x = np.arange(L) / MSR; add(at + j * .26, lp(rng.standard_normal(L), 12) * np.exp(-x * 14) * .5)
            L = int(1.4 * MSR); x = np.arange(L) / MSR; add(at + .3, (np.sin(2 * np.pi * 523 * x) + np.sin(2 * np.pi * 659 * x)) * np.clip(x / .1, 0, 1) * np.clip((1.4 - x) / .3, 0, 1) * .12)
        elif kind == 'car':
            L = int((c[2] if len(c) > 2 else 4) * MSR); x = np.arange(L) / MSR; add(at, (saw(48, x, 5) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 11 * x))) * .18 + lp(rng.standard_normal(L), 20) * .1) * np.clip(x / .4, 0, 1) * np.clip((L / MSR - x) / .8, 0, 1))
        elif kind == 'bells':
            for j in range(3):
                L = int(3.5 * MSR); x = np.arange(L) / MSR; add(at + j * 1.1, sum(np.sin(2 * np.pi * 392 * r * x) * np.exp(-x * (1.2 + r)) * g for r, g in ((1, .4), (2.0, .2), (2.4, .15), (3.0, .1), (4.2, .06))) * .5)
        elif kind == 'waves':
            L = int(4 * MSR); x = np.arange(L) / MSR; add(at, lp(rng.standard_normal(L), 40) * (0.5 + 0.5 * np.sin(2 * np.pi * .4 * x)) * np.sin(np.pi * x / 4) * .9)
        elif kind == 'rain':   # steady rain (c[2] seconds), with a soft swell in and out
            L = int((c[2] if len(c) > 2 else 8) * MSR); x = np.arange(L) / MSR; nz = rng.standard_normal(L) - lp(rng.standard_normal(L), 3)
            add(at, (nz * .16 + lp(rng.standard_normal(L), 25) * .25) * np.clip(x / 1.5, 0, 1) * np.clip((L / MSR - x) / 1.5, 0, 1))
        elif kind == 'thunder':
            L = int(4.5 * MSR); x = np.arange(L) / MSR; add(at + .3, lp(rng.standard_normal(L), 220) * np.clip(x / .15, 0, 1) * np.exp(-x * .9) * 4 * (1 + .6 * np.sin(2 * np.pi * 1.7 * x)))
        elif kind == 'hiss':
            L = int(3 * MSR); x = np.arange(L) / MSR; add(at, (rng.standard_normal(L) - lp(rng.standard_normal(L), 8)) * np.sin(np.pi * x / 3) * .25)
        elif kind == 'wind':
            L = int(5 * MSR); x = np.arange(L) / MSR; add(at, lp(rng.standard_normal(L), 70) * (0.6 + 0.4 * np.sin(2 * np.pi * .3 * x)) * np.sin(np.pi * x / 5) * 1.4)
        elif kind == 'tick4':
            for j in range(6): L = int(.05 * MSR); x = np.arange(L) / MSR; add(at + j * .5, np.sin(2 * np.pi * (2400 if j % 2 else 1900) * x) * np.exp(-x * 160) * .45)
        elif kind == 'pen':
            L = int(1.2 * MSR); x = np.arange(L) / MSR; add(at, (rng.standard_normal(L) - lp(rng.standard_normal(L), 4)) * (np.abs(np.sin(2 * np.pi * 3 * x)) ** 2) * .18)
        elif kind == 'heart':
            for j in range(3):
                for o in (0, .28): L = int(.3 * MSR); x = np.arange(L) / MSR; add(at + j * 1.0 + o, np.sin(2 * np.pi * 52 * x) * np.exp(-x * 14) * (.7 if o == 0 else .5))
        elif kind == 'fire':
            L = int((c[2] if len(c) > 2 else 5) * MSR); x = np.arange(L) / MSR; base = lp(rng.standard_normal(L), 30) * .35 * np.clip(x / .6, 0, 1) * np.clip((L / MSR - x) / 1, 0, 1); add(at, base)
            for j in range(int(L / MSR * 14)): Lc = int(.01 * MSR); add(at + rng.uniform(0, L / MSR), rng.standard_normal(Lc) * .5)
        elif kind == 'press':
            for j in range(6): L = int(.08 * MSR); x = np.arange(L) / MSR; add(at + j * .09, (lp(rng.standard_normal(L), 5) + np.sin(2 * np.pi * 140 * x)) * np.exp(-x * 30) * .4)
        elif kind == 'blip':
            who = c[2]; f = SPEAK.setdefault(who, 420 + 90 * (len(SPEAK) % 6)); L = int(.045 * MSR); x = np.arange(L) / MSR; add(at, np.sign(np.sin(2 * np.pi * f * x)) * env(L, .002, .015) * .1)
    wet = convolve(out, reverb_ir(1.4, seed=5)); out *= .85; wet *= .25; out += wet; del wet
    out /= (np.abs(out).max() or 1); return out

# ---------- render ----------
class _Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
def game_flags():
    """doc/vendor/gameflags.js: the game's flag painters (every FlagBomb country), extracted from the game file."""
    src = os.path.join(os.path.dirname(HERE), 'game', 'blast-nations.html')
    if not os.path.exists(src): return   # Smoke & Borders repo: the flag painters are committed in doc/vendor/gameflags.js
    g = open(src).read()
    a = g.index('function rect(c,col,x,y,w,h)'); b = g.index('\n};\n', g.index('const FLAGS={', a)) + 3
    open(os.path.join(HERE, 'doc', 'vendor', 'gameflags.js'), 'w').write('// generated by make_doc.py from game/blast-nations.html\nwindow.GFLAGS=(()=>{' + g[a:b] + '\nreturn FLAGS})();\n')

async def render(era, tl, times=None, enc=None):
    game_flags()
    srv = socketserver.TCPServer(('127.0.0.1', 0), functools.partial(_Quiet, directory=HERE)); port = srv.server_address[1]; threading.Thread(target=srv.serve_forever, daemon=True).start()
    outs = []; errs = []
    try:
        async with async_playwright() as p:
            b = await launch(p); pg = await b.new_page(viewport={'width': 1920, 'height': 1080}); pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('http://127.0.0.1:%d/doc/doc.html' % port); await pg.wait_for_function('window.__ok'); await pg.evaluate('e=>load(e)', [era] + sorted({e['era'] for e in tl['events'] if e['k'] == 'era'} - {era})); await pg.evaluate('d=>init(d)', {**tl, 'era': era})
            ts = times if times is not None else [i / FPS for i in range(int(tl['total'] * FPS))]; t0 = time.time()
            for i in range(0, len(ts), 4):
                urls = await pg.evaluate("ts=>ts.map(t=>{frame(t);return document.getElementById('c').toDataURL('image/jpeg',.9)})", ts[i:i + 4])
                for u in urls:
                    d = base64.b64decode(u.split(',', 1)[1])
                    if enc: enc.stdin.write(d)
                    else: outs.append(d)
                if enc and i % 900 == 0: print('frame %d/%d (%.0fs)' % (i, len(ts), time.time() - t0), flush=True)
            await b.close()
    finally: srv.shutdown()
    if errs: raise RuntimeError('page errors: %s' % errs[:3])
    return outs

def srt(caps, path):
    f = lambda s: '%02d:%02d:%02d,%03d' % (s // 3600, s % 3600 // 60, s % 60, (s % 1) * 1000)
    open(path, 'w').write(''.join('%d\n%s --> %s\n%s\n\n' % (i + 1, f(c['t0']), f(c['t1']), ' '.join(w['w'] for w in c['words'])) for i, c in enumerate(caps)))

def film_check(tl, chapters, total):
    """Owner, 14 Nov 2026: episodes must play like a film, minute by minute, the map only where it is needed.
    Rules: scenes (photo / doc / card / set / drawn shots) cover at least 70% of the runtime, the map at most 30%;
    no shot (scene or map stretch) lasts over 20 s; every chapter opens on a scene. Prints a report; returns the problems."""
    sc = sorted([e for e in tl['events'] if e['k'] == 'scene'], key=lambda e: e['t']); bad = []; spans = []
    for i, e in enumerate(sc):
        end = sc[i + 1]['t'] if i + 1 < len(sc) else total
        spans.append((e['t'], end, e.get('shot') != 'off', e.get('shot')))
    if not sc or sc[0]['t'] > 1: spans.insert(0, (0, sc[0]['t'] if sc else total, False, 'map'))
    film = sum(b - a for a, b, on, _ in spans if on); share = film / total if total else 0
    cards = [(e['t'], e['t'] + e.get('dur', 4)) for e in tl['events'] if e['k'] == 'chapter']   # chapter title cards cover the shot
    seen = lambda a, b: (b - a) - sum(max(0, min(b, y) - max(a, x)) for x, y in cards)
    last = tl['beats'][-1][0] + 15 if tl.get('beats') else total   # the outro (subscribe, end card) is not a shot
    long_ = [(round(a), round(seen(a, min(b, last))), k or 'map') for a, b, on, k in spans if seen(a, min(b, last)) > 20.5]
    # a "set"/"photo" shot can hold longer if it has inner cuts; still, flag anything over 20 s
    opens = []
    for ch in chapters:
        t0 = ch['t'] if isinstance(ch, dict) else ch[0]
        if not any(on and (a <= t0 + 6 < b or t0 <= a <= t0 + 6) for a, b, on, k in spans): opens.append(ch['title'] if isinstance(ch, dict) else ch[1])   # a scene within 6 s (after the chapter card)
    import math
    def rnd(i): x = math.sin(i * 127.1 + 311.7) * 43758.5453; return x - math.floor(x)
    angle = 0
    for e in sc:
        if e.get('shot') in ('doc', 'card', 'talk', 'off') or e.get('angles') is False: continue
        a, i_ = 0, 0
        while True:
            a += 2.6 + rnd(e['t'] * 7 + i_ * 3.1) * 0.9
            if a > e.get('dur', 8) - 1.8: break
            angle += 1; i_ += 1
    talk = sum(1 for e in sc if e.get('shot') == 'talk')
    print('FILM CHECK: scenes %.0f%% of %.1f min (need 70%%), map %.0f%% (max 30%%), %d shots + %d angle cuts = a cut every %.1f s (aim 3-4), %d dialogue lines, %d over 20 s, %d chapters open on the map'
          % (share * 100, total / 60, (1 - share) * 100, len(spans), angle, total / max(1, len(spans) + angle), talk, len(long_), len(opens)))
    if share < .70: bad.append('scenes cover only %.0f%%' % (share * 100))
    if long_: bad.append('shots over 20 s at ' + ', '.join('%ds (%ds %s)' % x for x in long_[:12]))
    if opens: bad.append('chapters opening on the map: ' + '; '.join(opens))
    for b in bad: print('  FILM CHECK FAILED:', b)
    return bad

def pacing(tl, chapters, total, outdir):
    """Retention check before rendering (smoke/STYLE.md section 3): something new on screen every 10 s in the first 3 minutes and
    every 20 s after; prints every gap that breaks it, events per minute for each chapter, and saves pacing.json."""
    ts = sorted({round(e['t'], 1) for e in tl['events'] if 't' in e} | {0.0, round(total, 1)}); gaps = []
    for a, b in zip(ts, ts[1:]):
        lim = 10 if a < 180 else 20
        if b - a > lim: gaps.append({'from': a, 'to': b, 'gap': round(b - a, 1), 'limit': lim})
    starts = [c[0] if isinstance(c, (list, tuple)) else c for c in (chapters or [])]
    per = []
    for i, st in enumerate(starts):
        en = starts[i + 1] if i + 1 < len(starts) else total; n = sum(1 for t in ts if st <= t < en)
        per.append({'chapter': i, 'title': chapters[i][1] if isinstance(chapters[i], (list, tuple)) else '', 'start': round(st, 1), 'minutes': round((en - st) / 60, 1), 'events_per_min': round(n / max(.1, (en - st) / 60), 1)})
    rep = {'total_min': round(total / 60, 1), 'gaps': gaps, 'chapters': per}
    json.dump(rep, open(os.path.join(outdir, 'pacing.json'), 'w'), indent=1)
    print('length %.1f min, %d gaps over the limit' % (total / 60, len(gaps)))
    lo, hi = (25, 45) if tl.get('brand') == 'smoke' else (10, 20)   # owner, 15 Nov 2026: 25 minimum when the story is fully told
    if not tl.get('short') and not lo <= total / 60 <= hi: print('  LENGTH: %.1f min is outside the %d-%d minute target; expand or tighten the story before rendering' % (total / 60, lo, hi))
    for g in gaps: print('  %6.1f-%6.1f s: %4.1f s with nothing new (limit %d s)' % (g['from'], g['to'], g['gap'], g['limit']))
    for c in per: print('  %-34s at %5.0f s: %.1f min, %.1f events/min' % (c['title'][:34], c['start'], c['minutes'], c['events_per_min']))

def main():
    sid = sys.argv[1]; story = json.load(open(os.path.join(DOC, 'stories', sid + '.json'))); rng = np.random.default_rng(11)
    day = datetime.date.today().isoformat(); outdir = os.path.join(HERE, 'out', '%s-doc-%s' % (day, sid))
    if '--resume' in sys.argv:   # a render that started on an earlier day continues in that day's folder
        old = sorted(d for d in glob.glob(os.path.join(HERE, 'out', '*-doc-' + sid)) if glob.glob(os.path.join(d, 'seg-*.mp4')) or os.path.exists(os.path.join(d, 'video.tmp.mp4')))
        if old: outdir = old[-1]
    os.makedirs(outdir, exist_ok=True); t0 = time.time()
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(HERE, 'tts/kokoro.onnx'), os.path.join(HERE, 'tts/voices.bin'))
    tl, clips, cues, moods, chapters, total = build(story, k)
    free_voice()
    fc = film_check(tl, chapters, total) if story.get('film') else None   # film-style episodes (owner, 14 Nov 2026)
    if '--pacing' in sys.argv: pacing(tl, chapters, total, outdir); return
    if fc and '--stills' not in sys.argv and '--force' not in sys.argv: sys.exit('NOT RENDERING: the film check failed (see above). Add scenes, then run again.')
    if '--stills' in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index('--stills') + 1].split(',')]
        for t, d in zip(ts, asyncio.run(render(story['era'], tl, ts))): open(os.path.join(outdir, 'still-%06.1f.jpg' % t), 'wb').write(d)
        print(json.dumps({'total': total, 'chapters': chapters})); return
    vid = os.path.join(outdir, 'video.tmp.mp4')
    def vlen(f):
        try: return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).decode().strip())
        except Exception: return 0
    if '--resume' in sys.argv and os.path.exists(vid) and vlen(vid) >= total - .5: print('reusing rendered frames', file=sys.stderr)   # a stopped run: only redo the sound
    else: render_video(story, tl, vid)
    finish(story, sid, outdir, tl, clips, cues, moods, chapters, total, rng, vid, t0)

def render_video(story, tl, vid, seg=90):
    """Renders in 90-second pieces (seg-NNN.mp4) so a stopped run can continue with --resume instead of starting over."""
    d = os.path.dirname(vid); n = int(tl['total'] * FPS); per = seg * FPS; parts = []
    if '--resume' not in sys.argv:
        for f in glob.glob(os.path.join(d, 'seg-*.mp4')): os.remove(f)
    for k, a in enumerate(range(0, n, per)):
        p = os.path.join(d, 'seg-%03d.mp4' % k); parts.append(p)
        if os.path.exists(p): continue
        tmp = p[:-4] + '.part.mp4'
        enc = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-tune', 'film', '-maxrate', '14M', '-bufsize', '28M', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-f', 'mp4', tmp], stdin=subprocess.PIPE)
        try: asyncio.run(render(story['era'], tl, [i / FPS for i in range(a, min(n, a + per))], enc=enc))
        finally: enc.stdin.close(); enc.wait()
        os.replace(tmp, p); print('piece %d/%d done' % (k + 1, -(-n // per)), flush=True)
    lst = os.path.join(d, 'segs.txt'); open(lst, 'w').write(''.join("file '%s'\n" % os.path.basename(p) for p in parts))
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', vid], check=True)
    for p in parts + [lst]: os.remove(p)

def free_voice():
    """The voice model holds several GB. Once every clip is made, let it go: Chromium (frames) and the mix need that memory
    on an 8 GB machine (15 Nov 2026: a preview was killed while rendering frames with the model still loaded)."""
    if 'turbo' in sys.modules:
        import gc, ctypes, turbo; turbo._model = None; gc.collect()
        try: ctypes.CDLL('libc.so.6').malloc_trim(0)
        except Exception: pass

def finish(story, sid, outdir, tl, clips, cues, moods, chapters, total, rng, vid, t0):
    free_voice()
    # narration
    vo = np.zeros(int((total + 1) * SR), np.float32)
    for s0, a in clips: i = int(s0 * SR); vo[i:i + len(a)] += a[:len(vo) - i]
    vw = os.path.join(outdir, 'voice.wav'); sf.write(vw, vo, SR)
    # music: one piece per chapter mood, crossfaded
    n = int((total + 1) * MSR); mus = np.zeros(n); bounds = moods + [(total + 1, None)]
    for (s0, m), (s1, _) in zip(bounds, bounds[1:]):
        L = s1 - s0 + 2.5
        if story.get('brand') == 'smoke':   # orchestral score (score.py), not the synthesizer pads
            import score; seg = score.render(m, L, story.get('musicEra', 'modern'), seed=int(s0)).astype(np.float64); seg /= (np.abs(seg).max() or 1)
        else: seg = mood_music(m, L, rng)
        fade = int(2.0 * MSR); seg[:fade] *= np.linspace(0, 1, fade); seg[-fade:] *= np.linspace(1, 0, fade)
        i = int(max(0, s0 - .5) * MSR); j = min(n, i + len(seg)); mus[i:j] += seg[:j - i] * {'war': 1.0, 'tension': .85, 'clock': .85}.get(m, .75)
    mus = mus * .8 + convolve(mus.astype(np.float32), reverb_ir(2.2, seed=2)) * .3; mus /= (np.abs(mus).max() or 1)
    SMOKE = story.get('brand') == 'smoke'
    mw, xw, irw = (os.path.join(outdir, x) for x in ('music.wav', 'sfx.wav', 'ir.wav')); sf.write(mw, (mus * (.8 if SMOKE else .5)).astype(np.float32), MSR); sf.write(xw, (sfx_track(cues, total, rng) * .55).astype(np.float32), MSR); sf.write(irw, reverb_ir(1.2, seed=11), MSR)
    del mus   # free ~800 MB before the beds track (an 8 GB machine ran out of memory)
    bw = os.path.join(outdir, 'beds.wav'); sf.write(bw, sfx_track(cues, total, rng, beds=True), MSR)
    final = os.path.join(outdir, sid + '.mp4'); tmp = final[:-4] + '.tmp2.mp4'
    flt = ('[1:a]aresample=48000,rubberband=pitch=0.95:formant=preserved,highpass=f=70,lowshelf=g=3:f=170,equalizer=f=420:t=q:w=1:g=-2,equalizer=f=3300:t=q:w=1.2:g=2,'
           'deesser=i=0.4,acompressor=threshold=0.08:ratio=3:attack=8:release=150:makeup=2,asplit=4[dry][wet0][sc][sc2];[wet0][4:a]afir=dry=0:wet=1,volume=0.16[wet];[dry][wet]amix=inputs=2:normalize=0[v];'
           + ('[2:a]equalizer=f=2500:t=q:w=1.4:g=-5,volume=0.065[m];[m][sc]sidechaincompress=threshold=0.03:ratio=4:attack=40:release=900[md];' if SMOKE else '[2:a]volume=0.55[m];[m][sc]sidechaincompress=threshold=0.03:ratio=6:attack=25:release=700[md];') +
           '[3:a]volume=0.85[x];[5:a]volume=1.0[b0];[b0][sc2]sidechaincompress=threshold=0.03:ratio=3:attack=60:release=1200[bd];[md][x][bd][v]amix=inputs=4:duration=first:normalize=0,loudnorm=I=-15:TP=-2:LRA=11,alimiter=limit=0.84:level=false[a]')
    r = subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', vid, '-i', vw, '-i', mw, '-i', xw, '-i', irw, '-i', bw, '-filter_complex', flt, '-map', '0:v', '-map', '[a]', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', tmp], capture_output=True, text=True)
    if r.returncode: sys.exit('mux failed: ' + r.stderr[-800:])
    os.replace(tmp, final)
    for f in (vid, vw, mw, xw, irw, bw): os.remove(f)
    srt(tl['captions'], os.path.join(outdir, sid + '.srt'))
    cover_t = next((e['t'] + 1.5 for e in tl['events'] if e['k'] == 'link' and e.get('war')), total * .4)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(cover_t), '-i', final, '-frames:v', '1', '-q:v', '2', os.path.join(outdir, 'cover.jpg')], check=True)
    dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', final]).decode().strip())
    ch = [('0:00' if i == 0 else '%d:%02d' % (int(s) // 60, int(s) % 60)) + ' ' + name for i, (s, name) in enumerate(chapters)]
    summ = {'id': sid, 'title': story['title'], 'duration': round(dur, 1), 'chapters': ch, 'sources': story.get('sources', []), 'build_seconds': round(time.time() - t0), 'playlists': story.get('playlists') or ['sb-shorts' if story.get('short') else 'sb-episodes'] if story.get('brand') == 'smoke' else ['history-docs', 'long'], 'brand': story.get('brand', 'flagbomb'), 'file': final, 'srt': os.path.join(outdir, sid + '.srt')}
    if story.get('shorts'): summ['shortCuts'] = short_cuts(story, tl)
    json.dump(summ, open(os.path.join(outdir, 'summary.json'), 'w'), indent=1); print(json.dumps(summ))

def short_cuts(story, tl, most=57.5):
    """Where to cut the episode's Shorts (owner, 11 Nov 2026: Short 1 = where the story starts, Short 2 = a special moment).
    story["shorts"] = [{"from": "<first words of a beat>" (default: the very start), "head": "LINE 1|LINE 2", "title": "..."}, ...].
    Each cut starts half a second before that beat and ends on the last caption that finishes within ~57 s."""
    out = []
    for n, sh in enumerate(story['shorts'], 1):
        key = norm(sh.get('from', '')[:40]); st = 0.6
        if key: st = next((bt for bt, say in tl['beats'] if norm(say[:len(sh['from'][:40]) + 5]).startswith(key)), None)
        if st is None: print('  SHORT %d: no beat starts with "%s"' % (n, sh['from']), file=sys.stderr); continue
        st = max(0, st - .5); ends = [c['t1'] for c in tl['captions'] if st < c['t1'] <= st + most and re.search(r'[.?!…]["”]?$', c['words'][-1]['w'])]
        out.append({'n': n, 'start': round(st, 2), 'length': round((max(ends) if ends else st + 45) - st + .6, 2), 'head': sh.get('head', ''), 'title': sh.get('title', '')})
    return out

if __name__ == '__main__':
    main()
