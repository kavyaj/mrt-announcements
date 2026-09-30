"""Build an MRT-style announcement: chime + "Next station, X." + "Doors are closing." + door beeps.

Everything is generated from scratch: a synthesized chime and beeps (ffmpeg) plus
Microsoft Edge neural TTS (edge-tts), so no operator audio is reused. Tone pitches,
timings and the announcer's pitch range were measured from the sample recordings
with tools/analyze.py:
  chime   E5 (~656 Hz) held ~0.75 s, then C5 (~523 Hz) decaying; strong 3rd harmonic
  beeps   ~750 Hz, ~50 ms on, one every ~130 ms, ~10 beeps
  voice   median F0 ~230-265 Hz, narrow range (calm, flat delivery)

Usage: python tools/make_announcement.py "Farrer Road" <preset> out.mp3
"""
import asyncio, subprocess, sys, tempfile, os
import edge_tts

FF = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
SR = "44100"

# voice, rate, pitch — pitch raised so each voice's median F0 lands near the announcer's (~240 Hz)
PRESETS = {
    "luna":   ("en-SG-LunaNeural",   "+6%", "+55Hz"),
    "rosa":   ("en-PH-RosaNeural",   "+6%", "+30Hz"),
    "neerja": ("en-IN-NeerjaNeural", "+4%", "-20Hz"),
    "sonia":  ("en-GB-SoniaNeural",  "+6%", "+40Hz"),
    "yan":    ("en-HK-YanNeural",    "+6%", "+65Hz"),
}

# Cabin PA speaker: band-limited, lightly compressed, short metallic room reflections.
PA = ("highpass=f=280,lowpass=f=4800,equalizer=f=2200:t=q:w=1.2:g=4,"
      "acompressor=threshold=-18dB:ratio=3:attack=5:release=80,"
      "aecho=0.85:0.5:23|41:0.22|0.12")


def run(args):
    subprocess.run(FF + args, check=True)


def tone(f, t0, level=1.0):
    # Fundamental plus odd harmonics (soft square) — matches the chime's strong 3rd harmonic.
    return (f"{level}*(sin(2*PI*{f}*(t-{t0}))+0.45*sin(2*PI*{3*f}*(t-{t0}))+0.12*sin(2*PI*{5*f}*(t-{t0})))"
            f"*gte(t,{t0})")


def chime(path):
    # E5 with gentle decay for 0.75 s, then C5 ringing out.
    e5 = f"{tone(659.25, 0)}*min(1,t/0.01)*exp(-0.9*t)*lt(t,0.75)"
    c5 = f"{tone(523.25, 0.75)}*min(1,(t-0.75)/0.01)*exp(-2.2*(t-0.75))"
    run(["-f", "lavfi", "-i", f"aevalsrc='0.22*({e5}+{c5})':s={SR}:d=2.0", "-ac", "1", path])


def beeps(path, n=10, on=0.05, period=0.13):
    expr = f"0.25*({tone(750, 0)})*lt(mod(t,{period}),{on})"
    run(["-f", "lavfi", "-i", f"aevalsrc='{expr}':s={SR}:d={n * period}", "-ac", "1", path])


def silence(path, secs):
    run(["-f", "lavfi", "-i", f"anullsrc=r={SR}:cl=mono", "-t", str(secs), path])


async def tts(text, voice, rate, pitch, path):
    await edge_tts.Communicate(text, voice, rate=rate, pitch=pitch).save(path)


def build(station, preset, out):
    voice, rate, pitch = PRESETS[preset]
    with tempfile.TemporaryDirectory() as d:
        p = lambda n: os.path.join(d, n)
        chime(p("chime.wav")); beeps(p("beeps.wav"))
        silence(p("s1.wav"), 0.1); silence(p("s2.wav"), 0.6); silence(p("s3.wav"), 0.35)
        asyncio.run(tts(f"Next station, {station}.", voice, rate, pitch, p("next.mp3")))
        asyncio.run(tts("Doors are closing.", voice, rate, pitch, p("doors.mp3")))
        # Trim TTS leading/trailing silence so the pacing is controlled by our own gaps.
        trim = "silenceremove=start_periods=1:start_threshold=-45dB,areverse,silenceremove=start_periods=1:start_threshold=-45dB,areverse"
        parts = ["chime.wav", "s1.wav", "next.mp3", "s2.wav", "doors.mp3", "s3.wav", "beeps.wav"]
        inputs = sum((["-i", p(x)] for x in parts), [])
        filt = "".join(
            f"[{i}:a]aresample={SR},aformat=channel_layouts=mono{',' + trim if x.endswith('.mp3') else ''}[a{i}];"
            for i, x in enumerate(parts))
        filt += "".join(f"[a{i}]" for i in range(len(parts)))
        filt += f"concat=n={len(parts)}:v=0:a=1,{PA},apad=pad_dur=0.3,loudnorm=I=-16:TP=-1.5[out]"
        run(inputs + ["-filter_complex", filt, "-map", "[out]", "-ar", SR, "-ac", "1", "-b:a", "64k", out])


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2], sys.argv[3])
