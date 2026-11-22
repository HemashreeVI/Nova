# Kling AI prompts for the GitHub profile README

Shared style: dark background, purple–cyan neon, calm and cinematic.

---

## 1. Header banner (text to video)

**Settings:** text to video · 16:9 · 5 s · 1080p · 1 output
**Use:** crop to about 1280×320 and convert to a looping GIF

**Prompt:**

> Slow, steady dolly push-in through a dark futuristic digital landscape at night. Glowing purple and cyan grid lines stretch to a distant horizon, and soft particles of light drift upward like fireflies. Thin streams of light pulse along the grid toward the center, where a faint glow rises. Light haze and volumetric fog, deep navy-black sky, subtle stars. Calm, cinematic and minimal. The main action stays in the middle horizontal band of the frame. One smooth forward camera move, no cuts. The last frame matches the first so it loops seamlessly.

**Negative / exclusions:** no text, letters, logos, people, watermarks, flicker, or sudden camera shake.

**Alternatives with the same style:**

- **Code galaxy:** glowing lines of light swirl slowly into a spiral galaxy of purple and cyan stars, with a slow orbit camera move.
- **Desk at night:** a wide shot of a minimal developer desk by a rainy window, a monitor glowing cyan, rain streaks catching purple neon, and a static camera with only the rain and steam moving.

---

## 2. Animated avatar (image to video)

**Settings:** image to video · your photo or avatar as the **first frame** · keep its framing (square crop to 1:1 first) · 5 s · 1080p · 1 output
**Use:** loop it as a small GIF (about 200 px) next to your intro line

**Prompt:**

> The person in the image looks up toward the camera, gives a warm, natural smile and a small friendly wave with one hand, then lowers the hand and settles back into the original pose. Gentle purple and cyan rim light glows softly behind them, and a few light particles drift slowly in the background. The camera stays static. Keep the face, hairstyle, clothing and identity exactly as in the image. Smooth, natural motion. The final pose returns to match the first frame for a seamless loop.

**Negative / exclusions:** no change to the face or identity, no extra people, no text, no distorted hands, no fast motion.

**Calmer version (if the wave looks odd):**

> The person in the image blinks, smiles and gives a slight nod, then settles back into the original pose. Soft purple and cyan rim light, a few drifting light particles, static camera. Keep the face and identity exactly as in the image. The final pose matches the first frame for a seamless loop.

**Tips:**

- A clear, front-facing, well-lit photo works best. An illustrated or 3D avatar also works and often looks cleaner.

---

## Converting to a looping GIF (ffmpeg)

Banner (crop the center strip to 1280×320):

```bash
ffmpeg -i banner.mp4 -vf "scale=1280:-1,crop=1280:320,fps=15,split[a][b];[a]palettegen[p];[b][p]paletteuse" -loop 0 banner.gif
```

Avatar (square, 200 px):

```bash
ffmpeg -i avatar.mp4 -vf "crop='min(iw,ih)':'min(iw,ih)',scale=200:200,fps=15,split[a][b];[a]palettegen[p];[b][p]paletteuse" -loop 0 avatar.gif
```

Keep each GIF under about 5 MB.
