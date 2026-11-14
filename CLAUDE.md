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
- Uploads are always scheduled, never published at once. `YT_CHANNEL=smoke` (the default here).
- Commit and push every change; end commit messages with the attribution lines the session gives you.

## What a video is (read smoke/STYLE.md for the full rules)
- **Long episode:** 30–45 minutes (aim 30–35), 10–14 chapters, built around a **hidden person** nobody has heard of.
  Present-tense story, minute by minute: date, place, a person, small details, the turn.
- **Film, not a map (owner, 14 Nov 2026):** every spoken beat has its own shot, a new shot every 5–15 s, never one over
  20 s; the map only where geography explains something (at most 30%). Shot types (studio/doc/scenes.js + scenes2.js):
  `photo` (real archival photo from Wikimedia Commons in 2.5-D, made with `smoke/photo.py`), `doc` (letters, telegrams,
  newspapers typed out), `card` (the minute-by-minute time card), `set` (an illustrated scene composed from parts: sea,
  hills, forest, coast, town, fort, camp, ships, soldiers, cannons, crowd, farm, animals, flags, fire, rooms, tables,
  people), plus the Korea-specific drawn shots. Every episode gets its OWN storyboard and photos; add new parts to
  scenes2.js when a story needs them. `"film": true` turns on the FILM CHECK in make_doc.py, which blocks the render if
  scenes < 70%, map > 30%, a shot > 20 s, or a chapter opens on the map. `sb-pig-war.json` is the worked example.
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
- **Subscribe/like animation** mid-video and a warm closing call to action; playlist links in descriptions.
- **Shorts:** two per episode, CUT from the finished episode (Short 1 = the cold open, Short 2 = a special moment), listed
  in the story's `"shorts"`; `smoke/cut_shorts.py <id> auto`.

## Cadence (owner, 11 Nov 2026)
One video a day at most, 16:00 UTC (9 pm Pakistan): the episode, then Short 1, then Short 2, then the next episode (an
episode every 3 days). `smoke/plan.json` holds the dates; `python3 smoke/sbplan.py --today` turns them into jobs (WRITE,
RENDER then UPLOAD in the same run, LATE, REDO, Monday REVIEW). Film episodes start rendering 4.5 days ahead because they
take two runs.

## How the daily run works (smoke/RUNBOOK.md is the source of truth)
- A scheduled task runs daily at 3:30 pm Pakistan. Its instructions are in `tools/prompts/smoke-daily.md`.
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

## Where things stand (14 Nov 2026)
- Old channel (UChRyy_-XdfEp04lyQA1WoJg, @SmokeBorders): American Revolution (y2nbDhzbAN8, published), Rome vs Carthage
  (dfkC_dDN5M8, published), Korea (bWtNC0Mk7hg, goes public 15 Nov 9 pm Pakistan; the owner let it go out, map-heavy).
  New thumbnails + two-formula titles for the first two are in smoke/ab/ for the owner's Test & Compare.
- **Redo queue** (`plan.json` "redo"): American Revolution, Rome vs Carthage and Korea get redone in the film style, with
  their Shorts, then HELD (no upload) until the owner decides new channel or old.
- **Pig War** (`sb-pig-war`, 18 Nov): fully storyboarded (184 shots, 16 archival photos, 97% film), passes the film
  check; renders next. Next: WW2 both sides (21 Nov), then every 3 days (see plan.json).
- Trial review on 5 Dec 2026.

## Map of the repo
- `smoke/`: STYLE.md (all writing/editing/thumbnail rules), RUNBOOK.md (the daily run), plan.json + sbplan.py (calendar
  and jobs), make_meta.py (titles/descriptions/tags/comments), make_thumb_sb.py + thumb2.html (thumbnails), portrait.py
  and photo.py (Commons images), cut_shorts.py, scout.py (competitor watch), brand/ (characters, fonts), ab/, LEARNINGS.md.
- `studio/`: make_doc.py (timeline, voice, render, film check, pacing), doc/ (doc.html renderer, scenes.js + scenes2.js,
  data/ era maps, stories/sb-*.json, photos/<story>/), turbo.py (voice), score.py (orchestral music; setup downloads the
  soundfont), upload.py, wip.py, setup.sh (run once per fresh machine).
