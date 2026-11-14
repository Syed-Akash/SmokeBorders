"""Orchestral documentary score, rendered offline with FluidSynth and the FluidR3 GM soundfont (MIT licence, Frank Wen).
Used by make_doc.py for Smoke & Borders episodes instead of the synthesizer pads.
Scoring rules (smoke/STYLE.md, from the research): the music sits under the narration as texture and pulse, not melody.
It changes with each chapter's mood, builds by adding layers rather than volume, and leaves room for the voice: no busy
lines in the 1-4 kHz speech band while the narrator talks.
moods: uneasy, tension, clock, war, grief, hope.  era: 'ancient' | 'medieval' | '1700s' | 'modern' adds a period colour
(1700s = fife and military side drum in war, harpsichord touches in uneasy; ancient = frame drum and low drones).
usage: python3 score.py <mood> <seconds> [era] -> out.wav (for listening tests)"""
import os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__)); SF = os.path.join(HERE, 'music', 'FluidR3_GM.sf2'); SR = 48000
GM = {'strings': 48, 'slow_strings': 49, 'cello': 42, 'contrabass': 43, 'pizz': 45, 'harp': 46, 'timpani': 47, 'choir': 52, 'horn': 60, 'brass': 61,
      'trombone': 57, 'flute': 73, 'piccolo': 72, 'clarinet': 71, 'oboe': 68, 'piano': 0, 'celesta': 8, 'harpsichord': 6, 'pad': 89, 'bassoon': 70}
# chord progressions per mood (MIDI roots + quality), all in D so chapters flow into each other
MIN = [0, 3, 7]; MAJ = [0, 4, 7]
PROG = {'uneasy': [(50, MIN), (46, MAJ), (43, MIN), (45, MAJ)], 'tension': [(50, MIN), (50, MIN), (46, MAJ), (45, MAJ)],
        'war': [(50, MIN), (48, MAJ), (46, MAJ), (45, MAJ)], 'grief': [(50, MIN), (43, MIN), (46, MAJ), (45, MAJ)],
        'hope': [(50, MAJ), (47, MIN), (43, MAJ), (45, MAJ)], 'clock': [(50, MIN), (46, MAJ), (48, MAJ), (45, MAJ)]}
TEMPO = {'uneasy': 66, 'tension': 84, 'war': 96, 'grief': 58, 'hope': 72, 'clock': 90}

def compose(mood, dur, era, rng):
    """A list of (time, channel, note, velocity, length) plus the programs for each channel."""
    mood = {'sad': 'grief'}.get(mood, mood) if mood not in TEMPO else mood   # story moods outside the score's set
    mood = mood if mood in TEMPO else 'uneasy'
    bpm = TEMPO[mood]; beat = 60 / bpm; bar = beat * 4; prog = PROG[mood]; ev = []; chans = {}
    def ch(name, n):
        chans[n] = GM[name]; return n
    pad, low, mel, perc, extra, harp = ch('slow_strings', 0), ch('cello', 1), ch('horn', 2), ch('timpani', 3), ch('flute', 4), ch('harp', 5)
    # the owner's favourite (6 Nov 2026) is "uneasy": every mood keeps that foundation (soft string bed, cello pedal,
    # sparse piano or harpsichord) and only adds one gentle layer of its own on top
    key = ch('harpsichord' if era == '1700s' else 'piano', 7)
    if mood == 'grief': chans[2] = GM['cello']
    if mood == 'uneasy': chans[2] = GM['harpsichord' if era == '1700s' else 'piano']
    if mood == 'clock': chans[1] = GM['pizz']
    if mood == 'hope': chans[2] = GM['horn']
    nb = int(dur / bar) + 2
    for b in range(nb):
        t0 = b * bar; root, q = prog[b % len(prog)]
        # sustained string bed: always there, soft, voiced low and wide (out of the speech band)
        for iv in q: ev.append((t0, pad, root - 12 + iv + (12 if iv else 0), 38, bar * 1.02))
        if mood != 'clock': ev.append((t0, low, root - 24, 46, bar))
        if mood != 'uneasy' and b % 2 == 0: ev.append((t0 + beat * rng.choice([1, 2, 2.5]), key, root + 12 + int(rng.choice(q)), 30, beat * 3))
        if mood == 'uneasy':
            if b % 2 == 0: ev.append((t0 + beat * rng.choice([1, 2, 2.5]), mel, root + 12 + int(rng.choice(q)), 34, beat * 3))
            if b % 4 == 3: ev.append((t0, perc, root - 12, 30, beat * 2))
        elif mood == 'tension':
            for k in range(8): ev.append((t0 + k * beat / 2, low, root - 24, 44 if k % 2 == 0 else 32, beat * .4))
            if b % 4 == 0: ev.append((t0, perc, root - 12, 52, beat))
            if b % 2 == 1: ev.append((t0 + beat * 2, harp, root + q[1] + 12, 36, beat))
        elif mood == 'war':
            for k in range(16): ev.append((t0 + k * beat / 4, 6, root - 12 + (q[1] if k % 8 == 6 else 0), 40 if k % 4 == 0 else 28, beat * .2))
            chans[6] = GM['strings']
            ev.append((t0, perc, root - 12, 60, beat)); ev.append((t0 + beat * 2.5, perc, root - 12, 44, beat))
            if b % 2 == 0: ev.append((t0, mel, root + q[2], 44, bar * 1.8))
            if era == '1700s':
                for k in range(8): ev.append((t0 + k * beat / 2, 9, 38, 34 if k % 2 else 46, beat * .2))   # military side drum
                if b % 4 == 2: [ev.append((t0 + i * beat / 2, extra, n, 40, beat * .45)) for i, n in enumerate([root + 24, root + 26, root + 28, root + 26])]
        elif mood == 'grief':
            if b % 2 == 0:
                line = [root + 12 + q[2], root + 12 + q[1], root + 12 + q[1] - 2, root + 12]
                for i, n in enumerate(line): ev.append((t0 + i * beat, mel, n, 38, beat * 1.05))
            if b % 2 == 1: ev.append((t0, harp, root + 24 + q[1], 30, beat * 2))
        elif mood == 'hope':
            for k in range(8): ev.append((t0 + k * beat / 2, harp, root + 12 + [0, 7, 12, q[1] + 12][k % 4], 26, beat))
            if b % 2 == 1: ev.append((t0, mel, root + q[2], 44, bar * 1.6))
        elif mood == 'clock':
            for k in range(8): ev.append((t0 + k * beat / 2, low, root - 12 + (q[2] if k % 2 else 0), 40, beat * .3))
            if b % 2 == 0: ev.append((t0 + beat * 3, harp, root + 24 + q[1], 30, beat))
    return [e for e in ev if e[0] < dur + 2], chans

def render(mood, dur, era='modern', seed=0):
    import fluidsynth
    rng = np.random.default_rng(seed); ev, chans = compose(mood, dur, era, rng)
    fs = fluidsynth.Synth(samplerate=float(SR), gain=0.5); sfid = fs.sfload(SF)
    for c, p in chans.items(): fs.program_select(c, sfid, 0, p)
    fs.program_select(9, sfid, 128, 48 if era == '1700s' else 0)   # orchestral drum kit
    try: fs.set_reverb(0.85, 0.35, 0.95, 0.75)
    except Exception: pass
    offs = [(t + L, 0, c, n) for t, c, n, v, L in ev]; ons = [(t, 1, c, n, v) for t, c, n, v, L in ev]
    q = sorted([(e[0], e[1], e) for e in ons + offs], key=lambda x: (x[0], x[1])); out = []; now = 0.0
    for t, kind, e in q:
        if t > now:
            n = int((t - now) * SR); out.append(np.asarray(fs.get_samples(n), dtype=np.int16).reshape(-1, 2)); now += n / SR
        if kind == 1: fs.noteon(e[2], int(e[3]), int(e[4]))
        else: fs.noteoff(e[2], int(e[3]))
    n = int(max(0, dur + 2.5 - now) * SR)
    if n: out.append(np.asarray(fs.get_samples(n), dtype=np.int16).reshape(-1, 2))
    fs.delete(); a = np.concatenate(out).astype(np.float32) / 32768
    a = a[:int(dur * SR)]; return a.mean(axis=1)   # mono, like the old music track

if __name__ == '__main__':
    import soundfile as sf
    a = render(sys.argv[1], float(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else 'modern'); sf.write('out.wav', a / (np.abs(a).max() or 1) * .8, SR); print('out.wav', len(a) / SR)
