# MRT Announcements

An interactive Singapore MRT map for little train fans. Tap any station to hear it announced, then the doors closing.

**Live site:** https://kavyaj.github.io/mrt-announcements/ · [The story behind it](https://kavyaj.github.io/mrt-announcements/story.html)

Made by [Kavya](https://www.linkedin.com/in/kavya-jahagirdar/) for her three-year-old, who loves the MRT (especially the yellow line).

## What's where

| Path | What it is |
|---|---|
| `docs/` | The website (served by GitHub Pages) |
| `docs/network.js` | Stations, map coordinates and lines |
| `docs/recordings.js` | Real on-board announcements, by station |
| `docs/audio/` | Sounds: real recordings, spoken station names, door-closing sound |
| `tools/` | Python scripts used to clean recordings and generate station names |

### Adding a real recording
Put the mp3 in `docs/audio/stations/` and add a line to `docs/recordings.js`.

### Fixing a pronunciation
Edit `tools/pronunciation.json`, then run `python tools/make_names.py --only "Station Name"`.

## Credits and note
- Typeface: [IdentityFont](https://github.com/jglim/IdentityFont) by jglim, a reconstruction of the LTA Identity typeface.
- This is an unofficial, non-commercial fan project, not affiliated with LTA, SMRT or SBS Transit. The chime, door-closing sound and on-board announcements belong to their operators.
