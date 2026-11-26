import numpy as np, subprocess, sys, os
from PIL import Image, ImageDraw, ImageFont
from sim import G, car, pick, host, switch, stay_win, switch_win
F="/usr/share/fonts/truetype/dejavu/"
def ft(n,s): return ImageFont.truetype(F+n,s)
BG=(14,17,23);ACC=(255,184,0);CY=(64,224,208);WH=(235,235,228);RED=(255,80,80);GR=(130,135,145);PANEL=(20,24,32);DOOR=(44,50,62)
fS=ft("DejaVuSansMono-Bold.ttf",40);fT=ft("DejaVuSans-Bold.ttf",62);fL=ft("DejaVuSans-Bold.ttf",44);fP=ft("DejaVuSansMono-Bold.ttf",56)
fD=ft("DejaVuSans-Bold.ttf",34);fN=ft("DejaVuSans-Bold.ttf",60);fs=ft("DejaVuSansMono.ttf",28)
PY=[330,1110]; WINS=[np.cumsum(stay_win),np.cumsum(switch_win)]
SLOW=5; SLOWF=300; NF=1050
def ctext(d,y,t,f,c): d.text(((1080-d.textlength(t,font=f))/2,y),t,font=f,fill=c)
def header(d):
    ctext(d,60,"EXPERIMENT 003",fS,ACC)
    ctext(d,125,"Should you switch doors?",fT,WH)
    ctext(d,205,"The Monty Hall problem, played 10,000 times",ft("DejaVuSans.ttf",34),GR)
def games_at(f):
    if f<SLOWF: return f//60, (f%60)  # current game index, phase frame
    u=(f-SLOWF)/(NF-1-SLOWF); return int(SLOW+(G-SLOW)*u**3), 60
def frame(f,stats=True):
    im=Image.new("RGB",(1080,1920),BG); d=ImageDraw.Draw(im,"RGBA"); header(d)
    gi,ph=games_at(f); gi=min(gi,G-1)
    done=gi+(1 if ph>=45 else 0)  # games finished
    for k in range(2):
        y0=PY[k]; col=[WH,CY][k]
        d.rounded_rectangle([60,y0,1020,y0+720],18,fill=PANEL,outline=(255,255,255,35),width=3)
        d.text((90,y0+24),["ALWAYS STAY","ALWAYS SWITCH"][k],font=fL,fill=col)
        if stats and done>0:
            w=WINS[k][done-1]; p=100*w/done
            t=f"{p:4.1f}%"; d.text((990-d.textlength(t,font=fP),y0+16),t,font=fP,fill=col)
            t2=f"{w:,} wins / {done:,} games"; d.text((990-d.textlength(t2,font=fs),y0+86),t2,font=fs,fill=GR)
        # doors
        final=pick[gi] if k==0 else (switch[gi] if ph>=30 else pick[gi])
        for dn in range(3):
            x=150+dn*270; yd=y0+140
            opened=(ph>=15 and dn==host[gi]) or ph>=45
            fill=DOOR
            if opened: fill=(30,36,46)
            d.rounded_rectangle([x,yd,x+240,yd+260],14,fill=fill)
            if dn==final: d.rounded_rectangle([x-6,yd-6,x+246,yd+266],18,outline=ACC,width=8)
            if opened:
                iscar=dn==car[gi]; t="CAR" if iscar else "GOAT"
                d.text((x+120-d.textlength(t,font=fN)/2,yd+95),t,font=fN,fill=CY if iscar else GR)
            else:
                t=str(dn+1); d.text((x+120-d.textlength(t,font=fN)/2,yd+95),t,font=fN,fill=(90,98,112))
        if ph>=45:
            won=bool([stay_win,switch_win][k][gi]); t="WIN" if won else "LOSE"
            d.text((540-d.textlength(t,font=fD)/2,y0+420),t,font=fD,fill=CY if won else RED)
        # chart
        cx0,cy0,cw,chh=110,y0+480,860,200
        for lv in (1/3,2/3):
            yy=cy0+chh*(1-lv); d.line([cx0,yy,cx0+cw,yy],fill=(255,255,255,30),width=2)
            d.text((cx0+cw-60,yy-30),f"{round(lv*100)}%",font=fs,fill=(255,255,255,70))
        if done>1:
            xs=np.unique(np.geomspace(1,done,min(done,300)).astype(int))
            pts=[(cx0+cw*np.log(x)/np.log(G),cy0+chh*(1-WINS[k][x-1]/x)) for x in xs]
            d.line(pts,fill=col,width=5)
        d.text((cx0,cy0+chh+8),"games (log scale) →",font=fs,fill=GR)
    return im,d
def enc(name,frames):
    tmp=name+".tmp.mp4"
    pr=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s","1080x1920","-r","30","-i","-","-c:v","libx264","-crf","23","-preset","veryfast","-pix_fmt","yuv420p",tmp],stdin=subprocess.PIPE)
    for im in frames: pr.stdin.write(im.tobytes())
    pr.stdin.close(); assert pr.wait()==0; os.rename(tmp,name)
INTRO=[(0,"Three doors. One car, two goats.",WH),(25,"You pick a door.",WH),(45,"The host opens a goat door.",WH),(70,"Stay or switch?",ACC),(90,"Most people say: 50/50.",GR)]
def intro():
    for f in range(130):
        im,d=frame(0,stats=False)
        im=Image.alpha_composite(im.convert("RGBA"),Image.new("RGBA",im.size,(14,17,23,210))); d=ImageDraw.Draw(im); header(d)
        for n,(st,t,c) in enumerate(INTRO):
            if f>=st: ctext(d,700+n*100,t,ft("DejaVuSans-Bold.ttf",50),c+(min(255,(f-st)*20),))
        yield im.convert("RGB")
def main():
    for f in range(NF):
        im,d=frame(f)
        if f>=SLOWF: d.text((60,1870),"speeding up",font=fs,fill=GR)
        yield im
def outro():
    for f in range(190):
        im,d=frame(NF-1)
        im=Image.alpha_composite(im.convert("RGBA"),Image.new("RGBA",im.size,(14,17,23,min(240,f*12)))); d=ImageDraw.Draw(im); header(d)
        if f>8:
            ctext(d,420,"RESULT",fS,ACC)
            ctext(d,500,f"Stay: won {100*stay_win.mean():.1f}%",ft("DejaVuSans-Bold.ttf",64),WH)
            ctext(d,590,f"Switch: won {100*switch_win.mean():.1f}%",ft("DejaVuSans-Bold.ttf",64),CY)
        if f>45:
            for n,t in enumerate(["Your first pick is right 1 time in 3.","The host knows where the car is,","so he never opens it.","Switching wins the other 2 in 3."]):
                ctext(d,770+n*72,t,ft("DejaVuSans.ttf",46),WH if n<3 else CY)
        if f>105:
            ctext(d,1180,"It's not 50/50. Always switch.",ft("DejaVuSans-Bold.ttf",52),ACC)
            ctext(d,1330,"What should I test next?",ft("DejaVuSans-Bold.ttf",56),ACC)
            ctext(d,1410,"Comment below.",ft("DejaVuSans.ttf",50),WH)
        yield im.convert("RGB")
if __name__=="__main__":
    if sys.argv[1]=="still":
        frame(50)[0].save("st_slow.png"); frame(700)[0].save("st_fast.png"); list(intro())[-1].save("st_in.png"); list(outro())[-1].save("st_out.png")
    else:
        enc("s1.mp4",intro()); enc("s2.mp4",main()); enc("s3.mp4",outro())
