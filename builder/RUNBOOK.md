# Drivlume content runbook (for scheduled Claude sessions)

Owner: GM. Instagram @drivlume, cars only. Engine posts 5 reels/day from `posts/` (09:17, 12:17, 15:17, 18:17, 21:17 PKT) via `.github/workflows/loop.yml`. posted.log lists what is already posted.

## When to build
Count unposted folders = folders in posts/ not listed in posted.log. 5 are used per day.
- If unposted >= 25: do nothing, finish.
- Else build enough to reach ~35 unposted (usually 15-30 reels), in batches of ~10.

## Content rules (locked by GM)
- Cars only. GM rule (24 Nov): 4 out of every 5 reels = RECENT NEWS (last 2-4 weeks first, newest first; older 2025-2026 only if fresh news runs short). 1 in 5 = classic/legend. Spread them: never two classics in a row.
- Prefer FRESH car news from the last 2-4 weeks: records, launches, reveals, production ends, sales results, milestones.
- Facts: verify every number/date with WebSearch (official brand newsroom or 2 reputable outlets). Write dated facts ("In Nov 2026 ..."), never "still/current/fastest ever". Claims a company makes itself: say "X says".
- Never repeat a story in builder/used.txt. Same car is fine with a new story and a new photo.
- Photos: REAL photos only, never AI. Unsplash MCP search_photos (orientation=portrait, plus=none). Full-res portrait, car clearly visible, nice light. If the exact model has no photo, use a closely related car and say so in "Pictured:" (e.g. "Ferrari 812 Competizione (the car it replaced)"). Don't reuse a photo already in used.txt.
- Number plates: if a readable plate is visible, replace it with the DRIVLUME plate (`plates` field with the 4 corners at w=2160 scale; check a zoomed crop with a grid to get coordinates). Never blur.
- Style (locked): full-bleed photo, no blur, big lime Anton number behind the car (or `"front":true` when the car fills the frame / number gets hidden). Text 1 sentence, 12-20 words, 2-3 **highlights**.
- Caption: short hook line + emoji, 1-2 short fact paragraphs, a fun question; build.py appends Pictured/Source/Photo credit/hashtags. Tags sets: sup, jdm, it, de, lux, us, ev, hyp, cn. Mood = music search word (phonk, synthwave, epic, cinematic, chill).
- Write in English for the audience. No em dashes.
- "tag" APPROVED by GM (24 Nov): put a red pill tag on every recent-news reel, e.g. "JUST IN • NOV 2026" (news under ~2 weeks old), "BREAKING", "END OF AN ERA" (production ends), "NEW RECORD", "REVEALED". No tag on classics.

## How to build
1. `bash builder/setup.sh` (fresh session).
2. Write batch.json (see top of builder/build.py for the format).
3. `python3 builder/build.py batch.json --preview` then LOOK at builder/out/grid.jpg: number readable and not clipped, car cut clean, no plate visible, text fits. Fix (front/dim/overlap/other photo) and rebuild.
4. `python3 builder/build.py batch.json` -> creates posts/NNN_key and appends used.txt.
5. `git pull --rebase`, commit (posts + builder/used.txt), push to main.
6. Report to GM in Roman Urdu, short: how many added, queue lasts until which date (PKT), and send grid.jpg.
