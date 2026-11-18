"""Compact storyboard helpers: shots per beat -> story JSON (film style, STYLE.md 2b)."""
import json, copy, re
def P(img, cap=None, move='in', **k): return dict(shot='photo', img=img, move=move, **({'caption': cap} if cap else {}), **k)
def D(lines, header='', kind='letter', **k): return dict(shot='doc', kind=kind, header=header, lines=lines if isinstance(lines, list) else [lines], **k)
def NEWS(paper, head, date='', **k): return dict(shot='doc', kind='newspaper', paper=paper, head=head if isinstance(head, list) else [head], date=date, **k)
def C(time, place='', date='', **k): return dict(shot='card', time=time, place=place, date=date, **k)
def S(time, *parts, **k): return dict(shot='set', time=time, parts=list(parts), **k)
OFF = {'shot': 'off'}
# parts
def hills(y=.56, n=3, seed=1, d=.2): return dict(type='hills', y=y, n=n, seed=seed, depth=d)
def land(kind='grass', y=.7, d=.6): return dict(type='land', kind=kind, y=y, depth=d)
def forest(y=.64, n=50, seed=3, h=160, d=.45): return dict(type='forest', y=y, n=n, seed=seed, h=h, depth=d)
def sea(y=.6, d=.3): return dict(type='sea', y=y, depth=d)
def coast(x0=.55, x1=1.1, y=.6, h=90, d=.3): return dict(type='coast', x0=x0, x1=x1, y=y, h=h, depth=d)
def ships(n=3, flag='uk', x=.4, y=.66, s=.55, gap=300, steam=False, d=.5): return dict(type='ships', n=n, x=x, s=s, flag=flag, y=y, gap=gap, steam=steam, depth=d)
def town(n=14, y=.75, h=160, gap=140, col='#3a3028', d=.4): return dict(type='town', y=y, n=n, gap=gap, h=h, col=col, depth=d)
def fort(flag='uk', x=.5, y=.72, w=760, h=110, d=.6): return dict(type='fort', x=x, y=y, w=w, h=h, flag=flag, depth=d)
def camp(n=7, y=.76, x0=.05, gap=200, col='#e8e0c8', fire=.45, d=.6): return dict(type='camp', y=y, n=n, x0=x0, gap=gap, col=col, fire=fire, depth=d)
def soldiers(n=16, col='#8b1a1a', rows=3, x0=0, gap=80, y=.86, march=True, d=.7): return dict(type='soldiers', y=y, n=n, rows=rows, x0=x0, gap=gap, col=col, march=march, depth=d)
def cannons(n=3, x0=.25, gap=280, y=.8, d=.7): return dict(type='cannons', y=y, n=n, x0=x0, gap=gap, depth=d)
def crowd(n=90, y=.95, hats=True, d=.8): return dict(type='crowd', y=y, n=n, hats=hats, depth=d)
def farm(x=.78, s=.7, y=.7, night=False, d=.6): return dict(type='farm', x=x, s=s, y=y, night=night, depth=d)
def animal(kind='sheep', x=.45, s=.9, y=.86, walk=True, facing=1, d=.8): return dict(type='animal', kind=kind, x=x, s=s, y=y, walk=walk, facing=facing, depth=d)
def flagpole(flag='uk', x=.5, y=.78, h=420, d=.5): return dict(type='flagpole', x=x, y=y, flag=flag, h=h, depth=d)
def fire(x=.6, y=.62, r=240, d=.4): return dict(type='fire', x=x, y=y, r=r, depth=d)
def room(flag=None, window=.1, night=False, wall=None, d=.3): return dict(type='room', flag=flag, window=window, night=night, depth=d, **({'wall': wall} if wall else {}))
def table(lamp=.6, candles=0, papers=5, w=900, d=.6): return dict(type='table', lamp=lamp, candles=candles, papers=papers, w=w, depth=d)
def people(*lst, lx=.4, ly=.6, d=.85): return dict(type='people', list=list(lst), lx=lx, ly=ly, depth=d)
def man(x, pose=None, facing=1, h=.9, hat=None, photo=None, y=None):
    q = dict(x=x, facing=facing, h=h)
    if pose: q['pose'] = pose
    if hat: q['hat'] = hat
    if photo: q['photo'] = photo
    if y: q['y'] = y
    return q

def variant(sp):
    """A second angle on the same shot, for long beats: a punch-in (a real cut, never one held shot over 20 s)."""
    v = copy.deepcopy(sp)
    if v['shot'] == 'photo': v['move'] = {'in': 'out', 'out': 'in', 'left': 'right', 'right': 'left'}.get(v.get('move', 'in'), 'in'); v.pop('caption', None); v['focus'] = v.get('focus', [.6, .4])
    elif v['shot'] == 'set': v['push'] = .2; v['pan'] = [-120, 20]
    else: return None
    return v

def apply(story, board, rate=2.6, split=13.5):
    """board: {beat index: shot or [shot, (word, shot), ...]}. Beats without an entry keep the shot already running."""
    ch = ([story['intro']] if story.get('intro') else []) + story['chapters']; beats = [b for c in ch for b in c['beats']]
    for b in beats:   # clear an older storyboard
        b.pop('scene', None); b['do'] = [a for a in b.get('do', []) if 'scene' not in a]
    for i, shots in board.items():
        b = beats[i]; shots = shots if isinstance(shots, list) else [shots]
        b['scene'] = shots[0]
        extra = [s for s in shots[1:]]
        sec = len(b.get('say', '').split()) / rate
        if not extra and sec > split:
            v = variant(shots[0])
            if v:
                ws = b['say'].split(); mid = ws[len(ws) // 2:]; w = next((x for x in mid if len(re.sub(r'\W', '', x)) > 3), mid[0])
                extra = [(re.sub(r'[^\w\']', '', w), v)]
        for w, sp in extra:
            assert re.search(r'\b' + re.escape(w.lower()), b['say'].lower()), (i, w)
            b['do'].append({'on': w, 'scene': sp})
    story['film'] = True
    return story

def FACES(*ppl, nameAt=.4, push=.06, **k):
    """drawn characters with name plates (scenes.js 'faces'): FACES(('us_officer', 'COL. DEAN RUSK', 'War Department', 'grim'), ...)"""
    n = len(ppl); xs = [.5] if n == 1 else [.3, .7] if n == 2 else [.2, .5, .8]
    return dict(shot='faces', names=[[p[1], p[2]] for p in ppl], nameAt=nameAt, push=push,
                people=[dict(preset=p[0], x=xs[i], **({'mood': p[3]} if len(p) > 3 else {})) for i, p in enumerate(ppl)], **k)

def finish(story, photos, stand):
    """photos: {name: (Commons file or search words, flat)} -> story['photos'] (the daily run fetches what is missing);
    stand: {name: shot}: every photo shot gets that stand-in as its fallback (plays if the photo is missing)."""
    story['photos'] = {k: [v[0], bool(v[1])] for k, v in photos.items()}
    def walk(x):
        if isinstance(x, dict):
            if x.get('shot') == 'photo' and x.get('img') in stand: x['fallback'] = stand[x['img']]
            for v in list(x.values()): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(story)
    return story

def photolist(path):
    out = {}
    for line in open(path):
        p = line.rstrip('\n').split('\t')
        if len(p) >= 2 and p[0]: out[p[0]] = (p[1], len(p) > 2 and p[2] == 'flat')
    return out
def graves(rows=3, n=9, y=.78, col='#2a2420', d=.7): return dict(type='graves', rows=rows, n=n, y=y, col=col, depth=d)
