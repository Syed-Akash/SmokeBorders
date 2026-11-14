"""Pig War: characters act out the story in its scenes (owner, 15 Nov 2026: 'like a movie with a story going on')."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from lib import *
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../studio/doc/stories/sb-pig-war.json'); s = json.load(open(F))
def AC(preset, x, pose='idle', facing=1, h=.6, y=.93, **k): return dict(preset=preset, x=x, pose=pose, facing=facing, h=h, y=y, **k)
BLUE, RED = {'coat': '#1f3150'}, None
pig = lambda x=.7, walk=True, facing=-1: animal('pig', x, .8, .9, walk, facing, .8)
farmset = lambda tm='day', *extra: S(tm, hills(.55, 2, 3), land('grass', .74), farm(.8, .7, .72), *extra)
campset = lambda tm='day', *extra: S(tm, hills(.55, 2, 9), land('grass', .74), camp(5, .76, .55, 200, '#e8e0c8', .45), *extra)
room_ = lambda flag, *extra: S('day', room(flag, .7), table(.6, 0, 6), *extra)
deck = lambda *extra: S('day', sea(.6), ships(3, 'uk', .55, .66, .5, 300), coast(-.2, .3, .6, 90), *extra)
CUT, GRF = 'settler', 'hbc_man'
ACT = [   # (first words of the beat, actors, set to use if the beat's shot is not a set)
 ('June the fifteenth, 1859. On a small', [AC(CUT, .3, 'think', walk=[.15, .32, 0, 4]), ], farmset('dusk', pig(.62))),
 ('He picks up his rifle', [AC(CUT, .3, 'aim', mood='angry', act=[[1.4, 'fire']])], farmset('dusk', pig(.72, False))),
 ('Within two months, four hundred', [AC('pickett', .2, 'point', mood='smug', h=.62)], S('day', hills(.5, 2, 4), land('grass', .74), cannons(3, .35, 240), soldiers(14, '#1f3150', 2, .45, 80, .86, False))),
 ('Lyman Cutlar, the American farmer', [AC(CUT, .32, 'hips', talk=False), AC(GRF, .66, 'cross', facing=-1)], farmset('day', pig(.85))),
 ('Lyman Cutlar found a pig in his garden', [AC(CUT, .25, 'idle', mood='shock', act=[[1.2, 'point']])], farmset('day', pig(.6))),
 ('Cutlar had had enough', [AC(CUT, .3, 'aim', mood='angry', act=[[1.0, 'fire']])], farmset('day', pig(.72, False))),
 ('Then he did something decent', [AC(CUT, .2, 'idle', walk=[.12, .42, 0, 3.5], act=[[3.5, 'hold']], prop='coin'), AC(GRF, .7, 'hips', facing=-1)], farmset('day')),
 ('Griffin said no', [AC(CUT, .38, 'shrug', mood='shock'), AC(GRF, .66, 'point', facing=-1, mood='angry', talk=True)], farmset('day')),
 ('Cutlar thought it over', [AC(CUT, .45, 'think', mood='grim', act=[[2.5, 'cross']])], farmset('dusk')),
 ("Now the island's two sides", [AC(GRF, .62, 'point', facing=-1, mood='angry'), AC('rn_officer', .78, 'hips', facing=-1), AC(CUT, .25, 'shrug', mood='shock')], farmset('day')),
 ('To the Americans, that was outrageous', [AC(CUT, .3, 'point', mood='angry', talk=True), AC('settler', .5, 'hips', spec={'hair': '#2a1d12'}), AC('settler', .68, 'cross', facing=-1, spec={'hair': '#8a6a3a'})], S('day', town(10, .72, 140, 150, '#3a3028'), land('grass', .76))),
 ('His name was William Harney', [AC('us_officer', .5, 'hips', mood='grim', h=.66)], room_('us')),
 ('Harney moved fast', [AC('us_officer', .35, 'point', mood='angry', talk=True, h=.64), AC('us_officer', .72, 'idle', facing=-1, spec=BLUE)], room_('us')),
 ('The captain he picked was George Pickett', [AC('pickett', .2, 'idle', walk=[.05, .45, 0, 4], act=[[4, 'hips']], h=.64, mood='smug')], campset('day')),
 ('Now he took about sixty-six men', [AC('pickett', .2, 'point', h=.6, mood='smug')], S('day', sea(.62), ships(1, 'us', .6, .67, .6, 0, True), coast(-.2, .3, .6, 90), soldiers(10, '#1f3150', 2, .3, 70, .86, True))),
 ('Pickett pitched his camp', [AC('pickett', .3, 'point', mood='smug'), AC('us_officer', .45, 'idle', spec=BLUE)], S('day', sea(.62), ships(1, 'uk', .78, .67, .6, 0), land('grass', .74), camp(4, .76, .05, 200, '#e8e0c8', .4))),
 ('When someone pointed this out', [AC('us_officer', .3, 'dig', spec=BLUE), AC('us_officer', .5, 'dig', spec=BLUE, facing=-1), AC('pickett', .75, 'point', facing=-1)], S('day', hills(.5, 2, 4), land('mud', .74), cannons(2, .1, 260))),
 ('Now the British side. Captain Hornby', [AC('rn_officer', .32, 'hips', mood='grim', h=.62)], deck()),
 ('Governor Douglas gave him orders', [AC('douglas', .35, 'point', talk=True), AC('rn_officer', .65, 'idle', facing=-1)], room_('uk')),
 ('Hornby had the guns', [AC('rn_officer', .4, 'think', mood='grim', h=.62)], deck()),
 ('He sailed north, and took one look', [AC('douglas', .3, 'point', mood='angry'), AC('rn_officer', .66, 'cross', facing=-1, spec={'hair': '#d8d4cc'}, mood='grim')], room_('uk')),
 ('In September, Buchanan sent', [AC('us_officer', .3, 'idle', walk=[.1, .45, 0, 4], spec={'hair': '#e8e4dc'}, h=.66)], room_('us')),
 ('By November, they had a deal', [AC('us_officer', .36, 'hold', prop='paper', spec={'hair': '#e8e4dc'}), AC('douglas', .64, 'hold', facing=-1, prop='paper')], room_('uk')),
 ('In 1860, British Royal Marines', [AC('redcoat', .25, 'dig'), AC('redcoat', .45, 'idle', walk=[.6, .45, 0, 3]), AC('redcoat', .7, 'hips', facing=-1)], S('day', sea(.64, .3), coast(.0, .5, .62, 90), land('grass', .74), camp(4, .76, .5, 200, '#e8e0c8', .4))),
 ('The two garrisons visited', [AC('redcoat', .35, 'toast', mood='happy'), AC('us_officer', .62, 'toast', facing=-1, mood='happy', spec=BLUE)], campset('dusk', fire(.5, .8, 200))),
 ('They held sports contests', [AC('redcoat', .2, 'run', walk=[.1, .8, 0, 4]), AC('us_officer', .3, 'run', walk=[.05, .75, .2, 4.2], spec=BLUE), AC('redcoat', .85, 'wave', facing=-1)], S('day', land('grass', .74), hills(.56, 2, 7))),
 ('George Pickett had a choice', [AC('pickett', .5, 'think', mood='grim', act=[[2.5, 'idle']], walk=[.5, .9, 2.5, 7])], campset('dusk')),
 ('Years later, he was asked to run', [AC('us_officer', .5, 'shrug', mood='shock', spec={'hair': '#6b4a2a'}), AC('governor', .25, 'point', mood='angry'), AC('governor', .78, 'cross', facing=-1, spec={'hair': '#9a8a7a'})], S('day', room(None, .7, False, '#3a2a1c'), crowd(40, .99))),
 ('So he wrote them himself', [AC('us_officer', .45, 'hold', prop='paper', mood='happy', spec={'hair': '#6b4a2a'})], S('night', room(None, .1, True), table(.6, 2, 8))),
 ('Neither side trusted the other', [AC('king_george', .5, 'think', spec={'hair': '#e8e4dc', 'beard': 'full'}, h=.66)], S('day', room('de', .7), table(.6, 2, 9))),
 ('Haro Strait. The border would run', [AC('king_george', .45, 'point', spec={'hair': '#e8e4dc', 'beard': 'full'}, mood='smug', talk=True)], S('day', room('de', .7), table(.6, 2, 9))),
 ('Britain accepted it', [AC('redcoat', .3, 'idle', walk=[.3, .95, 0, 6]), AC('redcoat', .15, 'idle', walk=[.15, .85, .4, 6.4]), AC('us_officer', .1, 'wave', spec=BLUE)], S('day', sea(.64, .3), ships(1, 'uk', .8, .68, .6, 0), land('grass', .74))),
 ('And our two neighbours?', [AC(CUT, .3, 'cross', mood='grim'), AC(GRF, .68, 'hips', facing=-1, mood='angry')], farmset('dusk', pig(.5))),
 ('Wars start with small things', [AC(CUT, .4, 'idle', walk=[.4, .1, 2, 9])], farmset('dusk', pig(.75))),
]
beats = [b for c in ([s['intro']] if s.get('intro') else []) + s['chapters'] for b in c['beats']]
n = 0
for pre, acts, alt in ACT:
    b = next((b for b in beats if b.get('say', '').startswith(pre)), None); assert b, pre
    sc = b.get('scene')
    if not sc or sc.get('shot') != 'set': sc = b['scene'] = json.loads(json.dumps(alt)) if alt else sc
    if not sc or sc.get('shot') != 'set': print('no set for', pre); continue
    sc['parts'] = [p for p in sc['parts'] if p.get('type') not in ('people', 'actors')] + [{'type': 'actors', 'list': acts, 'depth': .85}]
    n += 1
json.dump(s, open(F, 'w'), indent=1, ensure_ascii=False); print('acting scenes:', n)
