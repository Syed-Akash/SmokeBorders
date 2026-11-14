"""Chatterbox Turbo narration (Resemble AI, MIT licence), chosen by the owner on 7 Nov 2026 (sample D) for both channels' long videos.
It speaks with expression (rising and falling tone, natural pauses on "...", and cues such as [chuckle] written into the script),
in the timbre of a reference clip. The reference is our own Kokoro voice (George for Smoke & Borders, Fenrir for FlagBomb),
so each channel keeps the voice the owner already picked.
Needs huggingface.co reachable for the first download (environment network access). If anything fails, make_doc.py falls back
to Kokoro and writes why into tts/engine.txt, so a run never stalls.
About 3x slower than real time on a 2-CPU machine (a 20-minute episode: about an hour); clips are cached in tts/cache."""
import os, re, subprocess, sys, zlib
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = re.compile(r'^\[(chuckle|laugh|cough|sigh|gasp|groan|sniff|clear throat)\]$', re.I)   # tested: [chuckle]; test others before relying on them
REF_TEXT = ("Let's start in London, because this story starts with a bill. Britain had just won the Seven Years' War, "
            "and somebody finally opened the accounts. Nobody liked what they found.")
_model = None

def ensure():
    try:
        import chatterbox  # noqa
    except ImportError:
        pip = [sys.executable, '-m', 'pip', 'install', '-q', '--break-system-packages']
        subprocess.run(pip + ['torch', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cpu'], check=False)
        subprocess.run(pip + ['chatterbox-tts'], check=True)

def model():
    global _model
    if _model is None:
        ensure()
        import torch
        torch.set_num_threads(os.cpu_count() or 2)
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        _model = ChatterboxTurboTTS.from_pretrained(device='cpu')
    return _model

def ref(k, name, style, lang, SR):
    """A 10-second reference clip of our Kokoro voice, made once."""
    import soundfile as sf
    p = os.path.join(HERE, 'tts', 'ref-%s.wav' % name)
    if not os.path.exists(p):
        a, sr = k.create(REF_TEXT, voice=style, speed=1.0, lang=lang); sf.write(p, a, sr)
    return p

def speak(text, refpath, SR):
    import torch
    m = model(); torch.manual_seed(zlib.crc32(text.encode()))   # the same line always sounds the same (resumed runs match)
    w = m.generate(text, audio_prompt_path=refpath, norm_loudness=False).squeeze(0).cpu().numpy().astype(np.float32)
    if m.sr != SR:
        n = int(len(w) * SR / m.sr); w = np.interp(np.linspace(0, len(w) - 1, n), np.arange(len(w)), w).astype(np.float32)
    # trim the model's leading/trailing silence so pauses stay under our control
    nz = np.where(np.abs(w) > .01)[0]
    if len(nz): w = w[max(0, nz[0] - int(.03 * SR)): nz[-1] + int(.08 * SR)]
    return w
