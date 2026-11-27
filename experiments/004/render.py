import numpy as np, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
from sim import run, burned, EMPTY, TREE, FIRE, ASH
SEED=3; DENS=[0.55,0.65]
S=[run(d,SEED) for d in DENS]; TREES=[(s[0]!=EMPTY).sum() for s in S]
MAXS=max(len(s) for s in S)-1; NF=720
F="/usr/share/fonts/truetype/dejavu/"
def ft(n,s): return ImageFont.truetype(F+n,s)
BG=(14,17,23);ACC=(255,184,0);CY=(64,224,208);WH=(235,235,228);RED=(255,80,80);GR=(130,135,145)
fS=ft("DejaVuSansMono-Bold.ttf",38);fT=ft("DejaVuSans-Bold.ttf",56);fL=ft("DejaVuSans-Bold.ttf",40);fP=ft("DejaVuSansMono-Bold.ttf",44);fs=ft("DejaVuSansMono.ttf",28)
PY=[310,1110]; X0=90; SC=5
rng=np.random.default_rng(1)
H,W=S[0].shape[1:]
green=np.stack([np.clip(40+rng.normal(0,10,(H,W)),20,70),np.clip(150+rng.normal(0,22,(H,W)),100,200),np.clip(70+rng.normal(0,12,(H,W)),40,100)],-1)
def ctext(d,y,t,f,c): d.text(((1080-d.textlength(t,font=f))/2,y),t,font=f,fill=c)
def header(d):
    ctext(d,40,"EXPERIMENT 004",fS,ACC)
    ctext(d,95,"10% more trees =",fT,WH); ctext(d,160,"how much more fire?",fT,WH)
def grid_img(g,f):
    img=np.zeros((H,W,3)); img[:]=(24,28,34)
    t=g==TREE; img[t]=green[t]
    fi=g==FIRE; fl=np.random.default_rng(f).random((H,W))
    img[fi]=np.where(fl[fi][:,None]<0.5,[255,140,20],[255,210,60])
    img[g==ASH]=(52,44,40)
    im=Image.fromarray(img.astype(np.uint8)).resize((W*SC,H*SC),Image.NEAREST)
    return im
def frame(f):
    im=Image.new("RGB",(1080,1920),BG); d=ImageDraw.Draw(im,"RGBA"); header(d)
    step=min(int(f*MAXS/(NF-1)),MAXS)
    for k in range(2):
        s=S[k]; g=s[min(step,len(s)-1)]
        im.paste(grid_img(g,f),(X0,PY[k]))
        d.rectangle([X0-2,PY[k]-2,X0+W*SC+1,PY[k]+H*SC+1],outline=(255,255,255,40),width=2)
        lab=f"FOREST {'AB'[k]}: {round(DENS[k]*100)}% trees"
        d.text((X0,PY[k]-58),lab,font=fL,fill=WH if k==0 else CY)
        b=((g==ASH)|(g==FIRE)).sum()/TREES[k]*100
        t=f"{b:4.1f}% burned"; d.text((X0+W*SC-d.textlength(t,font=fP),PY[k]-62),t,font=fP,fill=ACC if b>50 else WH)
        if not (g==FIRE).any() and step>0:
            t="fire out"; d.rounded_rectangle([X0+W*SC-200,PY[k]+H*SC-60,X0+W*SC-10,PY[k]+H*SC-10],10,fill=(14,17,23,220)); d.text((X0+W*SC-185,PY[k]+H*SC-55),t,font=fs,fill=GR)
    d.text((X0,1862),"same spark on the left edge of both",font=fs,fill=GR)
    return im,d
def enc(name,frames):
    tmp=name+".tmp.mp4"
    pr=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s","1080x1920","-r","30","-i","-","-c:v","libx264","-crf","23","-preset","veryfast","-pix_fmt","yuv420p",tmp],stdin=subprocess.PIPE)
    for im in frames: pr.stdin.write(im.tobytes())
    pr.stdin.close(); assert pr.wait()==0; os.rename(tmp,name)
def main():
    for f in range(NF): yield frame(f)[0]
BA=burned(S[0])*100; BB=burned(S[1])*100
def outro():
    for f in range(180):
        im,d=frame(NF-1)
        im=Image.alpha_composite(im.convert("RGBA"),Image.new("RGBA",im.size,(14,17,23,min(240,f*12)))); d=ImageDraw.Draw(im); header(d)
        if f>8:
            ctext(d,330,"RESULT",fS,ACC)
            ctext(d,400,f"55% trees: {BA:.0f}% burned",ft("DejaVuSans-Bold.ttf",64),WH)
            ctext(d,490,f"65% trees: {BB:.0f}% burned",ft("DejaVuSans-Bold.ttf",64),CY)
        if f>45:
            for n,t in enumerate(["Below ~59% trees, the fire","can't find a connected path.","Above it, it almost always can.","Tiny change. Huge difference."]):
                ctext(d,680+n*72,t,ft("DejaVuSans.ttf",48),WH if n<3 else ACC)
        if f>100:
            ctext(d,1100,"That's why firebreaks work.",ft("DejaVuSans-Bold.ttf",50),CY)
            ctext(d,1260,"Did you guess it?",ft("DejaVuSans-Bold.ttf",56),ACC)
            ctext(d,1340,"Comment YES or NO.",ft("DejaVuSans.ttf",50),WH)
        yield im.convert("RGB")
if __name__=="__main__":
    print(BA,BB,[len(s) for s in S])
    if sys.argv[1]=="still":
        frame(15)[0].save("st_a.png"); frame(400)[0].save("st_b.png"); list(outro())[-1].save("st_out.png")
    else:
        enc("s2.mp4",main()); enc("s3.mp4",outro())
