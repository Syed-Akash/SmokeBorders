# Smoke & Borders: daily run

The channel runs fully automatically. Cadence (owner, 11 Nov 2026; trial review on 5 Dec): **one video a day at most**, all at 16:00 UTC (11:00 New York, 16:00 London, 21:00 Pakistan), in a 3-day cycle:
- day 1: the long episode, 30-45 minutes (aim 30-35);
- day 2: Short 1, the story's opening (the cold open), cut from the episode;
- day 3: Short 2, a special moment from the middle, cut from the episode;
- day 4: the next episode.
Both Shorts are cut and uploaded (scheduled) in the same run as the episode; nobody writes separate Short stories any more. `smoke/plan.json` holds every date; `sbplan.py --today` turns them into jobs. The first episodes target the US, UK, Canada, Australia and Germany.

## Save effort (owner, 11 Nov 2026: the runs were using too much)
- Do only what `sbplan.py --today` lists. "Nothing due today" means: post queued comments, a 3-line summary, stop.
- Read only the sections of this file and STYLE.md that today's jobs need (WRITE: 1 and STYLE.md; RENDER/UPLOAD: 2 and 3; Monday: 6).
- Research for a WRITE: open each source once and note its facts in one pass; don't re-open pages or re-search a fact you already have.
- Wait for a render with ONE background command and a Monitor/`until` loop that wakes every 10 minutes and prints `tail -2` of the log. Never poll faster, never print a whole log.
- Look at frames as one contact sheet (one image, 6-8 frames), not one image per frame.
- No NexLev or competitor calls outside the Monday REVIEW.
- The final summary stays under 150 words.

Standing rules, never broken:
- Free tools only. Never print or commit keys.
- Never mention AI, bots or automation in any title, description, tag, comment, on-screen text or narration.
- Real facts only: every number comes from a page that was actually opened, and is listed in the story's `sources`.
- Both sides told fairly. Dark humour about decisions, never about victims. Never take sides in wars happening now.
- Category Entertainment (24). Upload with `YT_CHANNEL=smoke`; the uploader refuses any channel that isn't "Smoke & Borders".
- Commit and push every change to the repo (Syed-Akash/Flagbomb); end commit messages with the attribution lines the session gives.

## 0. Start
0. **Sync first:** `bash tools/sync_runs.sh`. Runs can only push to their own branch, so this merges every earlier run's branch into your checkout (uploads, queues, plans, rules). Skipping it means redoing or duplicating earlier work, such as uploading a Short twice. Never end a run with a merge that keeps only one side (`-s ours`): it silently deletes the other side's work. Comments are posted by the hourly GitHub job once a video is live; the run only queues them.
1. Check the last run finished (`git log -3`, `smoke/plan.json` statuses, any `out/*-doc-sb-*` folder with a half-finished render). Repair records first.
2. `python3 smoke/sbplan.py --today` lists today's jobs, most urgent first. Do them in order. A render is long (3–4 hours with the Turbo narrator): start it first, do the other jobs while it runs, and never end the run while it is still rendering (RENDER below).
3. Post queued first comments: `YT_CHANNEL=smoke python3 studio/upload.py --comments`.

## 1. WRITE an episode
1. Research the story (WebSearch, then open the pages you take facts from: encyclopedias, museums, national archives, universities, Battlefields.org-type sites). At least one opened source per number and date. If unsure, leave it out or say "historians still argue".
2. Pick the two sides (countries as countryballs, plus real people for the human story when the record allows; invented composites only if the narration says they are composites).
3. Write `studio/doc/stories/<id>.json` by `smoke/STYLE.md` and the format in `studio/doc/DOC-FORMAT.md`, with `"brand": "smoke"`, `"narrator": "bm_george"` and `voices` for every side that talks.
   - Every side is a `char` (illustrated character), never a countryball; see STYLE.md section 4.
   - Add a `logo` beat at the end of the intro (`{"do":[{"logo":1}],"pause":3.6}`).
   - Write an `outro` (`text`, `question`, `next` = the next episode's short name).
   - Add a `thumb` block (see `smoke/make_thumb_sb.py`) and `hook`, `about`, `tags`, plus `localizations` with translated titles and descriptions for de, es, fr and pt (more languages later).
   - Era maps live in `studio/doc/data` (bc1000, bc323, 100, 800, 1279, 1492, 1700, 1715, 1783, 1800, 1815, 1914, 1920, 1938, 1945, 1960, 1994); add more from aourednik/historical-basemaps if needed.
3d. **Storyboard (owner, 14 Nov 2026):** give every spoken beat its own shot and make the episode's archival photos, by STYLE.md 2b; set `"film": true`. Check with `./py make_doc.py <id> --pacing` (the FILM CHECK line) and one 16-shot contact sheet (`--stills`).
3c. Add `"shorts"`: the two Shorts cut from this episode (owner, 11 Nov 2026). Short 1 starts at the very beginning (the cold open); Short 2 starts at a special moment in the middle (a twist, a shocking number, a reveal) that works without context. `[{"head": "LINE 1|LINE 2", "title": "..."}, {"from": "<first words of that beat's say>", "head": "...", "title": "..."}]`. Heads are 1-3 words per line; titles are the hook plus one CAPS word plus #shorts. make_doc.py turns them into `shortCuts` (start and length, ending on a full sentence, under 58 s) in summary.json.
3b. Add `abTest` (during the layout test, see `smoke/layout_tests.json`: one title, three thumb2 layouts from its "next" list; update "next" and add the episode to "tests"): three title + thumbnail pairs for YouTube's Test & Compare (STYLE.md section 4 thumbnail rules). A is the best guess and is what gets uploaded; B and C try a different hook (the absurd cause, the underdog, the plain topic). Each pair is `{"title": "...", "thumb": {"kicker": "...", "word": "..."}}`; every title keeps the search words.
4a. Pacing: `cd studio && ./py make_doc.py <id> --pacing` and fix every gap it lists (STYLE.md section 3).
4. Check it: every `on` word appears in its beat's `say`, every `pin` is in `places`, and the word count is 4,300–6,400 (about 30–45 minutes, aiming for 30–35).
5. Render stills and look at them: `cd studio && ./py make_doc.py <id> --stills 3,40,120,300,600` (background; voice synthesis takes a few minutes). Fix what looks wrong.
6. `python3 smoke/sbplan.py set <id> scripted`; commit.

## 2. RENDER
- **A render outlives one run only if you save it.** Every scheduled run starts on a fresh computer and everything not pushed is gone when it ends.
  1. Before rendering: `cd studio && ./py wip.py restore <id>` (brings back finished pieces and voice clips from branch `wip/<id>`, if any).
  2. Start `./py make_doc.py <id> --resume > ../smoke/render-<id>.log 2>&1` with `run_in_background` and the longest timeout.
  3. **Do not end the run while it renders.** Do the other jobs, then wait in the foreground: check the log every ~10 minutes (a Monitor or an `until` loop), and every ~15 minutes run `./py wip.py save <id>`.
  4. If the run must stop before the render finishes, run `./py wip.py save <id>` first and say in the summary how many pieces are done; the next run restores and continues.
  5. After the upload succeeds: `./py wip.py clear <id>`.
- When `out/<date>-doc-<id>/<id>.mp4` and `summary.json` exist, watch three spots (start, middle, end) as stills (`ffmpeg -ss T -i file -frames:v 1`).
- Read `studio/tts/engine.txt` after the render starts: it says `turbo` (the owner's chosen narrator) or `kokoro (Turbo failed: …)`. If it fell back, say so in the summary. Turbo adds about an hour of voice work per episode, so start the render early.
- **Photos first:** for every entry in the story's `"photos"` ({name: [Commons file, flat]}) without `studio/doc/photos/<id>/<name>.jpg`, run `python3 smoke/photo.py <id> <name> "<file>"` (add `--flat` when flat is true). Commit the photos.
- **Portraits first:** for every entry in the story's `"portraits"` ({name: Commons file}) that has no `smoke/portraits/<name>.png` yet, run `python3 smoke/portrait.py <name> "<file>"` (it checks the licence; Wikimedia sometimes answers 429, then it waits and retries). Commit the PNGs and credits.json. Never mirror a photo with writing on it.
- Make the thumbnail (pair A): `python3 smoke/make_thumb_sb.py <id> studio/out/<dir>/thumb.jpg`, and look at it.
- Make all three pairs: `python3 smoke/make_thumb_sb.py <id> --ab` writes `smoke/ab/<id>/a.jpg, b.jpg, c.jpg` and `ab.md`. Look at each at 320x180, then commit them.
- `python3 smoke/sbplan.py set <id> rendered`; commit (not the video files). Then do UPLOAD in the same run: the video files are gone when the run ends.

## 3. UPLOAD (scheduled, never published immediately)
1. `python3 smoke/make_meta.py <id> <publish>` builds `meta.json`: title, description with chapters, tags, thumbnail, captions, playlist, sources as the first comment, and localizations. Read it; fix anything odd.
2. `cd studio && YT_CHANNEL=smoke python3 upload.py out/<dir>/<id>.mp4 out/<dir>/meta.json`.
3. Record the episode's `videoId` in `smoke/plan.json` (so the Shorts can link to it).
3a. **Both Shorts, cut from the episode:** `python3 smoke/cut_shorts.py <id> auto` (uses `shortCuts` from summary.json; if it's missing, give start and length by hand: `cut_shorts.py <id> <n> <start> <length> "LINE 1|LINE 2"`). Look at one contact sheet of both (2 frames each). For each: `python3 smoke/make_meta.py <id> <publish> --short <n>` (title from the story's `shorts`), then `cd studio && YT_CHANNEL=smoke python3 upload.py out/<dir>/short-<n>.mp4 out/<dir>/short-<n>.meta.json` scheduled at its date, then `python3 smoke/sbplan.py short <id> <n>`. Commit after each upload.
4. `python3 smoke/sbplan.py set <id> uploaded`; commit.
4b. **End screen.** Every long video ends with 20 seconds of end card. The API can't add end screen elements, so in the summary remind the owner: Studio > the video > Editor > End screen > Import from video (pick the previous episode), so the subscribe button and next video appear.
5. **Test & Compare.** YouTube's API can't start the test, so the owner does it in Studio (about a minute). In the run's summary, add a section "Set up the A/B test", with the video's Studio link (https://studio.youtube.com/video/<videoId>/edit), then the contents of `smoke/ab/<id>/ab.md` (three titles plus image links). Repeat it in every daily summary until the owner says it's done. Record the video IDs in `smoke/uploads.json`.
- No `YT_REFRESH_TOKEN_SMOKE` yet: do everything except the upload, and say so in the report.

## 6. REVIEW (Mondays)
1. **Competitors.** For every channel in `smoke/competitors.json`, use the NexLev free tools (`youtube_channel_videos` sorted newest, then popular) to collect their uploads from the last 14 days: title, views, length, age. Flag outliers (views well above that channel's usual) and why they likely worked: topic, title pattern, thumbnail idea, length. Also run `youtube_search` for our next two topics to see what already ranks. Save to `smoke/watch/<date>.json`.
1a. **Packaging scout.** `YT_CHANNEL=smoke python3 smoke/scout.py` (YouTube Data API, read-only; falls back to scrapetube). Read `smoke/watch/<date>/title-patterns.md` and LOOK at every `sheet-*.jpg`. In LEARNINGS.md, write what the outlier thumbnails share (layout, number of words, colours, characters, what the curiosity is) and what the outlier titles share. If a pattern repeats for two weeks, add it to STYLE.md 4/4b. Commit the watch folder.
1b. **Thumbnail tests.** Ask the owner for the YouTube Studio "Test & Compare" result of any finished test; the API doesn't expose it. Record the winner in LEARNINGS.md. The pairs themselves are made in WRITE 3b and RENDER.
2. **Our numbers.** `python3 smoke/stats.py` gives views, % viewed, average duration, subscribers gained, the retention curve and traffic sources per video. Look for:
   - the first big drop in each retention curve, and what was on screen and in the narration 10 seconds before it;
   - which chapters hold and which lose people;
   - which titles and thumbnails got clicked (views in the first 48 hours, browse versus suggested versus search).
3. **Learn.** Add a dated entry to `smoke/LEARNINGS.md`: 3–6 findings, each with its evidence, and one concrete change for each.
   - Apply the changes to `smoke/STYLE.md` (writing and editing rules), `smoke/plan.json` (topics and order: move up what works, add ideas that competitors proved), and the renderer when an editing change is needed.
   - Make small, testable changes, one or two per week, so we can tell what helped.
4. Commit everything.

## 7. Report
The daily FlagBomb email report includes a Smoke & Borders section: what was done today, the next episode and its status, the latest numbers, and this week's learning (from LEARNINGS.md).
