"""American Revolution redo, new style (STYLE.md 2c, owner 15 Nov 2026): acted exchanges about once a minute,
everyday comparisons, callbacks ("Who's paying for this?"), and a cold open that leads with Franklin.
Dialogue is dramatized from the record: real people only act out what the sources say they did or said
(Lord North's "Oh God, it is all over"; William Franklin asking to see his wife); jokes go to unnamed roles.
Safe to run again: it removes its own earlier insertions first."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from lib import *
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../studio/doc/stories/sb-american-revolution.json'); s = json.load(open(F))
BLUE, NAVY, BLACK = '#24407a', '#1d2f5a', '#5a3a22'
s['cast'] = {
 'FRA': {'preset': 'franklin', 'name': 'Benjamin Franklin'}, 'WIL': {'preset': 'governor', 'name': 'Gov. William Franklin', 'spec': {'hair': '#d8d3cb'}},
 'KING': {'preset': 'king_george', 'name': 'King George III'}, 'NORTH': {'preset': 'lord_north', 'name': 'Lord North'},
 'MP': {'preset': 'lord_north', 'name': 'A member of Parliament', 'spec': {'sash': 0, 'medal': 0, 'coat': '#4a3a2a'}},
 'CLERK': {'preset': 'governor', 'name': 'A Treasury clerk', 'spec': {'coat': '#3a3a3a', 'hairStyle': 'short', 'hair': '#5a3a22', 'glasses': 1}},
 'COL': {'preset': 'settler', 'name': 'A colonist'}, 'BOS': {'preset': 'settler', 'name': 'A Bostonian', 'spec': {'coat': '#4a3a2a', 'hat': 'tricorn', 'beard': 'none'}},
 'STAMP': {'preset': 'governor', 'name': 'A stamp collector', 'spec': {'coat': '#5a4a3a'}},
 'PRINTER': {'preset': 'settler', 'name': 'A printer', 'spec': {'hat': 'none', 'beard': 'none', 'coat': '#3a3028'}},
 'RED': {'preset': 'redcoat', 'name': 'A British soldier'}, 'OFF': {'preset': 'redcoat', 'name': 'A British officer', 'spec': {'epaulettes': 1}},
 'MIL': {'preset': 'continental', 'name': 'A militiaman', 'spec': {'coat': '#5a4a3a'}}, 'CAPT': {'preset': 'continental', 'name': 'A rebel captain'},
 'SAILOR': {'preset': 'us_sailor', 'name': 'A British sailor'}, 'COURT1': {'preset': 'governor', 'name': 'A courtier', 'spec': {'coat': '#5a2a3a'}},
 'COURT2': {'preset': 'governor', 'name': 'Another courtier', 'spec': {'coat': '#2a4a3a'}}, 'GUARD': {'preset': 'continental', 'name': 'A guard'},
 'HESS': {'preset': 'hessian', 'name': 'A Hessian soldier'}, 'HESS2': {'preset': 'hessian', 'name': 'A Hessian sentry', 'spec': {'beard': 'none'}},
 'FR1': {'preset': 'french_officer', 'name': 'A French minister'}, 'FR2': {'preset': 'french_officer', 'name': 'A French officer', 'spec': {'hat': 'none'}},
 'LOY': {'preset': 'settler', 'name': 'A Loyalist farmer', 'spec': {'coat': '#7a2a2a'}}, 'PAT': {'preset': 'continental', 'name': 'A Patriot neighbour', 'spec': {'coat': '#4a5a3a', 'hat': 'none'}},
 'FREE': {'preset': 'settler', 'name': 'A man escaping slavery', 'spec': {'skin': '#6b4429', 'hair': '#1c1a1a', 'hat': 'none', 'beard': 'none', 'coat': '#6b5a44'}},
 'DIPGB': {'preset': 'governor', 'name': 'A British negotiator'}, 'DIPUS': {'preset': 'franklin', 'name': 'An American negotiator', 'spec': {'hairStyle': 'wig', 'hair': '#efeae0', 'glasses': 0, 'coat': '#2a2a33'}},
}
s.setdefault('voices', {}).update({'FRA': 'am_michael', 'WIL': 'bm_daniel', 'KING': 'bm_fable', 'NORTH': 'bm_lewis', 'MP': 'bm_fable', 'CLERK': 'bm_daniel',
 'COL': 'am_adam', 'BOS': 'am_puck', 'STAMP': 'bm_lewis', 'PRINTER': 'am_fenrir', 'RED': 'bm_lewis', 'OFF': 'bm_fable', 'MIL': 'am_puck', 'CAPT': 'am_fenrir',
 'SAILOR': 'bm_daniel', 'COURT1': 'bm_lewis', 'COURT2': 'bm_daniel', 'GUARD': 'am_adam', 'HESS': 'am_fenrir', 'HESS2': 'am_puck', 'FR1': 'bm_fable', 'FR2': 'bm_lewis',
 'LOY': 'am_michael', 'PAT': 'am_adam', 'FREE': 'am_fenrir', 'DIPGB': 'bm_lewis', 'DIPUS': 'am_michael'})
# sets
officeuk = S('day', room('uk', .7), table(.6, 0, 8))
treasury = S('night', room('uk', .1, True), table(.5, 3, 12))
court = S('day', room('uk', .7, False, '#4a2a2a'), crowd(40, .99))
boston = S('day', town(14, .74, 160, 130, '#3a3028'), crowd(70))
harbour_night = S('night', sea(.62), ships(3, 'uk', .25, .66, .6, 320), town(8, .64, 120, 160, '#1c1a22'))
west = S('day', hills(.5, 3, 7), forest(.62, 40, 5), land('grass', .74))
printshop = S('day', room(None, .3, False, '#4a3a2a'), table(.6, 0, 14))
green = S('dawn', hills(.55, 2, 4), land('grass', .74), town(5, .7, 120, 200, '#3a3028'))
hill = S('day', hills(.5, 2, 12), land('mud', .74), cannons(1, .7, 300))
cell = S('night', room(None, .05, True, '#2a2a2a'), table(.3, 1, 1, 500))
snow = S('night', land('snow', .74), forest(.62, 30, 8), camp(3, .76, .6, 220, '#d8d0c0', .5), weather='snow')
germancamp = S('dusk', hills(.55, 2, 6), land('mud', .74), camp(5, .76, .1, 220, '#e8e0c8', .45))
paris = S('day', room('fr', .7, False, '#3a3a4a'), table(.6, 2, 6))
burnfarm = S('night', hills(.55, 2, 3), land('grass', .74), farm(.75, .7, .72, True), fire(.72, .62, 260))
camp_uk = S('day', land('mud', .74), camp(5, .76, .1, 220, '#e8e0c8', .45), flagpole('uk', .8))
yorktown = S('day', sea(.6), ships(3, 'fr', .45, .66, .55, 300), coast(-.2, .3, .6, 90))
paristable = S('day', room(None, .7, False, '#3a3a4a'), table(.6, 2, 16))
T = lambda *lines, bg=None: dict(talk=[dict(who=w, text=x, **({'mood': m} if m else {})) for w, x, m in [(l + (None,))[:3] for l in lines]], **({'bg': bg} if bg else {}))
N = lambda say, scene: {'say': say, 'scene': scene}
ADD = [   # (first words of the beat to insert AFTER, the new beat)
 ('Then somebody opened the accounts', T(('CLERK', 'A hundred and thirty-two million, sir.'), ('MP', 'Pounds?', 'shock'), ('CLERK', 'Pounds.'), ('MP', "...Who's paying for this?"), bg=treasury)),
 ('And now Britain had a huge new empire', N("That's thirty pounds a year, for every single soldier.", C('£30 A YEAR', 'FOR EVERY SOLDIER', '7,500 men in America', size=170))),
 ('West of it, the land was reserved', T(('COL', "So we can't go west?"), ('RED', 'Not past the mountains.'), ('COL', 'Who decided that?', 'angry'), ('RED', 'London.'), bg=west)),
 ('The first try was the Stamp Act', T(('PRINTER', 'A stamp? On every newspaper?', 'shock'), ('CLERK', 'And every contract.'), ('PRINTER', 'And the playing cards?'), ('CLERK', 'Especially the playing cards.', 'smug'), bg=printshop)),
 ('The colonies exploded', T(('STAMP', "I'm only the stamp collector!", 'shock'), ('BOS', 'Not any more.', 'angry'), bg=boston)),
 ('Then it tried again, with new taxes', T(('MP', 'Drop the taxes. All but tea.'), ('CLERK', 'Why keep the tea?'), ('MP', 'To prove we can.', 'smug'), bg=officeuk)),
 ('Patriots called it the Boston Massacre', T(('BOS', "John Adams is defending the soldiers?", 'shock'), ('COL', 'Somebody has to.'), bg=boston)),
 ('They did not accept', T(('BOS', 'Cheaper tea?'), ('COL', "Cheaper tea. And Parliament's right to tax it."), ('BOS', 'No, thank you.', 'angry'), bg=boston)),
 ('On the night of the sixteenth of December 1773', N("Ten thousand pounds, over three hundred and forty two chests. About twenty nine pounds a chest. Nearly what London paid to keep one soldier in America for a year. Every chest.", C('≈ £29 A CHEST', '≈ ONE SOLDIER FOR A YEAR', 'Boston Harbor, 16 Dec 1773', size=150))),
 ('The most expensive tea party in history', T(('SAILOR', 'Is that... our tea?', 'shock'), ('BOS', 'What tea?', 'smug'), bg=harbour_night)),
 ("From London, this wasn't a protest", T(('MP', 'They threw it in the sea?', 'angry'), ('CLERK', 'All of it, sir.'), ('MP', "Close the harbour. Until it's paid for.", 'angry'), bg=officeuk)),
 ('On the nineteenth of April 1775', T(('OFF', 'Who fired?', 'shock'), ('MIL', 'Not me!', 'shock'), ('RED', 'Not me either.'), bg=green)),
 ('Two months later, the rebels dug in', T(('MIL', 'Is this Bunker Hill?'), ('CAPT', 'Close enough.', 'smug'), ('MIL', "It's Breed's Hill."), ('CAPT', 'Keep digging.'), bg=hill)),
 ('Britain won. And it was a disaster', N('More than two British soldiers down, for every American.', C('2 FOR 1', 'BRITISH LOSSES FOR EVERY AMERICAN', "Breed's Hill, June 1775", size=170))),
 ('Now the other side. To London, this was a letter', T(('CLERK', 'A petition from the colonies, Your Majesty.'), ('CLERK', "...I'll just leave it here, then.", 'sad'), bg=S('day', room('uk', .7, False, '#5a2a2a'), table(.6, 4, 2)))),
 ("Then, in front of the King's Privy Council", T(('COURT1', 'Did he say anything back?'), ('COURT2', 'Not a word.'), ('COURT1', 'Not one?'), ('COURT2', 'He just stood there.'), bg=court)),
 ('By then, his son had already been arrested', T(('CAPT', 'William Franklin. You are under arrest.'), ('WIL', "I am the King's governor."), ('CAPT', 'Not any more.'), bg=S('day', room('uk', .7), table(.6, 2, 6)))),
 ('While he was there, his wife was dying', T(('WIL', 'Let me see my wife. Please.', 'sad'), ('GUARD', 'Request refused.'), bg=cell)),
 ('Britain had a problem. It had the best navy', T(('MP', 'We need more soldiers.'), ('CLERK', "We don't have more soldiers."), ('MP', 'Then rent some.', 'smug'), bg=officeuk)),
 ('On the night after Christmas, he crossed', T(('HESS2', 'Did you hear something?'), ('HESS', 'Only the river. Nobody attacks at Christmas.', 'smug'), bg=snow)),
 ('For the Germans, this was a war', T(('HESS', 'Remind me why we are here?'), ('HESS2', 'The prince got paid.', 'sad'), bg=germancamp)),
 ('In Paris, Benjamin Franklin had been waiting', T(('FR1', 'Saratoga? A whole British army?', 'shock'), ('FR2', 'Surrendered.'), ('FR1', 'Then perhaps they can win.', 'smug'), bg=paris)),
 ('Britain had started taxing the colonies', T(('CLERK', 'France, Spain and the Dutch, sir.'), ('MP', 'And the bill?'), ('CLERK', 'Bigger.', 'sad'), bg=treasury)),
 ("Inside America, this wasn't one people", T(('LOY', 'You turned me in?', 'angry'), ('PAT', "You'd have done the same."), bg=burnfarm)),
 ('In 1775, the British governor of Virginia', T(('FREE', 'Is it true? Freedom, if we reach the British?'), ('RED', "That is the governor's promise."), bg=camp_uk)),
 ('The Royal Navy never came', T(('RED', 'Ships, sir! Are they ours?', 'happy'), ('OFF', '...French.', 'sad'), bg=yorktown)),
 ('The news took more than a month', N('Thirty seven days, from Yorktown to London.', C('37 DAYS', 'FROM YORKTOWN TO LONDON', '19 Oct – 25 Nov 1781', size=170))),
 ('The new border ran through the middle', T(('DIPGB', 'Through the middle of the Great Lakes.'), ('DIPUS', 'Then down the Mississippi.'), ('DIPGB', 'Where does it start?'), ('DIPUS', 'Up there. Somewhere.', 'smug'), bg=paristable)),
 ('And the losers had to leave', N('Sixty thousand Loyalists, and fifteen thousand enslaved people taken with them. Seventy five thousand people, leaving one country for another.', C('75,000', 'PEOPLE LEFT', '60,000 Loyalists + 15,000 enslaved', size=170))),
 ('Around twenty five thousand Americans died', N('Fewer than one in three of them died in battle.', C('7 IN 25', 'DIED IN BATTLE', 'American deaths, 1775–1783', size=170))),
 ('Two neighbours. Two very different memories', T(('MP', "So... who's paying for this?"), ('COL', 'Not us.', 'smug'), bg=officeuk)),
]
chapters = ([s['intro']] if s.get('intro') else []) + s['chapters']
for c in chapters:   # drop an earlier run of this script
    c['beats'] = [b for b in c['beats'] if not b.get('_new')]
n = 0
for after, beat in ADD:
    beat['_new'] = 1; done = False
    for c in chapters:
        for i, b in enumerate(c['beats']):
            if b.get('say', '').startswith(after) and not done: c['beats'].insert(i + 1, beat); done = True; n += 1; break
    assert done, after
for c in chapters:
    for i, b in enumerate(c['beats']):
        t = b.get('talk')
        if t and t[0]['who'] in ('GB', 'US'):   # the two old countryball exchanges become people in a room
            for l in t: l['who'] = {'GB': 'MP', 'US': 'COL'}[l['who']]
            b.pop('scene', None); b['bg'] = officeuk
        elif b.get('say', '').startswith('Oh God. It is all over'):   # the real quote, spoken by its speaker
            c['beats'][i] = {'talk': [{'who': 'NORTH', 'text': 'Oh God. It is all over.', 'mood': 'shock'}], 'bg': S('day', room('uk', .7), table(.6, 2, 10)), '_quote': 1}
# cold open: lead with the famous name and the twist (STYLE.md 2c)
intro = s['intro']['beats']
if intro[0]['say'].startswith('In 1763'):
    fr = intro.pop(2); fr['say'] = 'Benjamin Franklin helped tear America away from the British Empire. His own son fought just as hard to keep it British.'
    intro.insert(0, fr)
    intro[1]['say'] = 'In 1763, Britain had just won the biggest war the world had ever seen. It took Canada from France. It took Florida from Spain. It was the most powerful empire on Earth.'
s['talkNote'] = 'Dialogue scenes are dramatized; every fact comes from the sources below.'
json.dump(s, open(F, 'w'), indent=1, ensure_ascii=False)
print('inserted', n, 'beats; talk beats now', sum(1 for c in chapters for b in c['beats'] if 'talk' in b))
