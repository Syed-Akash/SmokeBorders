# Korea dialogue pass (STYLE.md 2c): acted exchanges, dramatized from the record.
# Real people only say or do what the narration (and its sources) says; jokes and colour go to unnamed roles.
# Run once: python3 tools/storyboard/korea_talk.py   (idempotent: removes earlier "_talk" beats first)
import json, os
F = os.path.join(os.path.dirname(__file__), '..', '..', 'studio', 'doc', 'stories', 'sb-korea-38th.json')
s = json.load(open(F))

def room(flag, night=True, papers=8, window=.1):
    return {"shot": "set", "time": "night" if night else "day", "parts": [
        {"type": "room", "flag": flag, "window": window, "night": night, "depth": .3},
        {"type": "table", "lamp": .5, "candles": 1 if night else 0, "papers": papers, "w": 900, "depth": .6}]}
def village(time='day'):
    return {"shot": "set", "time": time, "parts": [
        {"type": "hills", "y": .5, "n": 3, "seed": 27, "depth": .15},
        {"type": "farm", "x": .3, "s": .7, "y": .72, "night": False, "depth": .6},
        {"type": "farm", "x": .72, "s": .6, "y": .73, "night": False, "depth": .6},
        {"type": "land", "kind": "grass", "y": .76, "depth": .6}]}
def seoul(time='day', crowd=False, flag=None):
    p = [{"type": "hills", "y": .52, "n": 3, "seed": 12, "depth": .15},
         {"type": "town", "y": .74, "n": 16, "gap": 125, "h": 150, "col": "#3a332c", "depth": .4}]
    if flag: p.append({"type": "flagpole", "x": .78, "y": .7, "flag": flag, "h": 360, "depth": .5})
    if crowd: p.append({"type": "crowd", "y": .95, "n": 90, "hats": True, "depth": .8})
    return {"shot": "set", "time": time, "parts": p}
def field(time='day', col='#4b5a3c', fx=None, camp=False):
    p = [{"type": "hills", "y": .5, "n": 3, "seed": 7, "depth": .15},
         {"type": "land", "kind": "grass", "y": .74, "depth": .6}]
    if camp: p.append({"type": "camp", "y": .76, "n": 4, "x0": .3, "gap": 220, "col": "#8a8270", "fire": .4, "depth": .6})
    p.append({"type": "soldiers", "y": .86, "n": 14, "rows": 2, "x0": 0, "gap": 80, "col": col, "march": False, "depth": .7})
    d = {"shot": "set", "time": time, "parts": p}
    if fx: d["fx"] = fx
    return d

US, SOV, ROK = '#4b5a3c', '#3c4a34', '#34465a'
L = lambda who, text, mood=None: dict({"who": who, "text": text}, **({"mood": mood} if mood else {}))

# (section, insert after beat index, lines, bg). section: 'intro' or chapter index 0..10
TALK = [
 ('intro', 2, [L('AIDE', 'Colonels. We need a line across Korea.'), L('AIDE', 'Tonight.', 'tension')], room('us')),
 ('intro', 4, [L('AIDE', 'Is this really the best map we have?'), L('AIDE2', "It's from National Geographic."), L('AIDE', '...So, yes.', 'smug')], room('us')),
 ('intro', 7, [L('FARMER', 'Any news from Seoul?'), L('WIFE', 'Nothing. Same as always.')], village('day')),
 (0, 3, [L('PROT', 'Long live Korean independence!', 'angry'), L('PROT2', "They're arresting everyone!", 'shock')], seoul('day', crowd=True)),
 (0, 6, [L('TEACH', 'In due course. How long is that?'), L('STUD', 'Nobody says.', 'uneasy')], room(None, False, 4, .7)),
 (0, 10, [L('SEOUL', 'Another master? After thirty-five years?', 'angry')], seoul('day')),
 (1, 5, [L('WASH1', 'How far south can the Soviets get?'), L('WASH2', 'All the way. If nobody stops them.', 'tension')], room('us', False, 10, .7)),
 (1, 12, [L('AIDE2', 'Do we ask a Korea expert first?'), L('AIDE', 'No time.'), L('AIDE2', '...Do we have one?', 'uneasy')], room('us')),
 (2, 12, [L('AIDE', 'A thousand years as one country.'), L('AIDE2', 'And one evening to split it.', 'uneasy')], room('us')),
 (3, 0, [L('SOVCLERK', 'The Americans propose the thirty-eighth parallel.'), L('SOVOFF', 'Any objection?'), L('SOVCLERK', 'None.')], room('ru', False, 6, .7)),
 (3, 1, [L('WASH1', 'They said yes?', 'shock'), L('WASH2', 'No argument at all.')], room('us', False, 10, .7)),
 (3, 2, [L('SHOP', 'What is this money?'), L('SOVSOLD', 'Red Army won. Take it.', 'smug')], seoul('day', flag='ru')),
 (3, 7, [L('VIL1', 'They fought Japan here. Let them in.'), L('VIL2', "Let's hope they leave as easily.", 'uneasy')], village('dusk')),
 (4, 0, [L('CROWD1', 'Japan has surrendered!', 'happy'), L('CROWD2', "We're free!", 'happy')], seoul('day', crowd=True)),
 (4, 1, [L('ABE', 'Will you take charge of order in Seoul?'), L('SONG', 'No. I would only be your puppet.')], room(None, False, 6, .7)),
 (4, 3, [L('JPRES', 'A Soviet army is coming by train!', 'shock'), L('JPRES2', 'Pack everything. Now.')], seoul('dusk')),
 (4, 7, [L('GI1', 'So what are our orders for governing, sir?'), L('SGT', "Washington hasn't really sent any.", 'uneasy')], field('day', US, camp=True)),
 (4, 12, [L('WOMAN', 'What does rice cost today?'), L('SELLER', "Don't ask today. Ask tomorrow.", 'sad')], seoul('day')),
 (5, 2, [L('CROWD1', 'Who is he?'), L('CROWD2', 'Kim Il Sung. A guerrilla, they say.'), L('CROWD1', 'He is so young!', 'shock')], seoul('day', crowd=True, flag='ru')),
 (5, 5, [L('FARMER', 'This field is mine now?', 'shock'), L('NKOFF', "Yours. The landlord is gone.", 'happy')], village('day')),
 (5, 6, [L('SOVCLERK', 'How many seats for each party?'), L('SOVOFF', 'Already decided.', 'smug')], room('ru', False, 9, .7)),
 (6, 6, [L('USOFF1', 'What do we make of Rhee?'), L('USOFF2', 'Hard to handle. But he hates communists.')], room('us', False, 6, .7)),
 (7, 2, [L('STUD', 'Five more years of foreigners?', 'angry'), L('STUD2', 'Not one more day!', 'angry')], seoul('day', crowd=True)),
 (7, 6, [L('SOVOFF', 'Sign your support for the trusteeship.'), L('CHO', 'I will not sign.')], room('ru', False, 3, .7)),
 (7, 12, [L('GUARD', 'Permit.'), L('TRAV', 'My mother lives two villages north.', 'sad'), L('GUARD', 'Permit.')], field('day', SOV)),
 (7, 13, [L('SOVDEL', 'Both armies leave. Let Koreans decide.'), L('USDEL', 'And who fills the gap?', 'uneasy')], room(None, False, 8, .7)),
 (8, 2, [L('WORKER', 'Two elections means two countries.'), L('WORKER2', 'Then we strike.', 'angry')], seoul('day')),
 (8, 10, [L('SOUTH', 'We have a country now!', 'happy'), L('NORTH', 'So do we.'), L('SOUTH', '...The same country?', 'uneasy')], village('dusk')),
 (9, 1, [L('ROK1', 'Tanks! Coming from the north!', 'shock'), L('ROK2', 'Fall back to Seoul!', 'war')], field('dawn', ROK, fx=['smoke'])),
 (9, 5, [L('GI1', 'Nothing we have stops those tanks!', 'shock'), L('SGT', 'Hold as long as you can!', 'war')], field('day', US, fx=['smoke'])),
 (9, 11, [L('NEG1', 'Same table. Same arguments.'), L('NEG2', 'See you tomorrow, then.', 'uneasy')], room(None, False, 12, .7)),
 (10, 0, [L('GI1', "So it's over?"), L('GI2', "It's stopped. That's not the same thing.")], field('day', US, camp=True)),
 (10, 10, [L('GI1', "Who's the new general?"), L('GI2', 'Bonesteel. They say he drew this line.'), L('GI1', 'Then he can guard it.', 'smug')], field('day', US, camp=True)),
 (10, 15, [L('ROK1', 'Anything moving out there?'), L('ROK2', 'Just the cranes.')], field('dusk', ROK)),
 (10, 17, [L('OLD', 'Any news about the line?'), L('GRAND', 'Still there, grandfather.', 'sad')], village('dusk')),
]

K = lambda name, spec=None: dict({"preset": "korean", "name": name}, **({"spec": spec} if spec else {}))
CAST = {
 "RUSK": {"preset": "us_officer", "name": "Col. Dean Rusk", "spec": {"hat": "none"}},
 "AIDE": {"preset": "us_officer", "name": "A Pentagon officer", "spec": {"hat": "none", "hair": "#2a1d12"}},
 "AIDE2": {"preset": "us_officer", "name": "Another officer", "spec": {"hat": "none", "hair": "#8a6a3a", "glasses": 1}},
 "WASH1": {"preset": "clerk", "name": "A Washington official"},
 "WASH2": {"preset": "civilian", "name": "Another official"},
 "FARMER": K("A Korean farmer", {"coat": "#d8d1c0", "coat2": "#8a7a5a"}),
 "WIFE": {"preset": "woman", "name": "His wife", "spec": {"coat": "#e8e2d4", "coat2": "#b3202a", "hair": "#1c1a1a", "skin": "#efc49c"}},
 "PROT": K("A protester"), "PROT2": K("Another protester", {"coat2": "#34465a"}),
 "TEACH": K("A teacher", {"coat": "#2b2b33", "glasses": 1}), "STUD": K("A student", {"coat": "#1f2a3a"}),
 "STUD2": K("Another student", {"coat": "#3a3226"}), "SEOUL": K("A man in Seoul", {"coat": "#4a4a52"}),
 "SOVCLERK": {"preset": "clerk", "name": "A Soviet clerk", "spec": {"coat": "#4a5a3a"}},
 "SOVOFF": {"preset": "soviet_officer", "name": "A Soviet officer"},
 "SOVSOLD": {"preset": "soviet_officer", "name": "A Red Army soldier", "spec": {"medal": 0, "epaulettes": 0}},
 "SHOP": K("A shopkeeper", {"coat": "#6a5a44"}), "VIL1": K("A villager"), "VIL2": K("Another villager", {"coat": "#b8a888"}),
 "CROWD1": K("A man in the crowd"), "CROWD2": {"preset": "woman", "name": "A woman in the crowd", "spec": {"hair": "#1c1a1a", "skin": "#efc49c"}},
 "ABE": {"preset": "civilian", "name": "Gov.-Gen. Nobuyuki Abe", "spec": {"hair": "#d8d3cb", "glasses": 1, "skin": "#efc49c"}},
 "SONG": K("Song Jin-woo", {"coat": "#2b2b33", "glasses": 1}),
 "JPRES": {"preset": "civilian", "name": "A Japanese resident", "spec": {"skin": "#efc49c", "hair": "#1c1a1a"}},
 "JPRES2": {"preset": "woman", "name": "His neighbour", "spec": {"skin": "#efc49c", "hair": "#1c1a1a", "coat": "#3a4a5a"}},
 "GI1": {"preset": "us_officer", "name": "An American private", "spec": {"medal": 0, "trim": "#6f6438"}},
 "GI2": {"preset": "us_officer", "name": "Another private", "spec": {"medal": 0, "trim": "#6f6438", "hair": "#2a1d12"}},
 "SGT": {"preset": "us_officer", "name": "An American sergeant", "spec": {"medal": 0}},
 "WOMAN": {"preset": "woman", "name": "A woman in Seoul", "spec": {"hair": "#1c1a1a", "skin": "#efc49c", "coat": "#e8e2d4"}},
 "SELLER": K("A rice seller", {"coat": "#6a5a44"}),
 "NKOFF": K("A land-reform official", {"coat": "#4a4a52"}),
 "USOFF1": {"preset": "us_officer", "name": "An American officer"},
 "USOFF2": {"preset": "us_officer", "name": "Another American officer", "spec": {"hair": "#8a6a3a"}},
 "CHO": K("Cho Man-sik", {"hair": "#d8d3cb", "glasses": 1}),
 "GUARD": {"preset": "soviet_officer", "name": "A border guard", "spec": {"medal": 0, "epaulettes": 0}},
 "TRAV": K("A traveller", {"coat": "#b8a888"}),
 "SOVDEL": {"preset": "soviet_officer", "name": "The Soviet delegate", "spec": {"hat": "none"}},
 "USDEL": {"preset": "civilian", "name": "An American delegate"},
 "WORKER": {"preset": "worker", "name": "A worker in Seoul", "spec": {"skin": "#efc49c", "hair": "#1c1a1a"}},
 "WORKER2": {"preset": "worker", "name": "Another worker", "spec": {"skin": "#efc49c", "hair": "#1c1a1a", "coat": "#4a4a52"}},
 "SOUTH": K("A man in the south"), "NORTH": K("A man in the north", {"coat": "#4a4a52"}),
 "ROK1": {"preset": "us_officer", "name": "A South Korean soldier", "spec": {"skin": "#efc49c", "hair": "#1c1a1a", "medal": 0, "coat": "#4a5a4a"}},
 "ROK2": {"preset": "us_officer", "name": "Another soldier", "spec": {"skin": "#efc49c", "hair": "#1c1a1a", "medal": 0, "coat": "#4a5a4a"}},
 "NEG1": {"preset": "us_officer", "name": "A UN negotiator", "spec": {"hat": "none"}},
 "NEG2": {"preset": "soviet_officer", "name": "A Communist negotiator", "spec": {"hat": "none", "skin": "#efc49c", "hair": "#1c1a1a"}},
 "OLD": K("An old farmer", {"hair": "#d8d3cb", "coat": "#d8d1c0"}), "GRAND": K("His grandson"),
 "RHEE": {"preset": "rhee", "name": "Syngman Rhee"}, "KIM": {"preset": "kim", "name": "Kim Il Sung"},
}
VOICES = {
 "RUSK": "am_michael", "AIDE": "am_adam", "AIDE2": "am_puck", "WASH1": "am_michael", "WASH2": "am_fenrir",
 "FARMER": "bm_daniel", "WIFE": "bf_emma", "PROT": "bm_lewis", "PROT2": "bm_daniel", "TEACH": "bm_fable", "STUD": "bm_lewis",
 "STUD2": "bm_daniel", "SEOUL": "bm_lewis", "SOVCLERK": "bm_fable", "SOVOFF": "bm_daniel", "SOVSOLD": "bm_lewis",
 "SHOP": "bm_fable", "VIL1": "bm_daniel", "VIL2": "bm_lewis", "CROWD1": "bm_lewis", "CROWD2": "bf_emma", "ABE": "bm_daniel",
 "SONG": "bm_fable", "JPRES": "bm_lewis", "JPRES2": "bf_emma", "GI1": "am_puck", "GI2": "am_adam", "SGT": "am_fenrir",
 "WOMAN": "bf_emma", "SELLER": "bm_daniel", "NKOFF": "bm_lewis", "USOFF1": "am_michael", "USOFF2": "am_fenrir",
 "CHO": "bm_fable", "GUARD": "bm_daniel", "TRAV": "bm_lewis", "SOVDEL": "bm_daniel", "USDEL": "am_michael",
 "WORKER": "bm_lewis", "WORKER2": "bm_daniel", "SOUTH": "bm_lewis", "NORTH": "bm_daniel", "ROK1": "bm_lewis", "ROK2": "bm_daniel",
 "NEG1": "am_michael", "NEG2": "bm_daniel", "OLD": "bm_fable", "GRAND": "bm_lewis",
}

secs = {'intro': s['intro'], **{i: c for i, c in enumerate(s['chapters'])}}
for c in secs.values():
    c['beats'] = [b for b in c['beats'] if not b.get('_talk')]
# the original exchange (chapter 3): Rusk's own account, recast to him with a background
for b in s['chapters'][2]['beats']:
    if 'talk' in b and not b.get('_talk'):
        for l in b['talk']: l['who'] = 'RUSK'
        b['bg'] = room('us'); b.pop('scene', None)
# insert from the back of each section so earlier indices stay valid
for sec, after, lines, bg in sorted(TALK, key=lambda t: (str(t[0]), -t[1])):
    beats = secs[sec]['beats']
    assert 0 <= after < len(beats) and 'say' in beats[after], (sec, after)
    beats.insert(after + 1, {"talk": lines, "bg": bg, "_talk": 1})
for t in TALK:
    for l in t[2]:
        assert l['who'] in CAST and l['who'] in VOICES, l['who']
        assert len(l['text'].split()) <= 12, l['text']
s['cast'] = CAST
s['voices'] = dict(s.get('voices', {}), **VOICES)
s['talkNote'] = "Dialogue scenes are dramatized; every fact comes from the sources below."
json.dump(s, open(F, 'w'), indent=1, ensure_ascii=False)
print(len(TALK) + 1, 'exchanges')
