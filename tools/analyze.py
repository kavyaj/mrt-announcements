"""Inspect sample recordings: find tonal events (chimes / door beeps) and the announcer's voice pitch.

Usage: python tools/analyze.py tones <file.mp3> [...]
       python tools/analyze.py voice <file.mp3> <start_s> <end_s>
"""
import subprocess, sys
import numpy as np

SR = 16000
NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def load(f):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", f, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, np.int16).astype(np.float32) / 32768


def note(hz):
    n = int(round(69 + 12 * np.log2(hz / 440)))
    return f"{NAMES[n % 12]}{n // 12 - 1}"


def tones(f, win=2048, hop=800, thresh=25):
    x = load(f)
    fr = np.fft.rfftfreq(win, 1 / SR)
    band = (fr > 300) & (fr < 4000)
    fb = fr[band]
    print("=====", f)
    for i in range(0, len(x) - win, hop):
        seg = x[i:i + win] * np.hanning(win)
        s = np.abs(np.fft.rfft(seg))[band]
        k = np.argmax(s)
        tonal = s[k] / (np.median(s) + 1e-9)
        if tonal > thresh:
            # second strongest peak (for two-tone chimes), at least 50 Hz away
            s2 = s.copy(); s2[np.abs(fb - fb[k]) < 50] = 0
            k2 = np.argmax(s2)
            print(f"{i / SR:6.2f}s  {fb[k]:7.1f}Hz {note(fb[k]):4s} | 2nd {fb[k2]:7.1f}Hz {note(fb[k2]):4s}"
                  f"  tonal={tonal:4.0f} rms={np.sqrt(np.mean(seg ** 2)):.3f}")


def voice(f, t0, t1, win=1024, hop=160):
    """Median F0 via autocorrelation over voiced frames in [t0, t1]."""
    x = load(f)[int(t0 * SR):int(t1 * SR)]
    f0s = []
    for i in range(0, len(x) - win, hop):
        seg = x[i:i + win] - np.mean(x[i:i + win])
        if np.sqrt(np.mean(seg ** 2)) < 0.01:
            continue
        ac = np.correlate(seg, seg, "full")[win - 1:]
        lo, hi = SR // 400, SR // 90
        lag = lo + np.argmax(ac[lo:hi])
        if ac[lag] / ac[0] > 0.5:
            f0s.append(SR / lag)
    f0s = np.array(f0s)
    print(f"{f} [{t0}-{t1}s] voiced frames={len(f0s)} median F0={np.median(f0s):.0f}Hz "
          f"p10={np.percentile(f0s, 10):.0f} p90={np.percentile(f0s, 90):.0f}")


if __name__ == "__main__":
    if sys.argv[1] == "tones":
        for f in sys.argv[2:]:
            tones(f)
    else:
        voice(sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
