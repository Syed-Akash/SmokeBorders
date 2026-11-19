# Korea FILM CHECK fixes (19 Nov 2026): cast every drawn person, no photo or set more than twice, 30+ acted scenes.
# Run after korea_talk.py: python3 tools/storyboard/korea_fix.py
import json, os, copy
F = os.path.join(os.path.dirname(__file__), '..', '..', 'studio', 'doc', 'stories', 'sb-korea-38th.json')
s = json.load(open(F))
secs = [s['intro']] + s['chapters']

def shots():   # every scene in play order: the beat's own scene, then its on-word scenes
    for ci, c in enumerate(secs):
        for b in c['beats']:
            for h in [b] + b.get('do', []):
                if isinstance(h.get('scene'), dict):
                    yield ci, b, h, 'scene'
                    if isinstance(h['scene'].get('fallback'), dict): yield ci, b, h['scene'], 'fallback'   # plays while a photo is missing

# who each archival portrait shows, as a drawn name-plate shot for its 3rd+ appearance
FACE = {'rhee': ('rhee', 'SYNGMAN RHEE', 'the exile'), 'kim': ('kim', 'KIM IL SUNG', 'the guerrilla'),
        'rusk': ('us_officer', 'DEAN RUSK', 'the colonel with the pencil'), 'bonesteel': ('us_officer', 'CHARLES BONESTEEL', 'the other colonel'),
        'hodge': ('us_officer', 'GEN. JOHN HODGE', 'the American commander'), 'cho': ('korean', 'CHO MAN-SIK', 'the "Gandhi of Korea"')}
def faces(k):
    p, n, sub = FACE[k]
    return {"shot": "faces", "names": [[n, sub]], "nameAt": .4, "push": .06, "people": [{"preset": p, "x": .5}]}
def troops(col, seed, time='day', fx=None):
    d = {"shot": "set", "time": time, "parts": [{"type": "hills", "y": .5, "n": 3, "seed": seed, "depth": .15},
         {"type": "land", "kind": "grass", "y": .74, "depth": .6},
         {"type": "soldiers", "y": .86, "n": 18, "rows": 3, "x0": 0, "gap": 75, "col": col, "march": True, "depth": .7}]}
    if fx: d['fx'] = fx
    return d
ALT = {'soviets45': lambda i: troops('#3c4a34', 40 + i, 'day', ['dust']),
       'dmz': lambda i: dict(troops('#34465a', 60 + i, 'dusk', ['fog']), parts=[{"type": "hills", "y": .5, "n": 3, "seed": 60 + i, "depth": .15},
             {"type": "forest", "y": .62, "n": 60, "seed": 60 + i, "h": 180, "depth": .4}, {"type": "land", "kind": "grass", "y": .76, "depth": .6}])}

# 1. photos: at most twice each
seen = {}
for ci, b, holder, key in shots():
    sc = holder[key]
    if sc.get('shot') != 'photo': continue
    k = sc['img']; seen[k] = seen.get(k, 0) + 1
    if seen[k] > 2:
        holder[key] = faces(k) if k in FACE else ALT[k](seen[k]) if k in ALT else sc

# 2. cast every drawn person: Washington rooms -> US officers, Moscow/Soviet rooms -> Soviet officers, everywhere else Koreans
US_CH = {0, 2, 3}   # intro, Eight Days in August, A Line on a Magazine Map: the Pentagon
for ci, b, holder, key in shots():
    sc = holder[key]
    if sc.get('shot') != 'set': continue
    flags = {p.get('flag') for p in sc['parts'] if p.get('type') in ('room', 'flagpole')}
    room = any(p.get('type') == 'room' for p in sc['parts'])
    pre = 'soviet_officer' if 'ru' in flags else 'us_officer' if ('us' in flags or (room and ci in US_CH)) else 'korean'
    for p in sc['parts']:
        if p.get('type') in ('people', 'actors') and not p.get('preset'):
            for q in p.get('list', []):
                if not q.get('preset') and not q.get('photo'): q['preset'] = pre if pre != 'us_officer' else 'us_officer'
                if pre == 'us_officer' and room: q.setdefault('spec', {'hat': 'none'})
                if 'jp' in flags: q['preset'] = 'civilian'; q['spec'] = {'skin': '#efc49c', 'hair': '#1c1a1a'}   # Japanese officials, in suits

# 3. no illustrated composition more than twice: later copies get other hills / another time of day
sig = lambda e: (e.get('time'),) + tuple(sorted((p.get('type'), p.get('seed'), p.get('kind'), p.get('flag'), p.get('n')) for p in e.get('parts') or [] if p.get('type') not in ('actors', 'people')))
TIMES = ['day', 'dusk', 'night', 'dawn']
for ci, b, holder, key in shots():   # the Pentagon rooms get the American flag on the wall
    sc = holder[key]
    if ci in US_CH and sc.get('shot') == 'set':
        for p in sc['parts']:
            if p.get('type') == 'room' and not p.get('flag'): p['flag'] = 'us'
    if 'Moscow' in b.get('say', '') and sc.get('shot') == 'set':   # the Moscow conference rooms: the Soviet flag
        for p in sc['parts']:
            if p.get('type') == 'room' and not p.get('flag'): p['flag'] = 'ru'
cnt = {}
def place(sc, tm):
    sc['time'] = tm
    for p in sc['parts']:
        if p.get('type') == 'room': p['night'] = tm == 'night'
        if p.get('type') == 'table': p['candles'] = 2 if tm == 'night' else 0
for ci, b, holder, key in shots():
    sc = holder[key]
    if sc.get('shot') != 'set': continue
    if cnt.get(sig(sc), 0) >= 2:
        hills = [p for p in sc['parts'] if p.get('type') in ('hills', 'forest')]
        if hills:
            while cnt.get(sig(sc), 0) >= 2: hills[0]['seed'] = (hills[0].get('seed') or 0) + 101
        else:
            room = next((p for p in sc['parts'] if p.get('type') == 'room'), None)
            side = 'us' if ci < 2 or ci == 8 else 'ru'   # the side in charge of this chapter's talks
            flags = [room.get('flag') if room is not None else None] + ([side] if room is not None and not room.get('flag') else [])
            for fl, tm in [(fl, tm) for fl in flags for tm in TIMES]:
                if room is not None: room['flag'] = fl
                if cnt.get(sig(dict(sc, time=tm)), 0) < 2: place(sc, tm); break
    cnt[sig(sc)] = cnt.get(sig(sc), 0) + 1

# 4. acted scenes (STYLE.md 2d wants 30+): put people into the Korean village and town shots that have none
acted = sum(1 for *_, h, k in shots() if h[k].get('shot') == 'set' and any(p.get('type') in ('people', 'actors') for p in h[k]['parts']))
POSES = ['point', None, 'think', None]
for ci, b, holder, key in shots():
    if acted >= 35: break
    sc = holder[key]
    if sc.get('shot') != 'set' or any(p.get('type') in ('people', 'actors', 'soldiers', 'crowd', 'room') for p in sc['parts']): continue
    if not any(p.get('type') in ('farm', 'town') for p in sc['parts']): continue
    i = acted % 4
    who = [dict(x=.36, facing=1, h=.85, preset='korean'), dict(x=.62, facing=-1, h=.82, preset='woman',
           spec={"hair": "#1c1a1a", "skin": "#efc49c", "coat": "#e8e2d4"})]
    if POSES[i]: who[0]['pose'] = POSES[i]
    sc['parts'].append({"type": "people", "list": who, "lx": .4, "ly": .6, "depth": .85}); acted += 1

json.dump(s, open(F, 'w'), indent=1, ensure_ascii=False)
print('photos', seen, '| acted scenes', acted)
