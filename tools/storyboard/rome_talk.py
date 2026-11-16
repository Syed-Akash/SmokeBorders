"""Rome vs Carthage redo, new style (STYLE.md 2c/2d/2e, owner 15 Nov 2026): acted exchanges about once a minute, every
person cast with a fitting preset, everyday comparisons for the big numbers, and callbacks ("You stay on land. We keep the sea.",
Cato's line). Dialogue is dramatized from the record: real people only act out what the story's sources say they did or said
(Hamilcar's condition and the boy's oath, Pulcher and the chickens, the young Scipio's oath at Canusium, the meeting before Zama,
Cato's line, Scipio Aemilianus quoting Homer to Polybius); jokes go to unnamed roles, never at victims.
Every number below is already in the story's sources; the comparisons are plain arithmetic on them.
Run after rome.py. Safe to run again: it removes its own earlier insertions first."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from lib import *
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../studio/doc/stories/sb-rome-carthage.json'); s = json.load(open(F))
TOGA, PURPLE = '#e9e2d0', '#5b2a6e'
s['cast'] = {
 'ROM': {'preset': 'roman', 'name': 'A Roman senator', 'spec': {'hat': 'none', 'coat': TOGA, 'coat2': '#9e1b2a', 'hair': '#8a8278'}},
 'CAR': {'preset': 'carthaginian', 'name': 'A Carthaginian merchant', 'spec': {'hat': 'none', 'coat': PURPLE}},
 'HAN': {'preset': 'carthaginian', 'name': 'Hannibal'},
 'SCI': {'preset': 'scipio', 'name': 'Scipio Africanus'},
 'FAB': {'preset': 'roman', 'name': 'Fabius Maximus', 'spec': {'hat': 'none', 'coat': TOGA, 'hair': '#c8c2b8'}},
 'CAT': {'preset': 'roman', 'name': 'Cato the Elder', 'spec': {'hat': 'none', 'coat': TOGA, 'coat2': '#7a6a5a', 'hairStyle': 'bald', 'hair': '#c8c2b8'}},
 'SEN2': {'preset': 'roman', 'name': 'Another senator', 'spec': {'hat': 'none', 'coat': TOGA, 'coat2': '#3a4a6a', 'hair': '#3b2a1a'}},
 'MAM': {'preset': 'worker', 'name': 'A Mamertine mercenary', 'spec': {'coat': '#6a5a44', 'hat': 'helmet', 'hatCol': '#7a6a4a', 'beard': 'full'}},
 'LEG': {'preset': 'roman', 'name': 'A Roman legionary'},
 'LEG2': {'preset': 'roman', 'name': 'Another legionary', 'spec': {'hair': '#5a3a22', 'beard': 'none'}},
 'ROWER': {'preset': 'worker', 'name': 'A Roman rower', 'spec': {'coat': '#8a7a5a'}},
 'CAPT': {'preset': 'roman', 'name': 'A Roman ship captain', 'spec': {'hat': 'none', 'coat': '#7a1d1d'}},
 'PRIEST': {'preset': 'roman', 'name': 'The keeper of the sacred chickens', 'spec': {'hat': 'none', 'coat': '#d8d0c0', 'coat2': '#d8d0c0', 'hairStyle': 'bald'}},
 'PUL': {'preset': 'roman', 'name': 'Claudius Pulcher', 'spec': {'hatCol': '#b8b8b8', 'coat': '#8a1a2a'}},
 'SAIL': {'preset': 'worker', 'name': 'A Carthaginian sailor', 'spec': {'coat': PURPLE, 'skin': '#c99068'}},
 'COUNC': {'preset': 'carthaginian', 'name': 'A Carthaginian councillor', 'spec': {'hat': 'none', 'coat': '#3d2a55', 'hair': '#8a8278'}},
 'HAM': {'preset': 'carthaginian', 'name': 'Hamilcar Barca', 'spec': {'hatCol': '#c8a24a', 'beard': 'full', 'hair': '#4a3626'}},
 'BOY': {'preset': 'carthaginian', 'name': 'Hannibal, aged about nine', 'spec': {'hat': 'none', 'beard': 'none', 'coat': '#7a4a8a'}},
 'MERC': {'preset': 'worker', 'name': 'An unpaid mercenary', 'spec': {'coat': '#5a4a34', 'beard': 'full'}},
 'ENVOY': {'preset': 'roman', 'name': 'A Roman envoy', 'spec': {'hat': 'none', 'coat': TOGA, 'coat2': '#9e1b2a'}},
 'GAUL': {'preset': 'worker', 'name': 'A Celtic warrior', 'spec': {'coat': '#4a6a3a', 'hair': '#b8732a', 'hairStyle': 'long', 'beard': 'full'}},
 'MULE': {'preset': 'carthaginian', 'name': 'A Carthaginian soldier', 'spec': {'beard': 'none'}},
 'YSCI': {'preset': 'scipio', 'name': 'The young Scipio', 'spec': {'hat': 'none'}},
 'OFFC': {'preset': 'roman', 'name': 'A surviving officer', 'spec': {'hat': 'none', 'coat': '#6a2a2a'}},
 'MAS': {'preset': 'carthaginian', 'name': 'A Numidian horseman', 'spec': {'coat': '#c9a85a', 'hat': 'turban', 'hatCol': '#e9e2d0', 'skin': '#8a5a3a'}},
 'NAS': {'preset': 'roman', 'name': 'Scipio Nasica', 'spec': {'hat': 'none', 'coat': TOGA, 'coat2': '#2a5a3a', 'hair': '#8a8278'}},
 'AEM': {'preset': 'scipio', 'name': 'Scipio Aemilianus', 'spec': {'hair': '#5a3a22'}},
 'POLY': {'preset': 'roman', 'name': 'Polybius', 'spec': {'hat': 'none', 'coat': '#3a4a6a', 'coat2': '#d8d0c0', 'beard': 'full', 'hair': '#8a8278'}},
}
s.setdefault('voices', {}).update({'ROM': 'bm_lewis', 'CAR': 'bm_daniel', 'HAN': 'bm_fable', 'SCI': 'am_michael', 'FAB': 'bm_lewis', 'CAT': 'bm_daniel',
 'SEN2': 'am_adam', 'MAM': 'am_fenrir', 'LEG': 'am_puck', 'LEG2': 'am_adam', 'ROWER': 'am_puck', 'CAPT': 'am_fenrir', 'PRIEST': 'bm_daniel',
 'PUL': 'bm_lewis', 'SAIL': 'am_adam', 'COUNC': 'bm_lewis', 'HAM': 'am_fenrir', 'BOY': 'am_puck', 'MERC': 'am_fenrir', 'ENVOY': 'bm_fable',
 'GAUL': 'am_fenrir', 'MULE': 'am_adam', 'YSCI': 'am_michael', 'OFFC': 'bm_daniel', 'MAS': 'am_adam', 'NAS': 'am_michael', 'AEM': 'am_michael', 'POLY': 'bm_daniel'})
# sets
senate = S('day', room(None, .7, False, '#6a5844'), crowd(40, .99))
council = S('day', room(None, .7, False, '#3d2a55'), table(.6, 2, 6))
messana = S('night', town(8, .72, 140, 150, '#2a2018'), fire(.75, .7, 200))
shipyard = S('day', sea(.62), coast(-.2, .5, .6, 90), ships(3, 'red', .5, .66, .55, 260))
beach = S('day', land('sand', .72), sea(.8, .2), fx=['dust'])
deck = S('day', sea(.6), ships(2, 'red', .2, .66, .6, 420))
deck_storm = S('night', sea(.58), ships(2, 'red', .2, .64, .6, 400), weather='storm', fx=['rain'])
altar = S('night', room(None, None, True, '#1a120c'), fire(.5, .74, 260, .4), fx=['embers'])
africa_camp = S('dusk', land('sand', .74), hills(.56, 2, 6), camp(4, .76, .1, 240, '#a08060', .4))
spain = S('day', hills(.5, 3, 31, .2), land('sand', .74), fx=['dust'])
snowpass = S('day', hills(.4, 3, 4, .2), land('snow', .7), weather='snow', fx=['fog'])
gaul_camp = S('dusk', hills(.55, 2, 6), land('grass', .74), camp(5, .76, .1, 220, '#e8e0c8', .45), forest(.62, 30, 8))
fog_lake = S('dawn', sea(.64, .25), hills(.5, 2, 5, .2), land('grass', .74), fx=['fog'])
plain = S('day', hills(.56, 2, 3), land('grass', .72), fx=['dust'])
canusium = S('night', room(None, .1, True, '#2a2018'), table(.5, 3, 2))
zama = S('day', land('sand', .74), hills(.56, 2, 6), fx=['dust'])
court_east = S('day', room(None, .7, False, '#5a3a22'), table(.6, 2, 10))
walls = S('night', town(14, .72, 160, 130, '#2a2018'), fire(.3, .66, 300), fire(.75, .68, 260), fx=['smoke', 'embers'])
hill = S('dusk', hills(.6, 2, 5, .1), town(10, .76, 140, 160, '#1d1612', .35), fire(.5, .74, 400, .35), fx=['smoke', 'embers'])
T = lambda *lines, bg=None: dict(talk=[dict(who=w, text=x, **({'mood': m} if m else {})) for w, x, m in [(l + (None,))[:3] for l in lines]], **({'bg': bg} if bg else {}))
N = lambda say, scene: {'say': say, 'scene': scene}
ADD = [   # (first words of the beat to insert AFTER, the new beat)
 ('The legend also says the locals offered her', T(('CAR', 'As much land as an ox hide covers?'), ('CAR', 'Fetch me a very sharp knife.', 'smug'), bg=beach)),
 ('The Mamertines were mercenaries', T(('MAM', 'Write to Carthage. Ask for help.'), ('MAM', 'And write to Rome as well.'), ('MAM', 'Both?'), ('MAM', 'Whoever comes first.', 'smug'), bg=messana)),
 ('Rome sent a consul with two legions', T(('LEG', 'Whose town is this, then?'), ('LEG2', 'Not ours.'), ('LEG', 'Not theirs either.'), ('LEG2', "Then let's hold it.", 'smug'), bg=messana)),
 ('So in 260 BC, Rome did something wild', N('A hundred and twenty ships in sixty days. That is two warships, every single day, for two months.', C('2 A DAY', 'WARSHIPS, FOR 60 DAYS', 'Rome, 260 BC', size=170))),
 ('They probably copied Carthaginian ships', T(('ROWER', 'When do we get a sea?'), ('CAPT', 'When the ship is finished. Row.'), ('ROWER', "It's sand, sir."), ('CAPT', 'Row harder.', 'angry'), bg=beach)),
 ('Then they added a trick', T(('SAIL', "What's that thing on the front?", 'shock'), ('LEG', 'A bridge. Coming over.', 'smug'), bg=deck)),
 ('So Carthage hired a Greek soldier', T(('COUNC', 'We need a general who has beaten Romans.'), ('COUNC', '...Do we have one?'), ('COUNC', 'We can hire one.', 'smug'), bg=council)),
 ('Then the sea itself joined the war', T(('ROWER', "Which enemy is this?", 'shock'), ('CAPT', 'The weather.', 'sad'), bg=deck_storm)),
 ('And then there is the admiral Claudius Pulcher', T(('PRIEST', "Admiral... the chickens won't eat.", 'sad'), ('PUL', 'Then let them drink.', 'angry'), bg=deck)),
 ('He lost ninety three of his hundred', N('Ninety three out of a hundred and twenty. Nearly four ships in every five.', C('93 OF 120', 'SHIPS LOST', 'Drepana, 249 BC', size=170))),
 ('On the tenth of March, 241 BC', T(('SAIL', 'Roman warships! Hundreds!', 'shock'), ('SAIL', 'And we are carrying grain.', 'sad'), bg=deck)),
 ('The price of peace was high', N('Three thousand two hundred talents over ten years. Three hundred and twenty talents of silver, every year, for a decade.', C('320 A YEAR', 'TALENTS OF SILVER', 'for 10 years, from 241 BC', size=170))),
 ('Then Carthage could not pay its own mercenaries', T(('MERC', 'Where is our pay?', 'angry'), ('COUNC', "Rome has it. Well, it will have.", 'sad'), ('MERC', 'Then we take the city.', 'angry'), bg=africa_camp)),
 ("His father agreed, on one condition", T(('HAM', 'Put your hand on the altar.'), ('BOY', 'I swear I will never be a friend to Rome.'), bg=altar)),
 ('Hamilcar died in Spain in 229 BC', T(('ENVOY', 'You stay south of the Ebro.'), ('CAR', 'And you stay north of it.'), ('ENVOY', 'We never said that.', 'smug'), bg=spain)),
 ('Rome sent envoys to Carthage', T(('ENVOY', 'Hand over Hannibal.'), ('COUNC', 'No.'), ('ENVOY', 'Then it is war.', 'angry'), ('COUNC', 'Then it is war.', 'angry'), bg=council)),
 ('Mountain tribes rolled rocks down', T(('MULE', 'The elephant will not move.'), ('MULE', 'It is from Africa. It has never seen snow.', 'sad'), bg=snowpass)),
 ('When he came down into the plains', N('About fifty nine thousand men and horsemen went up. About twenty six thousand came down. Fewer than one in two made it.', C('26,000 LEFT', 'OF ABOUT 59,000', 'northern Italy, 218 BC', size=150))),
 ('Most of his elephants soon died', T(('GAUL', 'You came over the mountains? To fight Rome?'), ('HAN', 'Yes.'), ('GAUL', 'Then we are coming with you.', 'happy'), bg=gaul_camp)),
 ('Hannibal\'s whole army was waiting in the hills', T(('LEG', "I can't see a thing."), ('LEG2', 'Neither can they.'), ('LEG', '...Then who is on that hill?', 'shock'), bg=fog_lake)),
 ('Fabius followed Hannibal everywhere', T(('SEN2', 'Another day without a battle?', 'angry'), ('ROM', 'He calls it a plan.'), ('SEN2', 'I call it delay.'), bg=senate)),
 ('Hannibal had fewer than fifty thousand', T(('GAUL', 'You put us in the middle?', 'shock'), ('HAN', "Bend. Don't break."), bg=plain)),
 ('Nobody knows exactly how many died', N('Even the lowest estimate is more than seven Romans killed for every man Hannibal lost.', C('7 FOR 1', 'ROMAN DEATHS FOR EACH OF HANNIBAL\'S', 'Cannae, 216 BC', size=170))),
 ('At a nearby town called Canusium', T(('OFFC', "Italy is lost. We should sail away.", 'sad'), ('YSCI', 'Swear you will not abandon Rome. All of you. Swear it.', 'angry'), bg=canusium)),
 ('Rome did not ask. It kept raising', N('Two hundred thousand men under arms, three years after Cannae. Two and a half times the whole army Rome took to Cannae.', C('200,000+', 'ROMANS UNDER ARMS', '213 BC', size=170))),
 ('Now the other side. Hannibal needed siege engines', T(('COUNC', 'He wants more men. And siege engines.'), ('COUNC', 'He keeps winning. Why does he need anything?'), bg=council)),
 ('Nobody wanted the Spanish command', T(('ROM', 'Who will take Spain?'), ('YSCI', 'I will.'), ('ROM', 'You are twenty four.'), ('YSCI', 'So was Hannibal, nearly.', 'smug'), bg=senate)),
 ('Then they cut off his head', T(('MULE', 'Something was thrown over the wall, sir.'), ('HAN', 'I know that face.', 'sad'), bg=africa_camp)),
 ('That cavalry belonged to Masinissa', T(('MAS', 'Our prince rides with Rome now.'), ('MAS', 'Then so do we.'), bg=zama)),
 ('Hannibal opened with eighty war elephants', T(('LEG', 'Here they come!', 'shock'), ('LEG2', 'Open the lines! Let them through!'), bg=zama)),
 ('About twenty thousand Carthaginians died', N('About twenty thousand Carthaginians killed, against about fifteen hundred Romans. More than thirteen for one. The numbers of Cannae, turned round.', C('13 FOR 1', 'THE OTHER WAY ROUND', 'Zama, 202 BC', size=170))),
 ('The terms were brutal', N('Ten thousand talents over fifty years. Two hundred talents a year. Payments that would outlive almost everyone who signed the treaty.', C('50 YEARS', '200 TALENTS A YEAR', 'peace of 201 BC', size=170))),
 ('And the general turned out to be a very good accountant', T(('COUNC', 'Where did all this money come from?', 'shock'), ('HAN', 'From counting it properly.', 'smug'), bg=council)),
 ('He spent the rest of his life moving', T(('HAN', "Rome is coming. I'd move fast, Your Majesty."), ('ROM', 'Hannibal is there? Then we are coming.', 'angry'), bg=court_east)),
 ('Back in the Senate, Plutarch says', T(('CAT', 'A fresh fig. From Africa.'), ('CAT', "Three days' sail from here.", 'angry'), bg=senate)),
 ('Not everyone agreed. Another senator', T(('NAS', 'Carthage must be spared.'), ('CAT', 'Carthage must be destroyed.', 'angry'), ('ROM', 'Can we vote on the drains now?', 'sad'), bg=senate)),
 ('Carthage begged for peace and offered to obey', T(('ENVOY', 'Three hundred children.'), ('COUNC', 'Here.', 'sad'), ('ENVOY', 'Every weapon.'), ('COUNC', '...Here.', 'sad'), bg=council)),
 ('Then Rome made its final demand', N('Sixteen kilometres. About a four hour walk from the sea, for a city that lived on ships.', C('16 KM', 'FROM THE SEA', 'Rome\'s last demand, 149 BC', size=170))),
 ('And Scipio Aemilianus wept', T(('POLY', 'You have won. Why are you crying?'), ('AEM', 'One day, someone will give the same order about Rome.', 'sad'), bg=hill)),
 ('Two cities fought for a hundred and eighteen years', T(('CAR', 'You stay on land. We keep the sea.'), ('ROM', 'We kept both.', 'sad'), bg=S('dusk', sea(.64, .25), coast(.0, .75, .62, 120, .3), town(6, .7, 120, 160, '#3a2a22', .4), fx=['smoke']))),
]
EXIST_BG = {'You stay on land': senate, 'Is that our ship design': shipyard, "That island wasn't": council, "They're guarding the sea": spain,
            'We have the biggest army': plain, "I've beaten you three times": walls, 'Fortune changes': zama, "They're paying early": senate,
            'Also, Carthage must be destroyed': senate}
chapters = ([s['intro']] if s.get('intro') else []) + s['chapters'] + ([s['outro']] if s.get('outro', {}).get('beats') else [])
for c in chapters:   # drop an earlier run of this script
    c['beats'] = [b for b in c['beats'] if not b.get('_new')]
n = 0
for after, beat in ADD:
    beat['_new'] = 1; done = False
    for c in chapters:
        for i, b in enumerate(c['beats']):
            if b.get('say', '').startswith(after) and not done: c['beats'].insert(i + 1, beat); done = True; n += 1; break
    assert done, after
for c in chapters:   # the old exchanges get a room and their people (they were countryball shots)
    for b in c['beats']:
        t = b.get('talk')
        if t and not b.get('_new'):
            for k, bg in EXIST_BG.items():
                if t[0]['text'].startswith(k): b.pop('scene', None); b['bg'] = bg
            if t[0]['text'] == 'Fortune changes. I\'ve seen it change on me.': t[0]['text'] = "Fortune changes. I have seen it change on me. Let us make peace."
# cold open: hook on the famous name (STYLE.md 2c)
for b in s['intro']['beats']:
    if b.get('say', '').startswith('This is the end of Rome versus Carthage. The Punic Wars'):
        b['say'] = 'This is the end of Rome versus Carthage. The war of Hannibal, and his elephants over the Alps. The Punic Wars, 264 to 146 BC. Three wars, one hundred and eighteen years, and two of the most powerful cities in the ancient world.'
s['talkNote'] = 'Dialogue scenes are dramatized; every fact comes from the sources below.'
json.dump(s, open(F, 'w'), indent=1, ensure_ascii=False)
print('inserted', n, 'beats; talk beats now', sum(1 for c in chapters for b in c['beats'] if 'talk' in b))
