"""Pick the respelling whose TTS pronunciation sounds closest to a reference recording of the word.

Compares the sound shape (MFCCs with per-clip mean removed, so voice differences matter less)
using dynamic time warping, which lines up the two clips even if one is spoken faster.

Usage: python tools/match_pronunciation.py <reference.wav/m4a> <start_s> <end_s> [<start_s> <end_s> ...] -- <spelling> [<spelling> ...]
"""
import asyncio, os, sys, tempfile
import numpy as np, librosa, edge_tts

SR = 16000
VOICE, RATE, PITCH = "en-PH-RosaNeural", "-12%", "+8Hz"


def feats(y):
    y = librosa.effects.trim(y, top_db=30)[0]
    m = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=20, n_fft=512, hop_length=160)[1:14]
    m = m - m.mean(axis=1, keepdims=True)
    return m / (m.std(axis=1, keepdims=True) + 1e-6), len(y) / SR


def distance(a, b):
    D, wp = librosa.sequence.dtw(X=a, Y=b, metric="euclidean")
    return D[-1, -1] / len(wp)


def main():
    args = sys.argv[1:]
    cut = args.index("--")
    ref_path, times, spellings = args[0], list(map(float, args[1:cut])), args[cut + 1:]
    full, _ = librosa.load(ref_path, sr=SR, mono=True)
    refs = [feats(full[int(a * SR):int(b * SR)]) for a, b in zip(times[::2], times[1::2])]
    print("reference takes:", ", ".join(f"{d:.2f}s" for _, d in refs))
    rows = []
    with tempfile.TemporaryDirectory() as d:
        for sp in spellings:
            p = os.path.join(d, "x.mp3")
            asyncio.run(edge_tts.Communicate(sp + ".", VOICE, rate=RATE, pitch=PITCH).save(p))
            y, _ = librosa.load(p, sr=SR, mono=True)
            f, dur = feats(y)
            dist = np.mean([distance(f, r) for r, _ in refs])
            rows.append((dist, sp, dur))
    for dist, sp, dur in sorted(rows):
        print(f"  {dist:6.3f}  {sp:14s}  {dur:.2f}s")


if __name__ == "__main__":
    main()
