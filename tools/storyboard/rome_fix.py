"""Rome vs Carthage redo: FILM CHECK fixes (STYLE.md 2e, owner 15 Nov 2026). Run after rome_talk.py.
- every drawn person in a set gets a fitting preset (Roman legionary or senator, Carthaginian, Carthaginian woman), read from
  the beat's words;
- no photo more than twice: later uses rotate through more archival pictures of the same subject from Commons;
- no illustrated composition more than twice: later copies get a new layout (another seed, more or fewer houses/ships)
  and a different light;
- chapter 1 stays on the harbour photo past its title card (the map comes in on "Tunisia").
Safe to run again."""
import json, os, re, collections, copy
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../studio/doc/stories/sb-rome-carthage.json'); s = json.load(open(F))
MORE = {   # name: [Commons search words, flat]
 'han2': ['Hannibal Barca statue Slodtz Louvre', False], 'han3': ['Hannibal Barcid coin Carthage shekel', True],
 'han4': ['Hannibal crossing the Rhone Henri Motte', True], 'han5': ['Hannibal swears eternal enmity to Rome Amigoni', True],
 'sci2': ['Continence of Scipio painting', True], 'sci3': ['Scipio Africanus statue', False],
 'ruins2': ['Carthage Antonine Baths ruins', True], 'ruins3': ['Carthage Punic quarter Byrsa hill excavation', True],
}
ROT = {'hannibal': ['hannibal', 'han2', 'han3', 'han4', 'han5'], 'scipio': ['scipio', 'sci2', 'sci3'], 'ruins': ['ruins', 'ruins2', 'ruins3']}
s['photos'].update(MORE)
TOGA = {'hat': 'none', 'coat': '#e9e2d0', 'coat2': '#9e1b2a'}
CARW = re.compile(r'Carthag|Hannibal|Hamilcar|Hasdrubal|Barca|Xanthippus|Punic|Mamertine|mercenar|Dido|Tyre|Numidian|Masinissa', re.I)
ROMW = re.compile(r'Rom|Scipio|Cato|consul|legion|Fabius|Regulus|Pulcher|Flaminius|Senate|senator|Paullus|Varro|Polybius', re.I)
def cast_people(sp, say, room):
    for p in sp.get('parts') or []:
        if p.get('type') not in ('people', 'actors') or p.get('preset'): continue
        for j, q in enumerate(p.get('list', [])):
            if q.get('preset') or q.get('photo'): continue
            c, r = bool(CARW.search(say)), bool(ROMW.search(say))
            if re.search(r'queen|Dido|wife', say, re.I) and j == 0: q['preset'] = 'carthaginian_woman'; continue
            side = 'carthaginian' if (c and not r) or (c and r and j % 2 == 0) else 'roman' if r else ('carthaginian' if j % 2 == 0 else 'roman')
            q['preset'] = side
            if side == 'roman' and room: q['spec'] = dict(TOGA)
            if side == 'carthaginian' and room: q['spec'] = {'hat': 'none'}
def shots():   # every scene in story order, with the words it plays under
    for c in [s['intro']] + s['chapters']:
        for b in c['beats']:
            say = b.get('say', '')
            if isinstance(b.get('scene'), dict): yield b['scene'], say
            for d in b.get('do', []):
                if isinstance(d.get('scene'), dict): yield d['scene'], say
ph = collections.Counter(); st = collections.Counter()
sig = lambda e: (e.get('time'),) + tuple(sorted((p.get('type'), p.get('seed'), p.get('kind'), p.get('flag'), p.get('n')) for p in e.get('parts') or [] if p.get('type') not in ('actors', 'people')))
LIGHT = ['day', 'dusk', 'dawn', 'night']
for sp, say in shots():
    for e in [sp] + ([sp['fallback']] if isinstance(sp.get('fallback'), dict) else []):
        if e.get('shot') == 'set': cast_people(e, say, any(p.get('type') == 'room' for p in e.get('parts') or []))
    if sp.get('shot') == 'photo':
        base = next((k for k, v in ROT.items() if sp.get('img') in v), None)
        if base:
            for name in ROT[base]:
                if ph[name] < 2: sp['img'] = name; break
            if sp['img'] != base: sp.pop('caption', None)
        ph[sp['img']] += 1
    if sp.get('shot') == 'set':
        k = 0
        while st[sig(sp)] >= 2 and k < 12:   # a new layout, not the same picture again
            k += 1
            for p in sp['parts']:
                if 'seed' in p: p['seed'] = (p['seed'] or 0) + 7
                if p.get('type') in ('town', 'ships', 'soldiers', 'crowd') and p.get('n'): p['n'] = max(2, p['n'] + (2 if k % 2 else -1))
            if k % 3 == 0: sp['time'] = LIGHT[(LIGHT.index(sp.get('time', 'day')) + 1) % 4] if sp.get('time') in LIGHT else 'day'
        st[sig(sp)] += 1
# chapter 1: hold the harbour photo past the title card
b0 = s['chapters'][0]['beats'][0]
for d in b0.get('do', []):
    if d.get('on') == 'coast' and d.get('scene', {}).get('shot') == 'off': d['on'] = 'Tunisia'
json.dump(s, open(F, 'w'), indent=1, ensure_ascii=False)
print('photos', dict(ph)); print('max set repeats', max(st.values()))
# the spoken chapter title pushed the first shot past 6 s; a shorter title fixes it
s = json.load(open(F)); s['chapters'][0]['title'] = 'A Fight Over Sicily'; json.dump(s, open(F, 'w'), indent=1, ensure_ascii=False)
# STYLE.md 2d: 30+ acted scenes. Outdoor scenes with soldiers, camps or towns get a commander or two acting in front.
s = json.load(open(F)); added = sum(1 for sp, _ in shots() for p in sp.get('parts') or [] if p.get('_fix'))
POSES = ['point', None, 'lean', 'point', None]
for sp, say in shots():
    if added >= 12: break
    parts = sp.get('parts') or []
    if sp.get('shot') != 'set' or any(p.get('type') in ('people', 'actors') for p in parts): continue
    if not any(p.get('type') in ('soldiers', 'camp', 'town', 'ships', 'farm') for p in parts): continue
    if re.search(r'died|killed|slave|drown|flames|children', say, re.I): continue   # no figures acting over the dead
    pose = POSES[added % len(POSES)]
    lst = [dict(x=.28, facing=1, h=.85, **({'pose': pose} if pose else {}))]
    if added % 2: lst.append(dict(x=.72, facing=-1, h=.8))
    parts.append(dict(type='people', list=lst, lx=.4, ly=.6, depth=.85, _fix=1)); cast_people(sp, say, False); added += 1
json.dump(s, open(F, 'w'), indent=1, ensure_ascii=False); print('acted scenes added', added)
