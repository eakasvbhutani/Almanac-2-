"""Original desi-trap beat synced to the cuts in teen.py. Everything is synthesised — no samples, no copyrighted audio."""
import os, numpy as np
from scipy.signal import lfilter, butter
from scipy.io import wavfile

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 44100; FPS = 15
# must mirror SCENES in teen.py
DURS = [.6, .7, .14, .85, 1.0, .14, .85, .7, .7, .7, .14, 4.2]
frames = [max(1, round(d * FPS)) for d in DURS]
cuts = np.cumsum([0] + frames) / FPS          # scene start times
TOTAL = cuts[-1]
T_FINAL = cuts[11]                              # the drop lands on the final card
N = int(TOTAL * SR) + SR
L = np.zeros(N); R = np.zeros(N)
rng = np.random.default_rng(5)

def add(sig, t, gain=1.0, pan=0.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[: N - i]
    L[i:i + len(sig)] += sig * gain * (1 - max(0, pan))
    R[i:i + len(sig)] += sig * gain * (1 + min(0, pan))

def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)

def bp(x, lo, hi, order=2):
    b, a = butter(order, [lo / (SR / 2), hi / (SR / 2)], "band"); return lfilter(b, a, x)
def hp(x, f): b, a = butter(2, f / (SR / 2), "high"); return lfilter(b, a, x)
def lp(x, f): b, a = butter(2, f / (SR / 2), "low"); return lfilter(b, a, x)

def kick(dur=.45):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 45 + 110 * np.exp(-t / .03)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .16)
    s[:200] += rng.uniform(-1, 1, 200) * np.linspace(.6, 0, 200)
    return np.tanh(s * 1.8)

def b808(freq, dur=.7, glide_from=None):
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.full(n, freq) if glide_from is None else freq + (glide_from - freq) * np.exp(-t / .06)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .003, .45)
    return np.tanh(s * 2.2) * .8

def clap():
    n = int(.25 * SR); out = np.zeros(n)
    for off in (0, .011, .022):
        k = int(off * SR); m = n - k
        out[k:] += bp(rng.uniform(-1, 1, m), 900, 4000) * env(m, .001, .05 if off < .02 else .12)
    return out * 1.4

def hat(open_=False):
    n = int((.2 if open_ else .05) * SR)
    return hp(rng.uniform(-1, 1, n), 7000) * env(n, .0005, .08 if open_ else .012)

def dhol_dha():
    n = int(.35 * SR); t = np.arange(n) / SR
    f = 70 + 40 * np.exp(-t / .04)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .001, .18)
    s += lp(rng.uniform(-1, 1, n), 400) * env(n, .001, .03) * 2
    return np.tanh(s * 1.5)

def dhol_ta():
    n = int(.15 * SR); t = np.arange(n) / SR
    f = 380 + 260 * np.exp(-t / .01)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, .0005, .045)
    s += bp(rng.uniform(-1, 1, n), 1500, 6000) * env(n, .0005, .02) * 1.2
    return s

def sitarish(freq, dur=.45):
    """Karplus-Strong pluck with a buzzing 'jawari' bridge for a sitar-ish twang."""
    n = int(dur * SR); p = max(2, int(SR / freq))
    buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        v = buf[i % p]
        nxt = .5 * (v + buf[(i + 1) % p]) * .996
        buf[i % p] = nxt
        out[i] = v
    out = out + .35 * np.tanh(out * 6) * env(n, .001, .12)    # bridge buzz
    return hp(out, 180) * env(n, .001, .35)

def whoosh(dur=.18):
    n = int(dur * SR); x = rng.uniform(-1, 1, n)
    out = np.zeros(n); seg = n // 8
    for k in range(8):
        lo = 300 + k * 700
        out[k * seg:(k + 1) * seg] = bp(x[k * seg:(k + 1) * seg], lo, lo + 1500)
    return out * np.linspace(0, 1, n) ** 2 * .7

def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 180 * (8 ** (t / dur))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * .25
    s += hp(rng.uniform(-1, 1, n), 2500) * .35
    return s * (t / dur) ** 2

def click():
    n = int(.012 * SR); return hp(rng.uniform(-1, 1, n), 3000) * env(n, .0003, .003)

def note(name):
    names = {"C": 0, "C#": 1, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
    return 440 * 2 ** ((names[name[:-1]] + 12 * (int(name[-1]) + 1) - 69) / 12)

# ---------------- arrangement ----------------
BPM = 140; beat = 60 / BPM; step = beat / 4          # 16th note
GRID0 = cuts[1]                                         # beat starts on "U GOT INVITED"

# pov: typing clicks + low drone
for k in range(4): add(click(), k * .13 + .02, .9, -.3 + .2 * k)
drone_n = int(GRID0 * SR); tt = np.arange(drone_n) / SR
add(np.sin(2 * np.pi * 73.4 * tt) * np.minimum(1, tt / .4) * .18, 0)

# impacts on every cut (the edit's punch)
for c in cuts[1:-1]:
    add(whoosh(), c - .18, .55)
for c in cuts[1:11]:
    add(kick(), c, .5)

# groove (pre-drop) and drop
bass_pre = ["D2", "D2", "Eb2", "D2"]
bass_drop = ["D2", "Eb2", "C2", "D2"]
mel = ["D5", "Eb5", "F#5", "Eb5", "D5", None, "A4", "Bb4", "A4", None, "G4", "F#4", "G4", "A4", None, "D5"]
mel_hi = ["A5", "Bb5", "A5", "F#5", "G5", None, "F#5", "Eb5", "D5", None, "Eb5", "F#5", "G5", "F#5", "Eb5", "D5"]

pre_end = T_FINAL - 1.25
def groove(start, end, drop):
    i = 0; t = start
    while t < end - 1e-6:
        s16 = i % 16; bar = i // 16
        if s16 in (0, 10) or (drop and s16 == 7): add(kick(), t, .85)
        if s16 == 8: add(clap(), t, .55)
        if s16 % 2 == 0 or (drop and s16 in (13, 15)): add(hat(), t, .22, .25)
        if drop and s16 in (14,): add(hat(True), t, .18, .25)
        # bhangra-ish dhol chaal over the trap kit
        if s16 in (0, 6, 12): add(dhol_dha(), t, .55, -.15)
        if s16 in (3, 4, 9, 11, 15): add(dhol_ta(), t, .45, .3)
        if s16 == 0:
            roots = bass_drop if drop else bass_pre
            add(b808(note(roots[bar % 4]), beat * 3.5, glide_from=note(roots[(bar - 1) % 4]) if drop else None), t, .9)
        if s16 % 2 == 0:
            seq = mel_hi if (drop and bar % 2) else mel
            nm = seq[(s16 // 2) + 8 * (bar % 2)]
            if nm: add(sitarish(note(nm), .5), t, .55, .2 if s16 % 4 else -.2)
        i += 1; t += step

groove(GRID0, pre_end, False)
# build: dhol rolls speeding up + riser, then a breath of silence before the drop
add(riser(1.1), T_FINAL - 1.15, .8)
t = pre_end
for k in range(14):
    add(dhol_ta(), t, .35 + k * .03, .3 if k % 2 else -.3)
    t += step * (1 - k * .045)
    if t > T_FINAL - .12: break
add(kick(.9), T_FINAL, 1.1)
add(b808(note("D1") * 2, 1.2, glide_from=note("D3")), T_FINAL, 1.0)
add(clap(), T_FINAL, .6)
groove(T_FINAL, TOTAL, True)

# master: glue + fade out
mix = np.stack([L, R], 1)[: int(TOTAL * SR)]
fade = int(.8 * SR); mix[-fade:] *= np.linspace(1, 0, fade)[:, None] ** 1.5
mix = np.tanh(mix / (np.max(np.abs(mix)) * .55)) * .92
wavfile.write(os.path.join(HERE, "beat.wav"), SR, (mix * 32767).astype(np.int16))
print("ok", TOTAL, "s", "drop at", T_FINAL)
