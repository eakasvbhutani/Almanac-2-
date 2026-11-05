"""Long-exposure sparkler light-writing invite."""
import math, random, os, shutil, subprocess, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops
from HersheyFonts import HersheyFonts

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "frames2"); shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
W, H, S = 720, 960, 2
FPS, DUR = 15, 10.0
N = int(FPS * DUR)
WRITE_START, WRITE_END = 0.45, 7.4
rnd = random.Random(11)

hf = HersheyFonts(); hf.load_default_font("cursive")

def catmull(pts, sub=5):
    if len(pts) < 3: return pts
    out = []
    p = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = p[i - 1], p[i], p[i + 1], p[i + 2]
        for k in range(sub):
            t = k / sub; t2, t3 = t * t, t * t * t
            out.append(tuple(0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                                    + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3) for j in range(2)))
    out.append(pts[-1]); return out

def text_strokes(txt, cx, cy, width, tilt_deg):
    st = [list(s) for s in hf.strokes_for_text(txt)]
    xs = [p[0] for s in st for p in s]; ys = [p[1] for s in st for p in s]
    x0, x1 = min(xs), max(xs); ymid = (min(ys) + max(ys)) / 2
    sc = width / (x1 - x0); a = math.radians(tilt_deg)
    res = []
    for s in st:
        pts = []
        for (x, y) in s:
            u, v = (x - (x0 + x1) / 2) * sc, (y - ymid) * sc
            pts.append((cx + u * math.cos(a) - v * math.sin(a), cy + u * math.sin(a) + v * math.cos(a)))
        res.append(catmull(pts))
    return res

def star(cx, cy, r, rot=0):
    pts = [(cx + r * math.cos(rot - math.pi / 2 + k * 4 * math.pi / 5), cy + r * math.sin(rot - math.pi / 2 + k * 4 * math.pi / 5)) for k in range(6)]
    dense = []
    for i in range(5):
        for k in range(8):
            t = k / 8; dense.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t))
    dense.append(pts[5]); return [dense]

def swoosh(x0, x1, y):
    pts = []
    for k in range(60):
        t = k / 59
        pts.append((x0 + (x1 - x0) * t, y + 10 * math.sin(t * math.pi) - 14 * t * t))
    return [pts]

def arrow(x0, y0, x1, y1):
    shaft = [(x0 + (x1 - x0) * t / 20, y0 + (y1 - y0) * t / 20 + 4 * math.sin(t / 20 * math.pi)) for t in range(21)]
    a = math.atan2(y1 - y0, x1 - x0)
    head = [(x1 - 22 * math.cos(a - .5), y1 - 22 * math.sin(a - .5)), (x1, y1), (x1 - 22 * math.cos(a + .5), y1 - 22 * math.sin(a + .5))]
    head = [head[0]] + [(head[0][0] + (head[1][0] - head[0][0]) * k / 6, head[0][1] + (head[1][1] - head[0][1]) * k / 6) for k in range(1, 7)] + \
           [(head[1][0] + (head[2][0] - head[1][0]) * k / 6, head[1][1] + (head[2][1] - head[1][1]) * k / 6) for k in range(1, 7)]
    return [shaft, head]

# ---- the message, in writing order ----
GOLDT, PINKT, TEALT = "gold", "pink", "teal"
groups, gcol = [], []
def add(strokes, c):
    groups.extend(strokes); gcol.extend([c] * len(strokes))
add(text_strokes("diwali", 300, 196, 270, -7), GOLDT)
add(star(522, 160, 32, 0.2), PINKT)
add(text_strokes("party", 352, 352, 560, -5), GOLDT)
add(swoosh(140, 560, 452), PINKT)
add(text_strokes("fri 6th nov", 360, 590, 440, -3), GOLDT)
add(text_strokes("6pm", 268, 728, 210, -4), GOLDT)
add(arrow(400, 728, 540, 712), TEALT)

# wobble = human hand
def wobble(pts, seed):
    ph = seed * 1.7
    return [(x + 1.6 * math.sin(i * .21 + ph) + .8 * math.sin(i * .57 + ph * 2), y + 1.6 * math.cos(i * .17 + ph) + .8 * math.sin(i * .43 + ph)) for i, (x, y) in enumerate(pts)]
keep = [i for i, g in enumerate(groups) if len(g) > 1]
gcol = [gcol[i] for i in keep]
groups = [wobble(groups[i], i) for i in keep]

# timeline: build list of (x, y, drawing?) at constant speed
seq = []   # (t_end, p0, p1, draw)
def L(a, b): return math.hypot(b[0] - a[0], b[1] - a[1])
total_draw = sum(L(g[i], g[i + 1]) for g in groups for i in range(len(g) - 1))
total_jump = sum(L(groups[i][-1], groups[i + 1][0]) for i in range(len(groups) - 1))
JUMP_SPEEDUP = 3.0
span = WRITE_END - WRITE_START
v = (total_draw + total_jump / JUMP_SPEEDUP) / span
t = WRITE_START
for gi, g in enumerate(groups):
    if gi:
        a, b = groups[gi - 1][-1], g[0]
        t += L(a, b) / JUMP_SPEEDUP / v; seq.append((t, a, b, False, gi))
    for i in range(len(g) - 1):
        t += L(g[i], g[i + 1]) / v; seq.append((t, g[i], g[i + 1], True, gi))
all_trail_pts = [p for g in groups for p in g]

def head_at(tt):
    prev_t = WRITE_START
    for (te, a, b, dr, _) in seq:
        if tt <= te:
            f = (tt - prev_t) / max(1e-6, te - prev_t)
            return (a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f), dr
        prev_t = te
    return None, False

# ---- static background: warm night, bokeh fairy lights, grain ----
def make_bg():
    bg = Image.new("RGB", (W * S, H * S), (9, 6, 14))
    vg = Image.new("L", (W, H), 0); dv = ImageDraw.Draw(vg)
    for k in range(40):
        r = k / 40
        dv.ellipse((W / 2 - W * (1.0 - r * .6), H * .45 - H * (.9 - r * .5), W / 2 + W * (1.0 - r * .6), H * .45 + H * (.9 - r * .5)), fill=int(26 * r))
    vg = vg.filter(ImageFilter.GaussianBlur(40)).resize(bg.size)
    tint = Image.new("RGB", bg.size, (40, 14, 46))
    bg = Image.composite(tint, bg, vg)
    bok = Image.new("RGB", bg.size, (0, 0, 0)); db = ImageDraw.Draw(bok)
    palette = [(255, 170, 60), (255, 120, 40), (255, 60, 140), (60, 200, 200), (255, 210, 120), (190, 90, 255)]
    # string of fairy lights sagging across the top + scattered far lights
    for k in range(15):
        x = -20 + k * 54; y = 70 + 38 * math.sin(k / 14 * math.pi) + rnd.uniform(-6, 6)
        r = rnd.uniform(16, 30); c = palette[k % len(palette)]
        db.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=tuple(int(v * .42) for v in c), outline=tuple(int(v * .6) for v in c), width=2 * S)
    for k in range(22):
        x = rnd.uniform(0, W); y = rnd.uniform(780, 950); r = rnd.uniform(10, 34); c = rnd.choice(palette)
        db.ellipse(((x - r) * S, (y - r) * S, (x + r) * S, (y + r) * S), fill=tuple(int(v * .28) for v in c), outline=tuple(int(v * .4) for v in c), width=2 * S)
    bok = bok.filter(ImageFilter.GaussianBlur(7 * S))
    bg = ImageChops.add(bg, bok)
    # fixed film grain
    noise = Image.effect_noise(bg.size, 18).convert("RGB")
    bg = ImageChops.add(bg, ImageChops.multiply(noise, Image.new("RGB", bg.size, (14, 12, 16))))
    return bg

def seg7(d, x, y, ch, h, col, th):
    w = h * .55; segs = {
        'a': ((x, y), (x + w, y)), 'b': ((x + w, y), (x + w, y + h / 2)), 'c': ((x + w, y + h / 2), (x + w, y + h)),
        'd': ((x, y + h), (x + w, y + h)), 'e': ((x, y + h / 2), (x, y + h)), 'f': ((x, y), (x, y + h / 2)), 'g': ((x, y + h / 2), (x + w, y + h / 2))}
    m = {'0': 'abcdef', '1': 'bc', '2': 'abged', '3': 'abgcd', '4': 'fgbc', '5': 'afgcd', '6': 'afgedc', '7': 'abc', '8': 'abcdefg', '9': 'abcdfg'}
    if ch == "'":
        d.line(((x + w * .4) * S, y * S, (x + w * .2) * S, (y + h * .25) * S), fill=col, width=int(th * S)); return w * .5
    if ch == ' ': return w * .7
    for sname in m[ch]:
        (ax, ay), (bx, by) = segs[sname]
        sh = .14 * h  # shrink ends so segments look separate
        if ax == bx: ay += th * .6; by -= th * .6
        else: ax += th * .6; bx -= th * .6
        d.line((ax * S, ay * S, bx * S, by * S), fill=col, width=int(th * S))
    return w + h * .28

def make_overlay():
    """Things 'printed' on the photo: date stamp + exif caption. Drawn as light (screened)."""
    ov = Image.new("RGB", (W * S, H * S), (0, 0, 0)); d = ImageDraw.Draw(ov)
    x = 466; y = 880
    for ch in "6 11 '26":
        x += seg7(d, x, y, ch, 34, (255, 112, 40), 4.2)
    glow = ov.filter(ImageFilter.GaussianBlur(5 * S))
    ov = ImageChops.add(ov, glow)
    mono = ImageFont.truetype("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf", 14 * S)
    d = ImageDraw.Draw(ov)
    d.text((34 * S, 888 * S), "EXP 6:00PM → LATE", font=mono, fill=(150, 130, 150))
    d.text((34 * S, 908 * S), "BYO SPARKLERS · DRESS TO GLOW", font=mono, fill=(150, 130, 150))
    return ov

BG = make_bg(); OV = make_overlay()

core = Image.new("RGB", BG.size, (0, 0, 0)); dc = ImageDraw.Draw(core)
halo = Image.new("RGB", BG.size, (0, 0, 0)); dh = ImageDraw.Draw(halo)
drawn_upto = 0

def burn_until(tt):
    """Accumulate trail segments into the long-exposure canvases."""
    global drawn_upto
    while drawn_upto < len(seq) and seq[drawn_upto][0] <= tt:
        te, a, b, dr, gi = seq[drawn_upto]
        if dr:
            fl = 0.72 + 0.28 * math.sin(te * 41) * math.sin(te * 13)   # sparkler brightness flicker
            kind = gcol[gi]
            if kind == GOLDT: c, hc = (255, 238, int(170 + 60 * fl)), (255, 118, 18)
            elif kind == PINKT: c, hc = (255, 200, 230), (255, 30, 140)
            else: c, hc = (210, 255, 248), (0, 200, 190)
            dc.line((a[0] * S, a[1] * S, b[0] * S, b[1] * S), fill=c, width=int((2.6 + 1.6 * fl) * S))
            dh.line((a[0] * S, a[1] * S, b[0] * S, b[1] * S), fill=tuple(int(v * (0.7 + .3 * fl)) for v in hc), width=int(11 * S))
        drawn_upto += 1

def sparks(d, x, y, n, scale=1.0):
    for _ in range(n):
        a = rnd.uniform(0, 2 * math.pi); ln = rnd.uniform(6, 46) * scale * (rnd.random() ** .6)
        ex, ey = x + math.cos(a) * ln, y + math.sin(a) * ln + ln * ln * .004
        br = rnd.uniform(.6, 1)
        d.line((x * S, y * S, ex * S, ey * S), fill=(255, int(220 * br), int(140 * br)), width=int(1.3 * S))
        if rnd.random() < .45:   # forking sparks — the sparkler signature
            for sgn in (-1, 1):
                fa = a + sgn * rnd.uniform(.3, .8); fl_ = ln * rnd.uniform(.25, .5)
                d.line((ex * S, ey * S, (ex + math.cos(fa) * fl_) * S, (ey + math.sin(fa) * fl_) * S), fill=(255, 200, 110), width=int(1 * S))
                if rnd.random() < .5:
                    d.ellipse(((ex + math.cos(fa) * fl_ - 1.4) * S, (ey + math.sin(fa) * fl_ - 1.4) * S, (ex + math.cos(fa) * fl_ + 1.4) * S, (ey + math.sin(fa) * fl_ + 1.4) * S), fill=(255, 250, 220))

def twinkle(d, x, y, r, br):
    c = (int(255 * br), int(245 * br), int(220 * br))
    d.line(((x - r) * S, y * S, (x + r) * S, y * S), fill=c, width=int(1.6 * S))
    d.line((x * S, (y - r) * S, x * S, (y + r) * S), fill=c, width=int(1.6 * S))
    d.ellipse(((x - 2) * S, (y - 2) * S, (x + 2) * S, (y + 2) * S), fill=c)

tw_pts = [rnd.choice(all_trail_pts) for _ in range(60)]
tw_ph = [rnd.uniform(0, 1) for _ in tw_pts]

def frame(tt):
    burn_until(tt)
    sp = Image.new("RGB", BG.size, (0, 0, 0)); ds = ImageDraw.Draw(sp)
    head, drawing = head_at(tt)
    if head is not None:
        x, y = head
        sparks(ds, x, y, 95 if drawing else 60, 1.5)
        ds.ellipse(((x - 4) * S, (y - 4) * S, (x + 4) * S, (y + 4) * S), fill=(255, 255, 240))
    elif tt > WRITE_END:
        # the sparkler is set down; trails sparkle like it's still party time
        for p, ph in zip(tw_pts, tw_ph):
            k = ((tt * .9 + ph) % 1.0)
            if k < .25:
                twinkle(ds, p[0], p[1], 15 * math.sin(k / .25 * math.pi), math.sin(k / .25 * math.pi))
    halo_b = halo.filter(ImageFilter.GaussianBlur(11 * S))
    bloom = core.filter(ImageFilter.GaussianBlur(2.5 * S))
    spg = sp.filter(ImageFilter.GaussianBlur(6 * S))
    img = BG
    for layer in (halo_b, bloom, core, spg, sp, OV):
        img = ImageChops.screen(img, layer)
    if head is not None:   # local light cast by the sparkler
        lg = Image.new("RGB", BG.size, (0, 0, 0)); dl = ImageDraw.Draw(lg)
        dl.ellipse(((x - 110) * S, (y - 110) * S, (x + 110) * S, (y + 110) * S), fill=(70, 34, 10))
        img = ImageChops.screen(img, lg.filter(ImageFilter.GaussianBlur(50 * S)))
    out = img.resize((W, H), Image.LANCZOS)
    # camera shutter: curtains open at the start, snap shut at the end
    o = 1 - min(1, tt / .35) if tt < .35 else (min(1, (tt - (DUR - .3)) / .3) if tt > DUR - .3 else 0)
    if o > 0:
        e = o * o * (3 - 2 * o); hh = int(H / 2 * e)
        dd = ImageDraw.Draw(out); dd.rectangle((0, 0, W, hh), fill=(4, 3, 6)); dd.rectangle((0, H - hh, W, H), fill=(4, 3, 6))
    return out

if __name__ == "__main__":
    stills = [float(a) for a in sys.argv[1:]]
    if stills:
        for i in range(N):
            tt = i / FPS
            if any(abs(tt - s) < .5 / FPS for s in stills):
                frame(tt).save(os.path.join(HERE, f"sp_{s if False else round(tt,2)}.png"))
            else:
                burn_until(tt)
        sys.exit()
    for i in range(N):
        frame(i / FPS).save(os.path.join(OUT, f"f{i:04d}.png"))
    src = os.path.join(OUT, "f%04d.png")
    gif = os.path.join(HERE, "party_invite.gif"); mp4 = os.path.join(HERE, "party_invite.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", src, "-vf",
                    "split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle",
                    "-loop", "0", gif], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", src, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "17", "-movflags", "+faststart", mp4], check=True)
    print(os.path.getsize(gif) / 1e6, "MB")
