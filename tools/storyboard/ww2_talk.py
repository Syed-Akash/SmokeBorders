"""WW2 (sb-ww2-both-sides), new style (STYLE.md 2c): short acted exchanges about once a minute, everyday comparisons for big
numbers, and a running callback ("Name?" ... "Hitler." follows William from Liverpool to Berlin, the recruiting office and the
Navy, and is paid off when he changes it). Run after ww2_fix.py.
Truth rule: real people only say what the story's sources say they said or did (Chamberlain's "peace for our time", William's
words to The Times, Roosevelt's "infamy", Stagg's forecast and Eisenhower's decision, Private Shimura getting lost, Hirohito's
own phrases); the colour goes to unnamed roles (a cook, a customer, a border clerk, a purser, a recruiting officer). No jokes
about victims: the Holocaust, Hiroshima, Nanjing and the casualties chapters get no dialogue.
Every number in the cards is already in the story's sources; the comparisons are plain arithmetic on them."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from lib import *
from ww2_people import PEOPLE, who
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../studio/doc/stories/sb-ww2-both-sides.json'); s = json.load(open(F))
# speaker code: (look from ww2_people, name on screen, voice)
SPK = {
 'WPH': ('WPH', 'William Patrick Hitler', 'bm_lewis'), 'WPHN': ('WPHN', 'William Patrick Hitler', 'bm_lewis'),
 'BOY': ('BOY', 'William, aged about ten', 'bm_lewis'), 'BRID': ('BRID', 'Bridget Hitler', 'bf_emma'),
 'COOK': ('COOK', 'A hotel cook', 'bm_daniel'), 'COOK2': ('LIV', 'A kitchen boy', 'bm_fable'),
 'NB': ('LIVW', 'A Liverpool neighbour', 'bf_isabella'), 'NB2': ('LIV', 'Another neighbour', 'bm_daniel'),
 'TEACH': ('CIV', 'A schoolteacher', 'bm_fable'),
 'BORD': ('GERCIV', 'A German border clerk', 'am_fenrir'), 'CUST': ('CIV', 'A customer', 'am_adam'), 'CUST2': ('LIVW', "The customer's wife", 'af_sarah'),
 'AIDE': ('GERCIV', 'A party official', 'am_fenrir'),
 'CHAM': ('CHAM', 'Neville Chamberlain', 'bm_fable'), 'LOND': ('LIV', 'A Londoner', 'bm_daniel'), 'LOND2': ('LIVW', 'Another Londoner', 'bf_alice'),
 'REP': ('CIV', 'A reporter', 'bm_daniel'), 'PURSER': ('USCLK', "A ship's purser", 'am_michael'),
 'POL': ('POLE', 'A Polish soldier', 'am_adam'), 'POL2': ('POLE', 'His sergeant', 'am_fenrir'),
 'SKIP': ('LIV', 'A boat owner', 'bm_daniel'), 'NAVY': ('BRITOFF', 'A Royal Navy officer', 'bm_fable'),
 'TOMMY': ('TOMMY', 'A British soldier', 'bm_lewis'), 'CREW': ('SAILOR', 'A deckhand', 'bm_daniel'),
 'AUD': ('CIV', 'A man in the audience', 'am_adam'),
 'PILOT': ('RAF', 'An RAF pilot', 'bm_lewis'), 'PILOT2': ('RAF', 'His flight leader', 'bm_fable'),
 'LUFT': ('GERSOL', 'A German airman', 'am_fenrir'), 'LUFT2': ('GERSOL', 'His gunner', 'am_adam'),
 'GERS': ('GERSOL', 'A German soldier', 'am_fenrir'), 'GERS2': ('GERSOL', 'Another German soldier', 'am_adam'),
 'SOV': ('SOVSOL', 'A Soviet soldier', 'am_echo'), 'SOV2': ('SOV', 'His officer', 'am_onyx'),
 'JPOFF': ('JPOFF', 'A Japanese officer', 'am_onyx'), 'SHIM': ('JPOFF', 'Private Shimura Kikujiro', 'am_puck'),
 'JPMIN': ('JPCIV', 'A Japanese official', 'am_echo'), 'JPMIN2': ('JPOFF', 'An army officer', 'am_onyx'),
 'USS': ('SAILOR', 'An American sailor', 'am_puck'), 'USS2': ('SAILOR', 'Another sailor', 'am_michael'),
 'FDR': ('FDR', 'Franklin D. Roosevelt', 'am_onyx'),
 'RECR': ('USOFF', 'A recruiting officer', 'am_michael'),
 'WH1': ('USCLK', 'A White House clerk', 'am_adam'), 'WH2': ('USCLK', 'Another clerk', 'am_michael'),
 'CODE': ('USCLK', 'A Navy codebreaker', 'am_adam'), 'CODE2': ('USOFF', 'His officer', 'am_michael'),
 'CPO': ('USOFF', 'A Navy petty officer', 'am_fenrir'),
 'STAGG': ('RAF', 'Group Captain James Stagg', 'bm_daniel'), 'IKE': ('USOFF', 'General Dwight Eisenhower', 'am_michael'),
 'BERL': ('LIVW', 'A woman in Berlin', 'af_sarah'), 'BERL2': ('GERCIV', 'A man in Berlin', 'am_fenrir'),
 'MOSC': ('SOVSOL', 'A Soviet soldier in Berlin', 'am_echo'),
 'REBEL': ('JPOFF', 'A rebel officer', 'am_onyx'), 'STAFF': ('JPCIV', 'A palace official', 'am_echo'),
 'LIST': ('JPCIV', 'A listener in Tokyo', 'am_echo'), 'LIST2': ('LIVW', 'His neighbour', 'af_nicole'),
 'REG': ('USCLK', 'A clerk in New York', 'am_adam'),
}
s['cast'] = {}
for k, (look, name, v) in SPK.items():
    p, sp = PEOPLE[look]; s['cast'][k] = dict(preset=p, name=name, **({'spec': dict(sp)} if sp else {}))
s.setdefault('voices', {}).update({k: v[2] for k, v in SPK.items()})
# talk backgrounds
kitchen = S('night', room('uk', .1, True, '#4a4a3a'), table(.6, 0, 1))
lpool = S('dusk', town(9, .76, 160, 160, '#3a3028'), land('grass', .82))
school = S('day', room('uk', .7, False, '#5a5a4a'), table(.6, 0, 8))
border = S('day', room('de', .5, False, '#4a4a44'), table(.5, 0, 4), flagpole('de', .85, .7, 300))
showroom = S('day', town(6, .74, 200, 200, '#4a4440'), land('grass', .8))
office_de = S('night', room('de', .2, True, '#3a2e28'), table(.6, 0, 3))
london = S('day', town(12, .74, 190, 130, '#3a3530'), crowd(60, .96), flagpole('uk', .8, .72, 320))
press = S('day', room('uk', .5, False, '#3a3a44'), table(.6, 0, 10))
liner = S('day', sea(.62), ships(1, 'us', .5, .7, .9, 300, True))
pfield = S('dawn', hills(.55, 2, 21), land('grass', .74), forest(.62, 30, 14), fx=['smoke'])
harbour = S('dawn', sea(.64), coast(-.1, .45, .62, 100), ships(5, 'uk', .55, .68, .4, 160))
beach = S('night', sea(.66), land('sand', .82), ships(2, 'uk', .3, .7, .55, 420, True), fx=['smoke'])
hall = S('night', room('us', .1, True, '#4a3a2e'), crowd(40, .99))
airfield = S('day', hills(.58, 2, 17), land('grass', .76))
cockpit = S('dusk', hills(.62, 2, 23), town(8, .76, 90, 160, '#2a2622'), fx=['smoke'])
mud = S('dusk', hills(.56, 2, 33), forest(.62, 40, 33), land('grass', .76), weather='snow', fx=['snow'])
moscow = S('dusk', town(10, .74, 170, 150, '#2a2622'), land('snow', .8), fx=['snow'])
bridge = S('night', hills(.56, 2, 41), land('grass', .76), camp(3, .78, .1, 260, '#c8c0a8', .4))
tokyo = S('night', room('jp', .2, True, '#3a2e22'), table(.6, 0, 7))
pearl = S('dawn', sea(.64), coast(.0, .6, .62, 120), ships(3, 'us', .5, .7, .5, 260, True), fx=['smoke'])
oval = S('day', room('us', .6, False, '#5a5044'), table(.6, 0, 4))
recruit = S('day', room('us', .7, False, '#4a5a5a'), table(.6, 0, 5), flagpole('us', .85, .7, 300))
mailroom = S('day', room('us', .5, False, '#5a4a3a'), table(.7, 0, 12))
codes = S('night', room('us', .1, True, '#2e3a4a'), table(.8, 0, 11))
ring = S('night', town(8, .72, 140, 170, '#1d1612'), land('snow', .8), weather='snow', fx=['snow', 'smoke'])
sickbay = S('day', room('us', .4, False, '#d8d2c4'), table(.4, 0, 2))
weather = S('night', room('uk', .1, True, '#3a3a2e'), table(.7, 0, 9))
street_b = S('day', town(10, .72, 180, 150, '#3a3530'), land('grass', .8), fx=['smoke'])
palace = S('night', room('jp', .1, True, '#2a2218'), table(.5, 0, 9))
radio = S('day', town(10, .74, 120, 150, '#3a3028'), crowd(30, .97))
cityhall = S('day', room('us', .6, False, '#6a5a44'), table(.6, 0, 7))
T = lambda *lines, bg=None: dict(talk=[dict(who=w, text=x, **({'mood': m} if m else {})) for w, x, m in [(l + (None,))[:3] for l in lines]], **({'bg': bg} if bg else {}))
N = lambda say, scene: {'say': say, 'scene': scene}
ADD = [   # (first words of the beat to insert AFTER, the new beat)
 ('He is not wealthy. He is a poor kitchen porter', T(('COOK', 'The Irish girl thinks you own this hotel.'), ('COOK2', 'He told her that?', 'shock'), ('COOK', 'He told her that.', 'smug'), bg=kitchen)),
 ('Alois tries a restaurant on Dale Street', T(('NB', 'Another new business, Mr Hitler?'), ('NB2', 'Give it a month.', 'smug'), bg=lpool)),
 ('So the boy grows up English', T(('TEACH', 'Name?'), ('BOY', 'William Hitler, sir.'), ('TEACH', 'Fine. Sit down.'), bg=school)),
 ('That same year, 1933, William Patrick Hitler arrives', T(('BORD', 'Name?'), ('WPH', 'Hitler.'), ('BORD', '...Any relation?', 'shock'), ('WPH', 'Nephew.'), bg=border)),
 ('Later he sells cars for Opel', T(('CUST', 'And the salesman is called...?'), ('CUST2', 'Hitler. Like the Führer.', 'shock'), ('CUST', '...We will take it.', 'smug'), bg=showroom)),
 ('Then his uncle makes him an offer', T(('AIDE', 'Give up the British passport. A fine job awaits.'), ('WPH', 'No, thank you.'), bg=office_de)),
 ('He tells the crowds in London', T(('CHAM', 'Peace for our time.'), ('LOND', 'Peace!', 'happy'), ('LOND2', 'For how long?', 'sad'), bg=london)),
 ('He tells The Times newspaper', T(('REP', 'Your uncle. What is he like?'), ('WPH', 'I believe he has created a Frankenstein which even he perhaps cannot stop.', 'grim'), bg=press)),
 ('And an American newspaper owner', T(('PURSER', 'Name for the passenger list?'), ('BRID', 'Hitler. Mrs Bridget Hitler.'), ('PURSER', '...Welcome aboard.', 'shock'), bg=liner)),
 ('Across the border come sixty-six German divisions', N('Two thousand seven hundred and fifty tanks against two hundred and ten. Thirteen German tanks for every Polish one.', C('13 TO 1', 'GERMAN TANKS FOR EACH POLISH TANK', 'Poland, September 1939', size=160))),
 ('The Poles fight anyway', T(('POL', 'Any word from London?'), ('POL2', 'Not yet.', 'sad'), ('POL', 'Then we hold.'), bg=pfield)),
 ('Britain sends destroyers, ferries', T(('SKIP', 'A pleasure boat? To a war?', 'shock'), ('NAVY', 'Everything that floats.'), ('SKIP', 'Then fill her up.'), bg=harbour)),
 ('In nine days, three hundred and thirty-eight thousand', N('Three hundred and thirty-eight thousand men in nine days. About thirty-seven thousand every single day.', C('37,000 A DAY', 'MEN BROUGHT HOME', 'Dunkirk, 1940', size=160))),
 ('Of the eight hundred and sixty-one vessels', T(('TOMMY', 'Where are we going?'), ('CREW', 'Home. Get in.'), bg=beach)),
 ('And remember William Patrick Hitler? He is in America', T(('AUD', 'Is it true? You are really his nephew?'), ('WPH', 'I am.'), ('AUD', '...Can I have your autograph?', 'shock'), bg=hall)),
 ('If the Luftwaffe wins the sky', T(('PILOT', 'How many today?'), ('PILOT2', 'Too many. Up again in an hour.', 'sad'), bg=airfield)),
 ('Now the other side. The young German airmen', T(('LUFT', 'We are a long way from home.'), ('LUFT2', 'And it is their sky.', 'sad'), bg=cockpit)),
 ('Now the other side. For Soviet soldiers', T(('SOV', 'They are close to Moscow.'), ('SOV2', 'Then this is where we stop them.', 'angry'), bg=moscow)),
 ('Autumn rain turns the roads to mud', T(('GERS', 'Is the truck moving?'), ('GERS2', 'Not since Tuesday.', 'sad'), ('GERS', 'And now it is snowing.', 'sad'), bg=mud)),
 ('Private Shimura turns up safe', T(('JPOFF', 'Where were you?', 'angry'), ('SHIM', 'I got lost, sir.', 'sad'), ('JPOFF', '...It is too late now.', 'sad'), bg=bridge)),
 ('In July 1941, Japan seizes French Indochina', T(('JPMIN', 'How much oil is left?'), ('JPMIN2', 'Not enough. Not for long.', 'sad'), bg=tokyo)),
 ('Three hundred and fifty-three Japanese aircraft', T(('USS', 'Whose planes are those?', 'shock'), ('USS2', 'Not ours!', 'shock'), bg=pearl)),
 ('President Roosevelt calls it a date', T(('FDR', 'A date which will live in infamy.', 'grim'), bg=oval)),
 ('He is a British subject, living in America', T(('RECR', 'Name?'), ('WPH', 'Hitler.'), ('RECR', '...Next!', 'shock'), bg=recruit)),
 ('A letter to the President, from a man called Hitler', T(('WH1', 'A letter for the President. From a Mr... Hitler.', 'shock'), ('WH2', 'Put it on the pile. The big pile.', 'smug'), bg=mailroom)),
 ('So Midway sends out a fake report', T(('CODE', 'AF is short of water.'), ('CODE2', 'Then AF is Midway.', 'smug'), bg=codes)),
 ('Now the other side. Inside the ring', T(('GERS', 'Any bread?'), ('GERS2', 'Tomorrow. Maybe.', 'sad'), bg=ring)),
 ("He doesn't carry a rifle", T(('CPO', 'Name?'), ('WPHN', 'Hitler, sir.'), ('CPO', '...Welcome to the Navy, Hitler.'), bg=sickbay)),
 ('His weatherman, Group Captain James Stagg', T(('STAGG', 'A short break in the weather. On the sixth.'), ('IKE', 'Then we go on the sixth.'), bg=weather)),
 ('About five thousand ships. And a hundred and fifty-six thousand', N('A hundred and fifty-six thousand soldiers in one day. About sixty-five hundred every hour.', C('6,500 AN HOUR', 'SOLDIERS ASHORE', 'Normandy, 6 June 1944', size=150))),
 ('On the first of May, German radio announces', T(('BERL', 'Is it true?', 'shock'), ('BERL2', 'The radio says so.'), bg=street_b)),
 ('So the West celebrates victory in Europe', T(('LOND', "It's over!", 'happy'), ('MOSC', 'Not here. Not until after midnight.', 'smug'), bg=london)),
 ("They can't find it. It is hidden among documents", T(('REBEL', 'Where is the record?', 'angry'), ('STAFF', 'I could not say, sir.'), bg=palace)),
 ("He says the war has developed, quote", T(('LIST', 'Is that... the emperor?', 'shock'), ('LIST2', 'Quiet. Listen.'), bg=radio)),
 ('That same year he marries Phyllis', T(('REG', 'Name?'), ('WPH', 'Stuart-Houston.'), ('REG', 'Much easier.', 'smug'), bg=cityhall)),
]
chapters = [s['intro']] + s['chapters']
for c in chapters: c['beats'] = [b for b in c['beats'] if not b.get('_new')]   # drop an earlier run of this script
n = 0
for after, beat in ADD:
    beat['_new'] = 1; done = False
    for c in chapters:
        for i, b in enumerate(c['beats']):
            if b.get('say', '').startswith(after): c['beats'].insert(i + 1, beat); done = True; n += 1; break
        if done: break
    assert done, after
s['talkNote'] = 'Dialogue scenes are dramatized; every fact comes from the sources below.'
json.dump(s, open(F, 'w'), indent=1, ensure_ascii=False)
print('inserted', n, 'beats; talk beats', sum(1 for c in chapters for b in c['beats'] if 'talk' in b))
