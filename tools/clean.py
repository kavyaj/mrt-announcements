"""Remove train background noise from a recording (or a slice of it).

Usage: python tools/clean.py <in.mp3> <out.wav> [start_s end_s] [--noise n0 n1]
  --noise n0 n1   seconds of the SAME file with train noise but no announcement,
                  used as the noise profile (much better than guessing).
"""
import subprocess, sys
import numpy as np, noisereduce as nr, soundfile as sf

SR = 48000


def load(f, ss=None, to=None):
    cmd = ["ffmpeg", "-v", "error"]
    if ss is not None:
        cmd += ["-ss", str(ss), "-to", str(to)]
    cmd += ["-i", f, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"]
    raw = subprocess.run(cmd, capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def clean(f, ss=None, to=None, noise=None):
    x = load(f, ss, to)
    if noise:
        y = nr.reduce_noise(y=x, sr=SR, y_noise=load(f, *noise), stationary=True, prop_decrease=0.95, n_fft=2048)
        return nr.reduce_noise(y=y, sr=SR, stationary=False, prop_decrease=0.6, n_fft=2048)
    return nr.reduce_noise(y=x, sr=SR, stationary=False, prop_decrease=0.9, n_fft=2048)


if __name__ == "__main__":
    a = sys.argv[1:]
    noise = None
    if "--noise" in a:
        i = a.index("--noise"); noise = (float(a[i + 1]), float(a[i + 2])); a = a[:i] + a[i + 3:]
    ss, to = (float(a[2]), float(a[3])) if len(a) >= 4 else (None, None)
    sf.write(a[1], clean(a[0], ss, to, noise), SR)
