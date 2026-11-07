import sys
srt, out, size, marginv, playx, playy = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6]
def t(s):
    h,m,r=s.split(':'); sec,ms=r.split(','); x=int(h)*3600+int(m)*60+int(sec)+int(ms)/1000
    return f"{int(x//3600)}:{int(x%3600//60):02d}:{x%60:05.2f}"
blocks=open(srt,encoding='utf-8').read().strip().split('\n\n')
head=f"""[Script Info]
ScriptType: v4.00+
PlayResX: {playx}
PlayResY: {playy}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter SemiBold,{size},&H00FFFFFF,&H00FFFFFF,&H281A10,&H281A10,0,0,0,0,100,100,0,0,3,16,0,2,120,120,{marginv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=[]
for b in blocks:
    L=b.split('\n'); a,c=L[1].split(' --> '); ev.append(f"Dialogue: 0,{t(a)},{t(c)},Cap,,0,0,0,,{' '.join(L[2:])}")
open(out,'w',encoding='utf-8').write(head+'\n'.join(ev)+'\n')
