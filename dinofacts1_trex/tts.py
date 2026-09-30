import json, soundfile as sf, numpy as np
from kokoro_onnx import Kokoro
k=Kokoro('/home/user/dino/kokoro-v1.0.onnx','/home/user/dino/voices-v1.0.bin')
L=[
 "This T-Rex is as long as a school bus. Forty feet, from nose to tail!",
 "And just one tooth? As big as a banana.",
 "Meet Tyrannosaurus rex, the king of the tyrant lizards.",
 "It weighed more than an elephant, and it hunted giants, sixty-six million years ago.",
 "Its secret weapon was its nose. A huge part of its brain was made for smelling, so it could sniff out dinner from far, far away.",
 "Then... CHOMP! T-Rex had the strongest bite of any land animal ever. Strong enough to crush bone.",
 "And here's the craziest part. Stegosaurus lived so long before T-Rex, that T-Rex lived closer in time to you!",
 "Tiko is very proud of his giant family.",
 "So, which dinosaur should we explore next? Tell us in the comments!",
]
gaps=[0.9,0.7,0.9,0.9,0.9,1.0,1.0,0.8,1.8]
sr=24000; out=[np.zeros(int(0.3*sr),dtype=np.float32)]; t=0.3; timing=[]
for line,g in zip(L,gaps):
    a,sr=k.create(line,voice='am_onyx',speed=0.9,lang='en-us')
    timing.append({'start':round(t,3),'dur':round(len(a)/sr,3),'line':line})
    out+= [a.astype(np.float32), np.zeros(int(g*sr),dtype=np.float32)]
    t+=len(a)/sr+g
sf.write('narr_raw.wav',np.concatenate(out),sr)
json.dump(timing,open('timing.json','w'),indent=1)
print(round(t,2)); [print(x['start'],x['dur']) for x in timing]
