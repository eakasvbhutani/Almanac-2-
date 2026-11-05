"""Beat #2: bright jersey-club / pop party beat, synced to the cuts in teen.py. Fully synthesised."""
import os, numpy as np
from scipy.signal import lfilter, butter
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100; FPS = 15
DURS = [.6, .7, .14, .85, 1.0, .14, .85, .7, .7, .7, .14, 4.2]   # mirrors SCENES in teen.py
cuts = np.cumsum([0] + [max(1, round(d * FPS)) for d in DURS]) / FPS
TOTAL = cuts[-1]; T_FINAL = cuts[11]
N = int(TOTAL * SR) + 2 * SR
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(21)

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    if sig.ndim == 1: sig = np.stack([sig * (1 - max(0, pan)), sig * (1 + min(0, pan))], 1)
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig[:, 0] * gain; R[i:i + len(sig)] += sig[:, 1] * gain

def env(n, a=.002, d=.2):
    t = np.arange(n) / SR; return np.minimum(1, t / a) * np.exp(-t / d)
def adsr(n, a=.005, rel=.06):
    e = np.ones(n); ai = int(a * SR); ri = int(rel * SR)
    e[:ai] = np.linspace(0, 1, ai); e[-ri:] *= np.linspace(1, 0, ri); return e
def filt(x, kind, f, order=2):
    b, a = butter(order, np.array(f) / (SR / 2), kind); return lfilter(b, a, x, axis=0)
def hz(n):  # midi -> Hz
    return 440 * 2 ** ((n - 69) / 12)

def kick():
    n = int(.32 * SR); t = np.arange(n) / SR
    f = 52 + 160 * np.exp(-t / .022)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .0008, .11)
    return np.tanh(s * 2.4) * .9

def clap():
    n = int(.22 * SR); out = np.zeros(n)
    for off in (0, .008, .017, .026):
        k = int(off * SR); m = n - k
        out[k:] += filt(rng.uniform(-1, 1, m), "band", [1100, 5000]) * env(m, .0005, .03 if off < .02 else .09)
    return out * 1.3

def hat(open_=False):
    n = int((.16 if open_ else .04) * SR)
    return filt(rng.uniform(-1, 1, n), "high", 8000) * env(n, .0005, .06 if open_ else .01)

def supersaw(midis, dur, cutoff=5000, voices=7, spread=.18):
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros((n, 2))
    for m in midis:
        for v in range(voices):
            det = (v - (voices - 1) / 2) / ((voices - 1) / 2) * spread
            f = hz(m + det); ph = rng.uniform(0, 1)
            saw = 2 * ((f * t + ph) % 1) - 1
            pan = (v / (voices - 1)) * 2 - 1
            out[:, 0] += saw * (1 - pan) * .5; out[:, 1] += saw * (1 + pan) * .5
    out = filt(out, "low", cutoff) / (len(midis) * voices) * 3
    return out * adsr(n, .004, min(.08, dur * .5))[:, None]

def sub(m, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    return np.tanh(2 * np.sin(2 * np.pi * hz(m) * t)) * adsr(n, .004, .04) * .7

def bell(m, dur=.35):
    """FM bell/marimba lead — bright and toy-like."""
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    mod = np.sin(2 * np.pi * f * 3.5 * t) * 2.2 * np.exp(-t / .05)
    return np.sin(2 * np.pi * f * t + mod) * env(n, .001, .16)

def vox(vowel, m, dur):
    """chopped 'vocal' made with formant filters on a buzzy source"""
    F = {"hey": (530, 1840, 2480), "oh": (500, 900, 2400), "ah": (750, 1200, 2600)}[vowel]
    n = int(dur * SR); t = np.arange(n) / SR
    src = 2 * ((hz(m) * t) % 1) - 1 + .25 * rng.uniform(-1, 1, n)
    out = sum(filt(src, "band", [f * .88, f * 1.12]) * g for f, g in zip(F, (1, .6, .3)))
    if vowel == "hey": out[: int(.03 * SR)] += filt(rng.uniform(-1, 1, int(.03 * SR)), "high", 2500) * .6
    return out * adsr(n, .006, .05) * 1.6

def whoosh(dur=.2):
    n = int(dur * SR); x = rng.uniform(-1, 1, n); out = np.zeros(n); k = n // 10
    for j in range(10): out[j * k:(j + 1) * k] = filt(x[j * k:(j + 1) * k], "band", [400 + j * 600, 1400 + j * 900])
    return out * np.linspace(0, 1, n) ** 2 * .6

def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = supersaw([62, 69], dur, 9000)[:, 0] * 0
    noise = filt(rng.uniform(-1, 1, n), "high", 3000) * (t / dur) ** 2 * .5
    f = 300 * (6 ** (t / dur)); tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * .18 * (t / dur)
    return noise + tone + s

# ---------- arrangement: D major, I–V–vi–IV ----------
BPM = 140; beat = 60 / BPM; st = beat / 4
GRID0 = cuts[1]
CHORDS = [[62, 66, 69, 74], [61, 64, 69, 73], [59, 62, 66, 71], [59, 62, 67, 71]]   # D  A/C#  Bm  G
ROOTS = [38, 33, 35, 31]
LEAD = [78, 81, 83, 81, 78, 76, 74, 76, 78, 78, 81, 85, 83, 81, 78, 76]

# intro: typing ticks + filtered chord swell
for k in range(4): add(filt(rng.uniform(-1, 1, 500), "high", 3500) * env(500, .0003, .002), k * .13 + .02, .9, .3 - .2 * k)
add(supersaw(CHORDS[0], GRID0 + .05, 900), 0, .35)

for c in cuts[1:-1]: add(whoosh(), c - .2, .5)

JERSEY = {0, 4, 8, 11, 14}      # the bouncy jersey-club kick
def section(start, end, drop):
    i = 0; t = start
    while t < end - 1e-6:
        s, bar = i % 16, i // 16
        ch, root = CHORDS[bar % 4], ROOTS[bar % 4]
        if drop:
            if s in JERSEY or (bar % 2 == 1 and s in (13, 15)): add(kick(), t, .9)
            if s in (4, 12): add(clap(), t, .6)
            if s in (2, 6, 10, 14): add(hat(True), t, .2, .3)
            else: add(hat(), t, .12, -.3)
            if s in (0, 3, 6, 10, 12): add(supersaw(ch, st * 1.6, 6500), t, .55)   # stabs
            if s in (0, 3, 6, 10, 12): add(sub(root, st * 1.6), t, .8)
            if s % 2 == 0: add(bell(LEAD[(s // 2) + 8 * (bar % 2)]), t, .28, .25)
            if s == 14 and bar % 2 == 0: add(vox("hey", 62, .16), t, .55)
        else:
            if s % 4 == 0: add(kick(), t, .7)                       # four-on-floor build
            if s in (4, 12): add(clap(), t, .4)
            if s % 2 == 1: add(hat(), t, .12, .3)
            if s == 0: add(supersaw(ch, beat * 4, 1800 + 300 * bar), t, .35)   # pad opening up
            if s == 0: add(sub(root, beat * 2), t, .55)
            if s in (0, 3, 6, 8, 11): add(vox("oh" if s < 8 else "ah", [69, 71, 74, 71, 69][[0, 3, 6, 8, 11].index(s)], st * 1.8), t, .35, -.2)
        i += 1; t += st

pre_end = T_FINAL - 1.2
section(GRID0, pre_end, False)
# build: snare-roll that speeds up + riser, tiny silence, then DROP
add(riser(1.15), T_FINAL - 1.15, .9)
t = pre_end; k = 0
while t < T_FINAL - .1:
    add(clap(), t, .2 + .035 * k, .2 if k % 2 else -.2)
    t += st if k < 8 else st / 2; k += 1
add(vox("hey", 64, .22), T_FINAL - .02, .9)
add(kick(), T_FINAL, 1.1)
section(T_FINAL, TOTAL, True)

mix = np.stack([L, R], 1)[: int(TOTAL * SR)]
fade = int(.7 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
mix = np.tanh(mix / (np.max(np.abs(mix)) * .5)) * .92
wavfile.write(os.path.join(HERE, "beat2.wav"), SR, (mix * 32767).astype(np.int16))
print("ok", TOTAL, T_FINAL)
