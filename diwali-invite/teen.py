"""Teen Diwali party invite — fast-cut 'edit' style, ends on a sticker-bombed info card."""
import math, random, os, shutil, subprocess, sys
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "frames3"); shutil.rmtree(OUT, ignore_errors=True); os.makedirs(OUT)
W, H, S = 540, 960, 2
FPS = 15
FD = os.path.join(HERE, "fonts")

ACID = (198, 255, 0); HOT = (255, 45, 149); BLUE = (45, 91, 255); ORANGE = (255, 107, 0)
INK = (14, 14, 14); WHITE = (255, 255, 255); CREAM = (255, 246, 230); LILAC = (190, 160, 255)

@lru_cache(None)
def F(name, size): return ImageFont.truetype(os.path.join(FD, name), int(size * S))
ANTON, ARCH, RUBIK, MARK, BUNGEE = "Anton-Regular.ttf", "ArchivoBlack-Regular.ttf", "RubikMonoOne-Regular.ttf", "PermanentMarker-Regular.ttf", "Bungee-Regular.ttf"
EMO = ImageFont.truetype(os.path.join(FD, "NotoColorEmoji.ttf"), 109)

@lru_cache(None)
def emoji(ch, size):
    im = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((10, 10), ch, font=EMO, embedded_color=True)
    im = im.crop(im.getbbox())
    k = size * S / max(im.size)
    return im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)

@lru_cache(None)
def shades_diya(size):
    """original mascot: the diya emoji wearing sunglasses"""
    d = emoji("🪔", size).copy(); w, h = d.size; dr = ImageDraw.Draw(d)
    y0, y1 = h * .58, h * .78
    for (x0, x1) in ((w * .14, w * .40), (w * .46, w * .72)):
        dr.rounded_rectangle((x0, y0, x1, y1), radius=h * .07, fill=(10, 10, 10))
        dr.line((x0 + (x1 - x0) * .2, y0 + (y1 - y0) * .3, x0 + (x1 - x0) * .45, y0 + (y1 - y0) * .3), fill=(255, 255, 255), width=max(2, int(h * .03)))
    dr.line((w * .40, y0 + (y1 - y0) * .3, w * .46, y0 + (y1 - y0) * .3), fill=(10, 10, 10), width=max(2, int(h * .04)))
    return d

def sticker(im, border=7, shadow=True):
    """die-cut sticker: white outline + soft drop shadow"""
    b = max(2, int(border * S)); pad = b * 3
    base = Image.new("RGBA", (im.width + pad * 2, im.height + pad * 2), (0, 0, 0, 0))
    base.paste(im, (pad, pad), im)
    a = base.split()[3].filter(ImageFilter.MaxFilter(b * 2 + 1 if b % 2 == 0 else b * 2 + 1))
    out = Image.new("RGBA", base.size, (0, 0, 0, 0))
    if shadow:
        sh = Image.new("RGBA", base.size, (0, 0, 0, 0)); sh.putalpha(a.point(lambda v: int(v * .35)))
        sh = sh.filter(ImageFilter.GaussianBlur(b * .6))
        out.alpha_composite(sh, (int(b * .5), int(b * .9)))
    white = Image.new("RGBA", base.size, (255, 255, 255, 0)); white.putalpha(a)
    out = Image.alpha_composite(out, white)
    return Image.alpha_composite(out, base)

@lru_cache(None)
def text_img(s, font, size, fill, stroke=0, stroke_fill=None, pad=6):
    f = F(font, size)
    dmy = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    l, t, r, b = dmy.textbbox((0, 0), s, font=f, stroke_width=int(stroke * S))
    im = Image.new("RGBA", (r - l + pad * 2 * S, b - t + pad * 2 * S), (0, 0, 0, 0))
    ImageDraw.Draw(im).text((-l + pad * S, -t + pad * S), s, font=f, fill=fill, stroke_width=int(stroke * S), stroke_fill=stroke_fill)
    return im

def put(canvas, im, cx, cy, rot=0, scale=1.0):
    if scale < .03: return
    if scale != 1.0: im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if rot: im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    canvas.alpha_composite(im, (int(cx * S - im.width / 2), int(cy * S - im.height / 2)))

def chip(text, font, size, fg, bg, padx=16, pady=10, radius=14, outline=INK):
    t = text_img(text, font, size, fg, pad=0)
    im = Image.new("RGBA", (t.width + padx * 2 * S, t.height + pady * 2 * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, im.width - 1, im.height - 1), radius=radius * S, fill=bg, outline=outline, width=3 * S)
    im.alpha_composite(t, (padx * S, pady * S)); return im

def back(x, k=2.2): x -= 1; return 1 + (k + 1) * x ** 3 + k * x ** 2
def cl(x): return max(0.0, min(1.0, x))

rnd = random.Random(3)

# ---------------- scenes: each gets (canvas, u in 0..1, frame_in_scene) ----------------
def s_pov(c, u, i):
    c.paste(INK, (0, 0, W * S, H * S))
    txt = "pov:"; n = min(len(txt), int(u * 7) + 1)
    t = text_img(txt[:n] + ("|" if i % 4 < 2 else " "), ARCH, 64, WHITE)
    c.alpha_composite(t, (60 * S, 400 * S))
    put(c, text_img("(no sound needed. it's a gif bestie)", ARCH, 15, (120, 120, 120)), W / 2, 880)

def s_invited(c, u, i):
    c.paste(ACID, (0, 0, W * S, H * S))
    put(c, text_img("U GOT", ANTON, 120, INK), W / 2, 360, rot=-4, scale=back(cl(u * 3)) if u < .34 else 1)
    if u > .25: put(c, text_img("INVITED", ANTON, 150, INK), W / 2, 530, rot=3, scale=back(cl((u - .25) * 3)))
    if u > .5: put(c, sticker(emoji("👀", 80)), 420, 220, rot=12)

def s_flash(c, u, i):
    c.paste(WHITE if i == 0 else HOT, (0, 0, W * S, H * S))

def s_lit(c, u, i):
    c.paste(HOT, (0, 0, W * S, H * S))
    put(c, text_img("to the", MARK, 54, WHITE), W / 2, 230, rot=-6)
    if u > .15: put(c, text_img("MOST", ANTON, 170, INK), W / 2, 420, scale=back(cl((u - .15) * 4)))
    if u > .4: put(c, text_img("LIT", ANTON, 250, WHITE, stroke=5, stroke_fill=INK), W / 2, 660, rot=-3, scale=back(cl((u - .4) * 4)))
    for k, (x, y, r) in enumerate([(90, 600, -15), (455, 560, 14), (270, 845, 0)]):
        if u > .55 + k * .12: put(c, emoji("🔥", 90), x, y, rot=r, scale=back(cl((u - .55 - k * .12) * 6)))

def s_diwali(c, u, i):
    c.paste(BLUE, (0, 0, W * S, H * S))
    rows = 7
    for r in range(rows):
        y = 120 + r * 120
        dx = (u * 160 - 80) * (1 if r % 2 else -1)
        filled = r == 3
        t = text_img("DIWALI", ANTON, 118, WHITE if filled else BLUE, stroke=0 if filled else 3, stroke_fill=WHITE)
        put(c, t, W / 2 + dx, y)
    if u > .3: put(c, sticker(shades_diya(150)), 400, 760, rot=-10, scale=back(cl((u - .3) * 4)))

def s_party(c, u, i):
    c.paste(INK, (0, 0, W * S, H * S))
    cols = [ACID, HOT, ORANGE, BLUE, WHITE]
    for k, ch in enumerate("PARTY"):
        p = cl((u - k * .1) * 4)
        if p <= 0: continue
        y = 470 - (1 - back(p, 1.4)) * 400
        put(c, text_img(ch, RUBIK, 92, cols[k], stroke=2, stroke_fill=INK), 70 + k * 100, y, rot=(-8, 6, -4, 9, -6)[k])
    if u > .6:
        for (x, y, s) in [(80, 300, 50), (460, 330, 70), (260, 650, 60), (470, 640, 40)]:
            put(c, emoji("✨", s), x, y, scale=.6 + .4 * abs(math.sin(i * 1.3 + x)))

def s_date(c, u, i):
    c.paste(ORANGE, (0, 0, W * S, H * S))
    # tear-off calendar sticker
    cal = Image.new("RGBA", (300 * S, 330 * S), (0, 0, 0, 0)); d = ImageDraw.Draw(cal)
    d.rounded_rectangle((0, 0, cal.width - 1, cal.height - 1), radius=26 * S, fill=WHITE, outline=INK, width=4 * S)
    d.rounded_rectangle((0, 0, cal.width - 1, 80 * S), radius=26 * S, fill=HOT, outline=INK, width=4 * S)
    d.rectangle((4 * S, 50 * S, cal.width - 5 * S, 78 * S), fill=HOT)
    d.line((0, 80 * S, cal.width, 80 * S), fill=INK, width=4 * S)
    t = text_img("NOV", ANTON, 50, WHITE, pad=0); cal.alpha_composite(t, ((cal.width - t.width) // 2, 14 * S))
    t = text_img("6", ANTON, 190, INK, pad=0); cal.alpha_composite(t, ((cal.width - t.width) // 2, 105 * S))
    put(c, sticker(cal, 3), W / 2, 430, rot=-7, scale=back(cl(u * 3)))
    if u > .35: put(c, chip("FRIDAY", ANTON, 46, INK, ACID), W / 2 + 40, 680, rot=6, scale=back(cl((u - .35) * 4)))

def s_time(c, u, i):
    c.paste(ACID, (0, 0, W * S, H * S))
    put(c, text_img("6PM", ANTON, 215, INK), W / 2, 400, rot=-3, scale=back(cl(u * 3.5)))
    if u > .35:
        put(c, text_img("till the snacks", MARK, 46, HOT), W / 2, 620, rot=-4)
        put(c, text_img("run out", MARK, 46, HOT), W / 2 + 30, 685, rot=-4)
    if u > .55: put(c, sticker(emoji("🍿", 80)), 120, 800, rot=-14)

def s_dress(c, u, i):
    c.paste(LILAC, (0, 0, W * S, H * S))
    put(c, text_img("dress code:", ARCH, 44, INK), W / 2, 330)
    if u > .2:
        put(c, chip("MAIN", ANTON, 120, INK, WHITE, padx=24, pady=6), W / 2, 470, rot=-4, scale=back(cl((u - .2) * 4)))
    if u > .4:
        put(c, chip("CHARACTER", ANTON, 84, WHITE, HOT, padx=22, pady=6), W / 2, 620, rot=3, scale=back(cl((u - .4) * 4)))
    if u > .6: put(c, emoji("💅", 80), 450, 760, rot=10)

def marquee(c, y, text, fg, bg, t, speed, rot):
    band = Image.new("RGBA", (int(W * 1.4) * S, 54 * S), bg + (255,))
    ti = text_img(text, ANTON, 34, fg, pad=0)
    off = int((t * speed * S) % ti.width)
    x = -off
    while x < band.width:
        band.alpha_composite(ti, (x, (band.height - ti.height) // 2)); x += ti.width
    d = ImageDraw.Draw(band); d.line((0, 0, band.width, 0), fill=INK, width=3 * S); d.line((0, band.height - 2 * S, band.width, band.height - 2 * S), fill=INK, width=3 * S)
    put(c, band, W / 2, y, rot=rot)

def s_final(c, u, i, t):
    c.paste(INK, (0, 0, W * S, H * S))
    d = ImageDraw.Draw(c)
    for gx in range(0, W, 36):          # graph-paper grid, like a notebook doodle page
        d.line((gx * S, 0, gx * S, H * S), fill=(34, 34, 40), width=S)
    for gy in range(0, H, 36):
        d.line((0, gy * S, W * S, gy * S), fill=(34, 34, 40), width=S)
    intro = lambda k: back(cl((u * 4.0 - k * .12) * 2.2))
    marquee(c, 70, "DIWALI PARTY  •  YOU'RE INVITED  •  ", INK, ACID, t, 90, -3)
    put(c, text_img("DIWALI", ANTON, 150, INK, stroke=4, stroke_fill=HOT), W / 2 - 10, 225, rot=-5, scale=intro(0))
    put(c, text_img("PARTY", RUBIK, 82, ACID, stroke=3, stroke_fill=INK), W / 2 + 10, 365, rot=4, scale=intro(1))
    bob = math.sin(t * 6) * 6
    put(c, sticker(shades_diya(140)), 400, 500 + bob, rot=-8 + math.sin(t * 6) * 4, scale=intro(2))
    put(c, chip("FRI · 6 NOV", ANTON, 52, INK, WHITE), 175, 500, rot=-6, scale=intro(3))
    put(c, chip("6PM → TILL THE SNACKS RUN OUT", ANTON, 30, WHITE, HOT), W / 2, 628, rot=3, scale=intro(4))
    put(c, chip("DRESS CODE: MAIN CHARACTER", ANTON, 30, WHITE, BLUE), W / 2 - 6, 712, rot=-2, scale=intro(5))
    put(c, text_img("be there or be a sad diya", MARK, 30, WHITE), W / 2 - 20, 805, rot=-4, scale=intro(6))
    put(c, emoji("🥲", 34), 470, 795, scale=intro(6))
    marquee(c, 895, "NO CAP  •  BRING UR BESTIES  •  SPARKLERS  •  SNACKS  •  PICS  •  ", WHITE, HOT, t, -110, 2)
    for (x, y, s, ph) in [(60, 330, 46, 0), (495, 165, 40, 1.7), (40, 640, 36, 3), (500, 400, 30, 4.4), (90, 810, 30, 2.2)]:
        k = .55 + .45 * abs(math.sin(t * 4 + ph))
        put(c, emoji("✨", s), x, y, scale=k * intro(2))
    put(c, emoji("🎆", 62), 470, 300, rot=10, scale=intro(3))

SCENES = [(s_pov, .6), (s_invited, .7), (s_flash, .14), (s_lit, .85), (s_diwali, 1.0), (s_flash, .14), (s_party, .85),
          (s_date, .7), (s_time, .7), (s_dress, .7), (s_flash, .14), ("final", 4.2)]

def render():
    frames = []
    for fn, dur in SCENES:
        n = max(1, round(dur * FPS))
        for i in range(n):
            frames.append((fn, i / max(1, n - 1) if n > 1 else 0, i, n))
    total = len(frames)
    for k, (fn, u, i, n) in enumerate(frames):
        t = k / FPS
        c = Image.new("RGBA", (W * S, H * S), INK + (255,))
        if fn == "final": s_final(c, u, i, t)
        else: fn(c, u, i)
        img = c.convert("RGB")
        # edit energy: punch-in zoom + shake on the first frames of every cut
        if fn != "final" and fn is not s_flash and i < 3:
            z = 1 + (3 - i) * .03
            cw, chh = int(W * S / z), int(H * S / z)
            ox = (W * S - cw) // 2 + rnd.randint(-8, 8) * S; oy = (H * S - chh) // 2 + rnd.randint(-8, 8) * S
            ox = max(0, min(W * S - cw, ox)); oy = max(0, min(H * S - chh, oy))
            img = img.crop((ox, oy, ox + cw, oy + chh)).resize((W * S, H * S))
        img.resize((W, H), Image.LANCZOS).save(os.path.join(OUT, f"f{k:04d}.png"))
    return total

if __name__ == "__main__":
    n = render(); print(n, "frames")
    src = os.path.join(OUT, "f%04d.png")
    gif = os.path.join(HERE, "teen_invite.gif"); mp4 = os.path.join(HERE, "teen_invite.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", src, "-vf",
                    "split[a][b];[a]palettegen=max_colors=200:stats_mode=full[p];[b][p]paletteuse=dither=none:diff_mode=rectangle",
                    "-loop", "0", gif], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", src, "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "17", "-movflags", "+faststart", mp4], check=True)
    print(os.path.getsize(gif) / 1e6, "MB")
