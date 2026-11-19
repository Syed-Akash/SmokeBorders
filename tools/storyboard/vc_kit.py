"""Scene kit for The Real Vice City (sb-vice-city, 19 Nov 2026): Miami sets, varied automatically so no set repeats."""
import itertools
_n = itertools.count(1)
def _s(): return next(_n)
def S(time, *parts, **k): return dict(shot='set', time=time, parts=[p for p in parts if p], **k)
def P(img, cap=None, move='in', **k): return dict(shot='photo', img=img, move=move, **({'caption': cap} if cap else {}), **k)
def D(lines, header='', kind='letter', **k): return dict(shot='doc', kind=kind, header=header, lines=lines if isinstance(lines, list) else [lines], **k)
def NEWS(paper, head, date='', **k): return dict(shot='doc', kind='newspaper', paper=paper, head=head if isinstance(head, list) else [head], date=date, **k)
def C(time, place='', date='', **k): return dict(shot='card', time=time, place=place, date=date, **k)
MAP = {'shot': 'off'}
# parts
def sea(y=.6, d=.3): return dict(type='sea', y=y, depth=d)
def land(kind='grass', y=.72, d=.6): return dict(type='land', kind=kind, y=y, depth=d)
def hills(y=.58, n=2, d=.2): return dict(type='hills', y=y, n=n, seed=_s(), depth=d)
def forest(y=.64, n=50, h=160, d=.45): return dict(type='forest', y=y, n=n, seed=_s(), h=h, depth=d)
def coast(x0=.55, x1=1.1, y=.6, h=70, d=.3): return dict(type='coast', x0=x0, x1=x1, y=y, h=h, depth=d)
def palms(y=.8, n=6, h=420, wind=.15, x0=.04, gap=.16, d=.7): return dict(type='palms', y=y, n=n, h=h, wind=wind, x0=x0, gap=gap, seed=_s(), depth=d)
def city(y=.72, night=True, neon=True, h=360, n=16, d=.4): return dict(type='city', y=y, night=night, neon=neon, h=h, n=n, seed=_s(), depth=d)
def deco(y=.8, night=False, words=None, n=5, d=.45): return dict(type='deco', y=y, night=night, n=n, depth=d, **({'words': words} if words else {}))
def neon(text, x=.5, y=.3, col='255,60,170', size=110, d=.3): return dict(type='neon', text=text, x=x, y=y, col=col, size=size, depth=d)
def boats(n=4, y=.72, x=.12, gap=.22, s=.7, drift=0, crowded=True, d=.6): return dict(type='boats', n=n, y=y, x=x, gap=gap, s=s, drift=drift, crowded=crowded, depth=d)
def car(kind='sedan', x=.5, y=.9, s=.8, drive=None, text=None, col=None, facing=1, d=.8):
    q = dict(type='car', kind=kind, x=x, y=y, s=s, facing=facing, depth=d)
    if drive: q['drive'] = drive
    if text: q['text'] = text
    if col: q['col'] = col
    return q
def bus(x=.5, y=.92, s=.8, drive=None, d=.7): return dict(type='bus', x=x, y=y, s=s, depth=d, **({'drive': drive} if drive else {}))
def fence(y=.86, broken=None, h=220, d=.6): return dict(type='fence', y=y, h=h, depth=d, **({'broken': broken} if broken else {}))
def highway(y=.38, d=.7): return dict(type='highway', y=y, depth=d)
def houses(y=.8, n=6, night=False, d=.5): return dict(type='houses', y=y, n=n, night=night, seed=_s(), depth=d)
def train(y=.8, s=.7, drive=(.1, .9, 0, 7), d=.5): return dict(type='train', y=y, s=s, drive=list(drive), depth=d)
def shop(text, x=.5, y=.82, col=None, sign=None, d=.4): return dict(type='shopfront', text=text, x=x, y=y, depth=d, **({'col': col} if col else {}), **({'signCol': sign} if sign else {}))
def tv(x=.5, y=.5, w=760, d=.5): return dict(type='tv', x=x, y=y, w=w, depth=d)
def town(n=14, y=.75, h=160, gap=140, col='#3a3028', night=False, d=.4): return dict(type='town', y=y, n=n, gap=gap, h=h, col=col, night=night, depth=d)
def camp(n=7, y=.78, x0=.05, gap=200, col='#e8e0c8', fire=None, d=.6): return dict(type='camp', y=y, n=n, x0=x0, gap=gap, col=col, fire=fire, depth=d)
def crowd(n=80, y=.97, hats=False, d=.8): return dict(type='crowd', y=y, n=n, hats=hats, depth=d)
def soldiers(n=10, col='#5a6340', rows=2, x0=.1, gap=90, y=.88, march=True, d=.7): return dict(type='soldiers', y=y, n=n, rows=rows, x0=x0, gap=gap, col=col, march=march, depth=d)
def ships(n=1, flag='us', x=.5, y=.66, s=.5, gap=300, steam=True, d=.5): return dict(type='ships', n=n, x=x, s=s, flag=flag, y=y, gap=gap, steam=steam, depth=d)
def flagpole(flag='us', x=.5, y=.78, h=420, d=.5): return dict(type='flagpole', x=x, y=y, flag=flag, h=h, depth=d)
def fire(x=.6, y=.62, r=240, d=.4): return dict(type='fire', x=x, y=y, r=r, depth=d)
def room(flag=None, window=.1, night=False, wall=None, d=.3): return dict(type='room', flag=flag, window=window, night=night, depth=d, **({'wall': wall} if wall else {}))
def table(lamp=.6, candles=0, papers=5, w=900, d=.6): return dict(type='table', lamp=lamp, candles=candles, papers=papers, w=w, depth=d)
def graves(rows=3, n=9, y=.8, d=.7): return dict(type='graves', rows=rows, n=n, y=y, col='#a8a294', depth=d)
def A(*lst, d=.88):
    """actors: A(('preset', x, pose, {extra}), ...)"""
    out = []
    for a in lst:
        q = dict(preset=a[0], x=a[1], pose=a[2] if len(a) > 2 else 'idle', facing=1 if a[1] < .5 else -1, h=.62, y=.98)
        if len(a) > 3: q.update(a[3])
        out.append(q)
    return dict(type='actors', list=out, depth=d)
