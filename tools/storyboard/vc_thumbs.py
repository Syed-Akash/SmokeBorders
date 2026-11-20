import sys, json, os
sys.path.insert(0, 'smoke'); import make_thumb_sb as T
s = json.load(open('studio/doc/stories/sb-vice-city.json')); base = dict(s['thumb'])
M = lambda **k: dict({'era': '1994', 'center': [-80.12, 25.78], 'scale': 30000, 'cx': .42, 'cy': .52, 'detail': True, 'seed': 80, 'hl': [],
                      'labels': [[-80.19, 25.77, 'MIAMI']]}, **k)
C, R = {'portrait': 'smoke/portraits/castro.png'}, {'portrait': 'smoke/portraits/reagan.png'}
V = {
 'v1': dict(base, layout='spotlight', map=M(neon=True, cx=.3), dread=0, hidden=C, hook=['THE REAL', 'VICE CITY'], hi='VICE CITY', topic='MIAMI · 1980'),
 'v2': dict(base, layout='circled', map=M(neon=True), anchor=R, hidden=C, hook=['HE OPENED THE DOOR'], hi='DOOR', topic='MIAMI · 1980', dread=0),
 'v3': dict(base, layout='dossier', map=M(neon=True, scale=26000, cx=.3), hidden=C, hook=['THE REAL', 'VICE CITY'], hi='VICE CITY', caption='Fidel Castro, 1959', stamp='UNTOLD STORY', topic='MIAMI · 1980', dread=0),
 'v4': dict(base, layout='spotlight', map=M(neon=True, scale=30000, cx=.3), anchor=R, hidden=C, hook=['125,000', 'IN ONE SUMMER'], hi='125,000', topic='MIAMI · 1980'),
}
for k, sp in V.items(): T.make('sb-vice-city', '/tmp/vc/thumb-%s.jpg' % k, sp)
