"""Pig War, new style (owner, 15 Nov 2026): acted dialogue about once a minute, everyday comparisons, callbacks.
Dialogue is dramatized from the record: real people only act out what the sources say they did or said;
the jokes go to unnamed roles (a sailor, a clerk, a voter)."""
import json, sys, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from lib import *
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../studio/doc/stories/sb-pig-war.json'); s = json.load(open(F))
NAVY, BLUE = '#1c2a44', '#1f3150'
s['cast'] = {
 'CUT': {'preset': 'settler', 'name': 'Lyman Cutlar'}, 'GRF': {'preset': 'hbc_man', 'name': 'Charles Griffin'},
 'PIC': {'preset': 'pickett', 'name': 'Capt. George Pickett'}, 'HOR': {'preset': 'rn_officer', 'name': 'Capt. Geoffrey Hornby'},
 'BAY': {'preset': 'rn_officer', 'name': 'Rear Adm. Robert Baynes', 'spec': {'hair': '#d8d4cc'}}, 'DOU': {'preset': 'douglas', 'name': 'Gov. James Douglas'},
 'HAR': {'preset': 'us_officer', 'name': 'Gen. William Harney'}, 'SCO': {'preset': 'us_officer', 'name': 'Gen. Winfield Scott', 'spec': {'hair': '#e8e4dc'}},
 'PRE': {'preset': 'rn_officer', 'name': 'Capt. James Prevost'}, 'CAM': {'preset': 'us_officer', 'name': 'Archibald Campbell', 'spec': {'hair': '#3b2a1a'}},
 'BUC': {'preset': 'governor', 'name': 'President James Buchanan'}, 'POLK': {'preset': 'governor', 'name': 'President James K. Polk', 'spec': {'hair': '#3b2a1a'}},
 'ROB': {'preset': 'us_officer', 'name': 'Henry Robert', 'spec': {'hair': '#6b4a2a'}}, 'KAI': {'preset': 'king_george', 'name': 'Emperor Wilhelm I', 'spec': {'hair': '#e8e4dc', 'beard': 'full'}},
 'SAILOR': {'preset': 'us_sailor', 'name': 'A British sailor', 'spec': {'coat': NAVY}}, 'MARINE': {'preset': 'redcoat', 'name': 'A Royal Marine'},
 'SOLDIER': {'preset': 'us_officer', 'name': 'An American soldier', 'spec': {'coat': BLUE}}, 'AIDE': {'preset': 'us_officer', 'name': 'An aide'},
 'CLERK': {'preset': 'governor', 'name': 'A clerk', 'spec': {'hair': '#5a3a22'}}, 'SETTLER': {'preset': 'settler', 'name': 'A settler'},
 'COMPANY': {'preset': 'hbc_man', 'name': 'A company man', 'spec': {'hair': '#2a1d12'}}, 'VOTER1': {'preset': 'settler', 'name': 'A voter'},
 'VOTER2': {'preset': 'governor', 'name': 'Another voter', 'spec': {'hair': '#2a1d12'}}, 'MINER': {'preset': 'settler', 'name': 'A miner', 'spec': {'hair': '#8a6a3a'}},
 'LOCAL': {'preset': 'hbc_man', 'name': 'A Victoria local'}, 'MEMBER': {'preset': 'governor', 'name': 'A church member', 'spec': {'hair': '#9a8a7a'}},
 'EXPERT': {'preset': 'governor', 'name': 'A Geneva expert', 'spec': {'hair': '#c8c0b0', 'glasses': 1}},
}
s['voices'].update({'CUT': 'am_michael', 'GRF': 'bm_daniel', 'PIC': 'am_adam', 'HOR': 'bm_lewis', 'BAY': 'bm_fable', 'DOU': 'bm_daniel', 'HAR': 'am_fenrir',
 'SCO': 'am_michael', 'PRE': 'bm_lewis', 'CAM': 'am_adam', 'BUC': 'am_fenrir', 'POLK': 'am_adam', 'ROB': 'am_puck', 'KAI': 'bm_fable', 'SAILOR': 'bm_lewis',
 'MARINE': 'bm_daniel', 'SOLDIER': 'am_puck', 'AIDE': 'am_puck', 'CLERK': 'am_fenrir', 'SETTLER': 'am_adam', 'COMPANY': 'bm_lewis', 'VOTER1': 'am_michael',
 'VOTER2': 'am_puck', 'MINER': 'am_adam', 'LOCAL': 'bm_daniel', 'MEMBER': 'am_fenrir', 'EXPERT': 'bm_fable'})
farm = S('dusk', hills(.55, 2, 3), land('grass', .74), farm(.75, .7, .72), animal('pig', .4, .8, .88))
ship = S('day', sea(.62), ships(4, 'uk', .1, .68, .55, 260))
camp_ = S('day', hills(.55, 2, 9), land('grass', .74), camp(5, .76, .1, 220, '#e8e0c8', .45))
office = S('day', room('us', .7), table(.6, 0, 8))
officeuk = S('day', room('uk', .7), table(.6, 0, 8))
night = S('night', room(None, .1, True), table(.5, 3, 4))
fort_ = S('day', hills(.6, 2, 5), land('grass', .74), fort('hbc', .6, .72, 700, 100))
T = lambda *lines, bg=None: dict(talk=[dict(who=w, text=x, **({'mood': m} if m else {})) for w, x, m in [(l + (None,))[:3] for l in lines]], **({'bg': bg} if bg else {}))
N = lambda say, scene: {'say': say, 'scene': scene}
ADD = [   # (first words of the beat to insert AFTER, the new beat)
 ('He picks up his rifle', T(('CUT', 'Not again. Not my potatoes again.', 'angry'), bg=farm)),
 ('Two of the most powerful', T(('SAILOR', 'Guns ready, sir. What exactly are we shooting at?'), ('HOR', 'Officially? A misunderstanding. About a pig.', 'smug'), bg=ship)),
 ('In 1818, they agreed', T(('COMPANY', 'So who owns it?'), ('SETTLER', 'Both of us. For now.'), ('COMPANY', 'And after that?'), ('SETTLER', "We'll sort it out later.", 'smug'), bg=fort_)),
 ('In 1843, more than seven hundred', T(('SETTLER', 'Is this Oregon?'), ('COMPANY', "It's the Columbia District."), ('SETTLER', 'Not for long.', 'smug'), bg=fort_)),
 ('[chuckle] One of his real 1844', T(('VOTER1', 'Fifty-four forty, or fight!', 'angry'), ('VOTER2', "That's not even his slogan."), ('VOTER1', 'Then what is?'), ('VOTER2', 'Polk, Dallas, and the Tariff of forty-two.'), ('VOTER1', "I'll keep mine.", 'smug'), bg=S('day', town(14, .74, 150, 130, '#3a3028'), crowd(80)))),
 ('And Polk had a second problem', T(('AIDE', 'Mexico, or Britain, Mr President?'), ('POLK', 'One war at a time.'), bg=office)),
 ('The problem? Between Vancouver', T(('CLERK', 'Middle of the channel. Done.', 'happy'), ('AIDE', 'Which channel?'), ('CLERK', 'The channel.'), ('AIDE', 'There are two.'), ('CLERK', '...Done anyway.', 'smug'), bg=night)),
 ('Prevost had an answer', T(('PRE', "Your own government's maps draw the line through Rosario."), ('CAM', 'Maps can be wrong.', 'angry'), ('PRE', 'So can treaties, apparently.', 'smug'), bg=S('day', room('uk', .1), table(.6, 2, 10)))),
 ('Gold was found on the Fraser', N('That is sixty newcomers for every person who already lived there.', C('×60', 'NEWCOMERS FOR EVERY RESIDENT', 'Victoria, 1858', size=220))),
 ('That is sixty newcomers', T(('MINER', 'Which way to the gold?'), ('LOCAL', 'Up the river. Everyone else already went.'), bg=S('day', town(8, .74, 140, 170, '#4a3a2c'), crowd(90), sea(.66)))),
 ('He claimed the right to be there', N('Three hundred and twenty acres. That is about two hundred and forty football fields, for free.', C('320 ACRES', '≈ 240 FOOTBALL FIELDS', 'for free', size=170))),
 ('[chuckle] There was one small problem. The free land', T(('CLERK', 'Your claim?'), ('CUT', 'Three hundred and twenty acres. Free.'), ('CLERK', 'That offer ended in 1855.'), ('CUT', "...I'll keep the garden.", 'smug'), bg=office)),
 ('Then he did something decent', T(('CUT', 'Ten dollars. For the pig.'), ('GRF', 'A hundred.', 'angry'), ('CUT', 'For a pig?', 'shock'), ('GRF', 'For MY pig.', 'angry'), bg=farm)),
 ('Now the island\'s two sides', None),   # placeholder (kept for order)
 ('To the Americans, that was outrageous', T(('SETTLER', 'They want to arrest a man over a pig!', 'angry'), ('SOLDIER', "I'll send it up to the general."), bg=camp_)),
 ('At West Point, Pickett', T(('HAR', "Who's free?"), ('AIDE', 'Captain Pickett. Last in his class.'), ('HAR', 'Send him.', 'smug'), bg=office)),
 ('When someone pointed this out', T(('SOLDIER', "Captain. That's a British warship. Right there.", 'shock'), ('PIC', 'Then we move the cannon.'), bg=S('day', sea(.6), ships(1, 'uk', .7, .66, .7, 0), land('grass', .72), cannons(2, .15, 300)))),
 ('Governor Douglas gave him orders', T(('DOU', 'Get those American soldiers off the island.'), ('HOR', "And if they won't go?"), ('DOU', 'Avoid a fight. If possible.'), ('HOR', 'If possible.'), bg=officeuk)),
 ('Ask yourself what you would have done', T(('SAILOR', 'Seventy guns loaded, sir.'), ('HOR', 'And we wait.'), ('SAILOR', 'For what?'), ('HOR', 'The admiral.'), bg=ship)),
 ('Out on the water were five British', N('Seventy guns. Pointed at a camp that was there because of a pig that was already dead.', ship)),
 ('He sailed north, and took one look', T(('DOU', 'Land the Royal Marines.'), ('BAY', 'No. I will not involve two great nations in a war over a squabble about a pig.'), bg=officeuk)),
 ('The president was now James Buchanan', T(('BUC', 'Which channel did I write into that treaty?'), ('AIDE', 'The middle one, sir.'), ('BUC', '...Get me General Scott.'), bg=office)),
 ('Scott was seventy-three', T(('SCO', 'Gentlemen. Buttons done up, please.'), ('SCO', 'Now. About this pig.', 'smug'), bg=officeuk)),
 ('By November, they had a deal', T(('SCO', 'A hundred men each.'), ('DOU', 'Until when?'), ('SCO', 'Until the diplomats decide.'), ('DOU', 'So, later.', 'smug'), bg=officeuk)),
 ('So now two rival armies had to share', N('Twelve years. More than four thousand days of guarding one small island. Over a pig.', C('4,000+ DAYS', 'OF GUARD DUTY', 'over one pig', size=160))),
 ('The two garrisons visited', T(('MARINE', 'Happy Fourth of July!', 'happy'), ('SOLDIER', 'God save the Queen!', 'happy'), bg=camp_)),
 ('They held sports contests', T(('SOLDIER', 'Another round?'), ('MARINE', 'For peace.', 'happy'), bg=S('night', camp(5, .76, .1, 220, '#e8e0c8', .5), land('grass', .76), fire(.5, .7, 220)))),
 ('George Pickett had a choice', T(('PIC', 'Virginia.'), ('SOLDIER', "Then you're leaving the army, sir.", 'sad'), bg=camp_)),
 ('Years later, he was asked to run', T(('MEMBER', 'Point of order!', 'angry'), ('ROB', "...What's a point of order?", 'shock'), bg=S('day', room(None, .7, False, '#3a2a1c'), crowd(50, .99)))),
 ('[chuckle] So an island off the Pacific', T(('KAI', 'Haro, or Rosario?'), ('EXPERT', 'We will need about a year, Your Majesty.'), ('KAI', 'For a pig?', 'shock'), bg=S('day', room('de', .7), table(.6, 2, 9)))),
 ('Britain accepted it', T(('MARINE', 'Pack up, lads.'), ('SOLDIER', 'No hard feelings?'), ('MARINE', 'None. Mind the pigs.', 'smug'), bg=camp_)),
 ('Today, both camps are part', N('That is about eleven hundred people a day, visiting a war whose only casualty was a pig.', C('≈ 1,100 A DAY', 'VISITORS', 'San Juan Island, 2025', size=160))),
 ('And our two neighbours?', T(('CUT', 'Still not paying.', 'smug'), ('GRF', 'Still waiting.', 'angry'), bg=farm)),
]
chapters = ([s['intro']] if s.get('intro') else []) + s['chapters']
# narration lines that become acted lines
def conv(prefix, newsay, talk):
    for c in chapters:
        for i, b in enumerate(c['beats']):
            if b.get('say', '').startswith(prefix):
                if newsay is None: c['beats'][i] = dict(talk, scene=None) ; c['beats'][i].pop('scene'); return
                b['say'] = newsay; c['beats'].insert(i + 1, talk); return
    raise SystemExit('not found: ' + prefix)
for c in chapters:   # drop an earlier run of this script
    c['beats'] = [b for b in c['beats'] if not b.get('_new')]
n = 0
for after, beat in ADD:
    if beat is None: continue
    beat['_new'] = 1; done = False
    for c in chapters:
        for i, b in enumerate(c['beats']):
            if b.get('say', '').startswith(after) and not done: c['beats'].insert(i + 1, beat); done = True; n += 1; break
    assert done, after
# the famous exchange and two real quotes become acted lines
for c in chapters:
    for i, b in enumerate(c['beats']):
        if b.get('say', '').startswith('Cutlar: It was eating'): c['beats'][i] = {'talk': [{'who': 'CUT', 'text': 'It was eating my potatoes.', 'mood': 'angry'}, {'who': 'GRF', 'text': 'It is up to you to keep your potatoes out of my pig.', 'mood': 'smug'}], 'bg': farm, '_new': 1}
        elif b.get('say', '').startswith('Griffin: It is up to you'): c['beats'][i] = None
        elif b.get('say', '').startswith("And he said the line everyone remembers. Don't"): b['say'] = 'And he said the line everyone remembers.'; c['beats'].insert(i + 1, {'talk': [{'who': 'PIC', 'text': "Don't be afraid of their big guns. We'll make a Bunker Hill of it.", 'mood': 'smug'}], 'bg': camp_, '_new': 1})
        elif b.get('say', '').startswith('He would not, he said, involve two great nations'): c['beats'][i] = None   # now spoken by Baynes himself
    c['beats'] = [b for b in c['beats'] if b is not None]
s['talkNote'] = 'Dialogue scenes are dramatized; every fact comes from the sources below.'
json.dump(s, open(F, 'w'), indent=1, ensure_ascii=False); print('inserted', n, 'beats; talk beats now', sum(1 for c in chapters for b in c['beats'] if 'talk' in b))
