import numpy as np

W, H = 1000, 800
N = 500

class Arena:
    def __init__(self, flock, seed=1):
        rng = np.random.default_rng(seed)
        self.rng = np.random.default_rng(seed + 100)
        self.flock = flock
        self.p = rng.uniform([50, 50], [W - 50, H - 50], (N, 2))
        a = rng.uniform(0, 2 * np.pi, N)
        self.v = np.stack([np.cos(a), np.sin(a)], 1) * 2.5
        self.alive = np.ones(N, bool)
        self.pp = np.array([W / 2, H / 2], float)
        self.pv = np.array([3.0, 0.0])
        self.target = -1
        self.rest = 90
        self.eaten = []  # (frame, pos)
        self.t = 0

    def step(self):
        self.t += 1
        idx = np.where(self.alive)[0]
        p, v = self.p[idx], self.v[idx]
        acc = np.zeros_like(p)
        d = p[:, None, :] - p[None, :, :]
        dist = np.hypot(d[..., 0], d[..., 1]) + np.eye(len(p)) * 1e9
        # separation (both)
        close = dist < 12
        acc += (d * close[..., None] / (dist[..., None] ** 2)).sum(1) * 6
        if self.flock:
            nb = dist < 45
            cnt = nb.sum(1)[:, None]
            has = cnt[:, 0] > 0
            avg_v = (nb[..., None] * v[None]).sum(1) / np.maximum(cnt, 1)
            avg_p = (nb[..., None] * p[None]).sum(1) / np.maximum(cnt, 1)
            acc[has] += (avg_v[has] - v[has]) * 0.08
            acc[has] += (avg_p[has] - p[has]) * 0.004
        else:
            ang = self.rng.normal(0, 0.35, len(p))
            c, s = np.cos(ang), np.sin(ang)
            acc += np.stack([v[:, 0] * c - v[:, 1] * s, v[:, 0] * s + v[:, 1] * c], 1) * 0.05
        # flee
        dp = p - self.pp
        dd = np.hypot(dp[:, 0], dp[:, 1])
        fl = dd < 130
        acc[fl] += dp[fl] / dd[fl, None] * 0.35
        # walls
        m = 60
        acc[:, 0] += (p[:, 0] < m) * 0.3 - (p[:, 0] > W - m) * 0.3
        acc[:, 1] += (p[:, 1] < m) * 0.3 - (p[:, 1] > H - m) * 0.3
        v = v + acc
        sp = np.hypot(v[:, 0], v[:, 1])[:, None]
        maxs = np.where(fl[:, None], 3.6, 2.6)
        v = v / np.maximum(sp, 1e-6) * np.clip(sp, 1.5, maxs)
        p = np.clip(p + v, 5, [W - 5, H - 5])
        self.p[idx], self.v[idx] = p, v

        # predator
        if self.rest > 0:
            self.rest -= 1
            self.pv *= 0.95
        else:
            if self.target < 0 or not self.alive[self.target] or self.t % 120 == 0:
                dd2 = np.hypot(*(self.p[idx] - self.pp).T)
                self.target = idx[np.argmin(dd2)]
            tp = self.p[self.target]
            want = tp - self.pp
            want = want / (np.hypot(*want) + 1e-6) * 5.6
            self.pv += (want - self.pv) * 0.3
            # confusion: many birds near target -> predator re-targets & misses
            dt = np.hypot(*(self.p[idx] - tp).T)
            crowd = (dt < 35).sum() - 1
            if np.hypot(*(tp - self.pp)) < 14:
                if self.rng.random() < 1 / (1 + 0.35 * crowd):
                    self.alive[self.target] = False
                    self.eaten.append((self.t, tp.copy()))
                    self.rest = 8
                else:
                    self.target = idx[self.rng.integers(len(idx))]
        self.pp = np.clip(self.pp + self.pv, 5, [W - 5, H - 5])

if __name__ == "__main__":
    for seed in (1,):
        a, b = Arena(False, seed), Arena(True, seed)
        for _ in range(4200):
            a.step(); b.step()
        print(seed, "loners", a.alive.sum(), "flock", b.alive.sum())
