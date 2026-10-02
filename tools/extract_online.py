"""Cut the real "Next station, X" announcement for every station out of the online line recordings.

For each line:
  1. find every "Next station <name>" in work/transcripts/<LINE>*.json and match the name to that
     line's stations (fuzzy match, then fill single gaps using station order);
  2. look in the arrival announcement that follows for the station's Mandarin or Tamil name
     (language-detected per burst of speech); if there is one, the clip runs as one continuous piece
     from "Next station" through that arrival announcement (to "please mind the gap");
  3. clean with DeepFilterNet and write docs/audio/next/<CODE>-<slug>.mp3.
A report is written to work/extract_<LINE>.json.

Usage: python tools/extract_online.py CC [NE ...] [--dry]
"""
import difflib, glob, json, os, re, subprocess, sys, tempfile
import numpy as np, soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
SRC = os.path.join(ROOT, "Sample announcments", "online")
OUT = os.path.join(ROOT, "docs", "audio", "next")
STOP = {"please", "change", "this", "doors", "door", "next", "if", "dear", "thank", "passengers", "all", "old"}
GAP = 1.0          # a pause longer than this ends the station name
FIRST_GAP = 2.0    # ...but allow a longer pause right after "Next station"
NATIVE = ("zh", "ta")
# How the transcriber tends to hear some names (lower-case, no punctuation)
ALIASES = {
    "Dhoby Ghaut": ["dobigot", "dobigod", "doby god", "dobby got", "dobie got"], "MacPherson": ["megverson", "make person", "mcpherson"],
    "Tai Seng": ["high sing"], "Lorong Chuan": ["laorongchuan"], "Mountbatten": ["mount baton"],
    "Nicoll Highway": ["nickel highway"], "Haw Par Villa": ["ho pa villa"], "Buona Vista": ["borna vista", "bonavista"],
    "Paya Lebar": ["paya leba", "payalabha"], "Farrer Road": ["farrah road"], "HarbourFront": ["harbour front", "harbor front", "upper front"],
    "Bishan": ["bhishan"], "Telok Blangah": ["telok blangar"], "one-north": ["one north"],
    "Outram Park": ["uttrampak", "outrum park", "utron park"], "Farrer Park": ["sarah park", "farah park"], "Boon Keng": ["bunking"],
    "Clarke Quay": ["klak key", "clark key", "klakp"], "Serangoon": ["surrainant"], "Yew Tee": ["ut", "yuti"], "Bukit Gombak": ["bukit gumbak"],
}
# Announcements the transcriber missed, found by hand: code -> (station, start, end) in the line recording
MANUAL = {
    "CC": {"CC2": ("Bras Basah", 235.9, 239.5), "CC23": ("one-north", 791.06, 794.73)},
    "NS": {"NS11": ("Sembawang", 369.45, 372.7)},
}
SR16 = 16000
_audio, _model = {}, None


def network():
    js = open(os.path.join(ROOT, "docs", "network.js"), encoding="utf-8").read()
    lines = {}
    for m in re.finditer(r'\{ id: "(\w+)".*?stops: \[(.*?)\]\s*\}', js):
        lines[m.group(1)] = [(f"{m.group(1)}{n}", s) for n, s in re.findall(r'\[(\d+),"([^"]+)"\]', m.group(2)) if n != "0"]
    return lines


def norm(t):
    return re.sub(r"[^a-z ]", "", t.lower()).strip()


def load_words(line):
    words, seen = [], set()
    for f in sorted(glob.glob(os.path.join(ROOT, "work", "transcripts", f"{line}*.json"))):
        for seg in json.load(open(f, encoding="utf-8")):
            for w, a, b in seg["words"]:
                key = (round(a), norm(w))                 # chunks overlap: drop repeats
                if key in seen: continue
                seen.add(key); words.append((w.strip(), a, b))
    words.sort(key=lambda w: w[1])
    return words


def candidates(words):
    """Every 'Next station <name words>' with the name's time span."""
    out = []
    # the accurate model sometimes splits words ("ne xt", "S y mb al Wang"): glue a split "next" back
    glued = []
    for w in words:
        if glued and norm(glued[-1][0]) == "ne" and norm(w[0]) == "xt":
            glued[-1] = ("next", glued[-1][1], w[2])
        else:
            glued.append(w)
    words = glued
    for i in range(len(words) - 2):
        if norm(words[i][0]) == "next" and norm(words[i + 1][0]).startswith("station"):
            name, j = [], i + 2
            if j < len(words) and norm(words[j][0]) == "is": j += 1
            while j < len(words) and norm(words[j][0]) not in STOP and                     words[j][1] - words[j - 1][2] < (FIRST_GAP if not name else GAP):
                name.append(words[j]); j += 1
            if name:
                out.append({"start": words[i][1], "name_end": name[-1][2], "text": " ".join(w[0] for w in name),
                            "stop": words[j][1] if j < len(words) and words[j][1] - name[-1][2] < GAP else None})
    return out


def score(text, station):
    t = norm(text).replace(" interchange", "").replace(" terminal", "").replace(" station", "")
    if len(t.split()) > 3 * len(norm(station).split()) + 2: return 0     # a sentence, not a station name
    best, tj = 0, t.replace(" ", "")
    for form in [norm(station)] + ALIASES.get(station, []):
        fj = form.replace(" ", "")
        best = max(best, difflib.SequenceMatcher(None, t, form).ratio(),
                   difflib.SequenceMatcher(None, t[:len(form) + 2], form).ratio(),
                   difflib.SequenceMatcher(None, tj[:len(fj) + 2], fj).ratio())
    return best


def assign(cands, stations):
    """Fuzzy-match each candidate, then fill single gaps between matched neighbours using station order."""
    idx = {code: k for k, (code, _) in enumerate(stations)}
    for c in cands:
        c["score"], c["hit"] = max((score(c["text"], s), (code, s)) for code, s in stations)
    found = {}
    for c in cands:
        if c["score"] >= .55 and c["hit"][0] not in found:
            found[c["hit"][0]] = c
    # order fill: n unmatched candidates between two matched stations that are n+1 apart on the line
    ordered = sorted(found.items(), key=lambda kv: kv[1]["start"])
    used = {id(c) for c in found.values()}
    for (c1, a), (c2, b) in zip(ordered, ordered[1:]):
        k1, k2 = idx[c1], idx[c2]
        step = 1 if k2 > k1 else -1
        gap_codes = [stations[k] for k in range(k1 + step, k2, step)]
        between = [c for c in cands if a["start"] < c["start"] < b["start"] and id(c) not in used]
        if gap_codes and len(between) == len(gap_codes) and all(code not in found for code, _ in gap_codes):
            for c, (code, st) in zip(between, gap_codes):
                c["hit"] = (code, st); c["by_order"] = True; found[code] = c
    return found


def small_words(line, a, b):
    """Re-transcribe [a, b] with the more accurate model; words with absolute times."""
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=os.cpu_count())
    x = audio16(line)[int(max(0, a) * SR16):int(b * SR16)]
    segs, _ = _model.transcribe(x, word_timestamps=True, condition_on_previous_text=False, vad_filter=True)
    return [(w.word.strip(), round(a + w.start, 2), round(a + w.end, 2)) for s in segs for w in (s.words or [])]


def refine(line, found, words, stations, total):
    """Second pass for stations still missing (or only placed by order): re-transcribe the stretch between
    the confident neighbours with the small model and match only against the stations expected there."""
    idx = {code: k for k, (code, _) in enumerate(stations)}
    for code in [c for c, v in found.items() if v.get("by_order")]:
        del found[code]
    anchors = sorted(found.items(), key=lambda kv: kv[1]["start"])
    spans = []
    for (c1, a), (c2, b) in zip(anchors, anchors[1:]):
        k1, k2 = idx[c1], idx[c2]
        step = 1 if k2 > k1 else -1
        gap = [stations[k] for k in range(k1 + step, k2, step) if stations[k][0] not in found]
        if gap: spans.append((a["name_end"] + .5, b["start"] - .2, gap))
    if anchors:   # stations beyond the first / last confident match
        (cf, f), (cl, l) = anchors[0], anchors[-1]
        before = [s for s in stations if s[0] not in found and (idx[s[0]] < idx[cf]) == (idx[cl] > idx[cf])]
        after = [s for s in stations if s[0] not in found and s not in before]
        if before: spans.append((max(0, f["start"] - 120), f["start"] - .2, before))
        if after: spans.append((l["name_end"] + .5, min(total, l["name_end"] + 240), after))
    for a, b, gap in spans:
        if b - a < 2: continue
        for c in candidates(small_words(line, a, b)):
            r, hit = max((score(c["text"], s), (code, s)) for code, s in gap)
            if r >= .55 and hit[0] not in found:
                c["score"], c["hit"], c["refined"] = r, hit, True
                found[hit[0]] = c
    return found


def audio16(line):
    if line not in _audio:
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", os.path.join(SRC, line + ".mp3"), "-ac", "1",
                              "-ar", str(SR16), "-f", "s16le", "-"], capture_output=True).stdout
        _audio[line] = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    return _audio[line]


def language(line, a, b):
    global _model
    if _model is None:
        from faster_whisper import WhisperModel
        _model = WhisperModel("small", device="cpu", compute_type="int8", cpu_threads=os.cpu_count())
    x = audio16(line)[int(a * SR16):int(b * SR16)]
    lang, prob, _ = _model.detect_language(x)
    return lang, prob


def native_name(line, words, after, station):
    """First Mandarin/Tamil burst in the arrival announcement that follows (before 'please mind ...')."""
    win = [w for w in words if after + .3 < w[1] < after + 45]
    end = next((w[1] for k, w in enumerate(win[:-1]) if norm(w[0]) == "please" and norm(win[k + 1][0]) == "mind"), None)
    if end is None: return None
    # end of "... please mind the (platform) gap": the clip runs through it as one continuous piece
    gap_end = next((w[2] for w in win if w[1] >= end and norm(w[0]).startswith("gap")), end + 2.5)
    win = [w for w in win if w[1] < end]
    # start of the arrival announcement: first word after the longest pause in the window
    if len(win) < 2: return None
    gaps = [(win[k + 1][1] - win[k][2], k + 1) for k in range(len(win) - 1)]
    big = max(gaps)
    if big[0] > 2.5: win = win[big[1]:]
    bursts, cur = [], [win[0]]
    for w in win[1:]:
        if w[1] - cur[-1][2] > .3 or cur[-1][0].endswith((",", ".")):
            bursts.append(cur); cur = [w]
        else:
            cur.append(w)
    bursts.append(cur)
    for bu in bursts:
        a, b = bu[0][1], bu[-1][2]
        if b - a < .35 or "station" in norm(" ".join(w[0] for w in bu)): continue
        lang, p = language(line, a, b + .1)
        if lang in NATIVE and p > .5:
            return {"lang": lang, "prob": round(p, 2), "start": round(a - .12, 2), "end": round(b + .18, 2),
                    "gap_end": round(gap_end + .3, 2), "heard": " ".join(w[0] for w in bu)}
    return None


def render(line, parts, out):
    from cut_df import df_clean
    from cut import trim, fade
    pieces = []
    for a, b in parts:
        pieces += [fade(trim(df_clean(os.path.join(SRC, line + ".mp3"), a, b), rel_db=-32, pad=.08)), np.zeros(int(.35 * 48000))]
    y = np.concatenate(pieces[:-1])
    with tempfile.TemporaryDirectory() as d:
        w = os.path.join(d, "x.wav"); sf.write(w, y, 48000)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", w, "-af", "highpass=f=120,loudnorm=I=-16:TP=-1.5",
                        "-ar", "48000", "-ac", "1", "-b:a", "96k", out], check=True)


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry" in sys.argv
    os.makedirs(OUT, exist_ok=True)
    net = network()
    for line in args:
        stations = net[line] + net.get({"CC": "CE", "EW": "CG"}.get(line, ""), [])
        words = load_words(line)
        found = assign(candidates(words), stations)
        found = refine(line, found, words, stations, len(audio16(line)) / SR16)
        report = {}
        for code, c in found.items():
            end = min(c["stop"] - .08, c["name_end"] + 3.0) if c["stop"] else c["name_end"] + .6
            report[code] = {"station": c["hit"][1], "heard": c["text"], "score": round(c["score"], 2),
                            "by_order": c.get("refined", False), "start": round(c["start"] - .25, 2), "end": round(end, 2)}
            # Mandarin/Tamil already said right after the English name (e.g. Thomson-East Coast Line)?
            extra = [w for w in norm(c["text"]).split() if w not in ("interchange", "terminal", "station")]
            inline = len(extra) > len(norm(c["hit"][1]).split()) + 1
            report[code]["native"] = None if inline else native_name(line, words, end, c["hit"][1])
            report[code]["inline_native"] = inline
        for code, (st, a, b) in MANUAL.get(line, {}).items():
            report[code] = ({"station": st, "heard": "(manual)", "score": 1.0, "by_order": False,
                                     "start": a, "end": b, "native": native_name(line, words, b, st)})
        missing = [s for code, s in stations if code not in report]
        print(f"== {line}: {len(report)}/{len(stations)} stations found; missing: {', '.join(missing) or 'none'}", flush=True)
        for code, f in sorted(report.items(), key=lambda kv: kv[1]["start"]):
            nat = f["native"]
            print(f"  {code:5s} {f['station']:20s} <- '{f['heard']}' ({f['score']}{', 2nd pass' if f['by_order'] else ''})"
                  + (f"  + {nat['lang']} '{nat['heard']}' ({nat['prob']})" if nat else ""), flush=True)
            if not dry:
                slug = re.sub(r"[^a-z0-9]+", "-", f["station"].lower()).strip("-")
                f["file"] = f"next/{code}-{slug}.mp3"
                # one continuous piece: "Next station, X" alone, or through the arrival announcement
                # (up to "please mind the gap") when that is where the Mandarin/Tamil name is said
                parts = [(f["start"], nat["gap_end"] if nat else f["end"])]
                render(line, parts, os.path.join(ROOT, "docs", "audio", f["file"]))
        json.dump(report, open(os.path.join(ROOT, "work", f"extract_{line}.json"), "w", encoding="utf-8"),
                  indent=1, ensure_ascii=False)


if __name__ == "__main__":
    main()
