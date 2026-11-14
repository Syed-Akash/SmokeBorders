"""Launch the preinstalled Chromium, whatever Playwright version pip installed.
setup.sh writes its path to studio/.chromium; FB_CHROMIUM overrides it."""
import glob, os
HERE = os.path.dirname(os.path.abspath(__file__))

def chromium_path():
    p = os.environ.get('FB_CHROMIUM')
    if not p and os.path.exists(os.path.join(HERE, '.chromium')): p = open(os.path.join(HERE, '.chromium')).read().strip()
    return p if p and os.path.exists(p) else None

async def launch(pw, **kw):
    exe = chromium_path()
    try:
        return await pw.chromium.launch(**kw)                          # Playwright's own matching browser, if present
    except Exception:
        if not exe: raise
        return await pw.chromium.launch(executable_path=exe, **kw)    # fall back to the preinstalled one
