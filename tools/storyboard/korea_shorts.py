#!/usr/bin/env python3
"""The two "Do you know" Shorts for sb-korea-38th (RUNBOOK 3b). Each is its own story, built on one fact from the episode,
checked again on 26 Nov 2026 on the Wikipedia pages listed in its sources:
  short1: Bonesteel proposed the 38th parallel on 10 Aug 1945 and commanded US Forces Korea 1966-69 (Charles_H._Bonesteel_III).
  short2: Japan and Russia had discussed sharing Korea along the same parallel forty years earlier; the two officers were
          unaware; Rusk "almost surely" would have chosen a different line (Division_of_Korea).
Run: python3 tools/storyboard/korea_shorts.py"""
import json, os
D = os.path.join(os.path.dirname(__file__), '..', '..', 'studio', 'doc', 'stories')
ep = json.load(open(os.path.join(D, 'sb-korea-38th.json')))
SRC = ep['sources']

def card(t, p, d, size=140): return {"shot": "card", "time": t, "place": p, "date": d, "size": size}
def doc(h, lines, hl=1): return {"shot": "doc", "kind": "letter", "header": h, "lines": lines, "hl": hl}
def photo(img, cap=None, move="in"):
    s = {"shot": "photo", "img": img, "move": move}
    if cap: s["caption"] = cap
    return s
OFFICE = {"shot": "set", "time": "night", "parts": [{"type": "room", "flag": "us", "window": 0.1, "night": True, "depth": 0.3},
          {"type": "table", "lamp": 0.5, "candles": 1, "papers": 8, "w": 900, "depth": 0.6}]}
SNOW = {"shot": "set", "time": "night", "parts": [{"type": "hills", "y": 0.5, "n": 3, "seed": 15, "depth": 0.2},
        {"type": "forest", "y": 0.64, "n": 40, "seed": 3, "h": 160, "depth": 0.45}, {"type": "land", "kind": "snow", "y": 0.74, "depth": 0.6}],
        "weather": "snow", "fx": ["fog"]}
FARM = {"shot": "set", "time": "day", "parts": [{"type": "hills", "y": 0.5, "n": 3, "seed": 128, "depth": 0.15},
        {"type": "farm", "x": 0.3, "s": 0.7, "y": 0.72, "night": False, "depth": 0.6}, {"type": "land", "kind": "grass", "y": 0.76, "depth": 0.6},
        {"type": "people", "list": [{"x": 0.36, "facing": 1, "h": 0.85, "preset": "korean", "pose": "point"},
         {"x": 0.62, "facing": -1, "h": 0.82, "preset": "woman", "spec": {"hair": "#1c1a1a", "skin": "#efc49c", "coat": "#e8e2d4"}}],
         "lx": 0.4, "ly": 0.6, "depth": 0.8}]}
MAP = {"lon": 127.0, "lat": 38.0, "scale": 4500}
def B(say, scene, **k): return dict({"say": say, "scene": scene}, **k)
def T(lines, bg): return {"talk": [dict({"who": w, "text": t}, **({"mood": m[0]} if m else {})) for w, t, *m in lines], "bg": bg}

def short(sid, title, beats, srcs):
    sh = {k: ep[k] for k in ("brand", "narrator", "era", "musicEra", "places", "voices", "photos", "talkNote")}
    sh["cast"] = dict(ep["cast"], BONE={"preset": "us_officer", "name": "Col. Charles Bonesteel", "spec": {"hat": "none", "hair": "#6b4a2a", "glasses": 0}},
                      BONE66={"preset": "us_officer", "name": "Gen. Charles Bonesteel, 1966", "spec": {"hair": "#b8b0a4", "glasses": 0}})
    sh["voices"] = dict(ep["voices"], BONE=ep["voices"].get("AIDE2", "am_adam"), BONE66=ep["voices"].get("AIDE2", "am_adam"))
    sh.update({"balls": {}, "id": sid, "short": True, "film": True, "photosFrom": "sb-korea-38th", "title": title,
               "intro": {"mood": "tension", "beats": beats}, "chapters": [], "sources": srcs})
    json.dump(sh, open(os.path.join(D, sid + '.json'), 'w'), indent=1, ensure_ascii=False)
    print('wrote', sid, sum(len(b.get('say', '').split()) + sum(len(t['text'].split()) for t in b.get('talk', [])) for b in beats), 'words')

short("sb-korea-38th-short1", "Do You Know the Man Who Split Korea Came Back to GUARD the Line? #shorts", [
 B("Do you know the man who drew the line across Korea came back, twenty one years later, to guard it?", card("1945 → 1966", "THE 38TH PARALLEL", "one man, both ends"), cam=MAP),
 B("Tenth of August 1945. Soviet troops are pouring into northern Korea. In Washington, a colonel named Charles Bonesteel needs a line. Tonight.", photo("bonesteel", "Charles H. Bonesteel III")),
 T([("AIDE", "Where do we stop them?"), ("BONE", "North of Seoul. The thirty-eighth parallel.")], OFFICE),
 B("He proposes it on a National Geographic map. Six days later, Moscow says yes. It is meant to be temporary.", {"shot": "map-desk", "push": 0.12, "pan": [60, 40]}),
 B("Then come two Koreas, and a war that kills millions.", photo("refugees", "Refugees in Korea", move="out")),
 B("In 1966, Bonesteel is a general. And the army sends him to Korea, to command American forces along the border he proposed.", card("1966", "SEOUL", "Commander, US Forces Korea")),
 T([("GI1", "Sir, you know this line well?"), ("BONE66", "Better than anyone, son.", "sad")], SNOW),
 B("Three years of raids and clashes follow. Historians call it the Korean DMZ Conflict.", photo("dmz", "DMZ fence, August 1968", move="out")),
 B("He retires in 1969. The line he drew in one night is still there.", card("TODAY", "THE DMZ", "still there"), pause=1.0),
], [SRC[8], SRC[0]])

short("sb-korea-38th-short2", "Do You Know Korea Was Almost Split on the SAME Line 40 Years Earlier? #shorts", [
 B("Do you know Korea's border was almost drawn on the very same line, forty years before the Americans drew it?", card("40 YEARS EARLIER", "THE SAME PARALLEL", "Japan and Russia"), cam=MAP),
 B("August 1945. Two American colonels, Dean Rusk and Charles Bonesteel, choose the thirty-eighth parallel to split Korea.", photo("bonesteel", "Charles H. Bonesteel III")),
 T([("RUSK", "Seoul stays on our side."), ("BONE", "Then the thirty-eighth it is.")], OFFICE),
 B("What they did not know: about forty years earlier, Japan and the Russian Empire had already discussed sharing Korea. Along the same parallel.", doc("Japan and Russia, 40 years earlier (paraphrase)", ["Korea, shared", "along the 38th parallel"])),
 B("Korea was never asked either time.", FARM),
 B("Years later, Rusk admitted it. If he had known Korean history, he said, he would almost surely have chosen a different line.", doc("Dean Rusk, later", ["...almost surely,", "have chosen a different line."], hl=0)),
 B("He did not. And that line split a country for more than eighty years.", photo("dmz", "DMZ fence, August 1968", move="out"), pause=1.0),
], [SRC[0], SRC[6]])
