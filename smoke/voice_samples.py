"""Narrator test (7 Nov 2026): the same passage read by our current voice (Kokoro bm_george) and by Chatterbox (Resemble AI, MIT
licence), which can carry emotion. Chatterbox copies the timbre of a reference clip, so the reference is George himself.
Needs huggingface.co reachable (environment network access). Install: see install() below (CPU torch, then chatterbox-tts).
usage: python3 smoke/voice_samples.py   ->  smoke/voice/samples/*.mp3 and report.txt (speed on this machine)"""
import os, subprocess, sys, time, traceback
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE); OUT = os.path.join(HERE, 'voice', 'samples'); os.makedirs(OUT, exist_ok=True)
STUDIO = os.path.join(ROOT, 'studio')

# a cold open, a death, a dry joke: the three moods an episode needs
PLAIN = ("In 1763, Britain won the biggest war the world had ever seen. It was the most powerful empire on Earth. "
         "Twenty years later, it had lost almost all of America. "
         "On the hill above Boston, more than a thousand British soldiers fell in a single afternoon. "
         "The King's answer to all of this was a new tax on tea. It did not go well.")
TAGGED = ("In 1763, Britain won the biggest war the world had ever seen. It was the most powerful empire on Earth. "
          "Twenty years later... it had lost almost all of America. "
          "On the hill above Boston, more than a thousand British soldiers fell in a single afternoon. "
          "The King's answer to all of this? A new tax on tea. [chuckle] It did not go well.")
REF = ("Let's start in London, because this story starts with a bill. Britain had just won the Seven Years' War, "
       "and somebody finally opened the accounts. Nobody liked what they found.")
log = []

def say(msg): print(msg, flush=True); log.append(msg)

def mp3(wav, name):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', wav, '-af', 'loudnorm=I=-16:TP=-1.5', '-b:a', '160k', os.path.join(OUT, name)], check=True)

def install():
    pip = [sys.executable, '-m', 'pip', 'install', '-q', '--break-system-packages']
    subprocess.run(pip + ['torch', 'torchaudio', '--index-url', 'https://download.pytorch.org/whl/cpu'], check=False)
    subprocess.run(pip + ['chatterbox-tts'], check=False)

def kokoro():
    import soundfile as sf
    from kokoro_onnx import Kokoro
    k = Kokoro(os.path.join(STUDIO, 'tts/kokoro.onnx'), os.path.join(STUDIO, 'tts/voices.bin'))
    for name, text in [('ref', REF), ('A-current-george', PLAIN)]:
        a, sr = k.create(text, voice='bm_george', speed=1.0, lang='en-gb'); sf.write(os.path.join(OUT, name + '.wav'), a, sr)
    mp3(os.path.join(OUT, 'A-current-george.wav'), 'A-current-george.mp3')

def chatter():
    import torch, torchaudio as ta
    torch.set_num_threads(os.cpu_count() or 2); ref = os.path.join(OUT, 'ref.wav')
    try:
        from chatterbox.tts import ChatterboxTTS
        m = ChatterboxTTS.from_pretrained(device='cpu')
        for name, ex, cfg in [('B-chatterbox-calm', .45, .5), ('C-chatterbox-dramatic', .8, .3)]:
            t = time.time(); w = m.generate(PLAIN.replace('Twenty years later,', 'Twenty years later...'), audio_prompt_path=ref, exaggeration=ex, cfg_weight=cfg)
            p = os.path.join(OUT, name + '.wav'); ta.save(p, w, m.sr); mp3(p, name + '.mp3')
            say('%s: %.0f s of audio in %.0f s' % (name, w.shape[-1] / m.sr, time.time() - t))
        del m
    except Exception: say('Chatterbox failed:\n' + traceback.format_exc()[-1500:])
    try:
        from chatterbox.tts_turbo import ChatterboxTurboTTS
        m = ChatterboxTurboTTS.from_pretrained(device='cpu'); t = time.time()
        w = m.generate(TAGGED, audio_prompt_path=ref, norm_loudness=False)  # loudness step gives float64 -> dtype error
        p = os.path.join(OUT, 'D-chatterbox-turbo-tags.wav'); ta.save(p, w, m.sr); mp3(p, 'D-chatterbox-turbo-tags.mp3')
        say('D-chatterbox-turbo-tags: %.0f s of audio in %.0f s' % (w.shape[-1] / m.sr, time.time() - t))
    except Exception: say('Chatterbox Turbo failed:\n' + traceback.format_exc()[-1500:])

if __name__ == '__main__':
    say('cpus: %s' % os.cpu_count()); kokoro()
    if '--no-install' not in sys.argv: install()
    chatter()
    for f in os.listdir(OUT):
        if f.endswith('.wav'): os.remove(os.path.join(OUT, f))
    open(os.path.join(OUT, 'report.txt'), 'w').write('\n'.join(log)); print('done:', sorted(os.listdir(OUT)))
