"""Stamp a build version into docs/index.html so browsers fetch fresh data files and audio after an update.

The version is a short hash of the data scripts and the list of audio files (with sizes), so it only
changes when something changed. Script tags get ?v=<version>; audio fetches use the BUILD constant.

Usage: python tools/stamp_version.py
"""
import hashlib, os, re

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DOCS = os.path.join(ROOT, "docs")
SCRIPTS = ["network.js", "recordings.js", "names.js", "next.js", "extras.js", "transfers.js"]

h = hashlib.sha1()
for s in SCRIPTS:
    p = os.path.join(DOCS, s)
    if os.path.exists(p): h.update(open(p, "rb").read())
for root, _, files in os.walk(os.path.join(DOCS, "audio")):
    for f in sorted(files):
        p = os.path.join(root, f)
        h.update(f"{os.path.relpath(p, DOCS)}:{os.path.getsize(p)}:{int(os.path.getmtime(p))}".encode())
version = h.hexdigest()[:8]

p = os.path.join(DOCS, "index.html")
s = open(p, encoding="utf-8").read()
for name in SCRIPTS:
    s = re.sub(rf'<script src="{re.escape(name)}(\?v=[0-9a-f]+)?"></script>', f'<script src="{name}?v={version}"></script>', s)
s = re.sub(r'const BUILD = "[0-9a-f]*";', f'const BUILD = "{version}";', s)
open(p, "w", encoding="utf-8").write(s)
print("build", version)
