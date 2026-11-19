"""Two "Do you know" Shorts for sb-vice-city (RUNBOOK 3b)."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vc_kit import *
from vc_part1 import B, T
ep = json.load(open(os.path.join(os.path.dirname(__file__), '..', '..', 'studio', 'doc', 'stories', 'sb-vice-city.json')))
base = {k: ep[k] for k in ('brand', 'narrator', 'era', 'musicEra', 'balls', 'places', 'cast', 'voices', 'photos', 'talkNote')}
S1 = [
  B("Do you know a hijacked bus in Havana sent a hundred and twenty five thousand people to the real Vice City?",
    S('day', town(n=12, col='#d8c8a8'), bus(drive=[1.3, .45, 0, 3])), cam={'lon': -82.37, 'lat': 23.11, 'scale': 9000}),
  B("The first of April 1980. Héctor Sanyustiz and four friends empty a city bus, route 79, by pretending it has broken down.",
    S('day', town(n=10, col='#d8c8a8'), bus(x=.5, y=.95, s=.9), crowd(n=16, y=1.0))),
  T([('DRV', "Everybody off. The bus is broken."), ('HEC', "Stay on the bus.")], S('day', bus(x=.5, y=1.02, s=1.3), push=.1)),
  B("Then he floors it, through the fence of the Peruvian embassy. Guards open fire. One guard is killed in the crossfire.",
    S('day', fence(broken=.55), bus(x=.55, y=.95), fx=['dust', 'smoke'], push=.15)),
  B("Peru refuses to hand them back. So Castro pulls every guard away from the embassy. In about two days, ten thousand eight hundred people pour in.",
    S('day', fence(), crowd(n=140, y=1.0), push=.05)),
  B("Then he opens the port of Mariel to anyone who wants to leave. Exiles in Miami sail south to fetch their families.",
    S('day', sea(y=.56), boats(n=4, y=.72, drift=1))),
  B("By October, about a hundred and twenty five thousand Cubans have crossed to Florida. Most of them settle in Miami. All because of one bus.",
    S('night', city(h=360), palms(y=.98, n=5, h=330, d=.85), neon('VICE CITY', y=.3), push=.1)),
]
S2 = [
  B("Do you know Al Capone bought his Miami mansion from a beer family?",
    S('day', sea(y=.64), coast(x0=.2, x1=.8, y=.64, h=40), palms(y=.7, n=6, x0=.22, gap=.09, h=220, d=.4)), cam={'lon': -80.17, 'lat': 25.78, 'scale': 9000}),
  B("1928. Prohibition. Alcohol is illegal across America, and Capone, the boss of Chicago, has made a fortune selling it anyway.",
    P('capone', 'Al Capone')),
  B("He wants somewhere warm. So he buys a house on Palm Island, a man made island dug out of Biscayne Bay, for forty thousand dollars, in cash.",
    S('day', palms(y=.84, n=5), land('sand', y=.78), A(('capone', .4, 'hold', {'prop': 'coin'})))),
  T([('CAP', "Who owned it?"), ('AGENT', "Mr Busch. The brewing family."), ('CAP', "I'll take it. Cash.")],
    S('day', room(wall='#e8dcc8', window=.6), table(papers=2, w=700))),
  B("The seller: Clarence Busch, of the beer brewing Busch family. A brewer, selling his house to the king of illegal beer.",
    C('$40,000', 'IN CASH', 'Palm Island, 1928', size=200)),
  B("Miami's newspaper campaigns to drive him out. He stays, adds a pool and a guest house for armed guards, and dies there in 1947.",
    S('dusk', palms(y=.84, n=4, wind=.05), sea(y=.66), push=.05)),
  B("Gangsters, sunshine and money from somewhere else. The real Vice City had it all, long before the game.",
    S('night', sea(y=.66), boats(n=1, crowded=False, y=.78, s=.7, drift=1), palms(y=.92, n=3, h=330, d=.85), neon('VICE CITY', y=.3))),
]
srcs = [x for x in ep['sources'] if any(k in x for k in ('Sanyustiz', 'Peruvian', 'Mariel', 'mariel', 'Havana', 'Capone', 'capone', 'Prohibition', 'Palm Island', 'Busch'))]
for n, beats, title in ((1, S1, 'Do You Know a Hijacked Bus Sent 125,000 People to the Real Vice City? #shorts'), (2, S2, "Do You Know Al Capone Bought His Miami Mansion From a Beer Family? #shorts")):
    st = dict(base, id='sb-vice-city-short%d' % n, short=True, film=True, photosFrom='sb-vice-city', title=title, intro=dict(mood='tension', beats=beats), chapters=[], sources=srcs)
    json.dump(st, open(os.path.join(os.path.dirname(__file__), '..', '..', 'studio', 'doc', 'stories', 'sb-vice-city-short%d.json' % n), 'w'), indent=1, ensure_ascii=False)
print('ok')
