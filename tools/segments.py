"""Split a cleaned recording into sound segments and transcribe each one separately.

Usage: python tools/segments.py <clean.wav> [...]
Prints: start-end  transcript   (times in seconds, same timeline as the original file)
"""
import sys
import numpy as np, soundfile as sf
from faster_whisper import WhisperModel

HOP = 0.02


def segments(x, sr, rel_db=-28, min_len=0.5, bridge=0.6):
    h = int(HOP * sr)
    rms = np.array([np.sqrt(np.mean(x[i:i + h] ** 2)) + 1e-9 for i in range(0, len(x) - h, h)])
    db = 20 * np.log10(rms)
    on = db > db.max() + rel_db
    out, st, last = [], None, None
    for k, v in enumerate(on):
        t = k * HOP
        if v:
            if st is None: st = t
            last = t
        elif st is not None and t - last > bridge:
            if last - st >= min_len: out.append((st, last + HOP))
            st = None
    if st is not None and last - st >= min_len: out.append((st, last + HOP))
    return out


if __name__ == "__main__":
    m = WhisperModel("medium.en", device="cpu", compute_type="int8")
    for f in sys.argv[1:]:
        x, sr = sf.read(f)
        print("=====", f, flush=True)
        for a, z in segments(x, sr):
            clip = x[max(0, int((a - 0.2) * sr)):int((z + 0.2) * sr)].astype(np.float32)
            import librosa  # noqa: resample for whisper (16 kHz)
            clip = librosa.resample(clip, orig_sr=sr, target_sr=16000)
            segs, _ = m.transcribe(clip, condition_on_previous_text=False, beam_size=5)
            txt = " ".join(s.text.strip() for s in segs)
            print(f"  {a:6.1f}-{z:6.1f}  {txt}", flush=True)
