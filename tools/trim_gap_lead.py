"""Cut a leftover sound at the start of a clip when it is separated from the real speech by a near-silent gap.

Pattern (first 1.0 s): sound -> near silence (>= 40 dB below the clip's peak) -> speech (within 15 dB of peak).
The clip is cut at the last near-silent frame before that speech. Used for interchange clips that begin
with the tail of the station name ("...dens. Change at the next station ...").

Usage: python tools/trim_gap_lead.py docs/audio/change/*.mp3 [--dry]
"""
import os, subprocess, sys, tempfile
import numpy as np, soundfile as sf, librosa

SR, H = 48000, 1200         # 25 ms frames


_model = None


def first_word_end(y):
    """End time of the first word, per the transcriber (a leftover gets folded into that word)."""
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=os.cpu_count())
    segs, _ = _model.transcribe(librosa.resample(y, orig_sr=SR, target_sr=16000), language="en",
                                word_timestamps=True, vad_filter=False, condition_on_previous_text=False)
    ws = [w for s in segs for w in (s.words or [])]
    return ws[0].end if ws else 0.0


def cut_point(y):
    db = np.array([20 * np.log10(np.sqrt(np.mean(y[i:i + H] ** 2)) + 1e-9) for i in range(0, len(y) - H, H)])
    peak = db.max()
    # only look inside an unusually long first word ("Change" is ~0.4 s; a leftover makes it ~1 s+)
    end = first_word_end(y)
    if end < .6: return 0.0
    limit = int((end - .15) * SR / H)
    deep = [i for i in range(min(limit, len(db))) if db[i] < peak - 40]
    for i in reversed(deep):
        before = db[:i]
        after = db[i + 1:i + 1 + int(.4 * SR / H)]
        if len(after) and after.max() > peak - 15 and len(before) and before.max() > peak - 30:
            return i * H / SR
    return 0.0


if __name__ == "__main__":
    dry = "--dry" in sys.argv
    for p in [a for a in sys.argv[1:] if not a.startswith("--")]:
        y, _ = librosa.load(p, sr=SR, mono=True)
        c = cut_point(y)
        if c <= 0: continue
        print(f"{os.path.basename(p):30s} cut {c:.2f}s", flush=True)
        if dry: continue
        y = y[int(c * SR):]
        n = int(.008 * SR); y[:n] *= np.linspace(0, 1, n)
        with tempfile.TemporaryDirectory() as d:
            w = os.path.join(d, "x.wav"); sf.write(w, y, SR)
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", w, "-af", "loudnorm=I=-16:TP=-1.5",
                            "-ar", "48000", "-ac", "1", "-b:a", "96k", p], check=True)
