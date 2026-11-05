#!/usr/bin/env python3
"""Build the 16:9 "AI Explained" compilation for YouTube.

  intro card → Part 1 (full horizontal video) → Parts 2-4 (vertical Shorts beside a synced
  key-points panel) with a chapter card before each part → outro card.

Needs the four source videos rendered first (visuals/*/out/*.mp4).
Output: visuals/ai-explained/out/ai-explained.mp4, thumbnail.png, youtube.txt
"""
import json
import os
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.dirname(HERE)
ROOT = os.path.dirname(V)
OUT = os.path.join(HERE, "out")
RENDER = os.path.join(ROOT, ".claude/skills/full-visual/scripts/render.mjs")
FF = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y"]
ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", "30",
       "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "1"]

SRC = {
    1: f"{V}/how-ai-handles-a-prompt/out/how-ai-handles-a-prompt.mp4",
    2: f"{V}/short-ai-images/out/short-ai-images.mp4",
    3: f"{V}/short-rag/out/short-rag.mp4",
    4: f"{V}/short-ai-agents/out/short-ai-agents.mp4",
}
# chapter-card thumbnails: (time, crop) per part
FRAMES = {1: (99.7, None), 2: (30.9, "1080:608:0:495"), 3: (35.2, "1080:608:0:600"), 4: (16.9, "1080:608:0:555")}
PANELS = {
    2: dict(short="short-ai-images", kicker="PART 2", title="How AI creates images", color="#e879f9", bullets=[
        ("Training: add noise to millions of images", "train"),
        ("The model learns to predict the noise", "learn"),
        ("Generate: remove noise, step by step", "generate"),
        ("Your prompt guides every step", "prompt"),
        ("Latent space keeps it fast", "latent")]),
    3: dict(short="short-rag", kicker="PART 3", title="How AI reads your documents (RAG)", color="#2dd4bf", bullets=[
        ("Models only know their training data", "problem"),
        ("Chunk documents & embed them in a vector DB", "chunk"),
        ("Retrieve the chunks closest to your question", "retrieve"),
        ("Augment: paste them into the prompt", "augment"),
        ("Generate an answer, with sources", "generate")]),
    4: dict(short="short-ai-agents", kicker="PART 4", title="How AI agents take action", color="#a3e635", bullets=[
        ("An LLM in a loop: think, act, observe", "loop"),
        ("Tools: search, calculator, calendar, code", "tools"),
        ("It writes a tool request; your app runs it", "call"),
        ("Example: plan a trip under $500", "example"),
        ("Good agents ask before risky actions", "safety")]),
}


def run(*a):
    subprocess.run(list(a), check=True)


def dur(f):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f]).decode())


def main():
    os.makedirs(OUT, exist_ok=True)
    frames = os.path.join(HERE, "cards", "frames")
    os.makedirs(frames, exist_ok=True)

    # 1. chapter thumbnails from the source videos
    for n, (t, crop) in FRAMES.items():
        vf = (f"crop={crop}," if crop else "") + "scale=960:540"
        run(*FF, "-ss", str(t), "-i", SRC[n], "-frames:v", "1", "-vf", vf, "-q:v", "3", os.path.join(frames, f"p{n}.jpg"))

    # 2. intro / chapter / outro cards (narrated)
    run("node", RENDER, os.path.join(HERE, "cards"))
    cards = os.path.join(HERE, "cards", "out")
    ctiming = json.load(open(os.path.join(cards, "timing.json")))
    cmp4 = os.path.join(cards, "ai-explained-cards.mp4")
    seg = {}
    for s in ctiming["scenes"]:
        f = os.path.join(OUT, f"seg_{s['id']}.mp4")
        run(*FF, "-ss", f"{s['start']:.3f}", "-t", f"{s['dur']:.3f}", "-i", cmp4, *ENC, f)
        seg[s["id"]] = f

    # 3. part 1: the full horizontal video
    seg["part1"] = os.path.join(OUT, "seg_part1.mp4")
    run(*FF, "-i", SRC[1], *ENC, seg["part1"])

    # 4. parts 2-4: Short + synced key-points panel
    for n, cfg in PANELS.items():
        sdir = f"{V}/{cfg['short']}/out"
        st = json.load(open(os.path.join(sdir, "timing.json")))
        starts = {s["id"]: (s["start"], s["start"] + s["dur"]) for s in st["scenes"]}
        pdir = os.path.join(OUT, f"panel-{n}")
        os.makedirs(os.path.join(pdir, "out"), exist_ok=True)
        shutil.copy(os.path.join(HERE, "panel", "index.html"), pdir)
        json.dump({"slug": f"panel-{n}"}, open(os.path.join(pdir, "video.json"), "w"))
        panel = dict(part=n, kicker=cfg["kicker"], title=cfg["title"], color=cfg["color"],
                     bullets=[[txt, *starts[sid]] for txt, sid in cfg["bullets"]])
        open(os.path.join(pdir, "panel.js"), "w").write("window.PANEL = " + json.dumps(panel) + ";\n")
        timing = {"title": "", "total": st["total"], "captions": False, "endCard": "", "width": 1920, "height": 1080,
                  "scenes": [{"id": "all", "title": "", "start": 0, "dur": st["total"], "lines": []}]}
        json.dump(timing, open(os.path.join(pdir, "out", "timing.json"), "w"))
        open(os.path.join(pdir, "timing.js"), "w").write("window.FV_TIMING = " + json.dumps(timing) + ";\n")
        shutil.copy(os.path.join(sdir, "narration.wav"), os.path.join(pdir, "out", "narration.wav"))
        run("node", RENDER, pdir, "--no-tts")
        f = os.path.join(OUT, f"seg_part{n}.mp4")
        run(*FF, "-i", os.path.join(pdir, "out", f"panel-{n}.mp4"), "-i", SRC[n],
            "-filter_complex", "[1:v]scale=576:1024[s];[0:v][s]overlay=150:28[v]", "-map", "[v]", "-map", "1:a",
            *ENC, "-shortest", f)
        seg[f"part{n}"] = f

    # 5. concat
    order = ["intro", "ch1", "part1", "ch2", "part2", "ch3", "part3", "ch4", "part4", "outro"]
    lst = os.path.join(OUT, "concat.txt")
    open(lst, "w").write("".join(f"file '{seg[k]}'\n" for k in order))
    final = os.path.join(OUT, "ai-explained.mp4")
    run(*FF, "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", "-movflags", "+faststart", final)

    # 6. chapters + thumbnail
    t, marks = 0.0, {}
    for k in order:
        marks[k] = t
        t += dur(seg[k])
    ts = lambda x: f"{int(x // 60)}:{int(x % 60):02d}"
    chapters = [(0, "Intro"), (marks["ch1"], "Part 1: How AI answers your prompt"), (marks["ch2"], "Part 2: How AI creates images"),
                (marks["ch3"], "Part 3: How AI reads your documents (RAG)"), (marks["ch4"], "Part 4: How AI agents take action"),
                (marks["outro"], "Recap")]
    open(os.path.join(OUT, "chapters.txt"), "w").write("\n".join(f"{ts(a)} {b}" for a, b in chapters) + "\n")
    intro = next(s for s in ctiming["scenes"] if s["id"] == "intro")
    run(*FF, "-ss", f"{intro['dur'] - 0.4:.2f}", "-i", seg["intro"], "-frames:v", "1", "-vf", "scale=1280:720", os.path.join(OUT, "thumbnail.png"))
    print(f"done → {final} ({t:.1f}s)")
    print(open(os.path.join(OUT, "chapters.txt")).read())


if __name__ == "__main__":
    main()
