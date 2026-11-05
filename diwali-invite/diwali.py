import math, random, os, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "frames"); shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)

W, H, S = 720, 960, 2          # final size, supersample factor
FPS, DUR = 15, 8.0
N = int(FPS * DUR)

# palette — flat, saturated, festive
BG = (22, 9, 52); BG2 = (38, 14, 82)
GOLD = (255, 196, 61); MARI = (255, 140, 26); MARI2 = (255, 205, 40)
PINK = (255, 46, 136); TEAL = (20, 196, 170); CREAM = (255, 240, 214)
CLAY = (196, 72, 22); CLAY_D = (130, 40, 12); LEAF = (46, 160, 80)
PURP = (48, 16, 100)

FD = os.path.join(HERE, "fonts")
ROZHA = os.path.join(FD, "RozhaOne-Regular.ttf")
INTER_B = "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf"
INTER_S = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
def F(path, size): return ImageFont.truetype(path, int(size * S))

f_hindi = F(ROZHA, 46); f_title = F(ROZHA, 96); f_sub = F(INTER_S, 17)
f_date = F(ROZHA, 44); f_time = F(INTER_B, 22); f_foot = F(INTER_S, 15)

def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return cl((t - a) / (b - a))
def ease_out(x): return 1 - (1 - x) ** 3
def ease_io(x): return 3 * x * x - 2 * x * x * x
def back(x, k=1.7): x -= 1; return 1 + (k + 1) * x ** 3 + k * x ** 2
def P(*v): return [c * S for c in v]
def mix(c1, c2, a): return tuple(int(c1[i] + (c2[i] - c1[i]) * a) for i in range(3))
def alpha(c, a): return (*c[:3], int(255 * cl(a)))

rnd = random.Random(7)
stars = [(rnd.uniform(30, 690), rnd.uniform(130, 700), rnd.uniform(0.8, 2.0), rnd.uniform(0, 6.28)) for _ in range(55)]

# fireworks: (t0, x, y, colour, particles)
bursts = []
spots = [(100, 380), (622, 350), (96, 610), (626, 620), (104, 495), (616, 485), (96, 360)]
cols = [GOLD, PINK, TEAL, CREAM, MARI2, PINK, TEAL]
for i, t0 in enumerate([3.3, 3.9, 4.6, 5.2, 5.8, 6.4, 6.9]):
    x, y = spots[i]
    parts = []
    n = 26
    for k in range(n):
        a = 2 * math.pi * k / n + rnd.uniform(-.08, .08)
        sp = rnd.uniform(55, 78)
        parts.append((a, sp))
    bursts.append((t0, x, y, cols[i], parts))

def petal(d, cx, cy, ang, r0, r1, w, fill, line):
    pts = []
    steps = 14
    for side in (1, -1):
        rng = range(steps + 1) if side == 1 else range(steps, -1, -1)
        for i in rng:
            s = i / steps
            x = r0 + (r1 - r0) * s
            y = side * w * math.sin(math.pi * s) ** 0.75 * (1 - 0.35 * s)
            pts.append((cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)))
    pts = [(px * S, py * S) for px, py in pts]
    d.polygon(pts, fill=fill, outline=line, width=int(2 * S))

def dot(d, x, y, r, fill):
    d.ellipse(P(x - r, y - r, x + r, y + r), fill=fill)

def draw_toran(d, t):
    # top string
    d.line([(0, 18 * S), (W * S, 18 * S)], fill=GOLD, width=3 * S)
    xs = list(range(30, W, 52))
    for j, x in enumerate(xs):
        sway = math.sin(t * 2.4 + j * 0.7) * 0.06
        length = 4 if j % 2 == 0 else 2
        for k in range(length):
            ln = 16 + k * 17
            bx = x + math.sin(sway) * ln; by = 18 + math.cos(sway) * ln
            c = MARI if (k + j) % 2 == 0 else MARI2
            dot(d, bx, by, 9, c)
            dot(d, bx, by, 5.5, mix(c, (200, 60, 0), .35))
            dot(d, bx, by, 2.5, c)
        if j < len(xs) - 1:  # mango leaf between strands
            lx = x + 26
            petal(d, lx, 18, math.pi / 2 + math.sin(t * 2 + j) * 0.08, 0, 30, 8, LEAF, (20, 110, 50))

def draw_diya(d, gd, x, y, lit, t, i):
    # bowl
    d.chord(P(x - 34, y - 24, x + 34, y + 22), 0, 180, fill=CLAY)
    d.polygon([((x + 26) * S, (y - 2) * S), ((x + 44) * S, (y - 10) * S), ((x + 30) * S, (y + 8) * S)], fill=CLAY)
    d.line([((x - 34) * S, (y - 1) * S), ((x + 34) * S, (y - 1) * S)], fill=CLAY_D, width=3 * S)
    for k in range(5):
        dot(d, x - 20 + k * 10, y + 9, 2.6, [GOLD, TEAL, PINK, TEAL, GOLD][k])
    d.chord(P(x - 34, y - 26, x + 34, y + 4), 180, 360, fill=CLAY_D)   # rim/oil
    dot(d, x + 36, y - 10, 2, (60, 20, 5))
    if lit <= 0: return
    fl = 1 + 0.12 * math.sin(t * 19 + i * 2.1) + 0.06 * math.sin(t * 31 + i)
    h = 34 * ease_out(lit) * fl; wv = 11 * ease_out(lit)
    sway = math.sin(t * 7 + i) * 3
    fx, fy = x + 38, y - 12
    gr = 46 * ease_out(lit) * (0.92 + 0.08 * fl)
    gd.ellipse(P(fx - gr, fy - h * .6 - gr, fx + gr, fy - h * .6 + gr), fill=(255, 150, 30, 150))
    def flame(hh, ww, col):
        pts = []
        for k in range(21):
            s = k / 20
            yy = fy - hh * s
            xx = ww * math.sin(math.pi * s ** 0.7) * (1 - s) ** 0.5
            pts.append(((fx + xx + sway * s * s) * S, yy * S))
        for k in range(20, -1, -1):
            s = k / 20
            yy = fy - hh * s
            xx = ww * math.sin(math.pi * s ** 0.7) * (1 - s) ** 0.5
            pts.append(((fx - xx + sway * s * s) * S, yy * S))
        d.polygon(pts, fill=col)
    flame(h, wv, MARI); flame(h * .72, wv * .62, MARI2); flame(h * .4, wv * .32, CREAM)

def text_c(d, y, s, font, fill, spacing=0, anchor="ms"):
    if spacing:
        widths = [d.textlength(ch, font=font) for ch in s]
        total = sum(widths) + spacing * S * (len(s) - 1)
        x = (W * S - total) / 2
        for ch, w in zip(s, widths):
            d.text((x, y * S), ch, font=font, fill=fill, anchor="ls"); x += w + spacing * S
    else:
        d.text((W * S / 2, y * S), s, font=font, fill=fill, anchor=anchor)

def frame(t):
    img = Image.new("RGBA", (W * S, H * S), BG + (255,))
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img, "RGBA"); gd = ImageDraw.Draw(glow)

    # ground band behind diyas
    d.rectangle(P(0, 812, W, H), fill=BG2)
    for k in range(0, W, 24):   # zig-zag edge (rangoli border)
        d.polygon([(k * S, 812 * S), ((k + 12) * S, 800 * S), ((k + 24) * S, 812 * S)], fill=BG2)
    for k in range(12, W, 24):
        dot(d, k, 822, 2.2, PINK if (k // 24) % 2 else TEAL)

    # stars
    for (sx, sy, r, ph) in stars:
        a = 0.35 + 0.65 * (0.5 + 0.5 * math.sin(t * 3 + ph))
        dot(d, sx, sy, r, mix(BG, CREAM, a))

    # fireworks
    for (t0, bx, by, col, parts) in bursts:
        dt = t - t0
        if -0.45 < dt < 0:   # rocket
            ry = by + (-dt / 0.45) * 260
            d.line(P(bx, ry, bx, ry + 26), fill=alpha(GOLD, .9), width=3 * S)
            dot(d, bx, ry, 3, CREAM)
        elif 0 <= dt < 1.3:
            fade = 1 - dt / 1.3
            if dt < 0.12:
                gd.ellipse(P(bx - 60, by - 60, bx + 60, by + 60), fill=(*col, int(170 * (1 - dt / .12))))
            for (a, sp) in parts:
                r1 = sp * (1 - math.exp(-dt * 3.2)) / 1.0
                r0 = sp * (1 - math.exp(-max(0, dt - .18) * 3.2))
                g = 26 * dt * dt
                x1, y1 = bx + math.cos(a) * r1, by + math.sin(a) * r1 + g
                x0, y0 = bx + math.cos(a) * r0, by + math.sin(a) * r0 + g * .7
                d.line(P(x0, y0, x1, y1), fill=alpha(col, fade ** .5), width=int(3 * S))
                dot(d, x1, y1, 3 * fade + .8, alpha(CREAM, fade ** .4))

    # border
    d.rounded_rectangle(P(14, 60, W - 14, H - 14), radius=22 * S, outline=mix(BG, GOLD, .55), width=2 * S)

    # ---- rangoli clock ----
    cx, cy = 360, 480
    rot = t * 0.12
    b1 = back(seg(t, 0.15, 0.95)); b2 = back(seg(t, 0.35, 1.15)); b3 = back(seg(t, 0.55, 1.35))
    bd = ease_out(seg(t, 0.75, 1.5))
    if b1 > 0:
        for k in range(16):
            a = rot + 2 * math.pi * k / 16
            petal(d, cx, cy, a, 92 * b1, 170 * b1, 25 * b1, TEAL, CREAM)
    if b2 > 0:
        for k in range(16):
            a = -rot * 1.4 + 2 * math.pi * (k + .5) / 16
            petal(d, cx, cy, a, 84 * b2, 146 * b2, 20 * b2, PINK, CREAM)
    if b3 > 0:
        for k in range(8):
            a = rot * 2 + 2 * math.pi * k / 8
            petal(d, cx, cy, a, 58 * b3, 120 * b3, 32 * b3, MARI, CREAM)
            dot(d, cx + math.cos(a) * 98 * b3, cy + math.sin(a) * 98 * b3, 5 * b3, MARI2)
    if bd > 0:
        n = 36
        for k in range(int(n * bd)):
            a = -rot + 2 * math.pi * k / n
            dot(d, cx + math.cos(a) * 184, cy + math.sin(a) * 184, 4 if k % 2 else 2.5, GOLD if k % 2 else CREAM)
    dial = back(seg(t, 0.5, 1.2))
    if dial > 0:
        R = 76 * dial
        d.ellipse(P(cx - R, cy - R, cx + R, cy + R), fill=PURP, outline=GOLD, width=4 * S)
        for h in range(12):
            a = -math.pi / 2 + 2 * math.pi * h / 12
            big = h % 3 == 0
            col = PINK if h == 6 else (GOLD if big else CREAM)
            rr = (6 if h == 6 else 4.5 if big else 2.5) * dial
            dot(d, cx + math.cos(a) * 60 * dial, cy + math.sin(a) * 60 * dial, rr, col)
        # hands sweep to 6:00
        s = ease_io(seg(t, 1.0, 3.0))
        settle = math.sin(seg(t, 3.0, 3.5) * math.pi * 3) * (1 - seg(t, 3.0, 3.5)) * 0.08
        ha = -math.pi / 2 + math.radians(60 + 120 * s) + settle
        ma = -math.pi / 2 + 2 * math.pi * 4 * s + settle * 2
        d.line(P(cx, cy, cx + math.cos(ma) * 50 * dial, cy + math.sin(ma) * 50 * dial), fill=CREAM, width=4 * S)
        d.line(P(cx, cy, cx + math.cos(ha) * 34 * dial, cy + math.sin(ha) * 34 * dial), fill=GOLD, width=7 * S)
        dot(d, cx, cy, 7 * dial, PINK); dot(d, cx, cy, 3 * dial, CREAM)
        if t > 3.0:   # pulse at the 6
            p = 0.5 + 0.5 * math.sin((t - 3) * 5)
            gd.ellipse(P(cx - 22, cy + 60 - 22, cx + 22, cy + 60 + 22), fill=(255, 46, 136, int(120 + 100 * p)))

    # ---- text ----
    a_h = ease_out(seg(t, 0.2, 0.9))
    if a_h > 0:
        text_c(d, 128 + 14 * (1 - a_h), "दीपावली", f_hindi, alpha(GOLD, a_h), anchor="ms")
    a_t = ease_out(seg(t, 0.4, 1.2))
    if a_t > 0:
        y = 222 + 20 * (1 - a_t)
        text_c(d, y + 4, "Diwali Night", f_title, alpha(PINK, a_t))   # offset shadow = printed look
        text_c(d, y, "Diwali Night", f_title, alpha(CREAM, a_t))
    a_s = ease_out(seg(t, 0.8, 1.5))
    if a_s > 0:
        text_c(d, 262, "COME LIGHT UP THE NIGHT WITH US", f_sub, alpha(TEAL, a_s), spacing=3.2)

    a_d = ease_out(seg(t, 2.9, 3.6))
    if a_d > 0:
        y = 718 + 16 * (1 - a_d)
        text_c(d, y, "Friday, 6th November", f_date, alpha(CREAM, a_d))
        # time pill
        tw = 300; ty = y + 22
        d.rounded_rectangle(P(360 - tw / 2, ty, 360 + tw / 2, ty + 40), radius=20 * S, fill=alpha(PINK, a_d))
        text_c(d, ty + 28, "2026  ·  6 PM ONWARDS", f_time, alpha(CREAM, a_d), spacing=1.5)

    # ---- diyas ----
    xs = [80, 170, 260, 350, 440, 530, 620]
    for i, x in enumerate(xs):
        lit = seg(t, 1.4 + i * 0.22, 1.75 + i * 0.22)
        draw_diya(d, gd, x - 10, 880, lit, t, i)

    a_f = ease_out(seg(t, 3.4, 4.0))
    if a_f > 0:
        text_c(d, 940, "mithai  ·  music  ·  masti  ·  phuljhari", f_foot, alpha(mix(BG, GOLD, .85), a_f), spacing=1.2)

    draw_toran(d, t)

    glow = glow.filter(ImageFilter.GaussianBlur(18 * S))
    img = Image.alpha_composite(glow, img) if False else Image.alpha_composite(img, glow)
    # loop fade: last 0.4s dims everything back toward night
    fo = seg(t, DUR - 0.4, DUR)
    out = img.convert("RGB").resize((W, H), Image.LANCZOS)
    if fo > 0:
        out = Image.blend(out, Image.new("RGB", (W, H), BG), fo * .85)
    return out

if __name__ == "__main__":
    import sys
    only = sys.argv[1:] and [float(x) for x in sys.argv[1:]]
    if only:
        for tt in only: frame(tt).save(os.path.join(HERE, f"still_{tt}.png"))
    else:
        for i in range(N):
            frame(i / FPS).save(os.path.join(OUT, f"f{i:04d}.png"))
        hold = os.path.join(OUT, "f%04d.png")
        gif = os.path.join(HERE, "diwali_invite.gif")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", hold,
                        "-vf", "split[a][b];[a]palettegen=max_colors=192:stats_mode=full[p];[b][p]paletteuse=dither=sierra2_4a",
                        "-loop", "0", gif], check=True)
        mp4 = os.path.join(HERE, "diwali_invite.mp4")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", hold,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart", mp4], check=True)
        print(os.path.getsize(gif) / 1e6, "MB")
