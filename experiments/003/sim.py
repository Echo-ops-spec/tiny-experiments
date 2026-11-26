import numpy as np
G=10000
rng=np.random.default_rng(7)
car=rng.integers(0,3,G); pick=rng.integers(0,3,G)
host=np.empty(G,int)
for i in range(G):
    opts=[d for d in range(3) if d!=pick[i] and d!=car[i]]
    host[i]=opts[rng.integers(len(opts))]
switch=3-pick-host
stay_win=(pick==car); switch_win=(switch==car)
if __name__=="__main__":
    print(stay_win.mean(), switch_win.mean())
