# Smoke & Borders

Second channel: animated history documentaries told from both sides of a border. The strategy and the first 10 episodes are in the research doc
(https://claude.ai/artifact/21Dtv8pgh6QkJDkgRM82NX, section "The Smoke & Borders playbook").

## Branding (chosen 6 Nov 2026: "Then and Now")
- `brand/out/avatar.png` (800x800) and `brand/out/banner.png` (2560x1440, everything important inside the 1546x423 safe area).
- Source: `brand/concepts2.html?c=8`; re-render with `python3 smoke/brand/concepts.py 8`, then copy `concepts/8-avatar.png` and `8-banner.png` into `out/`.
- The idea: the world map split by a burning border. One side is the AD 100 world on parchment, the other is today's world in colour (historical-basemaps data in studio/doc/data).
- Palette: parchment `#e6d3a8` / `#8b7350`, modern sea `#13284a`, ember `#ff6a1f`, bone `#f3e7cf`, gold `#e0b45a`, badge `#16110d`.
- Type: Anton (titles, logo), Oswald 700 (taglines and labels). Fonts in `brand/fonts` (SIL OFL).
- Thumbnails use the same split: the "then" side in parchment, the "now" side in colour, a burning seam, one character on each side, 0-3 words.
- The other nine concepts are kept in `brand/concepts/` for reference.

## Channel description (Studio > Customisation > Basic info)
The first ~150 characters show in search, so they carry the search terms.

Animated history documentaries told from both sides of the border. Ancient empires, world wars and the story of every country, on maps that move.

Every border on the map was drawn by someone, fought over by someone, and lived with by millions. Smoke & Borders tells those stories from both sides: from Rome and Carthage to the Partition of India, from the Mongols to the Cold War.

In every episode:
• Animated maps that show exactly how the borders moved
• Both sides of the story, so you decide who was right
• Real sources, pinned in the comments
• Dark humour where history earns it, and silence where it doesn't

A new full story every Saturday, and short stories during the week.

Every border has two sides. We tell both.

## Channel keywords (Studio > Settings > Channel > Basic info, 500-character limit)
history "animated history" "history documentary" "world history" "history explained" "ancient history" "history maps" "animated maps" "map animation" borders empires "rise and fall" "world war 1" "world war 2" "cold war" "roman empire" "partition of india" "mongol empire" "ottoman empire" "history of every country" geopolitics

## Upload defaults (Studio > Settings > Upload defaults)
Basic info:
- Title: leave empty (every title follows the title formulas in the playbook).
- Description template:

[One line: the most shocking fact in the story]

[Two or three sentences: what happened, where, when, and the two sides. Use the words people search for.]

⏱️ Chapters
00:00 [Cold open]

📚 Sources: the full list is pinned in the comments.
🗺️ Every episode in order: [Every Episode playlist link]

Smoke & Borders: every border has two sides. We tell both.
#history #animatedhistory #documentary

- Tags: history, animated history, history documentary, world history, history explained, history maps, animated map, borders, empires, war history, smoke and borders
- Visibility: Private (the uploader schedules the publish time).

Advanced settings:
- Licence: Standard YouTube Licence. Allow embedding: on. Publish to subscriptions feed and notify subscribers: on.
- Category: Entertainment (same choice as FlagBomb).
- Video language and title/description language: English. Caption certification: "This content has never aired on television in the US".
- Comments: on, "Hold potentially inappropriate comments for review" (partitions and wars draw heated comments); sort by Top.
- Show how many viewers like this video: on.
- Shorts remixing: allow video and audio remixing (free reach).
- Automatic chapters: on. Featured places: off. Automatic concepts: on.
- Every upload: Made for kids "No". Paid promotion "No". Altered or synthetic content: answer what YouTube asks; clearly animated maps and cartoon characters count as clearly unrealistic.

## Uploads
`YT_CHANNEL=smoke python3 studio/upload.py video.mp4 meta.json` uploads with `YT_REFRESH_TOKEN_SMOKE` and refuses to upload unless the token's channel is titled exactly "Smoke & Borders". `YT_CHANNEL=smoke python3 studio/upload.py --whoami` shows which channel a token belongs to. Never print the token.

Rules that carry over from FlagBomb: Entertainment category (24), never mention AI or automation in any text, translated titles and descriptions, English captions, sources in the pinned comment.
