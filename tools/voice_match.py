"""Find the TTS voice + settings that sound closest to the real announcer, and match its tone colour.

Features compared against the reference (the announcer saying "Farrer Road"):
  pitch    median F0 and pitch range (semitones)
  pace     length of the spoken name
  timbre   mean MFCCs (overall voice colour)
The winner is then EQ-matched to the announcer's long-term spectrum (see eq_match()).

Usage: python tools/voice_match.py      # prints a ranked table and writes work/voice/*.mp3 candidates
"""
import asyncio, os, subprocess, sys, json
import numpy as np, librosa, soundfile as sf, edge_tts

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
WORK = os.path.join(ROOT, "work", "voice")
SR = 24000
sys.path.insert(0, HERE)

VOICES = ["en-SG-LunaNeural", "en-PH-RosaNeural", "en-IN-NeerjaNeural", "en-GB-SoniaNeural", "en-HK-YanNeural",
          "en-AU-NatashaNeural", "en-GB-LibbyNeural", "en-IE-EmilyNeural", "en-NZ-MollyNeural", "en-US-JennyNeural",
          "en-US-AriaNeural", "en-KE-AsiliaNeural", "en-ZA-LeahNeural", "en-CA-ClaraNeural"]


def load(path):
    y, _ = librosa.load(path, sr=SR, mono=True)
    y, _ = librosa.effects.trim(y, top_db=35)
    return y


def features(y):
    f0, vf, _ = librosa.pyin(y, fmin=110, fmax=420, sr=SR, frame_length=1024)
    f0 = f0[vf & ~np.isnan(f0)]
    st = 12 * np.log2(f0 / 440)
    mfcc = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=20)
    return {"f0": float(np.median(f0)), "range": float(np.percentile(st, 90) - np.percentile(st, 10)),
            "dur": len(y) / SR, "mfcc": mfcc[1:13].mean(axis=1)}


def score(f, ref):
    d_pitch = abs(12 * np.log2(f["f0"] / ref["f0"]))            # semitones
    d_range = abs(f["range"] - ref["range"])                     # semitones
    d_pace = abs(np.log(f["dur"] / ref["dur"])) * 12             # ~ semitone-like scale
    d_tim = float(np.linalg.norm(f["mfcc"] - ref["mfcc"])) / 10
    return d_pitch + .5 * d_range + d_pace + d_tim, (d_pitch, d_range, d_pace, d_tim)


async def say(text, voice, rate, pitch, path):
    await edge_tts.Communicate(text, voice, rate=f"{rate:+d}%", pitch=f"{pitch:+d}Hz").save(path)


def reference():
    """Announcer saying 'Farrer Road', cleaned with DeepFilterNet."""
    ref = os.path.join(WORK, "ref-farrer-road.wav")
    if not os.path.exists(ref):
        from cut_df import df_clean
        y = df_clean(os.path.join(ROOT, "Sample announcments", "Farrer Road.mp3"), 11.45, 13.45)
        sf.write(ref, y, 48000)
        full = df_clean(os.path.join(ROOT, "Sample announcments", "Farrer Road.mp3"), 11.45, 15.7)
        sf.write(os.path.join(WORK, "ref-phrase.wav"), full, 48000)
    return ref


def main():
    os.makedirs(WORK, exist_ok=True)
    ref = features(load(reference()))
    print(f"REFERENCE  F0 {ref['f0']:.0f} Hz  range {ref['range']:.1f} st  duration {ref['dur']:.2f}s")
    rows = []
    for v in VOICES:
        # pass 1: neutral settings, to learn this voice's natural pitch and pace
        p0 = os.path.join(WORK, f"{v}_base.mp3")
        try:
            asyncio.run(say("Farrer Road.", v, 0, 0, p0))
        except Exception:
            print(f"{v:22s} not available, skipped"); continue
        base = features(load(p0))
        pitch = int(round(ref["f0"] - base["f0"]))
        rate = int(round((base["dur"] / ref["dur"] - 1) * 100))
        rate = max(-40, min(40, rate))
        # pass 2: small grid around the estimate
        for dp in (-10, 0, 10):
            for dr in (-8, 0, 8):
                path = os.path.join(WORK, f"{v}_p{pitch + dp:+d}_r{rate + dr:+d}.mp3")
                asyncio.run(say("Farrer Road.", v, rate + dr, pitch + dp, path))
                f = features(load(path))
                s, parts = score(f, ref)
                rows.append((s, v, pitch + dp, rate + dr, f, parts, path))
        best_v = min((r for r in rows if r[1] == v), key=lambda r: r[0])
        print(f"{v:22s} best {best_v[0]:5.2f}  pitch {best_v[2]:+4d}Hz rate {best_v[3]:+3d}%  "
              f"F0 {best_v[4]['f0']:.0f} range {best_v[4]['range']:.1f} dur {best_v[4]['dur']:.2f}  parts " +
              " ".join(f"{x:.2f}" for x in best_v[5]), flush=True)
    rows.sort(key=lambda r: r[0])
    top = [{"voice": r[1], "pitch": r[2], "rate": r[3], "score": round(r[0], 2), "file": r[6]} for r in rows[:8]]
    json.dump(top, open(os.path.join(WORK, "ranking.json"), "w"), indent=1)
    print("\nTOP 8"); [print(t) for t in top]


if __name__ == "__main__":
    main()
