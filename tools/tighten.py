"""Tighten finished station clips: start exactly at "Next station" and shrink long pauses inside.

For each clip: find the word "next" with the accurate model, back up to the moment speech starts
(energy), drop everything before it; then shorten any pause longer than MAX_GAP to KEEP_GAP.
Clips are overwritten in place. Prints what changed.

Usage: python tools/tighten.py docs/audio/next/*.mp3
"""
import os, subprocess, sys, tempfile
import numpy as np, soundfile as sf, librosa

SR = 48000
MAX_GAP, KEEP_GAP = .6, .3
FRAME = .02
_model = None
TIGHT = "--tight" in sys.argv          # always cut at the quietest instant right before "next"


def model():
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=os.cpu_count())
    return _model


def frames_db(y):
    h = int(FRAME * SR)
    e = np.array([np.sqrt(np.mean(y[i:i + h] ** 2)) + 1e-9 for i in range(0, len(y) - h, h)])
    return 20 * np.log10(e)


def tighten(path):
    y, _ = librosa.load(path, sr=SR, mono=True)
    db = frames_db(y)
    thr = db.max() - 35
    loud = db > thr
    # 1) start at "next"
    y16 = librosa.resample(y, orig_sr=SR, target_sr=16000)
    segs, _ = model().transcribe(y16, language="en", word_timestamps=True, vad_filter=False, condition_on_previous_text=False)
    words = [w for s in segs for w in (s.words or [])]
    nxt = next((w for w in words if w.word.strip().lower().strip(",.").startswith(("next", "mixed", "nixed", "neck")))
           , None)
    cut_at, silent = 0.0, []
    if nxt is not None and nxt.start > .15:
        k = int(nxt.start / FRAME)
        lo = max(0, k - int(.4 / FRAME))
        silent = [i for i in range(lo, min(k + 1, len(loud))) if not loud[i]]
        cut_at = (silent[-1] + 1) * FRAME - .04 if silent else max(0, nxt.start - .06)
        cut_at = max(0.0, cut_at)
    if nxt is not None and (TIGHT or not silent if nxt.start > .15 else TIGHT):
        # no clean silence before "next" (tail of the previous announcement runs into it):
        # cut at the quietest instant just before the word
        lo, hi = int(max(0, nxt.start - .35) / FRAME), int((nxt.start + .05) / FRAME) + 1
        cut_at = (lo + int(np.argmin(db[lo:hi]))) * FRAME
    y = y[int(cut_at * SR):]
    # 2) shrink long pauses
    db = frames_db(y); loud = db > thr
    out, i, n = [], 0, len(loud)
    keep = int(KEEP_GAP / FRAME); h = int(FRAME * SR)
    shrunk = 0.0
    while i < n:
        j = i
        while j < n and loud[j] == loud[i]: j += 1
        seg = y[i * h:j * h]
        if not loud[i] and 0 < i and j < n and (j - i) * FRAME > MAX_GAP:
            shrunk += (j - i - keep) * FRAME
            seg = np.concatenate([seg[:keep * h // 2], seg[-keep * h // 2:]])
        out.append(seg); i = j
    y = np.concatenate(out + [y[n * h:]])
    n_fade = int(.01 * SR); y[:n_fade] *= np.linspace(0, 1, n_fade)
    with tempfile.TemporaryDirectory() as d:
        w = os.path.join(d, "x.wav"); sf.write(w, y, SR)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", w, "-af", "loudnorm=I=-16:TP=-1.5",
                        "-ar", "48000", "-ac", "1", "-b:a", "96k", path], check=True)
    first = " ".join(w.word.strip() for w in words[:3])
    return cut_at, shrunk, first


if __name__ == "__main__":
    for p in [a for a in sys.argv[1:] if not a.startswith("--")]:
        cut, shrunk, first = tighten(p)
        flag = "" if first.lower().startswith("next") or cut > 0 else "   <-- no 'next' found"
        print(f"{os.path.basename(p):34s} trimmed {cut:4.2f}s at start, {shrunk:4.2f}s of pauses  | heard: {first}{flag}", flush=True)
