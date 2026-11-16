#!/usr/bin/env python3
"""lesson.json -> video.json + index.html (+ lesson.js copy) for full-visual."""
import json, os, shutil, sys
proj = os.path.abspath(sys.argv[1])
here = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(proj, 'lesson.json')))
keys = ['title','slug','description','tags','voice','speed','fps','captions','endCard','thumbnail','pronounce','lineGap','endHold']
vj = {k: L[k] for k in keys if k in L}
vj['scenes'] = []
for s in L['scenes']:
    d = {'id': s['id'], 'title': s.get('chapter') or s.get('title','').replace('**',''), 'lines': s['lines']}
    for k in ('pad','hold','minDur'):
        if k in s: d[k] = s[k]
    vj['scenes'].append(d)
json.dump(vj, open(os.path.join(proj, 'video.json'), 'w'), indent=1, ensure_ascii=False)
data = {'scenes': [{k: v for k, v in s.items() if k not in ('lines','pad','hold','minDur','chapter')} for s in L['scenes']]}
open(os.path.join(proj, 'lesson-data.js'), 'w').write('window.LESSON = ' + json.dumps(data, ensure_ascii=False) + ';\n')
shutil.copy(os.path.join(here, 'lesson.js'), os.path.join(proj, 'lesson.js'))
html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{L['title']}</title></head>
<body><div id="fv-stage"></div>
<script src="timing.js"></script>
<script src="fv-runtime.js"></script>
<script src="lesson-data.js"></script>
<script src="lesson.js"></script>
</body></html>
'''
open(os.path.join(proj, 'index.html'), 'w').write(html)
n = sum(len(s['lines']) for s in L['scenes']); w = sum(len(l.split()) for s in L['scenes'] for l in s['lines'])
long = [(s['id'], l) for s in L['scenes'] for l in s['lines'] if len(l.split()) > 30]
print(f"built {L['slug']}: {len(L['scenes'])} scenes, {n} lines, {w} words (~{w/150:.1f} min)")
for x in long: print('  LONG LINE', x)
