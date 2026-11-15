"""American Revolution redo: the story was 19.9 minutes, under the 25-minute minimum (owner, 15 Nov 2026: 25 when the topic is
fully covered, never pad). This adds the parts of the hidden person's story that were missing, all from pages opened on 15 Nov 2026
(Wikipedia: William Franklin, Asgill Affair, William Temple Franklin, Hutchinson letters affair):
the leaked letters behind Benjamin's humiliation, William's advice, Temple the grandson, a new chapter on William's war in New York
and the Huddy-Asgill affair (1782), and the father-son ending (the claims money, the 1784 letters, the balloon airmail, the will's
real words). Safe to run again: it removes its own earlier insertions first. Run before amrev_talk.py."""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); from lib import *
F = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../../studio/doc/stories/sb-american-revolution.json'); s = json.load(open(F))
NEWSRC = ['Wikipedia, William Franklin: https://en.wikipedia.org/wiki/William_Franklin',
          'Wikipedia, Asgill Affair: https://en.wikipedia.org/wiki/Asgill_Affair',
          'Wikipedia, William Temple Franklin: https://en.wikipedia.org/wiki/William_Temple_Franklin',
          'Wikipedia, Hutchinson letters affair: https://en.wikipedia.org/wiki/Hutchinson_letters_affair']
s['sources'] = [x for x in s['sources'] if x not in NEWSRC] + NEWSRC
s['photos']['asgill'] = ['File:Sir Charles Asgill 2nd Baronet.jpg', False]
s.setdefault('cast', {}).update({
 'DRUM': {'preset': 'continental', 'name': 'A drummer boy', 'spec': {'hat': 'none', 'hair': '#8a6a3a'}},
 'DEL1': {'preset': 'governor', 'name': 'A member of Congress', 'spec': {'coat': '#3a2a1a'}},
 'DEL2': {'preset': 'governor', 'name': 'Another member', 'spec': {'coat': '#2a3a2a', 'hairStyle': 'short', 'hair': '#5a3a22'}},
 'SHIPCAP': {'preset': 'rn_officer', 'name': "The ship's captain"}, 'MAID': {'preset': 'governor', 'name': 'A servant', 'spec': {'coat': '#4a4a4a', 'hairStyle': 'short', 'hair': '#6b4a2a'}},
 'RAID1': {'preset': 'settler', 'name': 'A Loyalist raider', 'spec': {'coat': '#7a2a2a', 'hat': 'tricorn'}}, 'RAID2': {'preset': 'settler', 'name': 'Another raider', 'spec': {'coat': '#4a3a2a', 'beard': 'none'}},
 'FISH': {'preset': 'settler', 'name': 'A fisherman', 'spec': {'hat': 'none', 'coat': '#3a4a5a'}}, 'DOVER': {'preset': 'us_sailor', 'name': 'A sailor at Dover', 'spec': {'coat': '#1d2f5a'}},
})
s.setdefault('voices', {}).update({'DRUM': 'am_puck', 'DEL1': 'am_michael', 'DEL2': 'am_fenrir', 'SHIPCAP': 'bm_lewis', 'MAID': 'bf_emma',
 'RAID1': 'am_adam', 'RAID2': 'am_puck', 'FISH': 'bm_daniel', 'DOVER': 'bm_lewis'})
T = lambda *lines, bg=None: dict(talk=[dict(who=w, text=x, **({'mood': m} if m else {})) for w, x, m in [(l + (None,))[:3] for l in lines]], **({'bg': bg} if bg else {}))
N = lambda say, scene: {'say': say, 'scene': scene}
# sets
boston_n = S('night', town(14, .74, 160, 130, '#2a2430'), crowd(80), fire(.5, .62, 200))
printshop = S('day', room(None, .3, False, '#4a3a2a'), table(.6, 0, 14))
nyc = S('dusk', sea(.66), ships(4, 'uk', .1, .68, .5, 280), town(16, .66, 170, 120, '#2a2430'))
raid = S('night', forest(.62, 50, 9), land('mud', .76), soldiers(10, '#5a3a2a', 2, .3, 90, .88, True))
monmouth = S('dawn', sea(.64), coast(-.1, .5, .64, 80), land('sand', .76), weather='fog')
tavern = S('night', room(None, .05, True, '#3a2a1c'), table(.5, 4, 3))
usoffice = S('day', room('us', .7), table(.6, 2, 8))
congress = S('day', room('us', .7, False, '#3a2a1c'), crowd(50, .99))
versailles = S('day', room('fr', .7, False, '#4a4a5a'), table(.6, 4, 4))
ukroom_n = S('night', room('uk', .1, True), table(.5, 3, 2))
crossing = S('dusk', sea(.6), ships(2, 'uk', .3, .66, .6, 420), weather='storm')
garden = S('dusk', hills(.55, 2, 14), land('grass', .74), forest(.66, 18, 2, 120), farm(.8, .6, .72))
channel = S('day', sea(.66), coast(.6, 1.1, .66, 110), ships(1, 'uk', .2, .68, .5))
paristable = S('day', room(None, .7, False, '#3a3a4a'), table(.6, 2, 16))
london = S('day', room('uk', .7), table(.6, 0, 10))
AFTER = [   # (first words of the beat to insert AFTER, [new beats])
 ("Now rewind a little, because here's where the Franklins", [
   N('Here is how it went wrong. In December 1772, Franklin gets hold of about twenty private letters, written by the men who run Massachusetts, among them Thomas Hutchinson.',
     D(['"...an abridgement of what are called English liberties..."'], 'Private letters, 1768–1769', sign='T. Hutchinson')),
   N('He sends them to Boston, with one condition. Do not publish them. By June 1773, they are in a Boston newspaper.', NEWS('~ BOSTON, 1773 ~', ["THE GOVERNOR'S LETTERS"], 'June 1773')),
   T(('BOS', '"Not to be published," it says.'), ('PRINTER', 'Then why is it on my front page?', 'smug'), bg=printshop),
   N('Crowds burn the governor in effigy on Boston Common. And in London, two men fight a duel over who leaked the letters.', boston_n),
   N('So on Christmas Day 1773, Franklin publishes a letter admitting that he sent them, to stop a second duel.', D(['Franklin admits he sent', 'the Hutchinson letters to Boston,', 'to prevent "further mischief".'], 'London, 25 December 1773', sign='B. Franklin')),
 ]),
 ("Then, in front of the King's Privy Council", [
   N('That was the twenty ninth of January 1774. The lawyer was the Solicitor General, Alexander Wedderburn. Soon after, Franklin was fired from his post as Postmaster General.', C('29 JANUARY 1774', 'THE PRIVY COUNCIL, LONDON', 'Franklin stands in silence', size=120)),
 ]),
 ('His son William had taken a different road', [
   N("His father expected him to resign in protest. William's advice to his father, in short: take your medicine, and retire.", P('wfranklin', 'William Franklin', 'in', focus=[.5, .3])),
   N('His Two Roads speech asked New Jersey to choose loyalty over civil war. The assembly answered by voting, unanimously, to support Boston.', S('day', room('uk', .7, False, '#3a2a2a'), crowd(40, .99))),
 ]),
 ('His father was in France by then', [
   N("And with him went a sixteen year old secretary. Temple Franklin. William's own son, raised by his grandfather.", paristable),
 ]),
 ('And the Franklins? At the peace talks, Benjamin refused', [
   N('His grandson Temple, the secretary at those same talks, quietly asked one of the British negotiators if something could be done for his father.', paristable),
   N('In London, the British government paid William one thousand eight hundred pounds. That was the value of his furniture. Nothing for his lands. Plus a pension of eight hundred pounds a year.',
     C('£1,800', 'FOR HIS FURNITURE', 'nothing for his lands', size=170)),
   N('Eight hundred pounds a year. About what it once cost to keep twenty six British soldiers in America.', C('£800 A YEAR', '≈ 26 SOLDIERS', 'at £30 a soldier', size=170)),
 ]),
 ('William wrote to his father', [
   N('His father wrote back that they would try, as William proposed, to forget what had happened, as well as they could.',
     D(['"...will endeavor, as you propose', 'mutually to forget what has happened', 'relating to it, as well we can."'], 'Passy, 16 August 1784', sign='B. Franklin')),
   N('They met once more, in England, in 1785. Briefly. To tie up money and land.', london),
   N('That same winter, in January 1785, a letter from William to his son Temple crossed the English Channel in a hydrogen balloon. The first airmail in history.', C('JANUARY 1785', 'THE ENGLISH CHANNEL', 'the first airmail', size=130)),
   T(('FISH', 'Is that... a balloon?', 'shock'), ('DOVER', 'Carrying the post.', 'smug'), bg=channel),
 ]),
 ('In his will, Benjamin left his son', [
   N('The part he acted against me in the late war, which is of public notoriety, will account for my leaving him no more of an estate he endeavoured to deprive me of.',
     D(['"The part he acted against me in the late war,', 'which is of public notoriety, will account for', 'my leaving him no more of an estate', 'he endeavoured to deprive me of."'], 'Last will of Benjamin Franklin, 1788', sign='B. Franklin')),
 ]),
]
CUES = {'cold': 'Polite', 'money': 'Careful', 'reasoning': 'why'}
REPLACE = {   # first words -> new narration (the old wording kept in _orig, so a rerun can restore it)
 'William wrote to his father': 'On the twenty second of July 1784, William wrote to his father, hoping to make peace. The answer came three weeks later. Polite. Careful.',
 'In his will, Benjamin left his son': 'In his will of 1788, Benjamin left his son some land in Nova Scotia that was worth almost nothing. And he wrote down why.',
}
CHAPTER = {'title': 'The Unfortunate Ticket', 'years': '1778 – 1782', 'mood': 'tension', '_more': 1, 'beats': [
 N('Back to William. In 1778, he walks out of prison in a prisoner exchange, and goes straight to New York, held by the British.', C('1778', 'NEW YORK CITY', 'held by the British', size=170)),
 N('There, he becomes the leader of the Loyalists. He builds a network of spies, and raises Loyalist fighting units.', nyc),
 N('He wants a guerrilla war against the rebels. The British commander, General Henry Clinton, has little use for the idea, or for Loyalists.', S('day', room('uk', .7), table(.6, 0, 6))),
 N('But by 1780, William has official blessing. A group called the Associated Loyalists starts raiding New York, New Jersey and Connecticut.', raid),
 T(('RAID1', 'Where tonight?'), ('RAID2', 'New Jersey. Again.'), bg=raid),
 N('In New Jersey, neighbours are now killing neighbours, and every killing gets an answer.', S('night', hills(.55, 2, 3), land('grass', .74), farm(.75, .7, .72, True), fire(.72, .62, 240))),
 N('In March 1782, a Loyalist named Philip White is killed by Patriot militiamen. Accounts differ. One says he was shot trying to escape. Another says he was executed.', S('dusk', hills(.55, 2, 21), land('mud', .74), forest(.64, 30, 4))),
 N('On the twelfth of April, Loyalists take a Patriot militia captain, Joshua Huddy, and hang him by the shore. Huddy was not even there when White was killed.', monmouth),
 N('On his body, they leave a note.', D(['"Up goes Huddy for Philip White."'], 'Monmouth, New Jersey, 12 April 1782', kind='letter')),
 N('The men who did it belonged to William Franklin\'s Associated Loyalists. One account says he signed the order himself. Historians still argue how much he knew.', P('wfranklin', 'William Franklin', 'out', focus=[.5, .3])),
 N('Washington demands the officer who led the hanging, Richard Lippincott. A British court martial tries him, and lets him go.', usoffice),
 N('So Washington decides that someone else will pay. A British officer, of the same rank as Huddy, chosen by lot.', C('1 OFFICER', 'CHOSEN BY LOT', 'for one hanging', size=170)),
 N('The twenty seventh of May 1782. The Black Bear Tavern, in Lancaster, Pennsylvania. The names of captured British officers are drawn. A drummer boy pulls out one name, and with it, a paper marked Unfortunate.',
   C('27 MAY 1782', 'BLACK BEAR TAVERN', 'Lancaster, Pennsylvania', size=140)),
 T(('DRUM', 'Captain Charles Asgill.'), ('DRUM', '...And this one says "Unfortunate".', 'sad'), bg=tavern),
 N('Charles Asgill is a young captain, captured at Yorktown. And that is the problem. The Yorktown surrender, which Washington himself signed, protects him from exactly this.', P('asgill', 'Captain Charles Asgill', 'in', focus=[.5, .3])),
 N('Washington writes that the choice has distressed him exceedingly. But the order stands.', D(['"...has distressed me exceedingly."'], 'George Washington to Benjamin Lincoln, 1782', sign='G. Washington')),
 N('In England, Asgill\'s mother hears the news. Lady Asgill writes to the court of France, begging for her son\'s life.', ukroom_n),
 N('And here is the strangest turn of the whole war. King Louis the Sixteenth and Queen Marie Antoinette, at war with Britain, ask Washington to spare a British officer.', versailles),
 N('Their foreign minister, the Comte de Vergennes, writes to Washington on the twenty ninth of July.', D(['"...you will do what is', 'agreeable to their Majesties."'], 'Versailles, 29 July 1782', sign='Vergennes')),
 N('The French letter is read out in Congress on the very day it was planning to vote on hanging him.', congress),
 T(('DEL1', 'A letter. From the King of France.'), ('DEL2', 'Today? Of all days?', 'shock'), bg=congress),
 N('On the seventh of November 1782, after days of debate, Congress lets him go.', C('7 NOVEMBER 1782', 'PHILADELPHIA', 'Asgill is released', size=130)),
 N('A hundred and sixty four days, from the paper marked Unfortunate, to freedom.', C('164 DAYS', 'WAITING TO LEARN IF HE WOULD HANG', '27 May – 7 Nov 1782', size=170)),
 N('He rides for New York, misses his ship, pays a crew to row him out to catch it, and reaches England on the eighteenth of December.', crossing),
 N("At home, he hides in the bulrushes at the end of the garden, and sends the ship's captain in first with a letter, so the shock won't hurt his parents.", garden),
 T(('SHIPCAP', 'A letter, my lady. Good news.'), ('MAID', "She won't come down. She thinks it's bad news.", 'sad'), bg=S('dusk', room('uk', .5), table(.6, 2, 1))),
 N('The whole affair stalled the peace talks in Paris. And sitting at those talks, for the Americans, was Benjamin Franklin. A crisis his son\'s men had started, landing on his father\'s table.', paristable),
 N('By then, William had already sailed for Britain. He left America in 1782, and never came back.', S('dusk', sea(.6), ships(1, 'uk', .5, .66, .7, 0), coast(-.2, .25, .6, 80))),
]}
# undo an earlier run
s['chapters'] = [c for c in s['chapters'] if not c.get('_more')]
for c in s['chapters']:
    c['beats'] = [b for b in c['beats'] if not b.get('_more')]
    for b in c['beats']:
        if '_orig' in b: b['say'] = b.pop('_orig')
        for d in b.get('do', []):
            if '_on' in d: d['on'] = d.pop('_on')
for after, beats in AFTER:
    hit = False
    for c in s['chapters']:
        for i, b in enumerate(c['beats']):
            if b.get('say', '').startswith(after):
                for k, nb in enumerate(beats): nb['_more'] = 1; c['beats'].insert(i + 1 + k, nb)
                hit = True; break
        if hit: break
    assert hit, after
for pre, new in REPLACE.items():
    hit = [b for c in s['chapters'] for b in c['beats'] if b.get('say', '').startswith(pre) and not b.get('_more')]
    assert hit, pre; hit[0]['_orig'] = hit[0]['say']; hit[0]['say'] = new
    for d in hit[0].get('do', []):   # keep the word cues on words that are still spoken
        d['_on'] = d.get('_on', d['on']); d['on'] = CUES.get(d['_on'], d['_on'])
for nb in CHAPTER['beats']: nb['_more'] = 1
k = [i for i, c in enumerate(s['chapters']) if c['title'] == 'It Is All Over'][0]
s['chapters'].insert(k + 1, CHAPTER)
for c in s['chapters']:
    if c['title'] == 'Father Against Son': c['years'] = '1772 – 1777'
json.dump(s, open(F, 'w'), indent=1, ensure_ascii=False)
print('chapters', len(s['chapters']), 'new beats', sum(len(b) for _, b in AFTER) + len(CHAPTER['beats']))
