import json,re
T=json.load(open('timing.json')); c=json.load(open('cuts.json'))
def ts(t): h=int(t//3600); m=int(t%3600//60); s=t%60; return f"{h}:{m:02d}:{s:05.2f}"
H="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,DejaVu Sans,86,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,3,5,40,40,0,1
Style: Big,DejaVu Sans,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H90000000,-1,0,0,0,100,100,0,0,1,7,4,5,40,40,0,1
Style: Brand,DejaVu Sans,38,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,2,0,1,3,2,5,20,20,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
ev=[]
Y='{\\c&H00FFFF&}'; W='{\\c&HFFFFFF&}'
for x in T:
    words=x['line'].split(); lens=[len(re.sub(r'\W','',w))+2 for w in words]; tot=sum(lens)
    t=x['start']; wt=[]
    for w,l in zip(words,lens): d=x['dur']*l/tot; wt.append((w,t,t+d)); t+=d
    chunks=[]; cur=[]
    for w in wt:
        cur.append(w)
        if len(cur)==3 or len(' '.join(q[0] for q in cur))>=16 or re.search(r'[.,!?]$',w[0]): chunks.append(cur); cur=[]
    if cur: chunks.append(cur)
    for ch in chunks:
        for i,(w,s,e) in enumerate(ch):
            if i==len(ch)-1: e=ch[-1][2]+0.05
            txt=' '.join((Y+q[0].upper()+W) if j==i else q[0].upper() for j,q in enumerate(ch))
            ev.append(f"Dialogue: 1,{ts(s)},{ts(e)},Cap,,0,0,0,,{{\\pos(540,1330)}}{txt}")
def big(s,e,text,y=360,fs=92,col='&HFFFFFF&'):
    ev.append(f"Dialogue: 2,{ts(s)},{ts(e)},Big,,0,0,0,,{{\\pos(540,{y})\\fs{fs}\\c{col}\\fad(200,200)\\t(0,250,\\fscx112\\fscy112)\\t(250,450,\\fscx100\\fscy100)}}{text}")
big(0.2,c[1]-0.15,"T-REX vs\\NSCHOOL BUS",y=330)
big(c[1]+0.9,c[2]-0.1,"1 TOOTH = 1 BANANA",y=330,fs=84,col='&H00E5FF&')
big(c[6]+0.1,c[6]+3.9,"STEGOSAURUS → T-REX\\N80 MILLION YEARS",y=330,fs=72)
big(c[6]+4.0,c[7]-0.15,"T-REX → YOU\\N66 MILLION YEARS",y=330,fs=80,col='&H00E5FF&')
big(c[7]+0.5,57,"WHO'S NEXT?",y=330,fs=110,col='&H00E5FF&')
ev.append(f"Dialogue: 0,{ts(0)},{ts(57)},Brand,,0,0,0,,{{\\pos(540,1830)\\alpha&H40&}}DINO-EXPLORERS · DINO FACTS #1")
open('captions.ass','w').write(H+'\n'.join(ev)+'\n')
print(len(ev),'events')
