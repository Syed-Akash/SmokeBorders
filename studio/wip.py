"""Keeps a long render alive across scheduled runs. Every run starts on a fresh computer, so finished 90-second pieces and the
voice clips (the expensive part with Chatterbox Turbo) are saved to a throwaway git branch `wip/<story-id>` and restored by the next run.

usage (from studio/):
  ./py wip.py restore <story-id>   before rendering: brings back saved pieces + voice clips (does nothing if there are none);
                                   a finished render (video, Shorts, meta.json) comes back ready to upload
  ./py wip.py save <story-id>      while rendering (every ~15 minutes) and when stopping: saves what is finished so far
  ./py wip.py clear <story-id>     after the video is uploaded: deletes the branch
The branch always holds a single commit (force-pushed), so it never grows the repository's history."""
import datetime, glob, io, os, shutil, subprocess, sys, tarfile, tempfile

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); CHUNK = 90 * 1024 * 1024   # GitHub refuses files over 100 MB

def git(*a, cwd=ROOT, check=True): return subprocess.run(['git', *a], cwd=cwd, check=check, capture_output=True, text=True)

def outdir(sid, make=False):
    ds = sorted(glob.glob(os.path.join(HERE, 'out', '*-doc-' + sid)))
    if ds: return ds[-1]
    if make:
        d = os.path.join(HERE, 'out', '%s-doc-%s' % (datetime.date.today().isoformat(), sid)); os.makedirs(d, exist_ok=True); return d

def pack(files, base, dest, name):
    """tar.gz the files (paths relative to base), split into chunks under 100 MB."""
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode='w:gz', compresslevel=1) as t:
        for f in files: t.add(os.path.join(base, f), arcname=f)
    data = buf.getvalue()
    for i in range(0, len(data), CHUNK): open(os.path.join(dest, '%s.tgz.%03d' % (name, i // CHUNK)), 'wb').write(data[i:i + CHUNK])
    return len(data)

def unpack(src, name, base):
    parts = sorted(glob.glob(os.path.join(src, name + '.tgz.*')))
    if not parts: return 0
    data = b''.join(open(p, 'rb').read() for p in parts)
    with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as t: t.extractall(base, filter='data')
    return len(data)

def save(sid):
    d = outdir(sid)
    segs = sorted(os.path.basename(p) for p in glob.glob(os.path.join(d, 'seg-*.mp4')) if '.part.' not in p) if d else []
    cache = os.path.join(HERE, 'tts', 'cache'); clips = sorted(os.listdir(cache)) if os.path.isdir(cache) else []
    # a finished render merges and deletes its pieces: then save the finished files (video, Shorts, meta, thumb) instead,
    # so the next run can upload without rendering again (14 Nov 2026: a save after the render emptied the branch)
    fin = sorted(f for f in os.listdir(d) if not f.startswith('seg-') and '.part.' not in f and os.path.isfile(os.path.join(d, f))) if d else []
    if not any(f.endswith('.mp4') for f in fin): fin = []
    if fin: clips = []   # a finished render needs no voice clips; with them the push went over GitHub's 2 GB limit (15 Nov 2026)
    if not segs and not clips and not fin: print('nothing to save'); return
    w = tempfile.mkdtemp(prefix='wip-'); br = 'wip/' + sid
    try:
        git('worktree', 'add', '--detach', w); git('checkout', '--orphan', br + '-new', cwd=w); git('rm', '-rfq', '.', cwd=w, check=False)
        for f in os.listdir(w):
            if f != '.git': (shutil.rmtree if os.path.isdir(os.path.join(w, f)) else os.remove)(os.path.join(w, f))
        a = pack(segs, d, w, 'pieces') if segs else 0; b = pack(clips, cache, w, 'voice') if clips else 0
        c = pack(fin, d, w, 'final') if fin else 0
        open(os.path.join(w, 'README.md'), 'w').write('Render in progress for %s: %d pieces, %d voice clips, %d finished files (%s). Restore with `./py wip.py restore %s`; deleted after upload.\n'
                                                     % (sid, len(segs), len(clips), len(fin), datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d %H:%M UTC'), sid))
        git('add', '-A', cwd=w); git('-c', 'user.name=render', '-c', 'user.email=render@localhost', 'commit', '-qm', 'Render in progress: %s (%d pieces)' % (sid, len(segs)), cwd=w)
        git('push', '-qf', 'origin', 'HEAD:refs/heads/' + br, cwd=w)
        print('saved %d pieces (%.0f MB), %d voice clips (%.0f MB) and %d finished files (%.0f MB) to %s' % (len(segs), a / 1e6, len(clips), b / 1e6, len(fin), c / 1e6, br))
    finally:
        git('worktree', 'remove', '--force', w, check=False); git('branch', '-D', br + '-new', check=False); shutil.rmtree(w, ignore_errors=True)

def restore(sid):
    br = 'wip/' + sid
    if git('fetch', '-q', 'origin', '+refs/heads/%s:refs/remotes/origin/%s' % (br, br), check=False).returncode: print('no saved render for', sid); return
    if not git('ls-tree', '--name-only', 'origin/' + br).stdout.count('.tgz.'): print('saved render for %s was cleared (already uploaded)' % sid); return
    w = tempfile.mkdtemp(prefix='wip-')
    try:
        git('worktree', 'add', '--detach', w, 'origin/' + br)
        cache = os.path.join(HERE, 'tts', 'cache'); os.makedirs(cache, exist_ok=True)
        b = unpack(w, 'voice', cache); a = unpack(w, 'pieces', outdir(sid, make=True)); c = unpack(w, 'final', outdir(sid))
        if c: print('restored the FINISHED render (%.0f MB) to %s: no render needed, go straight to UPLOAD' % (c / 1e6, outdir(sid)))
        else: print('restored %.0f MB of pieces and %.0f MB of voice clips; continue with: ./py make_doc.py %s --resume' % (a / 1e6, b / 1e6, sid))
    finally:
        git('worktree', 'remove', '--force', w, check=False); shutil.rmtree(w, ignore_errors=True)

def clear(sid):
    """Delete the branch; where the git proxy refuses deletes, overwrite it with one tiny commit so the big files are gone."""
    br = 'wip/' + sid
    if git('push', '-q', 'origin', '--delete', br, check=False).returncode == 0: print('deleted', br); return
    w = tempfile.mkdtemp(prefix='wip-')
    try:
        git('worktree', 'add', '--detach', w); git('checkout', '--orphan', br + '-new', cwd=w); git('rm', '-rfq', '.', cwd=w, check=False)
        for f in os.listdir(w):
            if f != '.git': (shutil.rmtree if os.path.isdir(os.path.join(w, f)) else os.remove)(os.path.join(w, f))
        open(os.path.join(w, 'README.md'), 'w').write('Render of %s finished and uploaded; nothing saved here.\n' % sid)
        git('add', '-A', cwd=w); git('-c', 'user.name=render', '-c', 'user.email=render@localhost', 'commit', '-qm', 'Render finished: ' + sid, cwd=w)
        git('push', '-qf', 'origin', 'HEAD:refs/heads/' + br, cwd=w); print('emptied', br)
    finally:
        git('worktree', 'remove', '--force', w, check=False); git('branch', '-D', br + '-new', check=False); shutil.rmtree(w, ignore_errors=True)

if __name__ == '__main__':
    {'save': save, 'restore': restore, 'clear': clear}[sys.argv[1]](sys.argv[2])
