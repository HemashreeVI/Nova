#!/bin/bash
cd /home/user/JarvisAI
for p in "$@"; do
  until [ -f visuals/$p/.go ]; do sleep 15; done
  visuals/hci-exam/build.sh visuals/$p
  node .claude/skills/full-visual/scripts/render.mjs visuals/$p --no-tts --workers 3 > visuals/$p.render.log 2>&1
  touch visuals/$p/.rendered
done
