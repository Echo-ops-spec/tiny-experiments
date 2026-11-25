import numpy as np, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
R=np.load("rec.npz"); P,A,PP=R["P"],R["A"],R["PP"]
F="/usr/share/fonts/truetype/dejavu/"
def ft(n,s): return ImageFont.truetype(F+n,s)
BG=(14,17,23);ACC=(255,184,0);CY=(64,224,208);WH=(235,235,228);RED=(255,80,80);GR=(130,135,145)
OX=90; OY=[330,1160]; S=0.9
fT=ft("DejaVuSans-Bold.ttf",64); fS=ft("DejaVuSansMono-Bold.ttf",40); fL=ft("DejaVuSans-Bold.ttf",44); fC=ft("DejaVuSansMono-Bold.ttf",44); fs=ft("DejaVuSansMono.ttf",28)
def ctext(d,y,t,f,c):
    d.text(((1080-d.textlength(t,font=f))/2,y),t,font=f,fill=c)
def header(d):
    ctext(d,70,"EXPERIMENT 001",fS,ACC)
    ctext(d,135,"Does flocking save birds?",fT,WH)
def frame(i, header_on=True, counters=True):
    im=Image.new("RGB",(1080,1920),BG); d=ImageDraw.Draw(im,"RGBA")
    if header_on: header(d)
    j=i-1 if i>0 else 1
    for k in range(2):
        ox,oy=OX,OY[k]; col=WH if k==0 else CY
        d.rounded_rectangle([ox,oy,ox+900,oy+720],18,outline=(255,255,255,40),width=3,fill=(20,24,32))
        al=A[i,k]; p=P[i,k]*S; q=P[j,k]*S
        for (x,y),(x0,y0) in zip(p[al],q[al]):
            vx,vy=x-x0,y-y0
            if i==0: vx,vy=-vx,-vy
            d.line([ox+x-vx*2,oy+y-vy*2,ox+x,oy+y],fill=col+(255,),width=4)
        # recent kills
        for b in range(1,25):
            if i-b<1: break
            newly=A[i-b-1,k]&~A[i-b,k]
            for x,y in P[i-b,k][newly]*S:
                r=10+b*2; a=int(255*(1-b/25))
                d.ellipse([ox+x-r,oy+y-r,ox+x+r,oy+y+r],outline=RED+(a,),width=4)
        x,y=PP[i,k]*S
        for r,a in((34,40),(22,80)): d.ellipse([ox+x-r,oy+y-r,ox+x+r,oy+y+r],fill=ACC+(a,))
        d.ellipse([ox+x-12,oy+y-12,ox+x+12,oy+y+12],fill=ACC)
        lab="LONERS" if k==0 else "FLOCK"
        d.text((ox+4,oy-58),lab,font=fL,fill=col)
        if counters:
            t=f"{al.sum()} / 500 alive"; d.text((ox+900-d.textlength(t,font=fC),oy-56),t,font=fC,fill=col)
    return im,d
def enc(name, frames, fade_out=False):
    tmp=name+".tmp.mp4"
    cmd=["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s","1080x1920","-r","30","-i","-","-c:v","libx264","-crf","18","-preset","veryfast","-pix_fmt","yuv420p",tmp]
    pr=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    for im in frames: pr.stdin.write(im.tobytes())
    pr.stdin.close(); assert pr.wait()==0; os.rename(tmp,name)
def intro():
    lines=[(0,"Same predator."),(25,"Same 500 birds."),(50,"One difference:"),(70,"the bottom ones flock.")]
    for f in range(120):
        im,d=frame(0,counters=False)
        ov=Image.new("RGBA",im.size,(14,17,23,200)); im=Image.alpha_composite(im.convert("RGBA"),ov); d=ImageDraw.Draw(im)
        header(d)
        for st,t in lines:
            if f>=st:
                a=min(255,(f-st)*20); ctext(d,780+lines.index((st,t))*110,t,ft("DejaVuSans-Bold.ttf",66),(CY if "flock" in t else WH)+(a,))
        yield im.convert("RGB")
def main():
    for i in range(len(P)):
        im,d=frame(i)
        d.text((90,1884),"4x speed",font=fs,fill=GR)
        t=f"{(i*4)//30//60}:{(i*4)//30%60:02d}"; d.text((990-d.textlength(t,font=fs),1884),t,font=fs,fill=GR)
        yield im
def outro():
    la,fb=500-A[-1,0].sum(),500-A[-1,1].sum()
    for f in range(180):
        im,d=frame(len(P)-1)
        ov=Image.new("RGBA",im.size,(14,17,23,min(238,f*12))); im=Image.alpha_composite(im.convert("RGBA"),ov); d=ImageDraw.Draw(im)
        header(d)
        if f>8:
            ctext(d,620,"RESULT",fS,ACC)
            ctext(d,720,f"Loners lost {la}",ft("DejaVuSans-Bold.ttf",80),WH)
            ctext(d,830,f"Flock lost {fb}",ft("DejaVuSans-Bold.ttf",80),CY)
        if f>40:
            ctext(d,1010,f"Flocking cut losses by {round(100*(1-fb/la))}%.",ft("DejaVuSans.ttf",52),WH)
            ctext(d,1090,"Why? Crowds confuse the hunter.",ft("DejaVuSans.ttf",52),GR)
        if f>90:
            ctext(d,1300,"What should I test next?",ft("DejaVuSans-Bold.ttf",56),ACC)
            ctext(d,1380,"Comment below.",ft("DejaVuSans.ttf",50),WH)
        yield im.convert("RGB")
if __name__=="__main__":
    w=sys.argv[1]
    if w=="still":
        for i in (0,500,1049):
            frame(i)[0].save(f"still_{i}.png")
        list(outro())[-1].save("still_out.png"); list(intro())[-1].save("still_in.png")
    else:
        enc("s1.mp4",intro()); enc("s2.mp4",main()); enc("s3.mp4",outro())
