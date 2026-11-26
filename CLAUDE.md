# Smoke & Borders: everything a new session needs

This repository is the YouTube channel **Smoke & Borders** only: animated history documentaries told from both sides of a
border, built around a hidden person, playing like a film. It was split out of the FlagBomb repo on 14 Nov 2026 because
the owner found the two channels confusing in one place. FlagBomb (the countryball game channel) lives in
`Syed-Akash/Flagbomb`; nothing here is about FlagBomb.

The owner writes in quick, informal English and lives in Pakistan (Asia/Karachi). Give times in Pakistan time, answer in
plain words, keep it short, and send previews (frames, contact sheets, short clips) before big changes.

## Rules that never change
- Free tools only; never buy anything. Never print or commit a key or token; tell the owner never to paste secrets in chat.
- Never mention AI, bots or automation in any title, description, tag, comment, on-screen text or narration.
- Real facts only: every number comes from a page actually opened, listed in the story's `sources`. Only real wording in
  quotation marks; paraphrases are labelled. Never an invented headline under a real newspaper's name.
- Both sides told fairly. Dark humour at bad decisions, never at victims. No sides in wars happening now.
- Thumbnails: no blood, wounds or bodies (YouTube removes or age-restricts them); graves, smoke and fire instead.
  Text never covers a face.
- **The owner uploads by hand (17 Nov 2026):** API uploads got 0 impressions on the new channel, a hand upload got views at once.
  Runs make an upload kit (smoke/make_kit.py) and send it; never call upload.py for videos until the owner says so.
- Uploads are always scheduled, never published at once. `YT_CHANNEL=smoke` (the default here).
- Commit and push every change; end commit messages with the attribution lines the session gives you.

## What a video is (read smoke/STYLE.md for the full rules)
- **Long episode:** 25–45 minutes (aim 30–35 when the story has that much; owner, 15 Nov 2026: 25 is the minimum when the
  topic is fully covered, never pad to reach a length), 10–14 chapters, built around a **hidden person** nobody has heard of.
  Present-tense story, minute by minute: date, place, a person, small details, the turn.
- **Film, not a map (owner, 14 Nov 2026):** every spoken beat has its own shot, a new shot every 5–15 s, never one over
  20 s; the map only where geography explains something (at most 30%). Shot types (studio/doc/scenes.js + scenes2.js):
  `photo` (real archival photo from Wikimedia Commons in 2.5-D, made with `smoke/photo.py`), `doc` (letters, telegrams,
  newspapers typed out), `card` (the minute-by-minute time card), `set` (an illustrated scene composed from parts: sea,
  hills, forest, coast, town, fort, camp, ships, soldiers, cannons, crowd, farm, animals, flags, fire, rooms, tables,
  people), plus the Korea-specific drawn shots. Every episode gets its OWN storyboard and photos; add new parts to
  scenes2.js when a story needs them. `"film": true` turns on the FILM CHECK in make_doc.py, which blocks the render if
  scenes < 70%, map > 30%, a shot > 20 s, or a chapter opens on the map. `sb-pig-war.json` is the worked example.
- **Acted, fast, concrete (owner, 15 Nov 2026, smoke/STYLE.md 2c):** characters act out short exchanges about once a minute
  (`talk` beats + the story's `cast`; dramatized from the record, jokes only for unnamed roles, `talkNote` in the description);
  every big number made concrete; callbacks; hooks on famous names and the news.
- **The approved editing style (owner, 15 Nov 2026, STYLE.md 2d) for every new-channel video:** acting full-body characters
  (`actors` parts: walk, point, aim, fire, hold, toast...), close-up coverage of acted scenes, automatic whip/push/zoom/ink
  transitions, motion graphics (counting numbers, sliding name tags, highlighted document lines, circles drawn on photos).
  Never zoom into a still to fake a cut (rejected). Aim for a real cut every 4-6 s and 30+ acted scenes an episode.
- **In sync, never repeated (owner, 15 Nov 2026, STYLE.md 2e):** each shot shows what the words say, cut on the word; every
  person cast with a fitting `preset` (no wigs after 1800); no picture more than twice (the FILM CHECK fails on repeats and uncast
  people); every spoken number/money/year/name pops up automatically (`kinetic`); review `studio/storysheet.py <id>` sheets before rendering. Length 25-45 minutes and thumbnails stay the three templates (owner kept those).
- **Titles (owner, 12 Nov 2026): only two formulas.** A = "How X Happened — Minute by Minute"; B = "The N Days That Made
  X" (Days → Hours/Years when that is the real span; N stated in the script and sourced). Never Ziro's "in N Minutes".
- **Thumbnails (owner, 12 Nov 2026): only three templates**, always in the dark style over a burning relief map with
  real photos (`smoke/thumb2.html`, `smoke/make_thumb_sb.py`): A = spotlight ("13 MINUTES / TOO LATE"), B = circled
  ("HE ALMOST DID IT"), C = dossier ("UNTOLD STORY" polaroid). Red topic bar with place and date, a 1–3 word hook with one
  yellow word, red glowing eyes only on a villain the story treats as one, grave crosses only when people died
  (`"graves": 0` otherwise). Portraits come from Commons via `smoke/portrait.py`. Test & Compare = "Title and thumbnail":
  A + title A, B + title B, C + title A. `smoke/ab/<id>/` holds the images and the instructions.
- **Voice:** Chatterbox Turbo (MIT), timbre cloned from the Kokoro voice bm_george (`studio/turbo.py`); Kokoro is the
  fallback and measures timings. About 3x slower than real time on 2 CPUs.
- **Sound (owner, 14 Nov 2026: "not enough sound effects"):** every film shot gets sound automatically (make_doc.py
  `film_sound`): a soft whoosh on each cut, a quiet bed under the shot (waves for sea/ships, fire, wind outdoors, rain,
  crowd for towns, the film projector under archival photos, a ticking clock under time cards), paper on documents; a
  riser and sub drop on chapter cards; impacts on booms. Real recordings live in `studio/sfx/<kind>/` (51 picked from the
  owner's pack; `sfx/sources.json` says where each came from), with the old generated sounds as fallback. Beds are
  ducked under the voice. Stories can also call `"sfx": "braam" | "tension" | "riser" | "bells" | ...` on a beat.
  Never use the pack's meme/anime/game clips (copyright claims) or its BLASTWAVEFX files (a paid library).
- **Subscribe/like animation** mid-video and a warm closing call to action; playlist links in descriptions.
- **Shorts (owner, 18 Nov 2026): two "Do you know" Shorts per episode**, each its own story (`<id>-short1/2.json`) built on one
  surprising sourced fact, opening with "Do you know...", under 60 s (RUNBOOK 3b). Cut-from-episode Shorts got 3-4 views; the
  first "Do you know" Short got 800 in a day. The owner sets each Short's Related video to its episode.

## Cadence (owner, 11 Nov 2026)
One video a day at most, 16:00 UTC (9 pm Pakistan): the episode, then Short 1, then Short 2, then the next episode (an
episode every 3 days). `smoke/plan.json` holds the dates; `python3 smoke/sbplan.py --today` turns them into jobs (WRITE,
RENDER then UPLOAD in the same run, LATE, REDO, Monday REVIEW). Film episodes start rendering 4.5 days ahead because they
take two runs.

## How the daily run works (smoke/RUNBOOK.md is the source of truth)
- A scheduled task ("Smoke Borders Daily") runs daily at 8:30 am Pakistan. Its instructions are in `tools/prompts/smoke-daily.md`.
- Step 0: `tools/sync_runs.sh` merges recent run branches (only branches that moved in the last 36 h; never "theirs").
  Twice (12 and 13 Nov) a stale branch rolled the plan back; this is why.
- Renders run in the background in 90-second pieces; `studio/wip.py save/restore/clear <id>` keeps pieces and voice clips
  on a `wip/<id>` branch so the next run continues with `--resume`. Never end a run mid-render without saving.
- Wait with ONE Monitor/until loop that checks every 10 minutes (the runs were burning too many tokens; see "Save effort").
- `.github/workflows/runs.yml` merges pushed run branches into main and posts queued first comments hourly
  (`studio/pending_youtube_smoke.json`; comments only work once a video is public).
- Wikimedia rate-limits shared addresses (HTTP 429): portrait.py/photo.py back off and use standard thumbnail sizes;
  thumb.wikimedia.org is blocked, upload.wikimedia.org works.

## Secrets and accounts
- Repository secrets needed: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN_SMOKE` (signed in as the NEW channel).
- The uploader refuses any channel whose title is not "Smoke & Borders" AND whose handle is not **@SmokeAndBorders**
  (both channels share the title, so the handle is what stops an upload landing on the old one). `YT_EXPECT_HANDLE`
  overrides it. Check with `python3 studio/upload.py --whoami`.
- OAuth scopes: youtube.upload, youtube.force-ssl, yt-analytics.readonly. Tokens expire every 7 days while the Google
  OAuth app is in Testing mode: the owner should publish the app (OAuth consent screen → Publish app).
- **New channel (14 Nov 2026): "Smoke & Borders", @SmokeAndBorders**, on its own email (before, both channels shared one
  Google account). All new episodes (Pig War onwards) go there. Still needed from the owner: a refresh token signed in
  with that account (the new email must be a test user of the OAuth app, or the app published), and the decision where
  the redone episodes go. Until the token is in, runs do everything except upload.

## Where things stand (17 Nov 2026)
- **The old channel (@SmokeBorders) is deleted** (owner, 17 Nov). Everything goes on @SmokeAndBorders.
- Pig War (dr-cHJ-YyDk) is out (15 Nov) with both Shorts; the first days had almost no views (new channel). Channel description,
  keywords and Education category fixed on 16 Nov (smoke/channel_setup.py); captions go up with every upload. The owner adds
  @PlayFlagbomb as a collaborator on videos (Studio invite link, opened while signed in as FlagBomb).
- **The redos are now regular episodes** (owner, 17 Nov): American Revolution 18 Nov (rendered, on wip/), WW2 21 Nov, Rome
  24 Nov (storyboard done, renders ~20 Nov), Western Front 27 Nov, Korea 30 Nov (still needs its dialogue pass via the REDO job),
  then Berlin Wall, Cuban Missile Crisis, Shortest War, Mongols every 3 days. plan.json has the dates.
- Manual uploads so far: Pig War flag Short (VBOnWm5X9Yo, 800+ views), American Revolution (s8FoqUIAzZU, 18 Nov).
  The Franklin's-son "Do you know" Short was sent to the owner on 18 Nov.
- **The Real Vice City** (`sb-vice-city`, owner 19 Nov 2026, GTA 6 release day): 22.7 min, Shorts = stories sb-vice-city-short1/2,
  kit sent to the owner on 20 Nov for 24/25/26 Nov; Rome and later episodes moved 3 days later. Owner: 20-25 min is fine,
  exceed only if necessary. Full source lists that exceed YouTube's 10,000-character comment limit go to smoke/sources/<id>.md.
- **24 Nov 2026 run:** Rome vs Carthage expanded (Archimedes, Sophonisba, the siege, Hasdrubal's wife in full) and rendered (34.6 min);
  kit sent for 27/28/29 Nov with new "Do you know" Shorts (sb-rome-carthage-short1/2). Western Front drafted (3,630 words, ~25 min,
  hidden person Capt. Robert Miles; tools/storyboard/western_front.py builds it and its two Shorts); still needs its photos (Wikimedia 429
  all day), then `scripted`. New WW1 presets (tommy, german_1914, german_ww1, poilu, doughboy, nurse_ww1) and trench/wire/craters parts.
  Only Wikimedia hosts are reachable from the run sandbox; research comes from Wikipedia pages.
- **25 Nov 2026 run:** Western Front got its 14 photos, passes the FILM CHECK (trench part now takes a `seed` for set dressing so
  trench shots don't repeat), rendered at 26.9 min (Turbo) with both "Do you know" Shorts; thumbnails use Trébuchon (no photo of Miles
  exists on Commons) and Hitler. Kit sent for 30 Nov / 1 / 2 Dec. Korea REDO render not started (one render per run fits).
- **26 Nov 2026 run:** Korea (sb-korea-38th) got its last 11 photos and rendered at 34.1 min (Turbo); two "Do you know" Shorts written
  (tools/storyboard/korea_shorts.py: Bonesteel came back in 1966 to guard his own line; Japan and Russia discussed the same parallel
  40 years earlier). Kit sent for 3/4/5 Dec; Korea is off the redo list. No redos left. Next: Berlin Wall (6 Dec), still an idea.
  Vice City and WW2 kits still await the owner's video IDs.
- Five animation looks exist (`"look"`: cinematic default, paper, ink, flat, film); the owner hasn't picked one yet.
- Trial review on 5 Dec 2026.

## Map of the repo
- `smoke/`: STYLE.md (all writing/editing/thumbnail rules), RUNBOOK.md (the daily run), plan.json + sbplan.py (calendar
  and jobs), make_meta.py (titles/descriptions/tags/comments), make_thumb_sb.py + thumb2.html (thumbnails), portrait.py
  and photo.py (Commons images), cut_shorts.py, scout.py (competitor watch), brand/ (characters, fonts), ab/, LEARNINGS.md.
- `studio/`: make_doc.py (timeline, voice, render, film check, pacing), doc/ (doc.html renderer, scenes.js + scenes2.js,
  data/ era maps, stories/sb-*.json, photos/<story>/), turbo.py (voice), score.py (orchestral music; setup downloads the
  soundfont), upload.py, wip.py, setup.sh (run once per fresh machine).
