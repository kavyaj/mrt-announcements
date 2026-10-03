"""Remove a short, quieter leftover sound at the very start of a clip (tail of a previous announcement).

Pattern: within the first 0.7 s there is a sound, then a pause (>= 50 ms, 38 dB below the clip's peak),
then the real speech. If the leading sound is clearly quieter (>= 6 dB) than the speech after the pause,
everything up to the pause is cut. Clips are overwritten in place.

Usage: python tools/trim_lead.py docs/audio/next/*.mp3 [--dry]
"""
import os, subprocess, sys, tempfile
import numpy as np, soundfile as sf, librosa

SR, H = 48000, 480          # 10 ms frames


def lead_cut(y):
    db = np.array([20 * np.log10(np.sqrt(np.mean(y[i:i + H] ** 2)) + 1e-9) for i in range(0, len(y) - H, H)])
    peak = db.max()
    quiet = db < peak - 38
    loud = ~quiet
    first = np.argmax(loud)                       # first sound
    k = first
    while k < min(len(db), 70) and loud[k]: k += 1  # end of that first sound
    j = k
    while j < len(db) and quiet[j]: j += 1          # end of the pause
    if k >= 70 or j - k < 5 or j >= len(db): return 0.0
    before = db[first:k].max()
    after = db[j:j + 40].max()
    return (j - 2) * H / SR if after - before >= 6 else 0.0


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    for p in [a for a in sys.argv[1:] if not a.startswith("--")]:
        y, _ = librosa.load(p, sr=SR, mono=True)
        cut = lead_cut(y)
        if cut <= 0: continue
        print(f"{os.path.basename(p):34s} cut {cut:.2f}s leftover at the start", flush=True)
        if dry: continue
        y = y[int(cut * SR):]
        n = int(.01 * SR); y[:n] *= np.linspace(0, 1, n)
        with tempfile.TemporaryDirectory() as d:
            w = os.path.join(d, "x.wav"); sf.write(w, y, SR)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", w, "-af", "loudnorm=I=-16:TP=-1.5",
                            "-ar", "48000", "-ac", "1", "-b:a", "96k", p], check=True)
