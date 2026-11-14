"""Cut vertical Shorts (1080x1920) out of a finished Smoke & Borders episode.
usage: python3 smoke/cut_shorts.py <story-id> auto     cut every Short listed in the episode's summary.json "shortCuts"
       python3 smoke/cut_shorts.py <story-id> <n> <start-seconds> <length-seconds> "<HEADLINE LINE 1|LINE 2>"
Layout: the episode frame (with its burned-in captions) in the middle, a blurred copy filling the background,
a two-line Anton headline on top, and "Full story on Smoke & Borders" at the bottom. Keep Shorts 40-58 s and start
on a hook line (the cold open, a shocking number, a reveal)."""
import glob, os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); STUDIO = os.path.join(HERE, '..', 'studio')

def anton_ttf():
    ttf = os.path.join(HERE, 'brand', 'fonts', 'anton.ttf')
    if not os.path.exists(ttf):
        from fontTools.ttLib import TTFont
        f = TTFont(os.path.join(HERE, 'brand', 'fonts', 'anton.woff2')); f.flavor = None; f.save(ttf)
    return ttf

def esc(s): return s.replace('\\', '\\\\').replace(':', '\\:').replace("'", "’").replace('%', '\\%')

def main():
    if sys.argv[2:3] == ['auto']:   # owner, 11 Nov 2026: both Shorts come from the episode (story start + a special moment)
        import json
        outdir = sorted(glob.glob(os.path.join(STUDIO, 'out', '*-doc-' + sys.argv[1])))[-1]
        for c in json.load(open(os.path.join(outdir, 'summary.json'))).get('shortCuts', []): cut(sys.argv[1], str(c['n']), c['start'], c['length'], c['head'])
        return
    cut(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]), sys.argv[5])

def cut(sid, n, start, length, head):
    outdir = sorted(glob.glob(os.path.join(STUDIO, 'out', '*-doc-' + sid)))[-1]; src = os.path.join(outdir, sid + '.mp4'); out = os.path.join(outdir, 'short-%s.mp4' % n)
    font = anton_ttf(); l1, l2 = (head.split('|') + [''])[:2]
    vf = ('[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:3,eq=brightness=-0.18[bg];'
          '[b]scale=1600:-2,crop=1080:900[fg];[bg][fg]overlay=0:(H-h)/2+40,'
          "drawtext=fontfile=%s:text='%s':fontsize=104:fontcolor=0xF3E7CF:borderw=8:bordercolor=0x100B07:x=(w-tw)/2:y=250,"
          "drawtext=fontfile=%s:text='%s':fontsize=104:fontcolor=0xFF6A1F:borderw=8:bordercolor=0x100B07:x=(w-tw)/2:y=370,"
          "drawtext=fontfile=%s:text='FULL STORY ON SMOKE & BORDERS':fontsize=46:fontcolor=0xE0B45A:x=(w-tw)/2:y=h-330[v]") % (font, esc(l1), font, esc(l2), font)
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-ss', str(start), '-t', str(length), '-i', src, '-filter_complex', vf, '-map', '[v]', '-map', '0:a',
                    '-c:v', 'libx264', '-crf', '20', '-preset', 'medium', '-c:a', 'aac', '-b:a', '160k', '-movflags', '+faststart', out], check=True)
    print(out)

if __name__ == '__main__':
    main()
