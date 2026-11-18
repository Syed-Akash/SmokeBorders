"""WW2: storyboard-sheet fixes after ww2_fix.py + ww2_talk.py (storysheet.py marked these as the same picture as an earlier shot).
Matched by the first words of the beat, so it is safe to run again."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from lib import *
from ww2_people import who
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../studio/doc/stories/sb-ww2-both-sides.json'); s = json.load(open(F))
NEW = {
 # the Navy photo's stand-in is the New York harbour: this question gets the recruiting office instead
 "How does Hitler's own nephew end up": S('day', room('us', .7, False, '#4a5a5a'), table(.6, 0, 5), flagpole('us', .85, .7, 300),
     people(who('WPHN', x=.35, facing=1, h=.88), who('USOFF', x=.66, facing=-1, h=.85, pose='point'), lx=.5, ly=.55)),
 'On the fourteenth of June, German troops march into Paris': S('dawn', town(12, .72, 210, 140, '#4a4440'), soldiers(18, '#5a5e5a', 3, 0, 80, .88, True), flagpole('de', .8, .7, 360)),
 'Now the other side. For Soviet soldiers and families': S('night', town(9, .74, 150, 160, '#1d1612'), land('snow', .82), fire(.7, .7, 220),
     people(who('SOVSOL', x=.3, facing=1, h=.85, pose='rifle'), who('LIVW', x=.55, facing=-1, h=.78), lx=.4, ly=.6), fx=['snow']),
 # the Holocaust: plain cards, never a drawn camp with campfires
 'Extermination camps such as Auschwitz': C('AUSCHWITZ-BIRKENAU', 'GERMAN-OCCUPIED POLAND', 'extermination camp', size=120),
 'There is no other side to this': C('NO OTHER SIDE', '', '', size=150),
 # Long Island is flat: a street of houses, the home laboratory, the family; and a real cemetery for the burial
 'He settles in Patchogue, on Long Island': S('day', town(7, .76, 130, 210, '#6a5a4a'), land('grass', .84), people(who('WPH', x=.3, facing=1, h=.85, walk=[.15, .32, 0, 4]), lx=.3, ly=.6)),
 'He calls it Brookhaven Laboratories': S('day', room('us', .6, False, '#e0d8c8'), table(.7, 0, 6), people(who('WPH', x=.42, facing=1, h=.85, pose='hold'), lx=.42, ly=.55)),
 'He and Phyllis have four sons': S('dusk', town(6, .76, 130, 230, '#5a4a3a'), land('grass', .84), people(who('WPH', x=.3, facing=1, h=.85), who('LIVW', x=.45, facing=-1, h=.8), who('BOY', x=.6, facing=-1, h=.5), lx=.45, ly=.6)),
 'He is buried at Holy Sepulchre Cemetery': S('dusk', land('grass', .74), forest(.66, 18, 61, 140), graves(), fx=['fog']),
 'His uncle left behind a continent of ruins and graves': S('dusk', town(12, .7, 150, 130, '#2a2420'), land('grass', .74), graves(rows=3, n=11, y=.8), fx=['smoke']),
 'Count the dead side by side': S('dusk', land('grass', .72), hills(.6, 2, 71), graves(4, 12, .74), fx=['fog']),
 'About three in every hundred people alive in 1940': S('night', town(12, .72, 170, 130, '#1d1612'), graves(3, 10, .8, '#6a665e'), fx=['smoke']),
 'About five thousand ships.': S('day', sea(.6), ships(7, 'us', .1, .66, .35, 150, True), fx=['smoke']),
 'By nightfall, at least ten thousand Allied soldiers': S('night', sea(.64), land('sand', .8), ships(2, 'uk', .7, .68, .4, 300, True), fx=['smoke']),
 "He says the war has developed, quote": S('day', room('jp', .6, False, '#5a4a3a'), table(.5, 0, 0),
     people(who('JPCIV', x=.3, facing=1, h=.82), who('LIVW', x=.6, facing=-1, h=.78, spec={'hair': '#1a1a1a', 'skin': '#e8c49a', 'coat': '#4a3a4a'}), lx=.45, ly=.55)),
}
done = set()
# the two 1939 articles: plain documents with their real wording, no made-up masthead (the renderer's default paper name is invented)
for c in [s['intro']] + s['chapters']:
    for b in c['beats']:
        sc = b.get('scene') or {}
        if sc.get('kind') == 'newspaper' and sc.get('header') == '~ 1939 ~': sc.update(kind='letter', header='The Times, 1939', stamp='HIS WORDS')
        if sc.get('kind') == 'newspaper' and sc.get('header') == '~ LOOK ~': sc.update(kind='letter', header='Look magazine, 1939')
for c in [s['intro']] + s['chapters']:
    for b in c['beats']:
        for k, sc in NEW.items():
            if b.get('say', '').startswith(k): b['scene'] = sc; done.add(k)
assert done == set(NEW), set(NEW) - done
def soviet(x):   # 1940s: the Soviet red flag, never today's Russian tricolour
    if isinstance(x, dict):
        if x.get('flag') == 'ru': x['flag'] = 'red'
        for v in x.values(): soviet(v)
    elif isinstance(x, list):
        for v in x: soviet(v)
soviet(s)
# the Soviet soldier's line about Moscow's midnight is set in Berlin, not in London
for c in s['chapters']:
    for b in c['beats']:
        if b.get('talk') and b['talk'][0]['text'] == "It's over!":
            b['bg'] = S('night', town(11, .73, 190, 140, '#2a2622'), crowd(50, .96), flagpole('red', .78, .72, 340), fx=['smoke'])
def modern(x):   # every ship in this story is a 1930s-40s steel ship, never a sailing warship
    if isinstance(x, dict):
        if x.get('type') == 'ships': x['modern'] = True; x.pop('sails', None)
        for v in x.values(): modern(v)
    elif isinstance(x, list):
        for v in x: modern(v)
modern(s)
# again: no composition more than twice (the new shots above can collide with older ones)
import collections
st = collections.Counter(); LIGHT = ['day', 'dusk', 'dawn', 'night']; WALLS = ['#5a4a3a', '#3a4a4a', '#4a3a44', '#6a5a44', '#2e3a4a', '#4a4a3a']
sig = lambda e: (e.get('time'),) + tuple(sorted((p.get('type'), p.get('seed'), p.get('kind'), p.get('flag'), p.get('n')) for p in e.get('parts') or [] if p.get('type') not in ('actors', 'people')))
for c in [s['intro']] + s['chapters']:
    for b in c['beats']:
        for sp in [b.get('scene')] + [d.get('scene') for d in b.get('do', [])]:
            if not isinstance(sp, dict) or sp.get('shot') != 'set': continue
            k = 0
            while st[sig(sp)] >= 2 and k < 16:
                k += 1
                for p in sp['parts']:
                    if p.get('type') == 'room': p['seed'] = (p.get('seed') or 0) + 1; p['wall'] = WALLS[p['seed'] % len(WALLS)]
                    if p.get('type') in ('hills', 'forest'): p['seed'] = (p.get('seed') or 1) + 7
                if k % 3 == 0: sp['time'] = LIGHT[(LIGHT.index(sp.get('time', 'day')) + 1) % 4] if sp.get('time') in LIGHT else 'day'
            st[sig(sp)] += 1
json.dump(s, open(F, 'w'), indent=1, ensure_ascii=False); print('fixed', len(done))
