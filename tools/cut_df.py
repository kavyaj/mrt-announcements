"""Like cut.py, but removes noise with DeepFilterNet (AI speech enhancement) instead of spectral gating.

Usage: python tools/cut_df.py <in.mp3> <start_s> <end_s> <out.mp3> [--chime]
  --chime  prepend the approved chime (spectral-gated, since DeepFilterNet treats tones as noise)
"""
import subprocess, sys, os, tempfile
import numpy as np, soundfile as sf, torch
from df.enhance import init_df, enhance
from clean import clean, load, SR
from cut import trim, fade, CHIME_SRC, CHIME_AT, CHIME_NOISE

_model = None


def df_clean(src, ss, to):
    global _model
    if _model is None:
        _model = init_df()
    model, state, _ = _model
    x = load(src, ss, to)                     # 48 kHz mono float32
    y = enhance(model, state, torch.from_numpy(x).unsqueeze(0))
    return y.squeeze(0).numpy()


def main():
    a = sys.argv[1:]
    chime = "--chime" in a
    a = [x for x in a if x != "--chime"]
    src, ss, to, out = a[0], float(a[1]), float(a[2]), a[3]
    y = fade(trim(df_clean(src, ss, to)))
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
