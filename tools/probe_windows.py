"""Re-transcribe specific stretches of a line recording with the accurate model, saving word timings.

Usage: python tools/probe_windows.py DT 125:255 635:905 ...   -> work/probe_<LINE>.json
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import extract_online as X

line, wins = sys.argv[1], [tuple(map(float, w.split(":"))) for w in sys.argv[2:]]
out = {}
for a, b in wins:
    out[f"{a:g}-{b:g}"] = X.small_words(line, a, b)
    print(f"{line} {a:g}-{b:g}: {len(out[f'{a:g}-{b:g}'])} words", flush=True)
json.dump(out, open(os.path.join(HERE, "..", "work", f"probe_{line}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
