import sys, json, math, subprocess, numpy as np, cv2
IMG=sys.argv[2] if len(sys.argv)>2 else '/home/user/dino/img'
name=sys.argv[1]; c=json.load(open('cuts.json')); FPS=30; W,H=1080,1920; SW,SH=944,1680
order=['bus','teeth','intro','stalk','nose','bite','stego','tiko']; i=order.index(name)
dur=c[i+1]-c[i]+(0.3 if i<7 else 0)
src=cv2.resize(cv2.imread(f'{IMG}/{name}.jpg'),(SW,SH),interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
ease=lambda u:0.5-0.5*math.cos(math.pi*min(max(u,0),1))
# (zoom0,zoom1,cx0,cy0,cx1,cy1)
KB={'bus':(1.0,1.08,.5,.55,.45,.55),'teeth':(1.02,1.08,.6,.55,.66,.57),'intro':(1.18,1.0,.5,.45,.5,.5),
    'stalk':(1.15,1.15,.58,.5,.42,.5),'nose':(1.0,1.22,.5,.5,.5,.42),'bite':(1.05,1.16,.5,.4,.5,.36),
    'stego':(1.14,1.14,.4,.5,.6,.5),'tiko':(1.0,1.1,.5,.55,.5,.5)}[name]
SPOTS=[(545,800,-80,95),(605,790,-85,100),(672,772,-95,105),(735,842,-90,100),(778,852,-95,95),(826,820,-100,90),(866,772,-100,80),(500,1060,85,80),(542,1098,80,85),(584,1130,80,85),(622,1138,75,80)]
if name=='teeth':
    ban=cv2.imread(f'{IMG}/banana.png',cv2.IMREAD_UNCHANGED)
    ys,xs=np.where(ban[:,:,3]>10); ban=ban[ys.min():ys.max()+1,xs.min():xs.max()+1]
def paste(img,spr,x,y,ang,length,s):
    if s<=0.01: return
    sc=length*s/spr.shape[1]; h,w=spr.shape[:2]
    M=cv2.getRotationMatrix2D((w/2,h/2),-ang,sc); M[0,2]+=x-w/2; M[1,2]+=y-h/2
    r=cv2.warpAffine(spr,M,(SW,SH),flags=cv2.INTER_LINEAR,borderValue=(0,0,0,0)).astype(np.float32)
    a=r[:,:,3:4]/255.; img[:]=img*(1-a)+r[:,:,:3]*a
def shake(t,hits,amp,dec=6):
    dx=dy=0
    for h0 in hits:
        u=t-h0
        if u>=0: e=amp*math.exp(-u*dec); dx+=e*math.sin(u*55); dy+=e*math.cos(u*47)
    return dx,dy
p=subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-',
   '-c:v','libx264','-preset','medium','-crf','16','-pix_fmt','yuv420p',f'scene_{name}.mp4'],stdin=subprocess.PIPE)
N=int(round(dur*FPS)); base=W/SW
for f in range(N):
    t=f/FPS; u=ease(t/dur); z0,z1,x0,y0,x1,y1=KB; z=z0+(z1-z0)*u; cx=(x0+(x1-x0)*u)*SW; cy=(y0+(y1-y0)*u)*SH
    img=src
    if name=='teeth':
        img=src.copy()
        for k,(x,y,a,l) in enumerate(SPOTS):
            v=(t-(0.95+k*0.11))/0.16; s=0 if v<0 else (1.25*math.sin(v*math.pi/2) if v<1 else 1+0.25*math.exp(-(v-1)*3)*math.cos((v-1)*6))
            paste(img,ban,x,y,a,l,s)
    dx=dy=0
    if name=='bus': dx,dy=shake(t,[0.4+1.2*k for k in range(6)],14,7)
    if name=='bite': dx,dy=shake(t,[0.3,2.5],28,4)
    if name=='tiko': dy=6*math.sin(t*2.2)
    s=base*z; half_w=W/(2*s); half_h=H/(2*s)
    cx=min(max(cx,half_w),SW-half_w); cy=min(max(cy,half_h),SH-half_h)
    M=np.float32([[s,0,W/2-s*cx+dx],[0,s,H/2-s*cy+dy]])
    fr=cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
    p.stdin.write(np.clip(fr,0,255).astype(np.uint8).tobytes())
p.stdin.close(); p.wait(); print(name,N,'frames')
