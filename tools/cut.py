"""Cut an announcement out of a sample recording, remove train noise, tighten the edges and save as mp3.

Usage: python tools/cut.py <in.mp3> <start_s> <end_s> <noise_start_s> <noise_end_s> <out.mp3> [--chime]
  noise_*  a stretch of the same recording with train noise but no announcement or talking
  --chime  prepend the approved chime (taken from the Farrer Road arrival clip)
"""
import subprocess, sys, os, tempfile
import numpy as np, soundfile as sf
from clean import clean, SR

HERE = os.path.dirname(os.path.abspath(__file__))
CHIME_SRC = os.path.join(HERE, "..", "Sample announcments", "Farrer Road.mp3")
CHIME_AT = (8.75, 10.6)          # E5 -> C5 chime in that recording
CHIME_NOISE = (0.0, 8.4)


def trim(y, rel_db=-35, pad=0.12):
    """Drop leading/trailing near-silence left after noise removal."""
    h = int(0.01 * SR)
    db = 20 * np.log10(np.array([np.sqrt(np.mean(y[i:i + h] ** 2)) + 1e-9 for i in range(0, len(y) - h, h)]))
    on = np.flatnonzero(db > db.max() + rel_db)
    a, z = max(0, on[0] * h - int(pad * SR)), min(len(y), (on[-1] + 1) * h + int(pad * SR))
    return y[a:z]


def fade(y, ms=15):
    n = int(ms / 1000 * SR)
    y = y.copy(); y[:n] *= np.linspace(0, 1, n); y[-n:] *= np.linspace(1, 0, n)
    return y


def main():
    a = sys.argv[1:]
    chime = "--chime" in a
    a = [x for x in a if x != "--chime"]
    src, ss, to, n0, n1, out = a[0], float(a[1]), float(a[2]), float(a[3]), float(a[4]), a[5]
    y = fade(trim(clean(src, ss, to, (n0, n1))))
    if chime:
        c = fade(trim(clean(CHIME_SRC, *CHIME_AT, CHIME_NOISE)))
        y = np.concatenate([c, np.zeros(int(0.25 * SR)), y])
    with tempfile.TemporaryDirectory() as d:
        wav = os.path.join(d, "x.wav")
        sf.write(wav, y, SR)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav, "-af", "highpass=f=150,loudnorm=I=-16:TP=-1.5",
                        "-ar", "48000", "-ac", "1", "-b:a", "128k", out], check=True)


if __name__ == "__main__":
    main()
