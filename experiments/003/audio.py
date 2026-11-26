import numpy as np, wave
from sim import switch_win
sr=44100; T=45.67; n=int(sr*T); out=np.zeros(n); t=np.arange(n)/sr
I0=130/30; M=35.0
def note(f): return 440*2**((f-69)/12)
ch=[[45,52,57],[41,48,53],[43,50,55],[40,47,52]]  # Am F G Em
for i in range(12):
    s=int(i*4*sr); e=min(n,s+int(4.4*sr)); tt=t[s:e]-t[s]
    env=np.minimum(1,tt/0.8)*np.minimum(1,(4.4-tt)/0.8)
    for m in ch[i%4]:
        f=note(m); out[s:e]+=0.045*env*(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2.003*f*tt))
beat=60/100
for k in np.arange(I0,I0+M,beat):
    s=int(k*sr); L=int(0.18*sr); tt=np.arange(L)/sr
    out[s:s+L]+=0.11*np.sin(2*np.pi*55*tt*np.exp(-tt*8))*np.exp(-tt*18)
def blip(at,f,vol,dec=25):
    s=int(at*sr); L=int(0.3*sr)
    if s+L>n or s<0: return
    tt=np.arange(L)/sr; out[s:s+L]+=vol*np.sin(2*np.pi*f*tt*(1-0.3*tt))*np.exp(-tt*dec)
for g in range(5):
    b=I0+g*2.0
    blip(b,660,0.10,40); blip(b+0.5,300,0.12,20); blip(b+1.0,880,0.10,40)
    if switch_win[g]: blip(b+1.5,784,0.2,8); blip(b+1.5,1175,0.1,8)
    else: blip(b+1.5,196,0.2,10)
for fr in range(300,1050,3):
    u=(fr-300)/749; blip(I0+fr/30,500+700*u,0.05+0.05*u,50)
for fr in (0,25,45,70,90): blip(fr/30,880,0.12,40)
for fr,f in ((8,523),(45,659),(105,784)): blip(I0+M+fr/30,f,0.22,6); blip(I0+M+fr/30,f*1.5,0.1,6)
out[:int(0.3*sr)]*=np.linspace(0,1,int(0.3*sr)); out[-int(1.5*sr):]*=np.linspace(1,0,int(1.5*sr))
out=out/np.abs(out).max()*0.85
pcm=(np.repeat(out[:,None],2,1)*32767).astype(np.int16)
w=wave.open("audio.wav","wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes()); w.close()
