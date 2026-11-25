import numpy as np, subprocess, sys, os, math
from PIL import Image, ImageDraw, ImageFont
from sim import run, L, VMAX
XS,VS=[],[]
for s in (0,1):
    X,V=run(s); XS.append(X); VS.append(V)
STEPS=XS[0].shape[0]-1; NF=1050
F="/usr/share/fonts/truetype/dejavu/"
def ft(n,s): return ImageFont.truetype(F+n,s)
BG=(14,17,23);ACC=(255,184,0);CY=(64,224,208);WH=(235,235,228);RED=(255,80,80);GR=(130,135,145)
C=[(540,700),(540,1440)]; R=290
fS=ft("DejaVuSansMono-Bold.ttf",40); fT=ft("DejaVuSans-Bold.ttf",58); fL=ft("DejaVuSans-Bold.ttf",42); fC=ft("DejaVuSansMono-Bold.ttf",38); fs=ft("DejaVuSansMono.ttf",28)
KMH=27  # 1 cell/step = 7.5 m/s
def ctext(d,y,t,f,c): d.text(((1080-d.textlength(t,font=f))/2,y),t,font=f,fill=c)
def header(d):
    ctext(d,60,"EXPERIMENT 002",fS,ACC)
    ctext(d,125,"Why do traffic jams",fT,WH); ctext(d,195,"appear from nowhere?",fT,WH)
def scol(v):
    t=v/VMAX
    if t<0.5: a,b,u=RED,ACC,t/0.5
    else: a,b,u=ACC,CY,(t-0.5)/0.5
    return tuple(int(a[i]+(b[i]-a[i])*u) for i in range(3))
def state(k,f):
    s=f*STEPS/NF; i=min(int(s),STEPS-1); fr=s-i
    x0=XS[k][i].astype(float); x1=XS[k][i+1].astype(float)
    x1=np.where(x1<x0,x1+L,x1)
    return x0+(x1-x0)*fr, VS[k][i+1], i+1
def frame(f,counters=True):
    im=Image.new("RGB",(1080,1920),BG); d=ImageDraw.Draw(im,"RGBA"); header(d)
    for k in range(2):
        cx,cy=C[k]
        d.ellipse([cx-R-28,cy-R-28,cx+R+28,cy+R+28],outline=(255,255,255,30),width=56)
        d.ellipse([cx-R,cy-R,cx+R,cy+R],outline=(255,255,255,25),width=2)
        x,v,i=state(k,f)
        for xx,vv in zip(x,v):
            a=2*math.pi*xx/L-math.pi/2; a2=a+2*math.pi*2.2/L
            p=[(cx+(R)*math.cos(t),cy+(R)*math.sin(t)) for t in (a,a2)]
            d.line(p,fill=scol(vv),width=22)
        lab=["NORMAL DRIVERS","LOOK-AHEAD DRIVERS"][k]; col=[WH,CY][k]
        ty=cy-R-110
        d.text((60,ty),lab,font=fL,fill=col)
        if counters:
            lo=max(1,i-15); sp=VS[k][lo:i+1].mean()*KMH
            st=(VS[k][i]==0).sum()
            t1=f"{sp:3.0f} km/h avg"; d.text((cx-d.textlength(t1,font=fC)/2,cy-30),t1,font=fC,fill=col)
            t2=f"{st} cars stopped"; d.text((cx-d.textlength(t2,font=fs)/2,cy+22),t2,font=fs,fill=RED if st else GR)
    return im,d
def enc(name,frames):
    tmp=name+".tmp.mp4"
    pr=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s","1080x1920","-r","30","-i","-","-c:v","libx264","-crf","23","-preset","veryfast","-pix_fmt","yuv420p",tmp],stdin=subprocess.PIPE)
    for im in frames: pr.stdin.write(im.tobytes())
    pr.stdin.close(); assert pr.wait()==0; os.rename(tmp,name)
INTRO=[(0,"48 cars. One ring road.",WH),(28,"No accidents. No roadworks.",WH),(56,"Top: normal drivers.",WH),(80,"Bottom: they look ahead",CY),(98,"and never overbrake.",CY)]
def intro():
    for f in range(120):
        im,d=frame(0,counters=False)
        im=Image.alpha_composite(im.convert("RGBA"),Image.new("RGBA",im.size,(14,17,23,205))); d=ImageDraw.Draw(im); header(d)
        for n,(st,t,c) in enumerate(INTRO):
            if f>=st: ctext(d,790+n*95,t,ft("DejaVuSans-Bold.ttf",60),c+(min(255,(f-st)*20),))
        yield im.convert("RGB")
def main():
    for f in range(NF):
        im,d=frame(f)
        d.text((60,1884),"~10x speed",font=fs,fill=GR)
        yield im
SP=[VS[k][60:].mean()*KMH for k in (0,1)]; STP=[(VS[k][60:]==0).mean()*100 for k in (0,1)]
def outro():
    for f in range(180):
        im,d=frame(NF-1)
        im=Image.alpha_composite(im.convert("RGBA"),Image.new("RGBA",im.size,(14,17,23,min(240,f*12)))); d=ImageDraw.Draw(im); header(d)
        if f>8:
            ctext(d,430,"RESULT",fS,ACC)
            ctext(d,510,f"Normal: {SP[0]:.0f} km/h avg",ft("DejaVuSans-Bold.ttf",58),WH)
            ctext(d,600,f"Look-ahead: {SP[1]:.0f} km/h avg",ft("DejaVuSans-Bold.ttf",58),CY)
            ctext(d,700,f"Standing still: {STP[0]:.0f}% vs {STP[1]:.0f}% of the time",ft("DejaVuSans.ttf",40),GR)
        if f>45:
            for n,t in enumerate(["One driver brakes a bit too hard.","The car behind brakes harder.","Ten cars later, someone stops.","That's the whole jam."]):
                ctext(d,830+n*72,t,ft("DejaVuSans.ttf",48),WH)
        if f>100:
            ctext(d,1220,"Leave a gap. Look further ahead.",ft("DejaVuSans-Bold.ttf",52),CY)
            ctext(d,1360,"What should I test next?",ft("DejaVuSans-Bold.ttf",56),ACC)
            ctext(d,1440,"Comment below.",ft("DejaVuSans.ttf",50),WH)
        yield im.convert("RGB")
if __name__=="__main__":
    if sys.argv[1]=="still":
        frame(600)[0].save("still_mid.png"); list(intro())[-1].save("still_in.png"); list(outro())[-1].save("still_out.png")
        print(SP,STP)
    else:
        enc("s1.mp4",intro()); enc("s2.mp4",main()); enc("s3.mp4",outro())
