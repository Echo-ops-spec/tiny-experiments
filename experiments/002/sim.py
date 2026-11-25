import numpy as np
L=240; N=48; VMAX=5; P=0.22
def run(smooth, steps=360, seed=3):
    rng=np.random.default_rng(seed)
    x=np.sort(rng.choice(L,N,replace=False)); v=np.full(N,2)
    X=[x.copy()]; V=[v.copy()]
    for t in range(steps):
        gap=(np.roll(x,-1)-x-1)%L
        if smooth:
            # anticipation: also count the leader's likely next move
            gap_eff=gap+np.maximum(np.roll(v,-1)-1,0)
        else: gap_eff=gap
        v=np.minimum(v+1,VMAX)
        v=np.minimum(v,gap_eff)
        r=rng.random(N)<P
        if smooth:
            # smooth drivers only brake randomly when cruising, never overreact
            v=np.where(r&(v>3),v-1,v)
        else:
            v=np.where(r,np.maximum(v-1,0),v)
        v=np.minimum(v,gap+np.maximum(np.roll(v,-1),0))  # safety: never pass through leader
        x=(x+v)%L
        X.append(x.copy()); V.append(v.copy())
    return np.array(X),np.array(V)
if __name__=="__main__":
    for s in (0,1):
        X,V=run(s); print("smooth" if s else "human", V[60:].mean()*27/VMAX*5/5, (V[60:]==0).mean())
