import numpy as np, wave
from render import S, NF, MAXS, FIRE
sr=44100; T=30.0; n=int(sr*T); out=np.zeros(n); t=np.arange(n)/sr
rng=np.random.default_rng(0)
def note(f): return 440*2**((f-69)/12)
ch=[[50,57,62],[48,55,60],[46,53,58],[45,52,57]]  # Dm C Bb A
for i in range(8):
    s=int(i*4*sr); e=min(n,s+int(4.4*sr))
    if s>=n: break
    tt=t[s:e]-t[s]; env=np.minimum(1,tt/0.6)*np.minimum(1,(4.4-tt)/0.8)
    for m in ch[i%4]:
        f=note(m-12); out[s:e]+=0.05*env*(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2.003*f*tt))
beat=60/96
for k in np.arange(0,24,beat):
    s=int(k*sr); L=int(0.2*sr); tt=np.arange(L)/sr
    out[s:s+L]+=0.12*np.sin(2*np.pi*50*tt*np.exp(-tt*8))*np.exp(-tt*16)
# fire crackle: sparse clicks, density follows number of burning cells
for f in range(NF):
    step=min(int(f*MAXS/(NF-1)),MAXS)
    burning=sum((s_[min(step,len(s_)-1)]==FIRE).sum() for s_ in S)
    k=int(min(40,burning/6))
    for _ in range(k):
        p=int((f/30+rng.random()/30)*sr); L=int(0.006*sr)
        if p+L<n: out[p:p+L]+=rng.normal(0,0.12,L)*np.exp(-np.arange(L)/(0.0015*sr))
def blip(at,f,vol,dec=25):
    s=int(at*sr); L=int(0.3*sr)
    if s+L>n: return
    tt=np.arange(L)/sr; out[s:s+L]+=vol*np.sin(2*np.pi*f*tt*(1-0.3*tt))*np.exp(-tt*dec)
for fr,f in ((8,523),(45,659),(100,784)): blip(24+fr/30,f,0.22,6); blip(24+fr/30,f*1.5,0.1,6)
out[:int(0.05*sr)]*=np.linspace(0,1,int(0.05*sr)); out[-int(1.5*sr):]*=np.linspace(1,0,int(1.5*sr))
out=out/np.abs(out).max()*0.85
pcm=(np.repeat(out[:,None],2,1)*32767).astype(np.int16)
w=wave.open("audio.wav","wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes()); w.close()
