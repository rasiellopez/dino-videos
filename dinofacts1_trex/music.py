import json, numpy as np, pretty_midi as pm, soundfile as sf, subprocess
T=json.load(open('timing.json')); st=[x['start'] for x in T]
cut=[0]+[st[i]-0.15 for i in range(1,8)]+[57.0]   # 8 escenas
json.dump(cut,open('cuts.json','w'))
BPM=100; b=60/BPM; END=57.0
m=pm.PrettyMIDI(initial_tempo=BPM)
def inst(p,drum=False): i=pm.Instrument(program=p,is_drum=drum); m.instruments.append(i); return i
strings=inst(48); pizz=inst(45); horn=inst(60); brass=inst(61); timp=inst(47); celes=inst(8); bass=inst(43); drums=inst(0,True)
def n(i,p,s,d,v=80):
    if s<END: i.notes.append(pm.Note(v,p,s,min(s+d,END)))
D=[62,66,69]; G=[55,59,62]; A=[57,61,64]; Bm=[59,62,66]; Em=[52,55,59]
prog=[D,G,A,D,Bm,G,A,A]
def pad(s,e,v=55,oct=0):
    t=s;k=0
    while t<e:
        c=prog[k%len(prog)]
        for p in c: n(strings,p-12+oct,t,min(4*b,e-t),v)
        n(bass,c[0]-24,t,min(4*b,e-t),v+5); t+=4*b; k+=1
c=cut
# 1 bus: pasos con timbal
t=0.4
while t<c[1]: n(timp,38,t,0.5,110); n(drums,36,t,0.2,100); t+=1.2
pad(0,c[1],45)
# 2-3 dientes + intro: pizzicato juguetón
t=c[1]; k=0; mel=[74,78,81,78,76,79,83,79,74,78,81,86]
while t<c[3]: n(pizz,mel[k%12],t,b/2,85); n(pizz,mel[k%12]-24,t,b/2,70) if k%2==0 else None; t+=b/2; k+=1
pad(c[2],c[3],50)
# 4-6 aventura con trompa
pad(c[3],c[6],62)
hm=[(62,2),(66,1),(69,1),(74,3),(71,1),(69,2),(67,2),(66,4),(64,2),(66,1),(67,1),(69,3),(74,1),(73,4),(69,4)]
t=c[3]+0.2
while t<c[5]:
    for p,d in hm:
        if t>=c[5]: break
        n(horn,p,t,d*b*0.95,88); t+=d*b
t=c[3]
while t<c[6]: n(drums,42,t,0.1,55); n(drums,36,t,0.1,70) if int((t-c[3])/b)%2==0 else None; t+=b
# golpes en la mordida
for s in [c[5]+0.3,c[5]+0.3+b,c[5]+2.5,c[5]+2.5+b/2]:
    for p in [38,50]: n(brass,p,s,0.6,120)
    n(timp,38,s,0.8,127); n(drums,49,s,1,110)
# 7 misterio en estego: celesta + cuerdas graves
t=c[6]
for p in [74,77,81,77,74,72,76,79,76,72,69,74]*2:
    if t>=c[7]: break
    n(celes,p,t,b*0.9,70); t+=b*0.75
for p in [50,53,57]: n(strings,p,c[6],c[7]-c[6],50)
# 8 final con metales
t=c[7]
for ch,d in [(D,2),(G,2),(A,2),(Bm,2),(G,2),(A,2),(D,4),(D,4)]:
    for p in ch: n(brass,p,t,d*b*0.95,95); n(strings,p-12,t,d*b,70)
    n(bass,ch[0]-24,t,d*b,80); n(timp,38,t,0.4,100); t+=d*b
m.write('score.mid')
subprocess.run(['fluidsynth','-ni','-g','0.8','-r','48000','-F','score_raw.wav','/usr/share/sounds/sf2/FluidR3_GM.sf2','score.mid'],check=True,capture_output=True)

# ---- FX ----
sr=48000; N=int(END*sr); fx=np.zeros(N,np.float32); rng=np.random.default_rng(7)
def add(s,x,g=1.0):
    i=int(s*sr); x=x[:N-i]; fx[i:i+len(x)]+=g*x
def env(L,a,d): t=np.arange(L)/sr; return np.minimum(t/a,1)*np.exp(-t/d)
def boom(d=1.2):
    L=int(d*sr); t=np.arange(L)/sr; f=55*np.exp(-t*2)+30
    return (np.sin(2*np.pi*np.cumsum(f)/sr)*env(L,0.005,0.35)).astype(np.float32)
def pop():
    L=int(0.12*sr); t=np.arange(L)/sr; f=900-5000*t
    return (np.sin(2*np.pi*np.cumsum(f)/sr)*env(L,0.002,0.03)).astype(np.float32)
def lp(x,a): 
    y=np.zeros_like(x); acc=0.0
    for i in range(len(x)): acc+=a*(x[i]-acc); y[i]=acc
    return y
def whoosh(d=0.7):
    L=int(d*sr); t=np.arange(L)/sr; w=rng.standard_normal(L).astype(np.float32)
    w=np.diff(np.concatenate([[0],w])); return (w*np.sin(np.pi*t/d)**2*0.25).astype(np.float32)
def roar(d=2.2):
    L=int(d*sr); t=np.arange(L)/sr; w=rng.standard_normal(L)
    base=70+25*np.sin(2*np.pi*3*t); saw=((np.cumsum(base)/sr)%1-0.5)
    x=lp(w*0.6+saw*1.5,0.04)*(1+0.5*np.sin(2*np.pi*23*t))
    x=x*np.minimum(t/0.25,1)*np.minimum((d-t)/0.6,1); return (x/np.abs(x).max()).astype(np.float32)
t=0.4
while t<c[1]: add(t,boom(),0.9); t+=1.2
for i in range(11): add(c[1]+0.95+i*0.11,pop(),0.5)
for s in c[1:8]: add(s-0.35,whoosh(),0.6)
add(c[2]+0.4,roar(2.4),0.55); add(c[5]+0.1,roar(1.8),0.7); add(c[5]+0.3,boom(1.5),1.0); add(c[5]+2.5,boom(1.5),1.0)
sf.write('fx.wav',np.stack([fx,fx],1)*0.8,sr)
subprocess.run(['ffmpeg','-y','-loglevel','error','-i','score_raw.wav','-af','aecho=0.8:0.5:60|120:0.3|0.2,highpass=f=35,loudnorm=I=-20','-ar','48000','-ac','2','-t',str(END),'music.wav'],check=True)
print('cuts',[round(x,2) for x in cut])
