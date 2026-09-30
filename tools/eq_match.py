"""EQ-match TTS speech to the announcer's tone colour.

Compares the long-term average spectrum of the reference phrase (announcer, DeepFilterNet-cleaned)
with the same phrase spoken by the TTS voice, smooths the difference to 1/3 octave, limits it to
+/-MAX_DB and turns it into a linear-phase FIR filter.

Usage: python tools/eq_match.py <voice> <rate%> <pitch Hz>      -> writes work/voice/eq_<voice>.npy
"""
import asyncio, os, sys
import numpy as np, librosa, edge_tts
from scipy.signal import firwin2, welch

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, "..", "work", "voice")
SR = 48000
MAX_DB = 10
PHRASE = "Farrer Road, please mind the platform gap."


def ltas(y):
    f, p = welch(y, SR, nperseg=4096)
    return f, 10 * np.log10(p + 1e-12)


def smooth_third_octave(f, db):
    out = np.empty_like(db)
    for i, fc in enumerate(f):
        lo, hi = fc / 2 ** (1 / 6), fc * 2 ** (1 / 6)
        m = (f >= lo) & (f <= hi)
        out[i] = db[m].mean() if m.any() else db[i]
    return out


def speech(path):
    y, _ = librosa.load(path, sr=SR, mono=True)
    return librosa.effects.trim(y, top_db=35)[0]


def build(voice, rate, pitch):
    tts = os.path.join(WORK, f"phrase_{voice}.mp3")
    asyncio.run(edge_tts.Communicate(PHRASE, voice, rate=f"{rate:+d}%", pitch=f"{pitch:+d}Hz").save(tts))
    f, ref = ltas(speech(os.path.join(WORK, "ref-phrase.wav")))
    _, syn = ltas(speech(tts))
    diff = smooth_third_octave(f, ref - syn)
    band = (f >= 180) & (f <= 7000)
    diff -= np.average(diff[band])                           # keep loudness, change only the shape
    diff = np.clip(diff, -MAX_DB, MAX_DB)
    diff[f < 180] = np.minimum(diff[f < 180], 0)             # never boost rumble
    diff[f > 7000] = np.minimum(diff[f > 7000], diff[band][-1])
    taps = firwin2(1023, f / (SR / 2), 10 ** (diff / 20))
    np.save(os.path.join(WORK, f"eq_{voice}.npy"), taps)
    for fc in (200, 400, 800, 1600, 3200, 6400):
        print(f"  {fc:5d} Hz  {diff[np.argmin(abs(f - fc))]:+5.1f} dB")
    return taps


if __name__ == "__main__":
    build(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]))
