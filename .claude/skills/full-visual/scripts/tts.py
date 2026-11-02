#!/usr/bin/env python3
"""full-visual narration builder.

Reads <project>/video.json, voices every narration line with the offline Kokoro
neural TTS model, and writes:

  <project>/timing.js          window.FV_TIMING — scene + line timings for the page
  <project>/out/timing.json    same data, for render.mjs
  <project>/out/narration.wav  the full voice track
  <project>/out/captions.srt   subtitles (upload to YouTube as closed captions)

Each line is synthesised separately, so the page knows exactly when every
sentence starts (ctx.line(i)) and animations can land on the words.
Synthesised clips are cached in out/tts/, so editing one line only re-voices that line.
"""
import hashlib
import json
import os
import re
import subprocess
import sys

import numpy as np
import soundfile as sf

MODEL_FILES = {
    "kokoro-v1.0.onnx": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx",
    "voices-v1.0.bin": "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin",
}
SR = 24000


def model_dir():
    d = os.environ.get("FV_MODEL_DIR") or os.path.expanduser("~/.cache/full-visual/kokoro")
    os.makedirs(d, exist_ok=True)
    for name, url in MODEL_FILES.items():
        p = os.path.join(d, name)
        if not os.path.exists(p) or os.path.getsize(p) == 0:
            print(f"[tts] downloading {name} …", flush=True)
            subprocess.run(["curl", "-fsSL", "-o", p + ".part", url], check=True)
            os.replace(p + ".part", p)
    return d


def chunk(text, start, end, max_words=12):
    """Split a line into caption-sized chunks, timed by character share."""
    parts = [p.strip() for p in re.split(r"(?<=[,.;:?!—])\s+", text) if p.strip()]
    out = []
    for p in parts:
        words = p.split()
        while len(words) > max_words:
            n = (len(words) + 1) // 2 if len(words) <= max_words * 2 else max_words
            out.append(" ".join(words[:n]))
            words = words[n:]
        out.append(" ".join(words))
    total = sum(len(c) for c in out) or 1
    t, res = start, []
    for c in out:
        d = (end - start) * len(c) / total
        res.append({"text": c, "start": round(t, 3), "end": round(t + d, 3)})
        t += d
    return res


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}"


def main():
    proj = os.path.abspath(sys.argv[1])
    cfg = json.load(open(os.path.join(proj, "video.json")))
    voice = cfg.get("voice", "am_michael")
    speed = float(cfg.get("speed", 1.0))
    lang = cfg.get("lang", "en-us")
    gap = float(cfg.get("lineGap", 0.35))
    out = os.path.join(proj, "out")
    cache = os.path.join(out, "tts")
    os.makedirs(cache, exist_ok=True)

    kokoro = None

    def synth(text):
        nonlocal kokoro
        key = hashlib.sha1(f"{voice}|{speed}|{lang}|{text}".encode()).hexdigest()[:16]
        p = os.path.join(cache, key + ".wav")
        if not os.path.exists(p):
            if kokoro is None:
                from kokoro_onnx import Kokoro
                d = model_dir()
                kokoro = Kokoro(os.path.join(d, "kokoro-v1.0.onnx"), os.path.join(d, "voices-v1.0.bin"))
            print(f"[tts] {text[:70]}", flush=True)
            samples, sr = kokoro.create(text, voice=voice, speed=speed, lang=lang)
            assert sr == SR, sr
            sf.write(p, samples, SR)
        s, _ = sf.read(p, dtype="float32")
        # trim near-silent edges so line timings are tight
        idx = np.where(np.abs(s) > 0.01)[0]
        if len(idx):
            s = s[max(0, idx[0] - int(0.03 * SR)): idx[-1] + int(0.08 * SR)]
        return s

    clips, scenes, t = [], [], 0.0
    for sc in cfg["scenes"]:
        lead, tail = sc.get("pad", [0.5, 0.9])
        cur, lines = float(lead), []
        for i, txt in enumerate(sc.get("lines", [])):
            s = synth(txt)
            d = len(s) / SR
            lines.append({"text": txt, "start": round(cur, 3), "end": round(cur + d, 3),
                          "chunks": chunk(txt, cur, cur + d)})
            clips.append((t + cur, s))
            cur += d + (gap if i < len(sc["lines"]) - 1 else 0)
        dur = max(cur + float(tail) + float(sc.get("hold", 0)), float(sc.get("minDur", 0)))
        scenes.append({"id": sc["id"], "title": sc.get("title", sc["id"]), "start": round(t, 3),
                       "dur": round(dur, 3), "lines": lines})
        t += dur
    total = round(t + float(cfg.get("endHold", 0.5)), 3)

    audio = np.zeros(int(total * SR) + SR, dtype=np.float32)
    for off, s in clips:
        i = int(off * SR)
        audio[i:i + len(s)] += s
    peak = float(np.max(np.abs(audio))) or 1.0
    audio *= 0.89 / peak
    sf.write(os.path.join(out, "narration.wav"), audio[: int(total * SR)], SR)

    timing = {"title": cfg.get("title", ""), "total": total, "captions": bool(cfg.get("captions", True)),
              "scenes": scenes}
    json.dump(timing, open(os.path.join(out, "timing.json"), "w"), indent=1)
    with open(os.path.join(proj, "timing.js"), "w") as f:
        f.write("window.FV_TIMING = " + json.dumps(timing) + ";\n")

    n, srt = 1, []
    for sc in scenes:
        for ln in sc["lines"]:
            for c in ln["chunks"]:
                srt.append(f"{n}\n{srt_time(sc['start'] + c['start'])} --> {srt_time(sc['start'] + c['end'])}\n{c['text']}\n")
                n += 1
    open(os.path.join(out, "captions.srt"), "w").write("\n".join(srt))
    print(f"[tts] {len(scenes)} scenes, {total:.1f}s total", flush=True)


if __name__ == "__main__":
    main()
