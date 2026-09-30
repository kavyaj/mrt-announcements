"""Locate announcement chimes (E5 -> C5) and door-closing beep bursts (~750 Hz) in a recording.

Usage: python tools/find_events.py <file.mp3> [...]
"""
import sys
import numpy as np
from analyze import load, SR

HOP = 0.02


def band_ratio(x, f0, bw=25, win=2048):
    """Per-frame energy near f0 relative to the median spectrum level (tonal prominence)."""
    fr = np.fft.rfftfreq(win, 1 / SR)
    sel = (fr > f0 - bw) & (fr < f0 + bw)
    ref = (fr > 200) & (fr < 4000)
    h = int(HOP * SR)
    out = []
    for i in range(0, len(x) - win, h):
        sp = np.abs(np.fft.rfft(x[i:i + win] * np.hanning(win)))
        out.append(sp[sel].max() / (np.median(sp[ref]) + 1e-9))
    return np.array(out)


def runs(mask, min_len):
    out, st = [], None
    for k, v in enumerate(np.append(mask, False)):
        if v and st is None:
            st = k
        elif not v and st is not None:
            if (k - st) * HOP >= min_len:
                out.append((st * HOP, k * HOP))
            st = None
    return out


def find(f):
    x = load(f)
    e5, c5, b = band_ratio(x, 656), band_ratio(x, 523), band_ratio(x, 752)
    # chime: a sustained E5 run followed within ~0.9 s by a C5 run
    e_runs = runs(e5 > 40, 0.3)
    c_runs = runs(c5 > 40, 0.2)
    chimes = [a for a, z in e_runs if any(0.3 < c0 - a < 1.2 for c0, _ in c_runs)]
    # beeps: many short 750 Hz pulses packed together
    pulses = runs(b > 25, 0.02)
    bursts, cur = [], []
    for p in pulses:
        if cur and p[0] - cur[-1][1] > 0.3:
            if len(cur) >= 5: bursts.append((cur[0][0], cur[-1][1], len(cur)))
            cur = []
        cur.append(p)
    if len(cur) >= 5: bursts.append((cur[0][0], cur[-1][1], len(cur)))
    print("=====", f, f"({len(x) / SR:.0f}s)")
    print("  chimes at:", ", ".join(f"{t:.1f}s" for t in chimes) or "none")
    print("  door beeps:", ", ".join(f"{a:.1f}-{z:.1f}s ({n})" for a, z, n in bursts) or "none")


if __name__ == "__main__":
    for f in sys.argv[1:]:
        find(f)
