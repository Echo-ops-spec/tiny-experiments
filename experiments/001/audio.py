import numpy as np, wave
sr=44100; T=45.0; n=int(sr*T); out=np.zeros(n)
t=np.arange(n)/sr
R=np.load("rec.npz"); A=R["A"]
def note(f): return 440*2**((f-69)/12)
# pad chords (Am F C G), 4s each
ch=[[57,60,64],[53,57,60],[48,55,64],[55,59,62]]
for i in range(12):
    s=int(i*4*sr); e=min(n,s+int(4.4*sr)); tt=t[s:e]-t[s]
    env=np.minimum(1,tt/0.8)*np.minimum(1,(4.4-tt)/0.8)
    for m in ch[i%4]:
        f=note(m-12)
        out[s:e]+=0.05*env*(np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2.003*f*tt))
# soft pulse 100bpm during sim
beat=60/100
for k in np.arange(4.0,39.0,beat):
    s=int(k*sr); L=int(0.18*sr); tt=np.arange(L)/sr
    out[s:s+L]+=0.12*np.sin(2*np.pi*55*tt*np.exp(-tt*8))*np.exp(-tt*18)
    s2=int((k+beat/2)*sr); out[s2:s2+L]+=0.02*np.random.default_rng(int(k*10)).normal(0,1,L)*np.exp(-tt*60)
def blip(at,f,vol,dec=25):
    s=int(at*sr); L=int(0.25*sr)
    if s+L>n: return
    tt=np.arange(L)/sr
    out[s:s+L]+=vol*np.sin(2*np.pi*f*tt*(1-0.3*tt))*np.exp(-tt*dec)
# kills
for k,f in ((0,330),(1,660)):
    for fr in range(1,len(A)):
        c=(A[fr-1,k]&~A[fr,k]).sum()
        if c: blip(4.0+fr/30,f,0.18)
# intro text ticks
for fr in (0,25,50,70): blip(fr/30,880,0.12,40)
# outro chimes
for fr,f in ((8,523),(40,659),(90,784)): blip(39.0+fr/30,f,0.22,6); blip(39.0+fr/30,f*1.5,0.1,6)
# fade
out[:int(0.3*sr)]*=np.linspace(0,1,int(0.3*sr)); out[-int(1.5*sr):]*=np.linspace(1,0,int(1.5*sr))
out=out/np.abs(out).max()*0.85
pcm=(np.repeat(out[:,None],2,1)*32767).astype(np.int16)
w=wave.open("audio.wav","wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes()); w.close()
