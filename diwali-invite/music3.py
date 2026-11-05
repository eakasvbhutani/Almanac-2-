"""Beat #3: bouncy dance beat (sidechain pump, offbeat bass, jersey-club drop) + mechanical-keyboard typing, synced to the cuts in teen.py. Fully synthesised."""
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

# ---------- extra instruments ----------
M = np.zeros((N, 2))          # music bus — gets side-chained (ducked) by the kick
def addm(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    if sig.ndim == 1: sig = np.stack([sig * (1 - max(0, pan)), sig * (1 + min(0, pan))], 1)
    sig = sig[: N - i]; M[i:i + len(sig)] += sig * gain
kick_times = []
def kk(t, g=.95):
    add(kick(), t, g); kick_times.append(t)

def mech_key(heavy=False):
    """clicky mechanical switch: click leaf + plastic bottom-out 'thock' + spring ping + key-up"""
    n = int(.16 * SR); t = np.arange(n) / SR; out = np.zeros(n)
    c = int(.0015 * SR)
    out[:c] += filt(rng.uniform(-1, 1, c), "band", [3500, 9000]) * 1.4                     # click jacket snap
    d = int(.006 * SR); m = n - d; tt = np.arange(m) / SR
    th = sum(np.sin(2 * np.pi * f * tt + rng.uniform(0, 6)) * a for f, a in ((310, 1), (720, .55), (1650, .3)))
    out[d:] += th * np.exp(-tt / (.012 if not heavy else .02)) * (1.2 if heavy else .9)     # bottom-out thock
    out[d:d + 400] += filt(rng.uniform(-1, 1, 400), "band", [1500, 6000]) * np.linspace(.8, 0, 400)
    out[d:] += np.sin(2 * np.pi * 4200 * tt) * np.exp(-tt / .02) * .05                      # spring ping
    u = int(.085 * SR); m2 = min(500, n - u)
    out[u:u + m2] += filt(rng.uniform(-1, 1, m2), "band", [2000, 7000]) * np.linspace(.35, 0, m2)  # key-up rattle
    return out * .9

def bassbounce(m, dur):
    """plucky saw bass w/ filter envelope + sub — the 'bounce'"""
    n = int(dur * SR); t = np.arange(n) / SR; f = hz(m)
    saw = 2 * ((f * t) % 1) - 1
    # crude time-varying lowpass: blend of two fixed filters by envelope
    bright = filt(saw, "low", 2400); dark = filt(saw, "low", 300)
    e = np.exp(-t / .05)
    s = bright * e + dark * (1 - e) + np.sin(2 * np.pi * f / 2 * t) * .9
    return np.tanh(s * 1.6) * adsr(n, .002, .03) * .6

def shaker():
    n = int(.05 * SR); return filt(rng.uniform(-1, 1, n), "band", [5000, 11000]) * np.minimum(1, np.arange(n) / (.012 * SR)) * env(n, .001, .015)

def perc(m):   # wooden 'tok' / cowbell-ish for syncopation
    n = int(.12 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * hz(m) * t) + .5 * np.sign(np.sin(2 * np.pi * hz(m) * 1.48 * t))) * env(n, .0005, .03) * .5

# ---------- arrangement: D major, 140 BPM, swung 16ths ----------
BPM = 140; beat = 60 / BPM; st = beat / 4; SWING = .14
def T(start, i): return start + i * st + (SWING * st if i % 2 else 0)
GRID0 = cuts[1]
CHORDS = [[62, 66, 69, 74], [61, 64, 69, 73], [59, 62, 66, 71], [59, 62, 67, 71]]
ROOTS = [38, 33, 35, 31]
LEAD = [78, 81, 83, 81, 78, 76, 74, 76, 78, 78, 81, 85, 83, 81, 78, 76]

# pov: typed on a clicky mechanical keyboard — clicks land on the frames where each letter appears
for k, fr in enumerate([0, 2, 3, 4]):
    add(mech_key(), fr / FPS + .01, .95, -.25 + .15 * k)
add(mech_key(heavy=True), 6 / FPS + .02, 1.0, .1)          # 'enter'
for c in cuts[1:-1]: add(whoosh(), c - .2, .4)

JERSEY = {0, 3, 6, 8, 10, 11, 14}         # extra-bouncy jersey kick
def section(start, end, drop):
    i = 0
    while T(start, i) < end - 1e-6:
        t = T(start, i); s, bar = i % 16, i // 16
        ch, root = CHORDS[bar % 4], ROOTS[bar % 4]
        add(shaker(), t, .16 if s % 2 else .09, .35)
        if not drop:
            if s % 4 == 0: kk(t)                                         # four-on-the-floor
            if s in (4, 12): add(clap(), t, .5)
            if s in (2, 6, 10, 14): add(hat(True), t, .22, -.3)           # offbeat open hat
            if s in (2, 6, 10, 14): addm(bassbounce(root, st * 1.5), t, .85)   # offbeat bass = bounce
            if s in (7, 15): addm(bassbounce(root + 12, st * .9), t, .55)       # octave hop
            if s in (3, 11): add(perc(84), t, .35, .4)
            if s in (2, 6, 10, 14): addm(supersaw(ch, st * 1.4, 3500), t, .45)
            if s in (0, 3, 6, 8, 11): addm(vox("oh" if s < 8 else "ah", [69, 71, 74, 71, 69][[0, 3, 6, 8, 11].index(s)], st * 1.6), t, .3, -.2)
        else:
            if s in JERSEY or (bar % 2 and s in (13, 15)): kk(t)
            if s in (4, 12): add(clap(), t, .65)
            if s in (2, 6, 10, 14): add(hat(True), t, .22, -.3)
            else: add(hat(), t, .12, .3)
            if s in (2, 5, 7, 10, 13, 15): addm(bassbounce(root + (12 if s in (7, 15) else 0), st * 1.3), t, .9)
            if s in (0, 3, 6, 10, 12): addm(supersaw(ch, st * 1.5, 7000), t, .55)
            if s % 2 == 0: addm(bell(LEAD[(s // 2) + 8 * (bar % 2)]), t, .3, .25)
            if s in (1, 9): add(perc(88), t, .35, -.4)
            if s == 12: add(vox("hey", 62 + 2 * (bar % 2), .16), t, .6)
        i += 1

pre_end = T_FINAL - 1.2
section(GRID0, pre_end, False)
add(riser(1.15), T_FINAL - 1.15, .9)
t = pre_end; k = 0
while t < T_FINAL - .1:          # kick + clap roll that speeds up
    kk(t, .5 + .03 * k); add(clap(), t, .2 + .03 * k, .2 if k % 2 else -.2)
    t += beat / 2 if k < 4 else (st if k < 10 else st / 2); k += 1
add(vox("hey", 64, .22), T_FINAL - .03, 1.0)
section(T_FINAL, TOTAL, True)

# side-chain: duck the music bus on every kick (the 'pumping' bounce)
duck = np.ones(N); rec = int(beat * .55 * SR); curve = 1 - .8 * (1 - np.linspace(0, 1, rec)) ** 2
for kt in kick_times:
    i = int(kt * SR); j = min(N, i + rec)
    duck[i:j] = np.minimum(duck[i:j], curve[: j - i])
L += M[:, 0] * duck; R += M[:, 1] * duck

mix = np.stack([L, R], 1)[: int(TOTAL * SR)]
fade = int(.7 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
mix = np.tanh(mix / (np.max(np.abs(mix)) * .5)) * .92
wavfile.write(os.path.join(HERE, "beat3.wav"), SR, (mix * 32767).astype(np.int16))
print("ok", len(kick_times), "kicks")
