#!/bin/bash
# TTS then render each project in order, waiting for its video.json
cd /home/user/JarvisAI
for p in "$@"; do
  until [ -f visuals/$p/video.json ] && [ -f visuals/$p/.ready ]; do sleep 15; done
  python3 .claude/skills/full-visual/scripts/tts.py visuals/$p > visuals/$p.tts.log 2>&1
  touch visuals/$p/.tts_done
done
