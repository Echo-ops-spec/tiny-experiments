import numpy as np, sys
sys.path.insert(0,'.')
from sim import Arena
a,b=Arena(False,1),Arena(True,1)
P=[];A=[];PP=[];E=[[],[]]
for f in range(1050):
    for _ in range(4): a.step(); b.step()
    P.append(np.stack([a.p,b.p]).astype(np.float32)); A.append(np.stack([a.alive,b.alive])); PP.append(np.stack([a.pp,b.pp]).astype(np.float32))
np.savez("rec.npz",P=np.array(P),A=np.array(A),PP=np.array(PP))
print(a.alive.sum(),b.alive.sum())
