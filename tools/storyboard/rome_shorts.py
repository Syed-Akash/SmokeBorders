"""Builds the two 'Do you know' Shorts for sb-rome-carthage (RUNBOOK 3b), 24 Nov 2026. Scenes reuse the episode's specs."""
import json, os
D = os.path.join(os.path.dirname(__file__), '..', '..', 'studio', 'doc', 'stories')
ep = json.load(open(os.path.join(D, 'sb-rome-carthage.json')))
beats = [b for c in [ep['intro']] + ep['chapters'] for b in c['beats']]
def find(start): return next(b for b in beats if b.get('say', '').startswith(start) or (b.get('talk') and b['talk'][0]['text'].startswith(start)))
def sc(start): b = find(start); return b.get('scene') or b.get('bg')
def B(say, scene, **k): d = {"say": say, "scene": scene}; d.update(k); return d
def card(t, p, d): return {"shot": "card", "time": t, "place": p, "date": d}
def short(sid, title, bs, srcs):
    sh = {k: ep[k] for k in ("brand", "narrator", "era", "musicEra", "places", "cast", "voices", "photos", "talkNote")}
    sh.update({"balls": {}, "id": sid, "short": True, "film": True, "photosFrom": "sb-rome-carthage", "title": title, "intro": {"mood": "tension", "beats": bs}, "chapters": [], "sources": srcs})
    json.dump(sh, open(os.path.join(D, sid + '.json'), 'w'), indent=1, ensure_ascii=False); print(sid, sum(len(b.get('say', '').split()) for b in bs), 'words')
S = ep['sources']
short("sb-rome-carthage-short1", "Do You Know Rome ORDERED Its Soldiers Not to Kill Archimedes? #shorts", [
 B("Do you know a Roman general gave orders that Archimedes must not be killed, and a Roman soldier killed him anyway?", sc("One of the cities that went over"), cam={"lon": 15.29, "lat": 37.08, "scale": 9000}),
 B("Syracuse, Sicily, 213 BC. Rome besieges the city. Inside lives the most famous inventor in the Greek world.", card("213 BC", "SYRACUSE", "the Roman siege begins")),
 B("His huge crane with a hook reaches over the wall, lifts Roman ships out of the sea, and drops them.", sc("Archimedes built machines")),
 {"talk": find("What is that thing")['talk'], "bg": sc("What is that thing")},
 B("In 212 BC, the Romans climb the walls at night. Their commander, Marcellus, orders that Archimedes be spared.", sc("Syracuse held out")),
 B("A soldier finds him at home, still working. Archimedes rudely tells him to leave. The soldier doesn't know who he is, and kills him on the spot.", sc("A Roman soldier found him"), pause=1.0),
 B("Rome captured the city. And lost the one man it wanted alive.", card("212 BC", "ARCHIMEDES", "killed against orders")),
], [S[17]])
short("sb-rome-carthage-short2", "Do You Know a Roman Admiral Threw the SACRED CHICKENS Overboard? #shorts", [
 B("Do you know a Roman admiral threw the sacred chickens into the sea, and then lost almost his whole fleet?", sc("And then there is the admiral"), cam={"lon": 12.51, "lat": 38.0, "scale": 9000}),
 B("249 BC, off Sicily. Rome is at war with Carthage. Its admiral, Claudius Pulcher, is about to attack at Drepana.", card("249 BC", "DREPANA, SICILY", "Claudius Pulcher attacks")),
 B("Before the attack, the priests report that the sacred chickens will not eat. A very bad omen.", sc("Admiral... the chickens")),
 {"talk": find("Admiral... the chickens")['talk'], "bg": sc("Admiral... the chickens")},
 B("So, the story goes, Pulcher threw them overboard, and said that if they would not eat, they could drink.", sc("And then there is the admiral")),
 B("He lost ninety three of his hundred and twenty ships. Nearly four in every five.", card("93 OF 120", "SHIPS LOST", "Drepana, 249 BC"), pause=1.0),
 B("Ninety three warships, lost after a joke about chickens.", card("93 WARSHIPS", "ONE JOKE", "Drepana, 249 BC")),
], [S[0], S[1]])
