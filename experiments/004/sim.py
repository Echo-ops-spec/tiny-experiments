import numpy as np
W,H=180,144
EMPTY,TREE,FIRE,ASH=0,1,2,3
def run(density,seed):
    rng=np.random.default_rng(seed)
    g=np.where(rng.random((H,W))<density,TREE,EMPTY).astype(np.int8)
    g[:,0]=np.where(g[:,0]==TREE,FIRE,EMPTY)
    states=[g.copy()]
    while (g==FIRE).any():
        f=g==FIRE
        n=np.zeros_like(f)
        n[1:]|=f[:-1]; n[:-1]|=f[1:]; n[:,1:]|=f[:,:-1]; n[:,:-1]|=f[:,1:]
        g=g.copy(); g[f]=ASH; g[(g==TREE)&n]=FIRE
        states.append(g.copy())
    return np.array(states)
def burned(S): 
    trees=(S[0]!=EMPTY).sum(); return (S[-1]==ASH).sum()/trees
if __name__=="__main__":
    for seed in range(1,6):
        A=run(0.55,seed); B=run(0.65,seed)
        print(seed,len(A),round(burned(A)*100,1),len(B),round(burned(B)*100,1))
