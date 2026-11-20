import sys, json, os
sys.path.insert(0, 'smoke'); import make_thumb_sb as T
s = json.load(open('studio/doc/stories/sb-vice-city.json')); base = dict(s['thumb'])
M = lambda **k: dict({'era': '1994', 'center': [-80.2, 25.79], 'scale': 15000, 'cx': .3, 'cy': .5, 'detail': True, 'seed': 80, 'hl': [],
                      'labels': [[-80.19, 25.77, 'MIAMI']]}, **k)
C, R = {'portrait': 'smoke/portraits/castro.png'}, {'portrait': 'smoke/portraits/reagan.png'}
G = {'portrait': 'smoke/portraits/owner-vc-char.png'}
V = {
 'v1': dict(base, layout='spotlight', map=M(neon=True), dread=0, anchor=G, hidden=C, hook=['THE REAL', 'VICE CITY'], hi='VICE CITY', topic='MIAMI · 1980'),
 'v2': dict(base, layout='circled', map=M(neon=True), dread=0, anchor=G, hidden=C, hook=['THE REAL STORY'], hi='REAL', topic='MIAMI · 1980'),
 'v3': dict(base, layout='versus', map=M(neon=True, cx=.5), dread=0, anchor=G, hidden=C, hook=['GAME vs REALITY'], hi='REALITY', topic='MIAMI · 1980'),
 'v4': dict(base, layout='spotlight', map=M(neon=True), dread=1, anchor=C, hidden=G, hook=['125,000', 'IN ONE SUMMER'], hi='125,000', topic='MIAMI · 1980'),
}
for k, sp in V.items(): T.make('sb-vice-city', '/tmp/vc/thumbg-%s.jpg' % k, sp)
