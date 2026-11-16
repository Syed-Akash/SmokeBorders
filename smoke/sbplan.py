"""What the Smoke & Borders run should do today (see smoke/RUNBOOK.md).
usage: python3 smoke/sbplan.py --today          prints the jobs, most urgent first
       python3 smoke/sbplan.py set <id> <status>  after finishing a step (idea|scripted|rendered|uploaded)
       python3 smoke/sbplan.py short <id> <n>     after a Short is uploaded (scheduled)
Cadence (owner, 11 Nov 2026): one video a day at most, all at 16:00 UTC: the episode, then its Short 1 (the story's opening)
and Short 2 (a special moment), both cut from the finished episode, then the next episode, so an episode every 3 days.
To save effort, a run gets at most ONE writing job and ONE render; both Shorts are cut and uploaded with the episode."""
import datetime, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); F = os.path.join(HERE, 'plan.json')

def load(): return json.load(open(F))
def save(p): json.dump(p, open(F, 'w'), indent=1, ensure_ascii=False)

def today_jobs(now=None):
    now = now or datetime.datetime.now(datetime.timezone.utc); p = load(); jobs = []; wrote = rendered = False
    for e in p['episodes']:
        if e['status'] == 'uploaded':
            for n, sh in enumerate(e.get('shorts', []), 1):
                if sh.get('done'): continue
                sd = (datetime.datetime.fromisoformat(sh['publish'].replace('Z', '+00:00')) - now).total_seconds() / 86400
                if sd < 1.5: jobs.append((sd, 'SHORT %s #%d (publishes %s) was not uploaded with its episode: if the episode file is still in studio/out, cut it (cut_shorts.py %s auto) and upload it scheduled; otherwise mark it done with a note (sbplan.py short %s %d). Never write a new Short story for it.' % (e['id'], n, sh['publish'], e['id'], e['id'], n)))
            continue
        days = (datetime.datetime.fromisoformat(e['publish'].replace('Z', '+00:00')) - now).total_seconds() / 86400
        if days < 0: jobs.append((0, 'LATE: %s was due %s and is still "%s". Finish it and upload it for the next free 16:00 UTC (move the later episodes down 3 days in plan.json, Shorts with them).' % (e['id'], e['publish'], e['status']))); continue
        if e['status'] == 'idea' and days <= 7 and not wrote:
            wrote = True; jobs.append((days, 'WRITE %s ("%s"), publishes %s. Research, then write doc/stories/%s.json by smoke/STYLE.md, with its two "shorts" (RUNBOOK 1.3c).' % (e['id'], e['title'], e['publish'], e['id'])))
        elif e['status'] == 'scripted' and days <= 4.5 and not rendered:   # film episodes take two runs to render, so start a day earlier
            rendered = True; jobs.append((days, 'RENDER %s: ./py wip.py restore; ./py make_doc.py <id> --pacing: it must be 25-45 minutes (25 is fine when the story is fully told; never pad), aiming for 30-35 when the story has that much, with every gap fixed (STYLE.md 3); check the storyboard sheets (studio/storysheet.py, STYLE.md 2e: picture matches the words, no repeats, everyone cast) and fix them; then render with --resume; save with wip.py every ~15 min and do not end the run while it renders (RUNBOOK 2). Then go straight on to UPLOAD in the same run.' % e['id']))
        elif e['status'] == 'rendered' and days <= 5: jobs.append((days, 'UPLOAD %s: first `cd studio && ./py wip.py restore <id>` (a finished render comes back ready: video, Shorts, meta.json, thumb; no re-render), then thumbnail, meta, upload the episode, then cut both Shorts (cut_shorts.py %s auto) and upload them scheduled for %s; publish %s (RUNBOOK 3).' % (e['id'], e['id'], ' and '.join(s['publish'] for s in e.get('shorts', [])), e['publish'])))
        if e.get('replaces') and jobs and jobs[-1][1].startswith(('RENDER', 'UPLOAD')) and e['id'] in jobs[-1][1]: jobs[-1] = (jobs[-1][0], jobs[-1][1] + ' This REPLACES the old scheduled upload %s: its old saved pieces were already cleared, so wip restore only brings back this re-render\'s own pieces. Only after the new upload succeeds run `YT_CHANNEL=smoke python3 upload.py --replace %s <new id>`, then drop "replaces" from plan.json.' % (e['replaces'], e['replaces']))
        if e.get('angle') and jobs and e['id'] in jobs[-1][1] and jobs[-1][1].startswith(('WRITE', 'RENDER')): jobs[-1] = (jobs[-1][0], jobs[-1][1] + ' ANGLE: ' + e['angle'])
    # one-time channel fixes (16 Nov 2026): description, clean keywords, category Education, captions on the Pig War
    try: cs = json.load(open(os.path.join(HERE, 'channel_setup.json')))
    except Exception: cs = {'done': True}
    if not cs.get('done'): jobs.append((5, 'SETUP the channel once: cd studio && ./py wip.py restore sb-pig-war, then YT_CHANNEL=smoke ./py ../smoke/channel_setup.py --captions dr-cHJ-YyDk <the sb-pig-war .srt from the restored files>; commit smoke/channel_setup.json (it records done)'))
    # the redo queue (owner, 14 Nov 2026): one redo job per run, only when nothing urgent is rendering
    if not rendered and not any(j.startswith(('LATE', 'UPLOAD')) for _, j in jobs):
        r = next((x for x in p.get('redo', []) if x['status'] != 'held'), None)
        if r: jobs.append((50, 'REDO %s (%s): %s' % (r['id'], r['status'], {
            'storyboard': 'its film storyboard is done (tools/storyboard/<id>.py); add the acted dialogue, comparisons and callbacks of STYLE.md 2c (a cast entry and voice per speaker), keep it 25-45 minutes, never padded; storyboard anything new by STYLE.md 2b (every spoken beat its own shot; real archival photos with smoke/photo.py listed in "photos"; "film": true; the hook formulas; the three final thumbnails); pass the FILM CHECK (--pacing), then set its redo status to render',
            'render': 'render it (wip.py restore/save, --resume), cut both Shorts (cut_shorts.py <id> auto), make the thumbnails (make_thumb_sb.py --ab), then set its redo status to held. DO NOT UPLOAD: the owner decides where it goes'}[r['status']])))
    if now.weekday() == 0: jobs.append((99, 'REVIEW: weekly competitor watch + our channel numbers -> smoke/LEARNINGS.md, and update STYLE.md / plan.json if the numbers say so.'))
    return [j for _, j in sorted(jobs)]

if __name__ == '__main__':
    if sys.argv[1:2] == ['short']:
        p = load(); e = next(e for e in p['episodes'] if e['id'] == sys.argv[2]); e['shorts'][int(sys.argv[3]) - 1]['done'] = True; save(p); print(sys.argv[2], 'short', sys.argv[3], 'done')
    elif sys.argv[1:2] == ['set']:
        p = load(); [e.update(status=sys.argv[3]) for e in p['episodes'] if e['id'] == sys.argv[2]]; save(p); print(sys.argv[2], '->', sys.argv[3])
    else:
        for j in today_jobs() or ['Nothing due today. Post queued comments, write the summary in 3 lines and stop.']: print('-', j)
