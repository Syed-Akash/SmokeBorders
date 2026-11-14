# Smoke & Borders: how an episode is written and edited

Every episode has two audiences at once: people **listening** with the screen off (phone in a pocket, a second tab, a commute) and people **watching**. A listener must never miss anything, and a watcher must never get bored. Each rule below serves one or both. The weekly review (RUNBOOK step 6) edits this file when the numbers show something better, and logs why in LEARNINGS.md.

## 1. The story engine (both audiences)
- **Two sides, always.** Every episode has two sides with real faces (Benjamin vs William Franklin, Rome vs Carthage). Chapters switch sides. The viewer should be unsure who to root for at least twice.
- **Intention + obstacle.** Every chapter opens with what someone wants and what stands in the way.
- **But / therefore, never "and then".** Each beat either causes the next problem ("but…") or answers a question while opening a new one ("so…"). If two beats could swap places, the story is a list: rewrite it.
- **Open a loop every chapter.** End each chapter on a question the next one answers. Every 2–3 minutes, remind the viewer of the big question from the cold open.
- **Cold open (first 30–45 s).** Start mid-action with the most shocking true fact. Give the stakes in the first 15 seconds. No greeting, no "in this video". Say the search words (topic, year, the two sides) inside the first 30 seconds, because YouTube indexes speech.
- **Dark humour** comes from bad decisions, bureaucracy and irony, never from victims. Deaths are told plainly and slowly, with a beat of silence after.
- **Close.** "What the line remembers": one human truth, then one spoken question for the comments, then the next episode by name.
- **Subscribe, bell and like (owner, 7 Nov 2026).** The renderer adds them automatically; don't write them into the script.
  - Once in the middle: a silent lower-third card at the start of chapter 3 (about a quarter in, after real value), where a cursor clicks Subscribe, rings the bell and likes. `subChapter` moves it; `noSub` turns it off.
  - At the end, after the question: one warm spoken line ("If you enjoyed this story, subscribe to stay connected, and tap the bell so you never miss the next one.") with the same animation, then 20 seconds of end card for YouTube's end screen. `outro.cta` replaces the line.
  - Never at the start, never twice in a row, never pleading.

- **The hidden person (owner, 9 Nov 2026).** Every episode is built around one to three people or details almost nobody has heard of, and the title and thumbnail lead with them: the driver who was never told the route had changed (WW1), Hitler's nephew who joined the US Navy to fight his uncle (WW2), the Carthaginian general's wife who cursed him as the city burned (Rome). The big war is the setting; the hidden person is the story. Rules:
  - **It must be true and sourced**, and big enough to carry the episode: introduce them in the first 3 minutes, come back to them at least twice, and pay them off at the end. A thumbnail promise the video doesn't keep is misleading metadata and gets punished by viewers and by YouTube.
  - **Specific beats generic.** Names, ages, the exact words someone said, what they ate, what happened to them afterwards. Cut summaries any textbook has.
  - **Thumbnail:** the hidden person big, with a 1–3 word line that makes them a question ("SHE CURSED HIM", "NOBODY TOLD HIM", "HITLER'S NEPHEW?"). Add a new character preset in chars.js when the person needs one (`carthaginian_woman` exists).
  - **Title:** pair A stays the plain big promise ("Rome vs Carthage: The ENTIRE War From Both Sides") so search finds it; pairs B and C lead with the hidden person ("The Woman Who Cursed Her Husband as Carthage Burned"). The A/B test tells us which pulls more.
  - Never invent a relative, a secret or a twist. If the famous rumour is false (Hitler had no children), the true version usually makes a better story.

## 2. Writing for the ear (listeners)
- **One idea per sentence.** Aim for an average under 16 words, nothing over 28. Put the key word at the end of the sentence, where the ear lands.
- **Read it aloud.** If a line can't be said in one breath, split it. If two sentences in a row start the same way, change one.
- **Never rely on the screen.** Never say "as you can see" or "this", meaning something only on screen. Say the place, the side and the direction: "north, into Canada".
- **Numbers.** Round them ("about sixty thousand"), say them at most twice a minute, and give a comparison when it helps. Exact figures go on the stat card and in the pinned sources.
- **People.** Introduce each person once with a tag ("William, the King's governor"), then reuse the same tag. Never more than three named people in a chapter.
- **Signposts.** The narrator says every chapter title out loud (the renderer does this automatically). Use spoken transitions too: "Now the other side." "Meanwhile, in London."
- **Dialogue is voiced.** Every speech bubble is spoken in its own voice (`voices` in the story), so listeners hear the argument. Keep lines under 12 words.
- **Sound tells the place.** Each scene has a sound listeners can picture: sea for the fleet, crowds, gunfire, a pen on paper for treaties. Most are added automatically from the narration's words. Add `sfx` where a scene would otherwise be silent.
- **Silence.** Leave about a second of silence (music down) before a big reveal or after a death toll.

## 2b. A film, not a map (owner, 14 Nov 2026: "think like actual documentaries or movies... unique scenes according to the script... only show the map where it's necessary... we have a lot of competition")
Every episode is storyboarded like a film before it is rendered. **No episode reuses another episode's look: its shots come from its own script.**
- **Write it as a story, minute by minute, in the present tense.** Open each scene on a date, a place and a person doing something; the clock keeps moving ("15 June 1859 ... that afternoon ... by the tenth of August ..."). Every detail is still sourced; staging that isn't recorded (the lamp, the fog) stays on screen and out of the narration.
- **Every spoken beat has a shot** (`"scene"` in the beat). A new shot every 5-15 seconds; never one shot (or one map stretch) over 20 seconds.
- **The shot types** (studio/doc/scenes.js + scenes2.js):
  - `photo`: a REAL archival photo or painting from Wikimedia Commons in 2.5-D (subject cut out, camera drifting through the layers, sepia/bw grade, grain, smoke/fog/dust): `{"shot": "photo", "img": "<name>", "caption": "...", "move": "in|out|left|right", "focus": [x, y], "fx": [...]}`. Make each with `python3 smoke/photo.py <story-id> <name> "<File:...>" [--flat]` (--flat for landscapes and drawings) and list them in the story's `"photos"` {name: [file, flat]} so a later run can remake missing ones. Use real photos of the real people and places wherever they exist: they are what makes it feel true.
  - `doc`: a document filling the frame, typed out: `{"shot": "doc", "kind": "letter|telegram|newspaper", "header", "lines": [...], "sign", "stamp"}`. Only real wording in quotation marks; a paraphrase is labelled ("orders, in short"). Never put an invented headline under a real newspaper's name (use "~ 1859 ~").
  - `card`: the minute-by-minute clock card: `{"shot": "card", "time": "15 JUNE 1859", "place": "SAN JUAN ISLAND", "date": "Wednesday morning"}`. Times of day only when the sources give them.
  - `set`: an illustrated scene built from parts, so each one is new: `{"shot": "set", "time": "dawn|day|dusk|night", "weather": "fog|rain|snow|storm", "parts": [...], "fx": [...], "push", "pan"}`. Parts: sea, land (grass/mud/snow/sand/street/floor), hills, forest, coast, town, fort, camp, ships (sail/steam, flag), soldiers (colour, march), cannons (fire), crowd, farm, animal (pig/sheep), flagpole, fire, room (window, flag, portrait), table (lamp, candles, papers), people (silhouettes with poses, or `photo` cut-outs). If the story needs something the parts can't draw (a trench, a palace, a tank, a train), add a new part to scenes2.js in the same style, and keep it for later episodes.
  - the map (`{"shot": "off"}`) only when geography explains something: at most 30% of the runtime, never over 20 s at a time.
  - the earlier drawn shots (pentagon-night, office-night, map-desk, faces, village) are Korea's; reuse only when they fit.
- **The film check** (make_doc.py, on stories with `"film": true`): scenes at least 70% of the runtime, the map at most 30%, no shot over 20 s, every chapter opens on a scene. If it fails, the render does not start. Look at one contact sheet of 16 shots before the long render.
- `sb-pig-war.json` is the worked example (182 beats, 15 archival photos, documents, cards, sets).

## 2c. Acted, fast and concrete (owner, 15 Nov 2026, after studying Paper Billions: "go with" points 1, 2, 3, 5; length 25-45 min, thumbnails stay the three templates)
Paper Billions (@PaperBillionsTV) got millions of views with money stories drawn on paper. What we copy:
- **Characters talk.** About once a minute (25-35 exchanges an episode) a short acted exchange: 1-5 lines, each under ~12 words, in the
  characters' own voices. Write it as a `talk` beat: `{"talk": [{"who": "CUT", "text": "...", "mood": "angry"}], "bg": <set shot>}`. Every
  speaker needs an entry in the story's `"cast"` ({who: {preset, name, spec}}; presets in studio/doc/vendor/chars.js) and in `"voices"`.
  In film episodes each line becomes its own close-up (shot / reverse shot) with the line typed in a name-tagged box.
  **Truth rule for dialogue:** dramatized from the record. Real people only act out what the sources say they did or said (a real quote
  may be spoken by its speaker); jokes and colour go to unnamed roles ("A British sailor", "A clerk", "A voter"). Never put a new opinion,
  confession or claim in a real person's mouth. Add `"talkNote": "Dialogue scenes are dramatized; every fact comes from the sources below."`
- **A cut every 3-4 seconds.** The renderer adds angle cuts (wide / medium / close of the same picture) every ~3 s inside any shot
  longer than ~5 s; dialogue cuts on every line. The FILM CHECK prints "a cut every X s": aim 3-4.
- **Make every big number concrete.** Convert it into something people know, using only arithmetic on sourced numbers: per person,
  per day, "about the price of...", "sixty newcomers for every resident", "about 240 football fields". Show it on a time card.
- **Callbacks.** Plant 2-3 running lines early (a date, a sum of money, a phrase) and pay them off later; end on a callback to the
  cold open ("Still not paying." / "Still waiting.").
- **Hook on names people know, and on the news.** The cold open's first sentence names the most famous person or thing in the story and
  the twist ("The boss of the most valuable company on Earth is having dinner with a Chinese spy"). When an old border is in today's
  news, say so in the first minute. Pick topics that touch a famous name or a current headline when the plan allows.

## 3. Editing for the eye (watchers)
- **First 3 minutes:** something new on screen every 6–10 seconds, such as a camera move, pin, arrow, card, or a ball reacting. After that, every 15–25 seconds is enough, but the camera is never completely still.
- **Pattern interrupt at 25–35 seconds:** the logo sting, a big card or a sharp camera move.
- **A burst every 2–3 minutes:** 3–5 quick actions in a row (dates, arrows, explosion, stat card), then calm again.
- **Never hold one view more than about 20 seconds.** Never put two quote or stat cards back to back.
- **Shot size changes.** Alternate wide (the continent) and close (a city, a person) so cuts feel like cuts.
- **Map first.** Every place mentioned is pinned or highlighted at the moment it's said (`on` the spoken word).
- **Stat cards** carry the exact numbers; the narration says the rounded ones.
- **Music** changes at every chapter's mood and drops before reveals. The narrator always sits clearly above the music (the mix does this automatically).
- **Pace is new information, not cuts** (Mario Joos, MrBeast's former retention strategist): every 10–15 seconds the viewer must learn or see something that moves the story. Fast cuts with nothing new don't help.
- **Show the thumbnail's promise early.** The map change from the thumbnail (red empire → blue bite) appears in the first 30 seconds. Viewers who clicked for it and don't see it leave.
- **Value in 15 seconds.** Say what the viewer will get (the question and the stakes) within 15 seconds; this alone lifts 1-minute retention by about 18%.
- **Tease before every payoff.** Before each big scene, one teasing line and a short pause ("And that is when the King made the worst decision of his reign."). One creator moved a 20-minute video from 8–10 to 12+ minutes average watch time with only this.
- **Staircase.** Each chapter raises the stakes or changes the tone. Put peaks near 25%, 50% and 75% of the runtime, and a bridge line between chapters ("But the next move changed everything").
- **Alternate fast and slow.** Bursts of quick beats, then hold the emotional ones (a death toll, a letter) longer, with silence. Non-stop rapid editing numbs people.
- **Check it before rendering:** `./py make_doc.py <id> --pacing` lists every stretch with nothing new on screen (over 10 s in the first 3 minutes, over 20 s after) and the events per minute of each chapter. Fix every gap before the render.
- **Benchmarks** for 20–30 minute animated history: average view percentage 35–45% is good, and 40–50% of viewers still there at the end is strong. Compare with our own past episodes, not with Shorts.

## 4. Characters, thumbnails, Shorts (decided 6 Nov 2026 from the competitors' best videos)
- **No countryballs anywhere.** That's FlagBomb's look. Every side is an illustrated character from `smoke/brand/chars.js`: kings, generals, soldiers and statesmen, with period hats and coats and a small flag. In a story, give each ball a `char` (`{"preset": "king_george", "facing": -1}`, or any preset plus overrides). Add new presets to chars.js when an era needs them (samurai, legionary, Soviet officer…).
- **Thumbnails** use the Animated History layout with our twist (`smoke/make_thumb_sb.py`):
  - the old world on parchment on the left, today's world in colour on the right, split by our burning border;
  - one big character per side, looking at each other with opposite moods;
  - two black year boxes at the top, and one huge word at the bottom (HOW? LOST? STOLEN? WHY?);
  - the ember "BOTH SIDES" ribbon in the corner.
- **What makes it work is curiosity, not the layout** (owner review, 7 Nov 2026). The first thumbnail copied the layout and failed: the two maps had different framing, the brown territories were noise, and the characters hid the one thing that changed. Rules:
  - **Same map, same framing on both halves**, so the eye compares them without trying. The left half may draw an earlier year from a later map file if its borders tell the story better (1763 Britain = the 1783 US + Quebec + Rupert's Land).
  - **One bright change.** One saturated colour that grows, shrinks or gets bitten out. Everything else stays plain (`"plain": true`). Outline the shape that changed (`outline`).
  - **Characters sit at the outer edges** (h about 430), never covering the change.
  - **The text is a hook a stranger understands** (owner, 7 Nov 2026: "HOW?" or "LOST?" alone says nothing). Use two lines: a small ember `kicker` that names the topic ("BRITAIN LOST AMERICA"), then a huge `word` with the twist or the absurd cause ("OVER TEA?", "TO FARMERS?", "OVER A PIG?"). Put it at the top (`textY` 250) and the year boxes at the bottom (`yearsY` 600), so the text never covers the change on the map. It must be true or an honest question that the video answers.
  - **Label the sides on the map** (`labels`: BRITAIN on the red, USA on the blue), so nobody has to guess who is who.
  - Check it at 320x180 before uploading. If the change can't be seen at that size, the thumbnail fails.
- **Thumbnail text is 1–3 concrete words, ideally under 12 characters** (1of10 study of 300,000 videos: thumbnails with no text or under 10 characters do best, heavy text averages 19% fewer views). Use a concrete noun or number that makes the map ask a question ("OVER TEA?", "1 PIG", "38 MINUTES"), never an abstract word on its own ("HOW?", "LOST?"). The small `kicker` line is optional; test it in one A/B pair rather than using it everywhere.
- **Bright, not dark.** Dark thumbnails underperform. Keep the "now" half bright, with cyan, blue, green, yellow or orange; the parchment half stays light.
- **Two characters beat one.** Several faces do better than a single face. Big faces only help channels above about 200K subscribers, so characters are a supporting element and the map change is the hero.
- **Title + thumbnail are one package; never repeat the words.** The title promises the topic and the scope; the thumbnail adds the emotion or the twist.

- **FINAL thumbnail templates (owner, 12 Nov 2026: "we finalized these templates only"). Use ONLY these three, every episode:**
  - **spotlight**: the hidden person huge on the right, the famous figure smaller in the middle (red glowing eyes only if he is the villain), red topic bar with place and date top-left, a two-line hook ("13 MINUTES / TOO LATE").
  - **circled**: the famous figure big on the left, the hidden person small on the right inside a red circle with an arrow from the hook ("HE ALMOST DID IT").
  - **dossier**: the hidden person's real photo pinned like a polaroid, stamped "UNTOLD STORY", with a caption (name, year), and the two-line hook on the left.
  - All three are always in the dark style: `"scene": "relief"` (the country red on the map), `"dread": 1` (fire grade, embers, fire-lit real photos), grave crosses only when the story has deaths (`"graves": 0` otherwise, e.g. the Pig War). Real photos only (`smoke/portrait.py`), never cartoon characters. Red eyes (`eyes`) only on a villain the story itself treats as one. One yellow word (`hi`). No blood, wounds or bodies (YouTube removes or age-restricts them).
  - **Test & Compare (Title and thumbnail):** A = spotlight + "How X Happened — Minute by Minute", B = circled + "The N Days That Made X", C = dossier + A's title. Record the winner in LEARNINGS.md.
  - **Text never covers a person.** thumb2.html shrinks any person that touches text until nothing overlaps; make_thumb_sb.py prints a WARNING if it can't. On a warning, shorten the hook; never upload a thumbnail with a face behind words.
  - Retired (never use again): atlas, atlassplit, versus, mapperson, the plain dread layout, the v1 split, and cartoon characters on thumbnails. The code stays only so old thumbnails can be re-rendered.

## 4b. Titles (researched 7 Nov 2026: competitor outliers + 1of10 study of 300,000 videos)
- **What wins in our niche is a plain, big promise, not a riddle.** Current outliers: "The ENTIRE History of WW2 Explained" (2.1M, 4x that channel's median), "2000 Years of Israel History in 35 Minutes" (1.4M, 2.3x), "1500 Years of Russian History in 27 Minutes" (1.2M), "WW2 - OverSimplified (Part 1)" (105M). None of the outliers is a question.
- **Patterns that work:** "The ENTIRE History of X (Explained)", "N Years of X History in M Minutes", "X vs Y: The ENTIRE War", "Your Life as… / POV: You're…", "How X Became Y".
- **Short.** Five-word titles get the most engagement; past 6 words it drops and 10+ words underperform. Titles of 30 characters or fewer averaged about 60% more views. Keep the topic in the first 4–5 words and the whole title under about 60 characters, so it isn't cut on phones.
- **Plain spoken words, one CAPS word at most** (ENTIRE, EVER). Negative or dramatic emotion beats neutral (+22%), but no clickbait the video doesn't deliver.
- **Every episode gets 3 title + thumbnail pairs** (`abTest`): A = "How X Happened — Minute by Minute", B = "The N Days That Made X", C = A's title with a third layout (see above). The Monday review records winners in LEARNINGS.md.
- **The scout** (`smoke/scout.py`) collects every competitor's latest videos with their outlier scores, makes contact sheets of the best thumbnails and a table of title patterns (winners vs the rest). Look at the sheets before writing an episode's packaging.
- **Length: 25–45 minutes, aiming for 30–35 when the story has that much** (owner, 9 Nov 2026; minimum lowered to 25 on 15 Nov 2026: "if the topic can be covered completely... set 25 min as the minimum". Never pad a story to reach a length: no repeated points, no filler chapters, no stretched pauses). That is about 4,300–6,400 spoken words in 10–14 chapters, filled with specific people and details, never padding. A topic that can't fill 25 minutes honestly gets widened (the Shortest War becomes the Scramble for Africa through Zanzibar), never padded.
- **Shorts are cut from the episode** (owner, 11 Nov 2026, replacing standalone Short stories to save effort): Short 1 is the cold open, Short 2 a special moment from the middle that works without context (a twist, a shocking number, a reveal). Write both in the story's `"shorts"` (RUNBOOK 1.3c). That's why the cold open must hook on its own in under 58 seconds and end on a sentence that makes people want the rest.

## 5. Voice and music (researched 6 Nov 2026)
- **Narrator.** A deep, measured voice in the classic-documentary style ("a deep, measured baritone, similar to classic BBC narrators, is often preferred"), at **135–150 words a minute**. Under 120 loses people, and over 180 tires them.
  - Default `bm_george` at `narratorSpeed` 1.05, about 143 wpm. Change only via the owner's pick or the weekly review.
  - Match the accent to the story where it matters; a modern American voice narrating ancient Rome can feel jarring.
- **Engine: Chatterbox Turbo** (owner's pick from four samples, 7 Nov 2026), in George's timbre (`studio/turbo.py`). It rises and falls with the sentence, slows on "..." and can do a few non-word sounds. Write for it:
  - `...` for a held breath before a reveal ("Twenty years later... it had lost almost all of America.").
  - `[chuckle]` before a dry joke, at most once or twice an episode. Only `[chuckle]` is tested so far; try `[sigh]` or `[gasp]` in a test clip before using them in an episode.
  - Question marks and short sentences give it the most natural rise and fall; long lists flatten it.
  - Cues never show in the captions. If Turbo can't load, the run narrates with Kokoro and `studio/tts/engine.txt` says why; say so in the run summary.
- **Pauses.** About 200–300 ms between sentences and a beat more between sections; the renderer does this. Silence before reveals.
- **Music is texture and pulse under the voice, not melody.**
  - It changes only when the place, time or meaning changes (one mood per chapter), and builds by adding layers rather than volume.
  - No trailer risers or impacts the facts don't earn, and no music that implies a verdict on a disputed question.
  - The orchestral score comes from `studio/score.py`, set per chapter by `mood`. `musicEra` adds a period colour, for example fife and drum for the 1700s.
- **Mix.** Music sits about 20 dB under the narration (the researched documentary range is 18–24 dB). It is ducked a further 3–6 dB while the narrator speaks and cut about 5 dB around 2.5 kHz so it never fights the words. The final mix is normalized for YouTube.
- Sources: https://fluxnote.io/guides/best-ai-voice-for-history-documentary · https://syllaby.io/blog/voiceover-pacing-silence-trimming-retention-editing/ · https://sonilo.com/blog/guides/good-music-for-history-videos · https://www.overseeros.com/blog/background-music-volume-under-voiceover

## 6. Format checks before rendering
- Length 25–45 minutes, aiming for 30–35 when the story supports it (about 3,600–6,400 spoken words); never padded; 10–14 chapters of 5–9 beats. `--pacing` warns when it's outside.
- Every number is in `sources`, with a page that was actually opened.
- Search words are in the title, the first 30 seconds and the first chapter name.
- The episode's thumbnail block uses the "Then and Now" split (parchment on one side, colour on the other, burning seam, one character per side, 0–3 words).
- Text never mentions AI, bots or automation.

## Sources behind these rules
- Titles, thumbnails, length (300,000 videos): https://1of10.com/blog/what-actually-makes-a-youtube-video-go-viral-in-2025
- Thumbnail rules (MrBeast, MKBHD and a 100-tester blind experiment): https://chatimg.ai/en/blog/video-cover-methodology
- Retention editing (Mario Joos): https://vidpros.com/retention-editing-what-you-can-learn-from-mario-joos/
- Storytelling and teasing before payoffs (WinterKloudz, JW case studies): https://1of10.com/blog/storytelling-techniques-top-youtubers-use-to-keep-viewers-hooked
- Animated retention benchmarks: https://longstories.ai/blog/retention-benchmarks-animated-youtube-videos
- Test & Compare (titles and thumbnails, decided by watch time per impression): https://routenote.com/blog/youtube-expand-test-compare-how-to-use-it/
- Retention editing and pacing (cuts every 10–20 s early, 25–40 s later, rehook every ~2 min, bursts every 2–3 min, a beat of silence before reveals, music changes per chapter): https://air.io/en/youtube-hacks/advanced-retention-editing-cutting-patterns-that-keep-viewers-past-minute-8
- Writing for the ear (short lines, read aloud, conversational, start mid-story): https://www.themxgroup.com/resources/how-to-write-for-human-ear/
- Story mechanics (intention + obstacle, but/therefore, cut lines that change nothing): https://videotoblog.ai/blog/youtube-retention-cinema-story-mechanics-show-intention-obstacle-cause-effect
- The competitor research doc: https://claude.ai/artifact/21Dtv8pgh6QkJDkgRM82NX
