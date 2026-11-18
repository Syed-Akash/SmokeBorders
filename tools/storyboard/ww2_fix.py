"""WW2 (sb-ww2-both-sides): FILM CHECK fixes (STYLE.md 2d/2e). Run BEFORE ww2_talk.py (beat numbers are the original ones).
- every drawn person gets a preset that fits who they are and the 1930s-40s (no wigs, no tricorns);
- no photo more than twice: the nephew's Navy photo stays at the start and the end, other uses become acted scenes;
- every photo shot gets an illustrated stand-in (`fallback`), so a photo Wikimedia would not hand out cannot break the render;
- no illustrated composition more than twice (new seed, size or light for later copies);
- the death in the bunker is shown as an empty, closed room, never acted.
Safe to run again only on the original storyboard (git checkout the story first)."""
import json, os, sys, collections, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from lib import *
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../studio/doc/stories/sb-ww2-both-sides.json'); s = json.load(open(F))
B = [s['intro']['beats']] + [c['beats'] for c in s['chapters']]

from ww2_people import PEOPLE, who

# cast per beat (chapter.beat of the original storyboard): one code per drawn person, in order
CAST = {
 (1, 2): ['ALO', 'CIV'], (1, 3): ['ALO', 'COOK'], (1, 7): ['ALO', 'BRID'], (1, 8): ['ALO', 'BRID'], (1, 11): ['LIV', 'LIVW'],
 (1, 14): ['BRID', 'BOY'], (1, 17): ['BOY', 'BRID'],
 (2, 2): ['POLIT', 'POLIT'], (2, 5): ['WPH', 'GERCIV'], (2, 7): ['ALO', 'WPH'], (2, 8): ['WPH'], (2, 9): ['WPH', 'CIV'],
 (2, 10): ['WPH', 'POLICE'], (2, 11): ['WPH', 'AH'], (2, 13): ['AH', 'WPH'], (2, 14): ['WPH'], (2, 15): ['WPH', 'GERCIV'],
 (3, 9): ['CHAM', 'POLIT'], (4, 3): ['GERSOL'], (4, 4): ['GERSOL'], (4, 16): ['GERSOL', 'POLCIV'], (5, 2): ['BRITOFF'],
 (7, 5): ['JPOFF'], (7, 8): ['JPADM', 'JPOFF'], (8, 1): ['WPH'], (8, 2): ['WPH', 'USCLK'], (8, 5): ['WPH'], (8, 12): ['USCLK'],
 (9, 14): ['WPH', 'BRID'], (10, 3): ['WPHN', 'SAILOR'], (10, 6): ['WPHN', 'SAILOR'], (11, 2): ['RAF'], (11, 3): ['USOFF', 'RAF'],
 (12, 1): ['AH', 'GEROFF'], (12, 2): ['AH', 'EVA'], (12, 6): ['GERCIV'], (12, 9): ['GEROFF', 'SOV'], (12, 11): ['ALO', 'TOMMY'],
 (13, 6): ['JPOFF', 'JPOFF'], (13, 7): ['JPOFF', 'JPOFF'], (13, 8): ['JPCIV'], (13, 10): ['JPCIV'], (13, 11): ['JPCIV'],
 (13, 12): ['JPOFF'], (14, 13): ['ALO', 'LIVW'],
}
POSE = {(2, 8): ['hold'], (2, 9): ['point', 'think'], (2, 11): ['point', 'cross'], (2, 13): ['point', 'think'], (2, 14): ['shrug'],
        (8, 1): ['shrug'], (8, 5): ['hold'], (8, 12): ['think'], (10, 3): ['hold', None], (4, 16): ['rifle', None], (12, 11): [None, 'rifle']}
for (ci, bi), codes in CAST.items():
    sc = B[ci][bi]['scene']; pp = next(p for p in sc['parts'] if p['type'] in ('people', 'actors'))
    assert len(pp['list']) == len(codes), ((ci, bi), len(pp['list']))
    for j, q in enumerate(pp['list']):
        c = codes[j]; p, sp = PEOPLE[c]; q['preset'] = p
        if sp: q['spec'] = dict(sp)
        if c == 'BOY': q['h'] = .6
        ps = POSE.get((ci, bi), [])
        if j < len(ps) and ps[j]: q['pose'] = ps[j]
# the bunker, 30 April: an empty room behind a closed door, nobody acted
b = B[12][4]; b['scene'] = S('day', room('de', None, True, '#2a2622'), table(.25, 0, 1), fx=['dust'])

# ---- photos: at most twice; stand-ins for every photo ----
NY_DECK = S('dawn', sea(.64), coast(-.15, .4, .64, 110), ships(1, 'us', .62, .7, .75, 300, True),
            people(who('WPHN', x=.3, facing=1, h=.9), lx=.3, ly=.6))
REPL = {
 (0, 9): NY_DECK,
 (2, 6): S('day', town(12, .74, 200, 130, '#3a3530'), flagpole('de', .78, .74, 380), people(who('WPH', x=.35, facing=1, h=.9, walk=[.15, .4, 0, 4]), lx=.35, ly=.6)),
 (8, 0): S('night', room('us', .2, True), table(.7, 0, 6), people(who('WPH', x=.42, facing=1, h=.85, pose='hold'), lx=.42, ly=.55)),
 (10, 1): S('day', room('us', .7, False, '#5a5044'), table(.6, 0, 9), people(who('USCLK', x=.35, facing=1, h=.85, pose='hold'), who('USOFF', x=.68, facing=-1, h=.85), lx=.5, ly=.55)),
 (10, 2): S('day', room('us', .5, False, '#d8d2c4'), table(.4, 0, 2), people(who('WPHN', x=.4, facing=1, h=.88, pose='hold'), who('SAILOR', x=.7, facing=-1, h=.8), lx=.45, ly=.55)),
 (10, 7): C('HIS CHOICE', 'THE OTHER SIDE', 'U.S. Navy, 1944', size=150),
 (14, 7): S('dusk', sea(.64), coast(.5, 1.1, .62, 100), ships(2, 'us', .3, .68, .55, 380, True), people(who('WPHN', x=.6, facing=-1, h=.85, walk=[.75, .55, 0, 4]), lx=.6, ly=.6)),
}
for (ci, bi), sc in REPL.items(): B[ci][bi]['scene'] = sc
STAND = {
 'wph_navy': NY_DECK, 'potsdam': S('day', town(10, .74, 220, 150, '#4a4038'), crowd(70, .95), flagpole('de', .5, .72)),
 'liverpool': S('dusk', town(10, .76, 160, 150, '#3a3028'), land('grass', .8)),
 'bridget': S('day', room('uk', .6), people(who('BRID', x=.45, facing=1, h=.88), lx=.45, ly=.55)),
 'munich': S('night', room('de', .2, True), table(.6, 0, 6), people(who('POLIT', x=.3), who('POLIT', x=.62, facing=-1), lx=.45, ly=.55)),
 'heston': S('day', land('grass', .74), crowd(50, .96), people(who('CHAM', x=.45, h=.9, pose='hold'), lx=.45, ly=.6)),
 'westerplatte': S('dawn', sea(.62), coast(.45, 1.1, .6, 90), ships(1, 'de', .25, .68, .8, 300, True), fire(.75, .58, 220), fx=['smoke']),
 'dunkirk': S('dusk', sea(.62), ships(4, 'uk', .2, .68, .5, 260, True), land('sand', .8), fx=['smoke']),
 'stpauls': S('night', town(14, .74, 200, 120, '#1d1612'), fire(.6, .66, 300), fx=['smoke', 'embers']),
 'stalingrad': S('dusk', town(12, .72, 180, 140, '#2a2622'), fire(.3, .66, 200), fx=['smoke', 'snow']),
 'arizona': S('day', sea(.62), ships(1, 'us', .5, .68, .9, 300, True), fire(.5, .6, 260), fx=['smoke']),
 'fdr': S('day', room('us', .6, False, '#5a5044'), table(.6, 0, 6), people(who('FDR', x=.45, facing=1, h=.88), lx=.45, ly=.55)),
 'midway': S('day', sea(.62), ships(1, 'jp', .55, .68, .8, 300, True), fire(.55, .6, 200), fx=['smoke']),
 'dday': S('dawn', sea(.66), land('sand', .8), soldiers(14, '#55603a', 2, 0, 90, .86, True), fx=['smoke']),
 'reichstag': S('day', town(10, .72, 220, 160, '#3a3530'), flagpole('ru', .55, .6, 300), fx=['smoke']),
 'hiroshima': S('dawn', hills(.55, 2, 9), town(12, .74, 120, 140, '#3a3028'), fx=['smoke']),
 'hirohito': S('day', room('jp', .5, False, '#4a3a2a'), people(who('HIRO', x=.45, facing=1, h=.88), lx=.45, ly=.55)),
 'surrender': S('day', sea(.6), ships(1, 'us', .5, .7, .9, 300, True), people(who('JPCIV', x=.35, pose='hold'), who('USOFF', x=.65, facing=-1), lx=.5, ly=.6)),
}
def scenes():
    for bs in B:
        for b in bs:
            if isinstance(b.get('scene'), dict): yield b['scene']
            for d in b.get('do', []):
                if isinstance(d.get('scene'), dict): yield d['scene']
ph = collections.Counter(); st = collections.Counter()
sig = lambda e: (e.get('time'),) + tuple(sorted((p.get('type'), p.get('seed'), p.get('kind'), p.get('flag'), p.get('n')) for p in e.get('parts') or [] if p.get('type') not in ('actors', 'people')))
LIGHT = ['day', 'dusk', 'dawn', 'night']
WALLS = ['#5a4a3a', '#3a4a4a', '#4a3a44', '#6a5a44', '#2e3a4a', '#4a4a3a']
for sp in scenes():
    if sp.get('shot') == 'photo':
        ph[sp['img']] += 1
        if sp['img'] in STAND: sp['fallback'] = STAND[sp['img']]
    if sp.get('shot') == 'set':
        k = 0
        while st[sig(sp)] >= 2 and k < 16:   # a new layout, not the same picture again
            k += 1
            for p in sp['parts']:
                if p.get('type') in ('hills', 'forest'): p['seed'] = (p.get('seed') or 1) + 7
                if p.get('type') in ('town', 'ships', 'soldiers', 'crowd', 'camp') and p.get('n'): p['n'] = max(2, p['n'] + (2 if k % 2 else -1))
                if p.get('type') == 'room':   # another room: new wall colour and window
                    p['seed'] = (p.get('seed') or 0) + 1; p['wall'] = WALLS[p['seed'] % len(WALLS)]; p['window'] = [.1, .7, .4, None][p['seed'] % 4]
                if p.get('type') == 'table': p['papers'] = (p.get('papers') or 0) % 9 + 3; p['n'] = p['papers']
            if k % 3 == 0: sp['time'] = LIGHT[(LIGHT.index(sp.get('time', 'day')) + 1) % 4] if sp.get('time') in LIGHT else 'day'
        st[sig(sp)] += 1
json.dump(s, open(F, 'w'), indent=1, ensure_ascii=False)
print('photos', dict(ph)); print('max set repeats', max(st.values()))
