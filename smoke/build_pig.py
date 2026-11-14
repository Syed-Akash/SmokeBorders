"""Builds studio/doc/stories/sb-pig-war.json. B(say, *actions, cam=...) where an action is (word, dict)."""
import json, sys
OUT = '/home/user/Flagbomb/studio/doc/stories/sb-pig-war.json'

REG = {"lon": -123.0, "lat": 48.4, "scale": 20000}      # Vancouver Island to Puget Sound
ISL = {"lon": -123.05, "lat": 48.52, "scale": 45000}    # the San Juan Islands
CAMP = {"lon": -123.0, "lat": 48.47, "scale": 90000}    # south end of San Juan Island
NW = {"lon": -122.5, "lat": 47.5, "scale": 5200}        # Oregon Country
NA = {"lon": -98.0, "lat": 44.0, "scale": 1300}         # North America
ATL = {"lon": -45.0, "lat": 45.0, "scale": 620}         # London to Washington

def B(say, *acts, cam=None, **kw):
    b = {"say": say, "do": [dict(a[1], on=a[0]) if a[0] else dict(a[1]) for a in acts]}
    if cam: b["cam"] = cam
    b.update(kw)
    return b
def zh(w): return (w, {"zoomhit": 1})
def mood(w, who, m): return (w, {"mood": [who, m]})
def pin(w, p): return (w, {"pin": p})
def big(w, t, d=2.4): return (w, {"card": {"kind": "big", "text": t, "dur": d}})
def stamp(w, t, d=2.6): return (w, {"card": {"kind": "stamp", "text": t, "dur": d}})
def stat(w, rows, note=None, d=4.0):
    c = {"kind": "stat", "rows": rows, "dur": d}
    if note: c["note"] = note
    return (w, {"card": c})
def quote(w, t, who, d=4.0): return (w, {"card": {"kind": "quote", "text": t, "who": who, "dur": d}})
def show(w, *ids): return (w, {"show": list(ids)})
def hide(w, *ids): return (w, {"hide": list(ids)})
def speak(w, who, t): return (w, {"say": [who, t]})
def date(w, t): return (w, {"date": t})
def arrow(w, pts, color="#1f6fd1", big_=False):
    a = {"arrow": pts, "color": color}
    if big_: a["big"] = 1
    return (w, a)
def hl(w, names, color): return (w, {"hl": names, "color": color})
def label(w, text, lon, lat, color="#f3e7cf"): return (w, {"label": {"text": text, "lon": lon, "lat": lat, "color": color}})

RED, BLUE = "#c8102e", "#1f6fd1"
HARO = [[-123.25, 48.75], [-123.2, 48.55], [-123.1, 48.3]]
ROSARIO = [[-122.75, 48.75], [-122.73, 48.55], [-122.78, 48.3]]
P49 = [[-128.0, 49.0], [-123.3, 49.0]]

intro = {"mood": "tension", "beats": [
 B("June the fifteenth, 1859. On a small island between British Vancouver Island and the United States, a farmer looks up from his potato patch. A pig is eating his potatoes. Again.",
   date("June", "15 JUNE 1859"), pin("island", "San Juan Island"), show("farmer", "CUT"), mood("Again", "CUT", "angry"), zh("pig"), cam=ISL),
 B("He picks up his rifle and shoots it dead.",
   ("shoots", {"shot": 1}), mood("dead", "CUT", "shock"), big("dead", "ONE PIG", 2.0)),
 B("Within two months, four hundred and sixty-one American soldiers and fourteen cannon are dug in on that island. Facing them are five British warships, seventy guns, and more than two thousand men.",
   show("American", "US"), ("cannon", {"cannon": [-123.02, 48.47]}), show("British", "RN"), ("guns", {"boom": 0.5}),
   stat("thousand", [["US soldiers", "461"], ["US cannon", "14"], ["British warships", "5"], ["British guns", "70"], ["British men", "2,140"]], "10 August 1859", 4.4), cam=REG),
 B("Two of the most powerful nations on Earth are one mistake away from war. Over a pig.",
   mood("powerful", "US", "angry"), mood("mistake", "RN", "angry"), zh("pig"), ("pig", {"shake": 0.4})),
 B("This is the Pig War of 1859, Britain against America, told from both sides. And at its heart are two neighbours almost nobody remembers.",
   label("Pig", "THE PIG WAR", -123.05, 48.62, "#ff6a1f"), mood("Britain", "RN", "neutral"), zh("neighbours"), cam=ISL),
 B("Lyman Cutlar, the American farmer from Kentucky who fired the shot. And Charles Griffin, the Irishman who owned the pig, and ran a British company's sheep farm next door.",
   big("Cutlar", "LYMAN CUTLAR", 2.2), show("Griffin", "GRF"), big("Griffin", "CHARLES GRIFFIN", 2.2), mood("pig", "GRF", "shock")),
 B("How did one dead pig bring two empires to the edge of war? And why, in the end, did nobody fire a single shot at a human being?",
   mood("dead", "GRF", "sad"), zh("empires"), zh("nobody"), cam=REG),
 B("To answer that, we have to go back to a map that was drawn wrong.",
   zh("map"), ("wrong", {"line": P49, "color": "#ff6a1f"})),
 {"do": [{"logo": 1}], "pause": 3.6},
]}

ch = []
ch.append({"title": "A Country With Two Owners", "years": "1818", "mood": "tension", "beats": [
 B("Picture the Pacific Northwest two hundred years ago. A huge land of forest and rivers, west of the Rocky Mountains, from what is now Oregon up to the edge of Russian Alaska.",
   ("Pacific", {"era": "1815"}), pin("Oregon", "Columbia River"), zh("Alaska"), arrow("Rocky", [[-112, 44], [-118, 45]], "#f3e7cf"), cam=NW),
 B("The British called it the Columbia District. The Americans called it Oregon Country. Both said it was theirs.",
   show("British", "RN"), show("Americans", "US"), label("Oregon", "OREGON COUNTRY?", -121.0, 46.5), mood("theirs", "US", "angry"), mood("British", "RN", "smug")),
 B("In 1818, they agreed not to fight about it. Both nations could use the land together, for ten years. In 1827 they renewed the deal, and either side could end it with one year's notice.",
   date("1818", "1818"), stamp("together", "JOINT OCCUPATION"), zh("1827"), zh("notice"), cam=NA),
 B("On the British side, the land was run by a company. The Hudson's Bay Company, founded in London in 1670, traded furs across a huge territory.",
   pin("London", "London"), stamp("company", "HUDSON'S BAY COMPANY"), zh("furs"), cam=ATL),
 B("Its regional headquarters was Fort Vancouver, on the Columbia River. At its peak, it oversaw thirty-four outposts, six ships and six hundred employees.",
   pin("Fort", "Fort Vancouver"), zh("Columbia"), zh("peak"), stat("thirty", [["Outposts", "34"], ["Ships", "6"], ["Employees", "600"]], "Fort Vancouver, late 1830s"), cam=NW),
 B("In 1837, the company's governor in North America, George Simpson, wrote that the region may become an object of very great importance.",
   date("1837", "1837"), zh("region"), quote("wrote", "...may become an object of very great importance.", "George Simpson, Hudson's Bay Company, 1837", 4.0), mood("importance", "RN", "smug")),
 B("Its chief factor, John McLoughlin, had a policy. Discourage the Americans. But the Americans kept coming.",
   mood("Discourage", "RN", "smug"), arrow("coming", [[-110, 42.5], [-118, 44.5], [-122.7, 45.5]], BLUE, True)),
 B("In 1843, more than seven hundred settlers arrived from the east. Americans called it the Great Migration.",
   date("1843", "1843"), big("seven", "700+ SETTLERS", 2.4), mood("Migration", "US", "happy"), zh("east")),
 B("So the company moved its bets north. That same year, it built a new post at the south tip of Vancouver Island, at a place called Camosun. It named it after the young Queen. Fort Victoria.",
   pin("Camosun", "Fort Victoria"), big("Victoria", "FORT VICTORIA", 2.2), zh("Island"), cam=REG),
 B("The people who cut its wooden walls were local First Nations workers. The pay was one company blanket for every forty posts they cut.",
   stat("blanket", [["Pay", "1 blanket"], ["For", "40 pickets"]], "Fort Victoria, 1843"), zh("forty")),
 B("Two powers now faced each other across a narrow sea. But the land they argued over was not empty. And that is the part of the story most maps leave out.",
   mood("powers", "US", "angry"), mood("faced", "RN", "angry"), zh("empty"), cam=ISL),
]})

ch.append({"title": "The People Already There", "years": "11,000 years", "mood": "sad", "beats": [
 B("People had lived on the San Juan Islands for something like eleven thousand years. They were Coast Salish peoples, among them the Lummi, the Klallam, the Saanich, the Samish and the Songhees.",
   pin("San", "San Juan Island"), big("eleven", "11,000 YEARS", 2.4), show("Coast", "SAL"), zh("Songhees"), cam=ISL),
 B("The Lummi alone controlled about half of the islands. On San Juan Island itself, one group had three villages, with the main one on a sheltered bay in the north. Garrison Bay.",
   hl("Lummi", ["United States"], "#e0b84a"), pin("Garrison", "Garrison Bay"), zh("three"), zh("half"), cam={"lon": -123.1, "lat": 48.56, "scale": 70000}),
 B("Remember that bay. British marines will camp on it one day.",
   zh("Remember"), zh("British"), mood("marines", "SAL", "worried")),
 B("Then the strangers brought something worse than guns. European exploration brought smallpox in the 1770s. It wiped out, or nearly wiped out, three villages in the San Juan Islands.",
   date("1770s", "1770s"), mood("smallpox", "SAL", "sad"), ("wiped", {"dim": 0.4}), zh("three"), cam=ISL),
 B("From the 1810s to the 1850s, raiders from the north, armed earlier with guns, attacked Coast Salish villages for slaves and loot. Many survivors left the islands for the mainland.",
   ("From", {"dim": 0}), arrow("north", [[-127.0, 50.5], [-125.0, 49.6], [-123.2, 48.7]], RED, True), mood("loot", "SAL", "shock"), zh("mainland"), cam=REG),
 B("By the 1850s, both empires were signing treaties with the peoples they found. On the British side, Governor James Douglas made fourteen land purchases on Vancouver Island between 1850 and 1854.",
   show("Governor", "DOU"), big("fourteen", "14 DOUGLAS TREATIES", 2.4), pin("Vancouver", "Fort Victoria")),
 B("On the American side, in January 1855, fourteen Lummi leaders, led by Chowitsoot, signed the Treaty of Point Elliott. They gave up roughly a hundred and seven thousand acres.",
   date("January", "22 JANUARY 1855"), stamp("Elliott", "TREATY OF POINT ELLIOTT"), stat("hundred", [["Lummi signers", "14"], ["Acres ceded", "about 107,000"]]), mood("gave", "SAL", "sad")),
 B("In the mid-1850s, around the British colony, there were about thirty thousand First Nations people. There were fewer than a thousand Europeans.",
   stat("thirty", [["First Nations", "about 30,000"], ["Europeans", "under 1,000"]], "mid-1850s"), zh("thousand"), cam=REG),
 B("So when London and Washington argued about who owned these islands, they were arguing about land where they were still the small minority. Nobody asked the people already there.",
   zh("London"), zh("Washington"), mood("asked", "SAL", "sad"), zh("minority")),
 B("Now the other side of the ocean. In Washington, a new president was about to turn a quiet argument into a shouting match.",
   mood("president", "US", "smug"), zh("shouting"), cam=NA),
]})

ch.append({"title": "Fifty-Four Forty, or Not", "years": "1844", "mood": "tension", "beats": [
 B("In 1844, the Democratic Party told voters that America's claim to the whole of Oregon was, in its words, clear and unquestionable.",
   date("1844", "1844"), quote("clear", "Our title to the whole of the Territory of Oregon is clear and unquestionable.", "Democratic platform, 1844", 4.2), mood("unquestionable", "US", "smug")),
 B("Its candidate, James K. Polk, won. He became the eleventh president of the United States.",
   show("Polk", "POLK"), big("eleventh", "PRESIDENT POLK", 2.2), mood("won", "POLK", "happy"), pin("States", "Washington, D.C."), cam=NA),
 B("You may have heard the famous slogan: fifty-four forty, or fight. Meaning all of Oregon, up to the Russian border, or war.",
   big("slogan", "“54°40′ OR FIGHT!”", 2.6), ("Russian", {"line": [[-140, 54.67], [-130, 54.67]], "color": RED}), zh("war"), cam=NW),
 B("Here is the twist. It was not Polk's campaign slogan at all. It only appears by January 1846, more than a year after the election. Many textbooks still get it wrong.",
   zh("twist"), stamp("slogan", "NOT HIS SLOGAN"), mood("wrong", "POLK", "shock"), date("January", "JANUARY 1846")),
 B("[chuckle] One of his real 1844 slogans was a lot less exciting. Polk, Dallas, and the Tariff of forty-two.",
   stamp("Tariff", "POLK, DALLAS AND THE TARIFF OF '42"), mood("exciting", "POLK", "neutral"), zh("real")),
 B("Still, Polk talked tough. In January 1846, he said the only way to treat John Bull was to look him straight in the eye.",
   quote("tough", "The only way to treat John Bull was to look him straight in the eye.", "James K. Polk, 4 January 1846", 4.2), mood("eye", "RN", "angry"), cam=ATL),
 B("He had already withdrawn an American offer to split the land along the forty-ninth parallel. In April 1846, Congress voted to end the joint occupation.",
   ("forty", {"line": P49, "color": "#f3e7cf"}), zh("withdrawn"), stamp("April", "JOINT OCCUPATION: ENDED"), date("April", "23 APRIL 1846"), cam=NW),
 B("Now the British side. London was not bluffing either. The American envoy reported that Britain was ready to commission, immediately, some thirty ships of the line.",
   pin("London", "London"), quote("ready", "...to commission immediately some thirty ships-of-the-line.", "US envoy Louis McLane, February 1846", 4.2), mood("thirty", "RN", "smug"), cam=ATL),
 B("In America, Daniel Webster warned that a war over Oregon would be stupendous folly and enormous crime.",
   quote("warned", "Stupendous folly and enormous crime.", "Daniel Webster", 3.6), zh("folly"), mood("crime", "US", "worried")),
 B("And Polk had a second problem. America was already sliding into a war with Mexico. Two wars at once was one too many.",
   pin("Mexico", "Mexico City"), mood("problem", "POLK", "worried"), big("Two", "TWO WARS?", 2.2), cam=NA),
 B("So both sides blinked. Secretary of State James Buchanan and the British minister, Richard Pakenham, worked out a deal. Keep that name, Buchanan. He comes back later, as president.",
   mood("blinked", "POLK", "neutral"), mood("blinked", "RN", "neutral"), show("Buchanan", "BUC"), zh("president")),
 B("The Senate voted thirty-eight to twelve to accept the British terms. The Oregon Treaty was signed on June the fifteenth, 1846.",
   stat("thirty", [["Senate vote", "38 to 12"]], "12 June 1846", 3.2), stamp("signed", "OREGON TREATY"), ("signed", {"sfx": "pen"}), date("June", "15 JUNE 1846")),
 B("June the fifteenth. Remember the date. Exactly thirteen years later, to the day, a farmer will shoot a pig.",
   big("fifteenth", "15 JUNE", 2.2), zh("thirteen"), zh("pig"), cam=REG),
]})

ch.append({"title": "The Middle of the Channel", "years": "1846", "mood": "tension", "beats": [
 B("The treaty drew the border along the forty-ninth parallel, west to the sea. Then it reached the water, and things got vague.",
   ("treaty", {"era": "1914"}), ("forty", {"line": P49, "color": "#f3e7cf"}), arrow("west", [[-117, 49], [-123.2, 49]], "#f3e7cf"), zh("vague"), cam=REG),
 B("The words said the line ran to the middle of the channel which separates the continent from Vancouver Island, and then southerly, through the middle of that channel, to the Pacific.",
   quote("words", "...to the middle of the channel which separates the continent from Vancouver Island, and thence southerly through the middle of the said channel...", "Oregon Treaty, 1846", 5.0), zh("southerly")),
 B("The problem? Between Vancouver Island and the mainland sit the San Juan Islands. And there are two channels. Not one.",
   pin("San", "San Juan Island"), big("two", "TWO CHANNELS", 2.4), zh("problem"), cam=ISL),
 B("To the west of the islands runs Haro Strait. To the east runs Rosario Strait.",
   ("Haro", {"line": HARO, "color": BLUE}), label("Haro", "HARO STRAIT", -123.35, 48.6, BLUE), ("Rosario", {"line": ROSARIO, "color": RED}), label("Rosario", "ROSARIO STRAIT", -122.6, 48.6, RED)),
 B("Haro Strait was named in 1790 by a Spanish explorer, Manuel Quimper, after his pilot, Gonzalo López de Haro. It is wider, but harder to sail. Rosario is the shortest shipping route.",
   date("1790", "1790"), stamp("Haro", "HARO STRAIT, 1790"), zh("wider"), zh("shortest")),
 B("If the border ran through Haro, the islands were American. If it ran through Rosario, they were British.",
   mood("Haro", "US", "happy"), mood("Rosario", "RN", "happy"), arrow("American", [[-123.25, 48.4], [-123.0, 48.52]], BLUE), arrow("British", [[-122.7, 48.4], [-122.95, 48.52]], RED)),
 B("How did the treaty writers miss this? The best maps of the day were Captain George Vancouver's, from 1798, and the American Charles Wilkes's, from 1845. Both were unclear around exactly this spot.",
   zh("miss"), stamp("1798", "MAP: 1798"), stamp("Wilkes", "MAP: 1845"), mood("unclear", "US", "shock")),
 B("And it may not have been an accident. During the talks, the head of the Hudson's Bay Company told the British foreign secretary to use Rosario. The final wording was left vague on purpose.",
   zh("accident"), mood("Rosario", "RN", "smug"), big("purpose", "VAGUE ON PURPOSE", 2.4)),
 B("Why fight for a few small islands? Because of where they sit. Whoever held San Juan Island could dominate every strait between the open sea and the inner waters.",
   arrow("sit", [[-124.5, 48.4], [-123.4, 48.3], [-123.15, 48.55], [-123.3, 49.0]], "#e0b84a", True), zh("dominate"), cam=REG),
 B("Meanwhile, the Americans organised their side. Oregon Territory was created in 1848. Washington Territory, just across the water from Vancouver Island, followed in 1853.",
   date("1848", "1848"), hl("Oregon", ["United States"], BLUE), date("1853", "1853"), zh("Washington"), cam=NW),
 B("The British moved first. In December 1853, the company set up a sheep farm on the south end of San Juan Island, Belle Vue farm. It was meant to show the island was British.",
   date("December", "13 DECEMBER 1853"), pin("Belle", "Belle Vue Farm"), stamp("British", "BELLE VUE SHEEP FARM"), mood("British", "RN", "smug"), cam=CAMP),
 B("The Americans answered with paperwork. In 1855, Washington Territory sent the company a tax bill for its property on the island. The company refused to pay.",
   date("1855", "1855"), big("tax", "TAX BILL", 2.2), mood("refused", "RN", "angry"), mood("tax", "US", "smug")),
 B("So both nations tried the grown-up way. They sent experts to settle the water line. It did not go well.",
   zh("grown"), zh("experts"), mood("well", "US", "worried"), cam=ISL),
]})

ch.append({"title": "Two Commissioners, Two Straits", "years": "1857", "mood": "tension", "beats": [
 B("In 1856, the two countries set up a Boundary Commission. For Britain, the First Commissioner was a naval captain, James Prevost. For the United States, it was Archibald Campbell.",
   date("1856", "1856"), stamp("Commission", "BOUNDARY COMMISSION"), show("Prevost", "PRE"), show("Campbell", "CAM"), cam=REG),
 B("They first met on the twenty-seventh of June, 1857, aboard a British warship, HMS Satellite, anchored in Esquimalt Harbour.",
   date("twenty", "27 JUNE 1857"), pin("Esquimalt", "Esquimalt"), ("Satellite", {"sfx": "waves"}), zh("warship")),
 B("Prevost said the treaty's channel had to pass three tests. It had to separate the continent from Vancouver Island. It had to run southerly. And ships had to be able to sail it. Only Rosario, he said, passed all three.",
   mood("tests", "PRE", "smug"), stat("three", [["Separates continent from island", "?"], ["Runs southerly", "?"], ["Navigable", "?"]], "Prevost's three tests", 4.4), ("Rosario", {"line": ROSARIO, "color": RED}), cam=ISL),
 B("Campbell fired back. Rosario, he said, did not separate the continent from Vancouver Island at all. It only separated some islands from other islands. And Haro was wider and more direct.",
   mood("Campbell", "CAM", "angry"), speak("fired", "CAM", "Haro is wider and more direct."), ("Haro", {"line": HARO, "color": BLUE}), zh("wider")),
 B("Then Campbell dared him. Show me any proof that the men who wrote the treaty meant Rosario.",
   speak("dared", "CAM", "Show me proof they meant Rosario."), mood("proof", "PRE", "shock"), zh("dared")),
 B("Prevost had an answer, and it stung. American maps. One by the explorer John Frémont, published by the American government itself, and one by Oregon's own surveyor general, both drew the line through Rosario.",
   mood("stung", "CAM", "shock"), stamp("maps", "AMERICAN MAPS: ROSARIO"), mood("Rosario", "PRE", "smug"), zh("government")),
 B("They argued from October to December. On the third of December, Prevost made a final offer: split the difference, down the middle channel, and America gets every main island except San Juan.",
   date("third", "3 DECEMBER 1857"), ("middle", {"line": [[-123.0, 48.7], [-123.0, 48.55], [-122.95, 48.4]], "color": "#e0b84a"}), big("except", "ALL BUT SAN JUAN", 2.4), cam=ISL),
 B("The one island that mattered most. Campbell said no. The commission broke up without a water boundary.",
   pin("mattered", "San Juan Island"), speak("no", "CAM", "No."), stamp("boundary", "NO DEAL"), mood("commission", "PRE", "angry")),
 B("So San Juan Island stayed in limbo. Claimed by two nations. Taxed by one, farmed by the other.",
   mood("limbo", "US", "worried"), mood("Claimed", "RN", "worried"), zh("Taxed"), hide("Taxed", "PRE", "CAM"), cam=CAMP),
 B("And then, in 1858, something happened that filled the whole region with strangers almost overnight. Gold.",
   date("1858", "1858"), zh("strangers"), big("Gold", "GOLD", 2.2), ("Gold", {"flash": 0.4})),
]})

ch.append({"title": "Gold, Sheep and Neighbours", "years": "1858", "mood": "hope", "beats": [
 B("Gold was found on the Fraser River, on the British mainland. Within a month, about thirty thousand men poured into Victoria, a village of about five hundred.",
   pin("Fraser", "Fraser River"), pin("Victoria", "Fort Victoria"), stat("thirty", [["Arrivals in a month", "about 30,000"], ["Victoria before", "about 500"]], "Fraser gold rush, 1858", 4.2), arrow("poured", [[-122.4, 37.8], [-125.5, 44.0], [-123.37, 48.43]], "#e0b84a", True), cam=NW),
 B("Four thousand of them were Chinese. Tens of thousands of the prospectors came up from California.",
   zh("Chinese"), zh("California"), mood("prospectors", "US", "happy")),
 B("By autumn, many miners were calling the Fraser a humbug. But in August 1858, Britain made the mainland a crown colony, British Columbia.",
   stamp("humbug", "HUMBUG!"), date("August", "2 AUGUST 1858"), hl("Columbia", ["Canada"], RED), mood("Britain", "RN", "worried"), cam=REG),
 B("The man in charge was James Douglas. Born in 1803 in Demerara, on the north-east coast of South America, the son of a wealthy Scottish planter and a free coloured woman of Creole ancestry. People called him Old Squaretoes.",
   show("Douglas", "DOU"), big("Douglas", "JAMES DOUGLAS", 2.2), zh("Demerara"), stamp("Squaretoes", "“OLD SQUARETOES”")),
 B("He had risen to chief factor in the Hudson's Bay Company. Now he was governor of Vancouver Island, and he wanted the San Juans British.",
   mood("British", "DOU", "smug"), pin("San", "San Juan Island"), zh("governor")),
 B("Meanwhile, Americans were quietly settling the island. By the middle of 1859, there were about two dozen American settlers on San Juan Island.",
   show("settling", "CUT"), stamp("dozen", "ABOUT 25 SETTLERS"), mood("settlers", "CUT", "happy"), cam=CAMP),
 B("One of them was Lyman Cutlar, a farmer from Kentucky. He moved onto the island, close to the company's sheep farm, and planted a garden.",
   big("Cutlar", "LYMAN CUTLAR", 2.2), pin("company's", "Belle Vue Farm"), zh("garden")),
 B("He claimed the right to be there under the Donation Land Claim Act, an American law that gave free land to settlers in the West. Three hundred and twenty acres for a single man.",
   stamp("Act", "DONATION LAND CLAIM ACT"), stat("hundred", [["Single man", "320 acres"], ["Married couple", "640 acres"]], "Donation Land Claim Act, 1850"), zh("free")),
 B("[chuckle] There was one small problem. The free land offer had expired, in December 1855. And the island might not even be American.",
   zh("problem"), stamp("expired", "EXPIRED: 1855"), mood("American", "CUT", "shock")),
 B("His neighbour was Charles Griffin, an Irishman who ran Belle Vue farm for the Hudson's Bay Company. Griffin kept pigs, and he let them roam free.",
   show("neighbour", "GRF"), big("Griffin", "CHARLES GRIFFIN", 2.2), mood("roam", "GRF", "happy"), zh("pigs")),
 B("The two men had lived side by side in peace. An American with a rifle and a garden. An Irishman with a farm and free-range pigs.",
   mood("peace", "CUT", "neutral"), mood("peace", "GRF", "neutral"), zh("rifle")),
 B("You can probably see where this is going.",
   zh("going"), ("going", {"sfx": "tick4"})),
]})

ch.append({"title": "The Pig", "years": "15 June 1859", "mood": "tension", "beats": [
 B("June the fifteenth, 1859. Thirteen years to the day after the Oregon Treaty was signed.",
   date("June", "15 JUNE 1859"), big("Thirteen", "13 YEARS TO THE DAY", 2.6), cam=CAMP),
 B("Lyman Cutlar found a pig in his garden, rooting up his potatoes. It was not the first time.",
   mood("pig", "CUT", "angry"), zh("potatoes"), stamp("first", "NOT THE FIRST TIME")),
 B("Cutlar had had enough. He shot the pig, and killed it.",
   ("shot", {"shot": 1}), ("killed", {"dim": 0.3}), mood("killed", "CUT", "shock"), cam={"lon": -122.98, "lat": 48.46, "scale": 140000}),
 B("Then he did something decent. He went to Griffin and offered to pay for it. Ten dollars.",
   ("decent", {"dim": 0}), speak("offered", "CUT", "I'll pay you ten dollars."), big("Ten", "$10", 2.0), mood("decent", "CUT", "neutral")),
 B("Griffin said no. He wanted a hundred.",
   speak("no", "GRF", "A hundred dollars."), big("hundred", "$100", 2.0), mood("no", "GRF", "angry")),
 B("Cutlar thought it over, and changed his mind. The pig had been trespassing on his land. Why should he pay anything at all?",
   mood("changed", "CUT", "angry"), speak("pay", "CUT", "Your pig was on my land."), zh("trespassing")),
 B("There is a famous exchange from that day. It is probably invented, but it is too good to leave out.",
   zh("famous"), stamp("invented", "PROBABLY INVENTED"), zh("good")),
 B("Cutlar: It was eating my potatoes.",
   speak("Cutlar", "CUT", "It was eating my potatoes."), mood("potatoes", "CUT", "angry")),
 B("Griffin: It is up to you to keep your potatoes out of my pig.",
   speak("Griffin", "GRF", "Keep your potatoes out of my pig."), mood("pig", "GRF", "smug"), zh("pig")),
 B("Now the island's two sides took over. According to the usual telling, British officials threatened to arrest Cutlar, and take him to Victoria.",
   mood("arrest", "CUT", "shock"), pin("Victoria", "Fort Victoria"), arrow("Victoria", [[-122.98, 48.46], [-123.37, 48.43]], RED), cam=ISL),
 B("To the Americans, that was outrageous. This was American soil, they said. The settlers asked the United States Army for protection.",
   mood("outrageous", "US", "angry"), speak("soil", "US", "This is American soil."), stamp("protection", "SEND THE ARMY")),
 B("So a small squabble between two neighbours went up the chain. And at the top of that chain, on the American side, sat exactly the wrong man.",
   zh("squabble"), arrow("chain", [[-123.0, 48.47], [-122.5, 48.75]], BLUE), zh("wrong"), cam=REG),
]})

ch.append({"title": "Send In Pickett", "years": "July 1859", "mood": "war", "beats": [
 B("His name was William Harney, a brigadier general, commanding the army's Department of Oregon. Harney did not do subtle.",
   show("Harney", "HAR"), big("Harney", "GENERAL HARNEY", 2.2), mood("subtle", "HAR", "angry"), cam=NW),
 B("Four years earlier, after a battle against the Lakota at Ash Hollow, the Lakota had given him a name. Woman Killer.",
   date("earlier", "ASH HOLLOW, 1855"), stamp("name", "“WOMAN KILLER”"), ("Killer", {"dim": 0.35}), cam=NA),
 B("Harney moved fast. He sent a company of soldiers to San Juan Island, with orders to stop the British from landing.",
   ("Harney", {"dim": 0}), mood("moved", "HAR", "smug"), arrow("sent", [[-122.5, 48.75], [-123.0, 48.47]], BLUE, True), pin("San", "San Juan Island"), cam=REG),
 B("The captain he picked was George Pickett, thirty-four years old, from Richmond, Virginia.",
   show("Pickett", "PIC"), big("Pickett", "CAPTAIN GEORGE PICKETT", 2.4), mood("captain", "PIC", "smug")),
 B("At West Point, Pickett had finished last in his class. Fifty-ninth out of fifty-nine.",
   stat("last", [["Class rank", "59th of 59"]], "West Point, 1846", 3.2), zh("last"), mood("Fifty", "PIC", "neutral")),
 B("In the Northwest he had married a Haida woman, known as Morning Mist. In 1857, she bore him a son, James.",
   zh("Haida"), stamp("Morning", "MORNING MIST"), zh("son")),
 B("Now he took about sixty-six men of the Ninth Infantry from Fort Bellingham, and sailed them across to San Juan Island aboard the steamer USS Massachusetts.",
   pin("Bellingham", "Fort Bellingham"), arrow("sailed", [[-122.48, 48.75], [-122.8, 48.55], [-123.0, 48.47]], BLUE, True), ("Massachusetts", {"sfx": "waves"}), big("sixty", "66 MEN", 2.0)),
 B("The British reply was not long coming. Governor Douglas sent warships. Three of them, under Captain Geoffrey Hornby.",
   show("British", "RN"), mood("warships", "DOU", "angry"), big("Three", "3 WARSHIPS", 2.2), ("warships", {"sfx": "waves"}), arrow("Hornby", [[-123.43, 48.43], [-123.1, 48.43], [-123.0, 48.46]], RED, True)),
 B("Pickett pitched his camp near the company's farm, at the south end of the island. The story goes that there was one problem. It was directly under the guns of a British warship.",
   pin("camp", "American Camp"), zh("problem"), mood("guns", "PIC", "shock"), ("guns", {"cannon": [-122.97, 48.44]}), cam=CAMP),
 B("When someone pointed this out, Pickett moved his cannon a few miles north, to high ground, and started digging in.",
   mood("pointed", "PIC", "neutral"), arrow("north", [[-122.98, 48.45], [-123.03, 48.47]], BLUE), zh("digging")),
 B("And he said the line everyone remembers. Don't be afraid of their big guns. We'll make a Bunker Hill of it.",
   quote("line", "Don't be afraid of their big guns... We'll make a Bunker Hill of it.", "Captain George Pickett, 1859", 4.4), speak("Bunker", "PIC", "We'll make a Bunker Hill of it!"), mood("Bunker", "RN", "angry")),
 B("Bunker Hill. A battle from the American Revolution, against the British. On a little island over a dead pig, a captain was talking about the last war, and asking for the next one.",
   stamp("Bunker", "BUNKER HILL"), zh("pig"), mood("next", "RN", "angry"), ("next", {"shake": 0.3})),
]})

ch.append({"title": "Seventy Guns", "years": "August 1859", "mood": "war", "beats": [
 B("Now the British side. Captain Hornby was a career naval officer, born in 1825. The same year as Pickett.",
   big("Hornby", "CAPTAIN HORNBY", 2.2), zh("1825"), mood("officer", "RN", "neutral"), cam=REG),
 B("Governor Douglas gave him orders: get the American soldiers off the island. And avoid a fight, if possible.",
   speak("orders", "DOU", "Get them off. Avoid a fight."), mood("possible", "RN", "worried"), zh("avoid")),
 B("If possible. Two words that left a young captain holding the peace of two empires.",
   big("possible", "IF POSSIBLE", 2.2), zh("empires"), ("empires", {"sfx": "heart"})),
 B("Both sides kept sending more. By the tenth of August, the Americans had four hundred and sixty-one soldiers and fourteen cannon on the island, now under a more senior officer, Colonel Silas Casey.",
   date("tenth", "10 AUGUST 1859"), troops("Americans", "US", -123.02, 48.47) if False else ("Americans", {"troops": ["US", -123.02, 48.47]}), ("fourteen", {"cannon": [-123.03, 48.47]}), show("Casey", "CAS"), cam=CAMP),
 B("Out on the water were five British warships. Seventy guns. Two thousand one hundred and forty men.",
   ("five", {"sfx": "waves"}), stat("five", [["US soldiers", "461"], ["US cannon", "14"], ["British warships", "5"], ["British guns", "70"], ["British men", "2,140"]], "10 August 1859", 4.6), mood("Seventy", "RN", "smug"), cam=ISL),
 B("The American redoubt, an earthen fort for the cannon, was built under a young engineer, Second Lieutenant Henry Martyn Robert. Keep an eye on him. His name lives on in a very unexpected place.",
   show("redoubt", "ROB"), big("Robert", "LT. HENRY ROBERT", 2.2), zh("unexpected"), ("built", {"sfx": "boots"}), cam=CAMP),
 B("It still stands today. It is considered the best-preserved fortification of its kind in the United States.",
   pin("stands", "American Camp"), stamp("best", "BEST-PRESERVED REDOUBT"), zh("today")),
 B("Ask yourself what you would have done. You have seventy guns, more than two thousand men, and orders to remove an enemy who is digging in. Every day you wait, he gets stronger.",
   zh("yourself"), zh("seventy"), mood("stronger", "US", "smug"), ("digging", {"sfx": "boots"}), cam=ISL),
 B("Hornby had the guns to blow it apart. But he did not fire. He would not act until his commander arrived.",
   ("guns", {"boom": 0.3}), mood("fire", "RN", "worried"), zh("commander"), cam=ISL),
 B("His commander was Rear Admiral Robert Lambert Baynes, in charge of the Royal Navy in the Pacific. When the crisis began, he was away, in Peru.",
   show("commander", "BAY"), big("Baynes", "ADMIRAL BAYNES", 2.2), pin("Peru", "Callao"), cam=ATL),
 B("Baynes was sixty-two. As a young officer, in the War of 1812, he had fought at the Battle of New Orleans, against the Americans. He knew exactly what a war with America meant.",
   stamp("Orleans", "THE WAR OF 1812"), pin("Orleans", "New Orleans"), mood("meant", "BAY", "grim"), cam=NA),
 B("He sailed north, and took one look. Douglas wanted the Royal Marines landed on the island. Baynes refused.",
   arrow("north", [[-77.2, -12.05], [-110, 20], [-123.4, 48.4]], RED, True), speak("Baynes", "DOU", "Land the Marines!"), mood("refused", "DOU", "shock"), cam=NW),
 B("He would not, he said, involve two great nations in a war over a squabble about a pig.",
   quote("squabble", "...involve two great nations in a war over a squabble about a pig.", "Rear Admiral Robert Baynes, 1859", 4.6), speak("pig", "BAY", "Over a squabble about a pig?"), mood("pig", "BAY", "smug"), cam=REG),
 B("One sentence, from one old sailor who had seen war. And that may have been the most important decision of the whole affair.",
   zh("sentence"), zh("decision"), mood("important", "US", "neutral"), mood("important", "RN", "neutral")),
 B("But the guns were still loaded. And in Washington and London, the news was only now arriving.",
   ("loaded", {"cannon": [-123.0, 48.44]}), (None, {"telegraph": ["US", "RN"]}) if False else zh("news"), cam=ATL),
]})

ch.append({"title": "Old Fuss and Feathers", "years": "September 1859", "mood": "tension", "beats": [
 B("When the news reached the two capitals, officials on both sides were shocked. Nobody in London or Washington wanted this war.",
   pin("London", "London"), pin("Washington", "Washington, D.C."), mood("shocked", "US", "shock"), mood("shocked", "RN", "shock"), cam=ATL),
 B("The president was now James Buchanan, the same man who had negotiated the Oregon Treaty thirteen years earlier. His own vague channel was about to start a war.",
   show("president", "BUC"), mood("vague", "BUC", "shock"), zh("thirteen"), stamp("Treaty", "HIS OWN TREATY")),
 B("And he had a bigger worry at home. North and South were tearing apart over slavery. The country was heading toward civil war.",
   mood("worry", "BUC", "worried"), ("tearing", {"line": [[-95, 36.5], [-75, 39.7]], "color": RED}), zh("civil"), cam=NA),
 B("Some suspected the worst. Years later, the general George McClellan claimed Harney and Pickett had wanted a war with Britain on purpose, to give a divided country a common enemy.",
   zh("worst"), mood("purpose", "HAR", "smug"), big("purpose", "ON PURPOSE?", 2.4)),
 B("Another officer said the plan, if there was one, was the opposite, to distract the North so the South could break away. Historians still argue. Nothing proves either story.",
   zh("opposite"), stamp("argue", "HISTORIANS STILL ARGUE"), zh("Nothing")),
 B("In September, Buchanan sent the most senior soldier in the country. General Winfield Scott, the army's General-in-Chief.",
   date("September", "SEPTEMBER 1859"), show("Scott", "SCO"), big("Scott", "GENERAL WINFIELD SCOTT", 2.4), pin("country", "Washington, D.C.")),
 B("Scott was seventy-three. He was famous for insisting on proper military etiquette. His nickname was Old Fuss and Feathers.",
   stamp("Feathers", "“OLD FUSS AND FEATHERS”"), mood("Feathers", "SCO", "smug"), zh("seventy")),
 B("[chuckle] But Scott had a rare skill. He had calmed two border crises with the British before, in the late 1830s, including the Aroostook War, between Maine and New Brunswick.",
   zh("skill"), pin("Aroostook", "Aroostook"), stamp("Aroostook", "AROOSTOOK WAR, 1838-39"), cam={"lon": -70, "lat": 45.5, "scale": 3800}),
 B("He sailed for the Pacific, and arrived in the San Juans in October. Then he sat down to negotiate with Governor Douglas.",
   arrow("sailed", [[-74, 40.7], [-80, 9], [-123.1, 48.5]], BLUE, True), date("October", "OCTOBER 1859"), mood("negotiate", "DOU", "neutral"), cam=NA),
 B("By November, they had a deal. Both sides could stay on the island, together, until the diplomats settled the border. But each could keep no more than a hundred men.",
   date("November", "NOVEMBER 1859"), stamp("deal", "JOINT MILITARY OCCUPATION"), big("hundred", "MAX 100 MEN EACH", 2.4), mood("deal", "SCO", "happy"), cam=ISL),
 B("The warships sailed away. The hundreds of soldiers left. And Harney? The army recalled him to St. Louis.",
   ("warships", {"hide": ["RN"]}), zh("hundreds"), mood("recalled", "HAR", "shock"), pin("Louis", "St. Louis"), hide("Louis", "HAR")),
 B("So now two rival armies had to share one small island. Nobody knew for how long. The answer turned out to be twelve years.",
   zh("rival"), big("twelve", "12 YEARS", 2.4), mood("share", "US", "neutral"), cam=ISL),
]})

ch.append({"title": "The Friendliest Occupation", "years": "1860", "mood": "hope", "beats": [
 B("In 1860, British Royal Marines set up camp on the north of San Juan Island. On Garrison Bay. The same bay where the island's people once had their main village.",
   date("1860", "1860"), show("Marines", "RM"), pin("Garrison", "English Camp"), zh("village"), cam={"lon": -123.1, "lat": 48.53, "scale": 70000}),
 B("The Americans stayed on the windswept prairie at the south end, with their cannon pointed out at the strait. A road was built between the two camps.",
   pin("Americans", "American Camp"), ("road", {"line": [[-123.15, 48.59], [-123.1, 48.53], [-123.03, 48.47]], "color": "#e0b84a"}), zh("cannon")),
 B("And then something odd happened. The enemies became friends.",
   zh("odd"), mood("friends", "US", "happy"), mood("friends", "RM", "happy"), big("friends", "FRIENDS?", 2.2)),
 B("The two garrisons visited each other's camps to celebrate their national holidays. Redcoats and bluecoats drank to each other's countries.",
   ("celebrate", {"sfx": "crowd"}), stamp("holidays", "NATIONAL HOLIDAYS"), mood("drank", "RM", "happy"), mood("drank", "US", "happy")),
 B("They held sports contests against each other. Park rangers today like to say the biggest threat to peace on the island was not the guns. It was the large amount of alcohol available.",
   zh("sports"), zh("rangers"), quote("alcohol", "...the large amounts of alcohol available.", "Park rangers, on the biggest threat to peace", 4.2), ("alcohol", {"sfx": "bells"})),
 B("Back on the farm, the story of our two neighbours fades out. The company gave up Belle Vue farm in 1861. Charles Griffin left the island in 1862.",
   pin("farm", "Belle Vue Farm"), mood("fades", "GRF", "sad"), hide("1862", "GRF"), date("1862", "1862"), cam=CAMP),
 B("Of Lyman Cutlar, the farmer who fired the shot, the records we found say almost nothing more. The man who nearly started a war simply walks out of history.",
   mood("records", "CUT", "neutral"), zh("nothing"), hide("history", "CUT"), zh("walks")),
 B("That same year, 1862, a darker visitor arrived. Smallpox came back to the coast, carried by a miner who landed in Victoria from San Francisco.",
   date("year", "1862"), pin("Victoria", "Fort Victoria"), mood("Smallpox", "SAL", "shock"), arrow("San", [[-122.4, 37.8], [-125.5, 44], [-123.37, 48.43]], RED), cam=NW),
 B("Police backed by gunboats forced thousands of First Nations people camped around Victoria to leave. Many went home to their villages, and the disease went with them. It killed about two-thirds of British Columbia's Native people.",
   ("Police", {"dim": 0.45}), mood("forced", "SAL", "sad"), stat("two", [["Native people of BC killed", "about 2 in 3"]], "smallpox, 1862", 3.6), cam=REG),
 B("Some consider that expulsion an act of genocide. On San Juan Island, a bay on the west side is still called Smallpox Bay, after its victims.",
   ("Some", {"dim": 0}), stamp("Smallpox", "SMALLPOX BAY"), pin("Smallpox", "Smallpox Bay"), mood("victims", "SAL", "sad"), cam=ISL),
 B("The soldiers on the island played their games and toasted each other. Around them, a whole people was being swept away.",
   mood("toasted", "RM", "neutral"), mood("swept", "SAL", "sad"), zh("whole")),
 B("And far to the east, the war that everyone had feared on the island was finally breaking out. Only it was not against Britain.",
   zh("east"), zh("feared"), big("Britain", "NOT AGAINST BRITAIN", 2.4), cam=NA),
]})

ch.append({"title": "The Men Who Left the Island", "years": "1861", "mood": "war", "beats": [
 B("In 1861, the American Civil War began. Over in Victoria, Governor Douglas saw a chance.",
   date("1861", "1861"), mood("chance", "DOU", "smug"), ("war", {"line": [[-95, 36.5], [-75, 39.7]], "color": RED}), cam=NA),
 B("In December 1861, during a crisis between Britain and the Union, he urged London to seize Washington Territory while the Americans were busy. London never did.",
   date("December", "DECEMBER 1861"), speak("urged", "DOU", "Seize Puget Sound!"), stamp("never", "LONDON: NO"), hl("seize", ["United States"], BLUE), cam=REG),
 B("George Pickett had a choice to make. He was from Virginia. On the twenty-fifth of June 1861, at Fort Steilacoom, he resigned from the United States Army and joined the Confederacy.",
   show("Pickett", "PIC"), pin("Steilacoom", "Fort Steilacoom"), date("twenty", "25 JUNE 1861"), stamp("Confederacy", "RESIGNED"), mood("Confederacy", "PIC", "grim")),
 B("Two years later, on the third of July 1863, at Gettysburg, in Pennsylvania, Pickett's name was given to one of the most famous attacks in American history. Pickett's Charge.",
   date("third", "3 JULY 1863"), pin("Gettysburg", "Gettysburg"), big("Charge", "PICKETT'S CHARGE", 2.6), ("Charge", {"guns": {"at": [-77.23, 39.82], "dur": 3}}), cam={"lon": -77.2, "lat": 39.8, "scale": 9000}),
 B("About twelve and a half thousand Confederate soldiers marched across open fields into Union guns. More than half of them became casualties.",
   ("marched", {"sfx": "boots"}), arrow("marched", [[-77.26, 39.81], [-77.23, 39.81]], "#8a7d6a", True), stat("half", [["Confederate attackers", "about 12,500"], ["Casualties", "over 50%"]], "Gettysburg, 3 July 1863", 4.2), ("half", {"boom": 0.6})),
 B("The captain who had talked about making a Bunker Hill on a quiet island got his real battle. It tore his division apart.",
   ("tore", {"dim": 0.4}), mood("battle", "PIC", "sad"), zh("apart")),
 B("He is said to have told General Lee, I have no division. Historians are not sure he said it. But it was true.",
   ("said", {"dim": 0}), speak("Lee", "PIC", "I have no division."), stamp("sure", "ALLEGEDLY"), zh("true")),
 B("Later in the war, in 1864, Pickett had twenty-two captured Union soldiers hanged at New Bern. After the war, he fled to Canada for a time. He died in 1875, at fifty.",
   date("1864", "NEW BERN, 1864"), stamp("hanged", "22 MEN HANGED"), mood("hanged", "PIC", "grim"), zh("Canada"), hide("fifty", "PIC")),
 B("More than forty thousand people lined the route of his funeral.",
   stat("forty", [["People along the funeral route", "40,000+"]], "Pickett's funeral, 1875", 3.4), zh("funeral")),
 B("Henry Robert, the young engineer who built the American redoubt, chose the Union. He spent the war building defences, for Washington, Philadelphia and the ports of New England.",
   show("Robert", "ROB"), mood("Union", "ROB", "neutral"), pin("Philadelphia", "Philadelphia"), zh("defences")),
 B("Years later, he was asked to run a church meeting in New Bedford, Massachusetts. It went badly. He did not know the rules of debate.",
   pin("Bedford", "New Bedford"), mood("badly", "ROB", "shock"), zh("rules"), cam={"lon": -72, "lat": 41.5, "scale": 6000}),
 B("So he wrote them himself. In February 1876, he published a pocket manual. Today it is known as Robert's Rules of Order.",
   date("February", "FEBRUARY 1876"), big("Robert's", "ROBERT'S RULES OF ORDER", 2.8), ("wrote", {"sfx": "pen"}), mood("Robert's", "ROB", "happy")),
 B("Robert rose to become the army's Chief of Engineers, in 1901. He died in 1923.",
   date("1901", "1901"), big("Chief", "CHIEF OF ENGINEERS", 2.2), hide("1923", "ROB")),
 B("[chuckle] The man who built a fort for a war that never came went on to write a famous rulebook for arguing without fighting.",
   zh("fort"), zh("never"), mood("arguing", "ROB", "smug")),
 B("Silas Casey, the colonel on the island, wrote a manual on infantry tactics. Both armies in the Civil War used it. Hornby rose to Admiral of the Fleet, the Royal Navy's highest rank.",
   show("Casey", "CAS"), stamp("tactics", "USED BY BOTH SIDES"), show("Hornby", "RN"), big("Admiral", "ADMIRAL OF THE FLEET", 2.4), cam=ATL),
 B("The admiral who refused to fight, Baynes, was knighted in 1860. The governor who wanted the island, Douglas, was knighted too. He retired in 1864, and died in Victoria in 1877, aged seventy-three.",
   show("admiral", "BAY"), stamp("knighted", "KNIGHTED"), show("governor", "DOU"), date("1877", "1877"), hide("seventy", "DOU", "BAY"), cam=REG),
 B("And Hornby, the captain who held his fire? The admiral John Fisher later called him the finest admiral afloat since Nelson.",
   quote("called", "The finest Admiral afloat since Nelson.", "Admiral John Fisher, on Geoffrey Hornby", 4.0), show("Hornby", "RN"), mood("Nelson", "RN", "smug"), cam=ATL),
 B("And back on San Juan Island, through all of it, the hundred redcoats and the hundred bluecoats just kept waiting. For someone, somewhere, to decide who owned it.",
   mood("waiting", "US", "neutral"), mood("waiting", "RM", "neutral"), zh("decide"), cam=ISL),
]})

ch.append({"title": "The Kaiser Decides", "years": "1871", "mood": "tension", "beats": [
 B("By 1871, the map had changed. The two British colonies on the coast had merged into one. And that year, British Columbia joined the new country of Canada.",
   date("1871", "1871"), hl("Canada", ["Canada"], RED), big("Canada", "BRITISH COLUMBIA JOINS CANADA", 2.6), cam=NW),
 B("In May 1871, Britain and the United States signed the Treaty of Washington, to clear up a list of old quarrels, many of them left over from the Civil War. The San Juan water boundary was on the list.",
   date("May", "8 MAY 1871"), stamp("Treaty", "TREATY OF WASHINGTON"), pin("Washington", "Washington, D.C."), ("signed", {"sfx": "pen"}), cam=ATL),
 B("Neither side trusted the other to judge. So they picked a referee from the other side of the world. Wilhelm the First, the new Emperor of Germany.",
   show("Wilhelm", "KAI"), pin("Germany", "Berlin"), big("Emperor", "THE KAISER", 2.2), mood("referee", "KAI", "smug")),
 B("[chuckle] So an island off the Pacific coast of North America, fought over because of a pig, would be decided by a German emperor in Berlin.",
   zh("pig"), zh("German"), mood("decided", "US", "shock"), mood("decided", "RN", "shock")),
 B("Wilhelm was seventy-four years old. He had just become emperor, after Germany's war with France.",
   zh("seventy"), mood("emperor", "KAI", "smug")),
 B("America sent a heavyweight to argue its case. George Bancroft, historian, diplomat, and the founder of the United States Naval Academy.",
   show("Bancroft", "BAN"), big("Bancroft", "GEORGE BANCROFT", 2.2), zh("Naval")),
 B("The emperor passed the question to a commission of three experts, who met in Geneva for nearly a year. They studied the treaty, the maps, and the two straits.",
   pin("Geneva", "Geneva"), stamp("three", "3 EXPERTS, GENEVA"), zh("year"), cam={"lon": 8, "lat": 49, "scale": 3500}),
 B("The same old question. Haro or Rosario. West of the islands, or east.",
   ("Haro", {"line": HARO, "color": BLUE}), ("Rosario", {"line": ROSARIO, "color": RED}), zh("West"), zh("east"), cam=ISL),
 B("On the twenty-first of October, 1872, the decision came.",
   date("twenty", "21 OCTOBER 1872"), ("decision", {"sfx": "heart"}), zh("decision")),
 B("Haro Strait. The border would run to the west of the islands. San Juan Island was American.",
   ("Haro", {"line": HARO, "color": BLUE}), big("Haro", "HARO STRAIT", 2.4), mood("American", "US", "happy"), mood("American", "RM", "sad"), ("American", {"flash": 0.3})),
 B("Britain accepted it. On the twenty-fifth of November, 1872, the Royal Marines marched out of English Camp and sailed away.",
   date("twenty", "25 NOVEMBER 1872"), pin("English", "English Camp"), hide("sailed", "RM"), ("sailed", {"sfx": "waves"}), cam={"lon": -123.1, "lat": 48.53, "scale": 70000}),
 B("The Americans followed by July 1874. The last soldiers left an island that was no longer in dispute.",
   date("July", "JULY 1874"), hide("left", "US"), zh("dispute")),
 B("A dead pig, thirteen years of standoff, twelve years of shared occupation. And not one human being killed in battle.",
   stat("pig", [["Pigs killed", "1"], ["People killed in battle", "0"], ["Years of joint occupation", "12"]], "The Pig War, 1859-1872", 4.4), zh("not")),
]})

ch.append({"title": "What the Line Remembers", "years": "Today", "mood": "sad", "beats": [
 B("Today, both camps are part of San Juan Island National Historical Park. In 2025, more than four hundred thousand people visited.",
   pin("both", "American Camp"), pin("camps", "English Camp"), stat("four", [["Visitors in 2025", "420,922"]], "San Juan Island National Historical Park", 3.4), cam=ISL),
 B("Henry Robert's redoubt still stands on the windswept prairie. On that same prairie lives the world's only viable population of a rare butterfly, the island marble.",
   pin("redoubt", "American Camp"), zh("butterfly"), stamp("marble", "THE ISLAND MARBLE"), cam=CAMP),
 B("And our two neighbours? In every telling we found, Charles Griffin never got his hundred dollars. And Lyman Cutlar never paid his ten.",
   show("neighbours", "CUT", "GRF"), mood("hundred", "GRF", "sad"), mood("ten", "CUT", "smug"), big("ten", "$0 PAID", 2.2)),
 B("So which side was right? America would say the treaty's words pointed to Haro, the wider channel, and the referee agreed.",
   mood("America", "US", "smug"), ("Haro", {"line": HARO, "color": BLUE}), zh("referee")),
 B("Britain would say the wording was left vague on purpose, that even American maps drew the line through Rosario, and that it lost the island without losing the peace.",
   mood("Britain", "RM", "neutral"), ("Rosario", {"line": ROSARIO, "color": RED}), zh("peace"), show("Britain", "RM")),
 B("And the Coast Salish peoples would say that the island was never really either empire's to argue over.",
   show("Coast", "SAL"), mood("never", "SAL", "neutral"), zh("empire's")),
 B("The Pig War is often told as a joke. A farmer, a pig, and two empires making fools of themselves. And some of it is funny.",
   zh("joke"), show("farmer", "CUT"), mood("funny", "CUT", "smug")),
 B("But it is also a story about how close it came. A captain with a loud mouth. A governor who wanted the island. A general who did not wait for orders.",
   show("captain", "PIC"), mood("loud", "PIC", "angry"), mood("governor", "DOU", "smug"), zh("orders"), cam=REG),
 B("And it is a story about the few people who said no. An old admiral who would not fight over a pig. An old general who knew how to calm things down.",
   show("admiral", "BAY"), mood("pig", "BAY", "smug"), show("general", "SCO"), mood("calm", "SCO", "happy")),
 B("Wars start with small things all the time. This one ended with a small thing too. One man, at the right moment, deciding that a pig was only a pig.",
   ("small", {"hide": ["PIC", "DOU", "SCO"]}), zh("ended"), big("pig", "ONLY A PIG", 2.4), mood("pig", "BAY", "happy"), cam=ISL),
]})

story = {
 "id": "sb-pig-war", "brand": "smoke", "narrator": "bm_george",
 "voices": {"CUT": "am_michael", "GRF": "bm_lewis", "US": "am_michael", "RN": "bm_lewis", "CAM": "am_adam", "PRE": "bm_daniel",
            "DOU": "bm_daniel", "PIC": "am_adam", "BAY": "bm_fable", "SCO": "am_michael", "POLK": "am_adam"},
 "title": "The Pig War: How ONE Pig Nearly Started a War Between Britain and America",
 "era": "1914", "musicEra": "1800s",
 "balls": {
  "CUT": {"flag": "US48", "label": "LYMAN CUTLAR", "at": [-122.9, 48.43], "r": 52, "char": {"preset": "settler", "facing": -1}},
  "GRF": {"flag": "GBR", "label": "CHARLES GRIFFIN", "at": [-123.08, 48.43], "r": 52, "char": {"preset": "hbc_man", "facing": 1}},
  "US": {"flag": "US48", "label": "UNITED STATES", "at": [-122.2, 47.9], "r": 56, "char": {"preset": "us_army_1859", "facing": -1}},
  "RN": {"flag": "GBR", "label": "BRITAIN", "at": [-124.0, 48.9], "r": 56, "char": {"preset": "rn_officer", "facing": 1}},
  "RM": {"flag": "GBR", "label": "ROYAL MARINES", "at": [-123.3, 48.75], "r": 50, "char": {"preset": "redcoat", "hat": "kepi", "hatCol": "#1c1a1a", "hairStyle": "short", "hair": "#3b2a1a", "facing": 1}},
  "SAL": {"flag": "CA", "label": "COAST SALISH", "at": [-122.6, 48.95], "r": 50, "char": {"coat": "#7a4a2a", "coat2": "#c9a85a", "hat": "none", "hairStyle": "long", "hair": "#1c1a1a", "skin": "#b07a55", "trim": "#b3202a", "facing": -1}},
  "DOU": {"flag": "GBR", "label": "GOV. JAMES DOUGLAS", "at": [-123.9, 48.25], "r": 50, "char": {"preset": "douglas", "facing": 1}},
  "POLK": {"flag": "US48", "label": "PRESIDENT POLK", "at": [-118.0, 44.0], "r": 52, "char": {"preset": "governor", "hairStyle": "short", "hair": "#8a8a8a", "coat": "#1c1c22", "facing": -1}},
  "BUC": {"flag": "US48", "label": "JAMES BUCHANAN", "at": [-118.5, 43.0], "r": 50, "char": {"preset": "governor", "hairStyle": "short", "hair": "#efeae0", "coat": "#1c1c22", "facing": -1}},
  "PRE": {"flag": "GBR", "label": "JAMES PREVOST", "at": [-123.7, 48.6], "r": 48, "char": {"preset": "rn_officer", "facing": 1}},
  "CAM": {"flag": "US48", "label": "ARCHIBALD CAMPBELL", "at": [-122.4, 48.6], "r": 48, "char": {"preset": "governor", "hairStyle": "short", "hair": "#5a3b22", "coat": "#2a2a33", "facing": -1}},
  "HAR": {"flag": "US48", "label": "GEN. HARNEY", "at": [-121.7, 47.2], "r": 50, "char": {"preset": "us_army_1859", "beard": "full", "hair": "#d8d3cb", "epaulettes": 1, "facing": -1}},
  "PIC": {"flag": "US48", "label": "CAPT. PICKETT", "at": [-122.85, 48.52], "r": 50, "char": {"preset": "pickett", "facing": -1}},
  "CAS": {"flag": "US48", "label": "COL. SILAS CASEY", "at": [-122.75, 48.38], "r": 46, "char": {"preset": "us_army_1859", "beard": "full", "hair": "#8a8a8a", "facing": -1}},
  "ROB": {"flag": "US48", "label": "LT. HENRY ROBERT", "at": [-122.95, 48.56], "r": 46, "char": {"preset": "us_army_1859", "beard": "none", "facing": -1}},
  "BAY": {"flag": "GBR", "label": "ADM. BAYNES", "at": [-123.6, 48.3], "r": 50, "char": {"preset": "rn_officer", "hair": "#d8d3cb", "beard": "full", "medal": 1, "facing": 1}},
  "SCO": {"flag": "US48", "label": "GEN. WINFIELD SCOTT", "at": [-122.6, 48.25], "r": 52, "char": {"preset": "us_army_1859", "hat": "bicorne", "hatCol": "#111", "hair": "#d8d3cb", "beard": "none", "epaulettes": 1, "medal": 1, "facing": -1}},
  "KAI": {"flag": "DE", "label": "KAISER WILHELM I", "at": [13.4, 54.0], "r": 52, "char": {"preset": "hessian", "hat": "none", "hair": "#d8d3cb", "beard": "full", "coat": "#1f2f4a", "medal": 1, "facing": -1}},
  "BAN": {"flag": "US48", "label": "GEORGE BANCROFT", "at": [2.0, 46.0], "r": 48, "char": {"preset": "governor", "hairStyle": "short", "hair": "#d8d3cb", "beard": "full", "coat": "#2a2a33", "facing": 1}}
 },
 "places": {
  "San Juan Island": [-123.08, 48.53], "Garrison Bay": [-123.15, 48.59], "English Camp": [-123.15, 48.59], "American Camp": [-123.03, 48.47],
  "Belle Vue Farm": [-122.98, 48.46], "Smallpox Bay": [-123.16, 48.55], "Fort Victoria": [-123.37, 48.43], "Esquimalt": [-123.43, 48.43],
  "Fort Bellingham": [-122.52, 48.77], "Fort Steilacoom": [-122.58, 47.17], "Fort Vancouver": [-122.66, 45.62], "Columbia River": [-123.9, 46.25],
  "Fraser River": [-121.44, 49.38], "Washington, D.C.": [-77.04, 38.9], "London": [-0.13, 51.5], "Mexico City": [-99.13, 19.43],
  "Callao": [-77.15, -12.05], "New Orleans": [-90.07, 29.95], "Aroostook": [-68.3, 46.7], "St. Louis": [-90.2, 38.63],
  "Gettysburg": [-77.23, 39.83], "Philadelphia": [-75.17, 39.95], "New Bedford": [-70.93, 41.64], "Berlin": [13.4, 52.52], "Geneva": [6.14, 46.2]
 },
 "sources": [
  "Wikipedia, Pig War (1859): https://en.wikipedia.org/wiki/Pig_War_(1859)",
  "Wikipedia, Oregon boundary dispute: https://en.wikipedia.org/wiki/Oregon_boundary_dispute",
  "Wikipedia, Oregon Treaty: https://en.wikipedia.org/wiki/Oregon_Treaty",
  "Wikipedia, James K. Polk: https://en.wikipedia.org/wiki/James_K._Polk",
  "Wikipedia, Hudson's Bay Company: https://en.wikipedia.org/wiki/Hudson%27s_Bay_Company",
  "Wikipedia, Fort Vancouver: https://en.wikipedia.org/wiki/Fort_Vancouver",
  "Wikipedia, Fort Victoria (British Columbia): https://en.wikipedia.org/wiki/Fort_Victoria_(British_Columbia)",
  "Wikipedia, James Douglas (governor): https://en.wikipedia.org/wiki/James_Douglas_(governor)",
  "Wikipedia, San Juan Island: https://en.wikipedia.org/wiki/San_Juan_Island",
  "Wikipedia, San Juan Islands: https://en.wikipedia.org/wiki/San_Juan_Islands",
  "Wikipedia, Lummi people: https://en.wikipedia.org/wiki/Lummi_people",
  "Wikipedia, Lekwungen: https://en.wikipedia.org/wiki/Lekwungen",
  "Wikipedia, Coast Salish peoples: https://en.wikipedia.org/wiki/Coast_Salish_peoples",
  "Wikipedia, Haro Strait: https://en.wikipedia.org/wiki/Haro_Strait",
  "Wikipedia, Rosario Strait: https://en.wikipedia.org/wiki/Rosario_Strait",
  "Wikipedia, James Charles Prevost: https://en.wikipedia.org/wiki/James_Charles_Prevost",
  "Wikipedia, Fraser Canyon Gold Rush: https://en.wikipedia.org/wiki/Fraser_Canyon_Gold_Rush",
  "Wikipedia, Donation Land Claim Act: https://en.wikipedia.org/wiki/Donation_Land_Claim_Act",
  "Wikipedia, Fort Bellingham: https://en.wikipedia.org/wiki/Fort_Bellingham",
  "Wikipedia, William S. Harney: https://en.wikipedia.org/wiki/William_S._Harney",
  "Wikipedia, George Pickett: https://en.wikipedia.org/wiki/George_Pickett",
  "Wikipedia, Pickett's Charge: https://en.wikipedia.org/wiki/Pickett%27s_Charge",
  "Wikipedia, Henry Martyn Robert: https://en.wikipedia.org/wiki/Henry_Martyn_Robert",
  "Wikipedia, Robert's Rules of Order: https://en.wikipedia.org/wiki/Robert%27s_Rules_of_Order",
  "Wikipedia, Silas Casey: https://en.wikipedia.org/wiki/Silas_Casey",
  "Wikipedia, Geoffrey Hornby: https://en.wikipedia.org/wiki/Geoffrey_Hornby",
  "Wikipedia, Robert Lambert Baynes: https://en.wikipedia.org/wiki/Robert_Lambert_Baynes",
  "Wikipedia, Winfield Scott: https://en.wikipedia.org/wiki/Winfield_Scott",
  "Wikipedia, Treaty of Washington (1871): https://en.wikipedia.org/wiki/Treaty_of_Washington_(1871)",
  "Wikipedia, Wilhelm I: https://en.wikipedia.org/wiki/Wilhelm_I",
  "Wikipedia, George Bancroft: https://en.wikipedia.org/wiki/George_Bancroft",
  "Wikipedia, San Juan Island National Historical Park: https://en.wikipedia.org/wiki/San_Juan_Island_National_Historical_Park"
 ],
 "intro": intro, "chapters": ch,
 "outro": {"text": "Every border has two sides. This one was nearly drawn in blood, over a pig, and was settled in the end by a referee and a few people who said no.",
           "question": "Was Admiral Baynes right to refuse, or would you have landed the Marines?",
           "next": "WORLD WAR TWO"},
 "thumb": {"layout": "versus", "scene": "sea", "topic": "THE PIG WAR · 1859", "hook": ["1 PIG.", "2 EMPIRES."], "hi": "PIG",
           "hidden": {"preset": "settler", "mood": "angry", "facing": -1}, "anchor": {"preset": "hbc_man", "mood": "angry", "facing": 1}},
 "hook": "In 1859, an American farmer shot a British company's pig. Within weeks, 461 American soldiers faced five British warships.",
 "about": "The Pig War of 1859, told from both sides: the Oregon Country and the Hudson's Bay Company, the Coast Salish peoples of the San Juan Islands, Polk and the 1846 Oregon Treaty, the two straits, the boundary commission, the Fraser gold rush, Lyman Cutlar and Charles Griffin, George Pickett and 'a Bunker Hill', Admiral Baynes and 'a squabble about a pig', Winfield Scott's deal, twelve years of joint occupation, Pickett's Charge and Robert's Rules of Order, and the Kaiser's 1872 decision.",
 "tags": ["pig war", "pig war 1859", "san juan island", "pig war explained", "britain vs america", "us canada border", "oregon treaty", "george pickett", "hudson's bay company", "british columbia history", "washington state history", "pacific northwest history", "history documentary", "both sides history", "bloodless war"],
 "abTest": [
  {"title": "The Pig War: How ONE Pig Nearly Started a War", "thumb": {}},
  {"title": "The Pig War: How ONE Pig Nearly Started a War", "thumb": {"layout": "mapperson", "hook": ["HE SHOT", "THE PIG"], "hi": "PIG"}},
  {"title": "The Pig War: How ONE Pig Nearly Started a War", "thumb": {"layout": "spotlight", "hook": ["NOBODY DIED.", "EXCEPT THE PIG."], "hi": "PIG"}}
 ],
 "localizations": {
  "de": {"title": "Der Schweinekrieg: Wie EIN Schwein fast einen Krieg auslöste",
         "description": "1859 erschoss ein amerikanischer Farmer das Schwein einer britischen Handelsgesellschaft. Wenige Wochen später standen 461 amerikanische Soldaten fünf britischen Kriegsschiffen gegenüber.\n\nDer Schweinekrieg von 1859, erzählt von beiden Seiten: das Oregon-Land und die Hudson's Bay Company, die Coast-Salish-Völker der San-Juan-Inseln, Polk und der Oregon-Vertrag von 1846, die zwei Meerengen, der Goldrausch am Fraser, Lyman Cutlar und Charles Griffin, George Pickett, Admiral Baynes, Winfield Scotts Abkommen, zwölf Jahre gemeinsamer Besatzung und der Schiedsspruch des Kaisers von 1872."},
  "es": {"title": "La Guerra del Cerdo: cómo UN cerdo casi provocó una guerra",
         "description": "En 1859, un granjero estadounidense mató a tiros el cerdo de una compañía británica. En pocas semanas, 461 soldados estadounidenses se enfrentaban a cinco buques de guerra británicos.\n\nLa Guerra del Cerdo de 1859, contada desde ambos lados: el territorio de Oregón y la Compañía de la Bahía de Hudson, los pueblos salish de las islas San Juan, Polk y el Tratado de Oregón de 1846, los dos estrechos, la fiebre del oro del Fraser, Lyman Cutlar y Charles Griffin, George Pickett, el almirante Baynes, el acuerdo de Winfield Scott, doce años de ocupación conjunta y el arbitraje del káiser en 1872."},
  "fr": {"title": "La guerre du Cochon : comment UN cochon a failli déclencher une guerre",
         "description": "En 1859, un fermier américain abat le cochon d'une compagnie britannique. En quelques semaines, 461 soldats américains font face à cinq navires de guerre britanniques.\n\nLa guerre du Cochon de 1859, racontée des deux côtés : le pays de l'Oregon et la Compagnie de la baie d'Hudson, les peuples salish des îles San Juan, Polk et le traité de l'Oregon de 1846, les deux détroits, la ruée vers l'or du Fraser, Lyman Cutlar et Charles Griffin, George Pickett, l'amiral Baynes, l'accord de Winfield Scott, douze ans d'occupation conjointe et l'arbitrage du Kaiser en 1872."},
  "pt": {"title": "A Guerra do Porco: como UM porco quase começou uma guerra",
         "description": "Em 1859, um fazendeiro americano matou a tiro o porco de uma companhia britânica. Em poucas semanas, 461 soldados americanos enfrentavam cinco navios de guerra britânicos.\n\nA Guerra do Porco de 1859, contada dos dois lados: o território do Oregon e a Companhia da Baía de Hudson, os povos salish das ilhas San Juan, Polk e o Tratado do Oregon de 1846, os dois estreitos, a corrida do ouro do Fraser, Lyman Cutlar e Charles Griffin, George Pickett, o almirante Baynes, o acordo de Winfield Scott, doze anos de ocupação conjunta e a arbitragem do Kaiser em 1872."}
 }
}


POS = {"RN": [-124.6, 49.2], "DOU": [-124.3, 48.15], "PRE": [-123.9, 49.0], "BAY": [-124.75, 48.6], "RM": [-123.5, 49.1], "GRF": [-123.25, 48.36],
       "US": [-121.9, 48.0], "CUT": [-122.75, 48.36], "HAR": [-121.6, 47.4], "PIC": [-122.4, 48.62], "CAS": [-122.15, 48.9], "ROB": [-122.85, 48.75],
       "SCO": [-122.5, 47.7], "CAM": [-122.0, 48.5], "SAL": [-121.6, 48.95]}
for k, v in POS.items(): story["balls"][k]["at"] = v
story["balls"]["SAL"]["flag"] = "DOT"
CAST = [["US", "RN"], ["SAL", "DOU"], ["POLK", "RN", "US", "BUC"], ["US", "RN"], ["PRE", "CAM", "US", "RN"], ["DOU", "CUT", "GRF", "RN", "US"],
        ["CUT", "GRF", "US"], ["HAR", "PIC", "RN", "DOU"], ["RN", "DOU", "US", "CAS", "ROB", "BAY"], ["US", "RN", "BUC", "HAR", "SCO", "DOU"],
        ["RM", "US", "GRF", "CUT", "SAL"], ["DOU", "PIC", "ROB", "CAS", "RN", "BAY", "US", "RM"], ["KAI", "BAN", "US", "RM"],
        ["US", "RM", "SAL", "CUT", "GRF", "PIC", "DOU", "BAY", "SCO"]]
assert len(CAST) == len(ch)
for c, cast in zip(ch, CAST):
    c["beats"][0]["do"].insert(0, {"hide": [k for k in story["balls"] if k not in cast]})

vis = set(); fixed = 0
for sec in [intro] + ch:
    for b in sec["beats"]:
        new = []
        for a in b.get("do", []):
            for k in a.get("hide", []): vis.discard(k)
            for k in a.get("show", []): vis.add(k)
            who = (a.get("mood") or a.get("say") or [None])[0] if isinstance(a.get("mood") or a.get("say"), list) else None
            if who and who in story["balls"] and who not in vis:
                new.append({"on": a["on"], "show": [who]} if a.get("on") else {"show": [who]}); vis.add(who); fixed += 1
            new.append(a)
        if "do" in b: b["do"] = new
print("auto-shows", fixed)

for c in ch:
    if not any("date" in a for a in c["beats"][0]["do"]):
        c["beats"][0]["do"].insert(1, {"date": c["years"].upper()})
# checks
words = 0; bad = []
for sec in [intro] + ch:
    for b in sec["beats"]:
        s = b.get("say", ""); words += len(s.split())
        for a in b.get("do", []):
            w = a.get("on")
            if w and w.lower() not in s.lower(): bad.append((w, s[:50]))
            if "pin" in a and a["pin"] not in story["places"]: bad.append(("PIN " + a["pin"], ""))
            for k in ("show", "hide"):
                for i in a.get(k, []):
                    if i not in story["balls"]: bad.append(("BALL " + i, ""))
            for k in ("mood",):
                if k in a and a[k][0] not in story["balls"]: bad.append(("BALL " + a[k][0], ""))
            if "say" in a and a["say"][0] not in story["balls"]: bad.append(("SAYBALL " + a["say"][0], ""))
print("words", words, "chapters", len(ch)); print("problems", bad)
json.dump(story, open(OUT, "w"), indent=1, ensure_ascii=False)
