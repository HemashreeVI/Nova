---
name: full-visual
description: Turn any "explain how X works" prompt into a narrated, animated explainer video (1080p MP4 with neural voice-over, burned-in captions, SRT subtitles, thumbnail and YouTube description with chapters) plus a playable web page. Use when the user types /full-visual, or asks for an animated explainer, an explainer video, a YouTube video explaining a concept, or "visualize how X works".
argument-hint: <topic to explain, e.g. "how a touchscreen works">
---

# /full-visual — narrated animated explainer videos

Topic: **$ARGUMENTS**

You produce a YouTube-ready video by writing **one HTML page whose scenes are pure functions of time**,
voicing a script with an offline neural TTS model, and stepping the page frame by frame in headless
Chromium. Everything lives in `visuals/<slug>/`.

```
.claude/skills/full-visual/
  runtime/fv-runtime.js   timeline engine (scene fades, captions, live preview player, FV.seek for rendering)
  scripts/tts.py          video.json → narration.wav, timing.js, captions.srt   (Kokoro TTS, cached per line)
  scripts/render.mjs      tts → stills or full render → out/<slug>.mp4, thumbnail.png, youtube.txt
  template/               starter video.json + index.html
```

Requirements: `python3` with `pip install kokoro-onnx soundfile` (≈350 MB model auto-downloads to
`~/.cache/full-visual/kokoro`), `ffmpeg`, and Node with `playwright` (Chromium).

## Workflow

1. **Understand the topic** well enough to be correct. Pick a concrete running example
   (one prompt, one finger touch, one packet…) and follow it through the whole video.

2. **Write the script** — `visuals/<slug>/video.json` (copy `template/video.json`):
   - 8–14 scenes, 2–4 minutes total. One idea per scene. Scene 1 hooks with a question; the last recaps.
   - `lines`: short spoken sentences (≤ 25 words). Each line is voiced separately, so its exact start time
     is available to the page as `ctx.line(i)` — this is how animations land on the words.
   - Write for the ear: no symbols, no abbreviations the voice can't read, spell numbers as words when unclear.
   - `title` of each scene becomes a YouTube chapter. Top-level `title`, `description`, `tags` go to `youtube.txt`.
   - Voices: `am_michael` (default, warm male), `am_adam`, `af_heart`, `af_bella`, `bf_emma` (British), `bm_george`.
     `speed` 0.9–1.1. `pad: [lead, tail]` seconds around a scene's narration; `hold` adds extra seconds.

3. **Build the page** — `visuals/<slug>/index.html` (copy `template/index.html`):
   - Fixed 1920×1080 stage `#fv-stage`; one `<section class="fv-scene" data-scene="<id>">` per scene id.
   - Register `FV.scene(id, (t, ctx) => { … })`. `t` = seconds since the scene started.
     `ctx.line(i)`/`ctx.lineEnd(i)` = narration line timings; `ctx.dur` = scene length.
   - **Everything must be a pure function of `t`.** No CSS animations/transitions, no `setTimeout`, no
     `Math.random` (use `FV.rand(seed)`), no state carried between frames. The renderer seeks to arbitrary times.
   - Helpers: `FV.seg(t,a,b,ease)` 0→1 progress, `FV.pulse(t,a,b)` 0→1→0, `FV.enter(el,t,start)` fade+rise,
     `FV.css(el,{o,x,y,s,r,...style})`, `FV.type(text,p)` typewriter, `FV.lerp`, `FV.clamp`, `FV.ease.{in,out,inOut,back}`.
   - Tie animation beats to narration: `ctx.line(1) + (ctx.lineEnd(1)-ctx.line(1)) * 0.6` = 60 % through line 2.
   - Design: dark background, Inter / JetBrains Mono, ≥ 24 px text, big readable diagrams, a consistent color per
     concept. Keep the bottom ~170 px clear for captions. Show *mechanisms* (things moving, splitting, flowing),
     not bullet lists. Label illustrative numbers as illustrative.
   - SVG for lines/arcs/graphs, HTML for chips/panels. Measure layout with `offsetLeft/offsetWidth` (not
     `getBoundingClientRect`, which is scaled in preview).

4. **Check stills before rendering** — fast feedback loop:
   ```bash
   node .claude/skills/full-visual/scripts/render.mjs visuals/<slug> --stills all
   node .claude/skills/full-visual/scripts/render.mjs visuals/<slug> --no-tts --stills "tokens@3.5,loop,42"
   ```
   Specs: `sceneId` (60 % in), `sceneId@seconds`, or absolute seconds. PNGs land in `out/stills/` — **look at
   them** (Read the images) and fix overlaps, clipping, empty frames, and caption collisions. Also check
   transitional moments (mid-animation), not just settled states. Page errors are printed to the console.

5. **Render**:
   ```bash
   node .claude/skills/full-visual/scripts/render.mjs visuals/<slug>
   ```
   ≈ 1–2 min of rendering per minute of video on 4 cores. Outputs in `visuals/<slug>/out/`:
   `<slug>.mp4` (H.264 1080p30 + AAC), `thumbnail.png` (1280×720, frame chosen by `thumbnail` in video.json),
   `captions.srt`, `youtube.txt` (title, description, chapters, tags).
   Spot-check the MP4 by extracting a few frames with ffmpeg and confirming duration/audio with ffprobe.

6. **Deliver**: send the MP4, thumbnail, SRT and youtube.txt to the user. The project folder (index.html +
   timing.js + fv-runtime.js + narration.mp3) is also a self-contained interactive page with a play bar —
   open it in a browser to preview with sound.

## Notes
- Re-running only re-voices lines whose text changed (cache in `out/tts/`). Use `--no-tts` when only the page changed.
- `captions: false` in video.json disables burned-in captions (upload `captions.srt` to YouTube instead).
- `out/` is git-ignored; commit `video.json` and `index.html` only.
- Example project: `visuals/how-ai-handles-a-prompt/`.
