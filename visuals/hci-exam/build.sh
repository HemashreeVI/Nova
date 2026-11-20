#!/bin/bash
# usage: build.sh <projectDir>  — copies kit + page, writes spec.js from video.json
set -e
K=$(dirname "$0"); P="$1"
cp "$K/kit.js" "$K/index.html" "$P/"
node -e "const j=require(require('path').resolve('$P/video.json'));require('fs').writeFileSync('$P/spec.js','window.SPEC='+JSON.stringify({kicker:j.kicker,scenes:j.scenes.map(s=>({id:s.id,title:s.title,viz:s.viz}))})+';')"
sed -i "s#<title>.*</title>#<title>$(node -e "console.log(require(require('path').resolve('$P/video.json')).title)")</title>#" "$P/index.html"
