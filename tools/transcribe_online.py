"""Transcribe the online line recordings (all languages) with word timings, one JSON per line.

Usage: python tools/transcribe_online.py CC NE ...      -> work/transcripts/<LINE>.json
"""
import json, os, re, subprocess, sys
import numpy as np
from faster_whisper import WhisperModel

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SRC = os.path.join(ROOT, "Sample announcments", "online")
OUT = os.path.join(ROOT, "work", "transcripts")


def script_of(text):
    if re.search(r"[一-鿿]", text): return "zh"
    if re.search(r"[஀-௿]", text): return "ta"
    return "latin"                                   # English or Malay


def main():
    os.makedirs(OUT, exist_ok=True)
    model = WhisperModel("small", device="cpu", compute_type="int8")
    for line in sys.argv[1:]:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SRC, line + ".mp3"),
                              "-ac", "1", "-ar", "16000", "-f", "s16le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
        segs, _ = model.transcribe(x, vad_filter=True, condition_on_previous_text=False,
                                   multilingual=True, word_timestamps=True)
        rows = []
        for s in segs:
            rows.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip(),
                         "script": script_of(s.text),
                         "words": [[w.word, round(w.start, 2), round(w.end, 2)] for w in (s.words or [])]})
        json.dump(rows, open(os.path.join(OUT, line + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        print(f"{line}: {len(rows)} segments", flush=True)


if __name__ == "__main__":
    main()
