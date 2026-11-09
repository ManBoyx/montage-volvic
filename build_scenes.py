# Rend chaque scène en clip 1920x1080 / 30 fps : mouvements de caméra sur les photos,
# plans de drone recadrés (pour masquer l'incrustation d'origine) et ralentis.
import subprocess, sys
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageFilter, ImageEnhance
from plan import SCENES, FPS

W169, H169 = 3840, 2160


def crop169(src, dst, fx=0.5, fy=0.5):
    im = Image.open(src).convert("RGB")
    w, h = im.size
    if w / h > 16 / 9:
        nw = int(h * 16 / 9); x = int((w - nw) * fx); im = im.crop((x, 0, x + nw, h))
    else:
        nh = int(w * 9 / 16); y = int((h - nh) * fy); im = im.crop((0, y, w, y + nh))
    im.resize((W169, H169), Image.LANCZOS).save(dst, quality=95)


def bottle_composite(src, dst):
    im = Image.open(src).convert("RGB")
    bg = im.copy()
    s = W169 / bg.width
    bg = bg.resize((W169, int(bg.height * s)), Image.LANCZOS)
    top = int((bg.height - H169) * 0.45)
    bg = bg.crop((0, top, W169, top + H169)).filter(ImageFilter.GaussianBlur(70))
    bg = ImageEnhance.Brightness(bg).enhance(0.5)
    fh = 2100
    fg = im.resize((int(im.width * fh / im.height), fh), Image.LANCZOS)
    x, y = (W169 - fg.width) // 2, (H169 - fh) // 2
    pad = 220
    mask = Image.new("L", (fg.width + 2 * pad, fh + 2 * pad), 0)
    mask.paste(150, (pad, pad, pad + fg.width, pad + fh))
    mask = mask.filter(ImageFilter.GaussianBlur(90))
    bg.paste(Image.new("RGB", mask.size, (0, 0, 0)), (x - pad, y - pad + 30), mask)
    bg.paste(fg, (x, y))
    bg.save(dst, quality=95)


def zoompan(img, out, dur, z0, z1, fx0, fx1, fy0, fy1, extra=""):
    n = int(round(dur * FPS))
    e = f"st(0,on/{n-1});"
    ease = "(ld(0)*ld(0)*(3-2*ld(0)))"
    z = f"{z0}+({z1}-{z0})*{ease}"
    vf = (f"zoompan=z='{e}{z}':"
          f"x='{e}iw*(1-1/({z}))*({fx0}+({fx1}-{fx0})*{ease})':"
          f"y='{e}ih*(1-1/({z}))*({fy0}+({fy1}-{fy0})*{ease})':"
          f"d={n}:s=1920x1080:fps={FPS}{extra},format=yuv420p")
    run(["ffmpeg", "-v", "error", "-y", "-i", img, "-vf", vf, "-frames:v", str(n),
         "-c:v", "mpeg4", "-q:v", "2", out])


def drone_clip(ss, length, slow, out):
    vf = (f"crop=1440:810:240:0,scale=1920:1080:flags=lanczos,setpts={slow}*PTS,"
          f"minterpolate=fps={FPS}:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1,format=yuv420p")
    run(["ffmpeg", "-v", "error", "-y", "-ss", str(ss), "-t", str(length), "-i", "dl/video.webm",
         "-vf", vf, "-an", "-c:v", "mpeg4", "-q:v", "2", out])


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print("ECHEC", " ".join(cmd[:6]), r.stderr[-600:]); sys.exit(1)


def main():
    P = "work/"
    for name, fx, fy in [("chaine1", .5, .25), ("chaine2", .5, .35), ("chaine3", .5, .5), ("dome1", .5, .15),
                         ("dome2", .5, .35), ("pariou3", .5, .5), ("source1", .5, .5), ("source2", .5, .45), ("pariou2", .5, .5)]:
        crop169(f"dl/{name}.jpg", f"{P}{name}_169.jpg", fx, fy)
    bottle_composite("dl/bouteille.jpg", P + "bouteille_169.jpg")
    d = dict(SCENES)
    jobs = [
        lambda: zoompan(P + "bouteille_169.jpg", P + "s00_bouteille.mp4", d["bouteille"], 1.0, 2.45, .5, .5, .5, .5),
        lambda: zoompan(P + "source2_169.jpg", P + "s01_source2.mp4", d["source2"], 1.0, 1.2, .25, .7, .6, .3),
        lambda: zoompan(P + "source1_169.jpg", P + "s02_source1.mp4", d["source1"], 1.22, 1.0, .5, .5, .4, .5),
        lambda: zoompan(P + "chaine1_169.jpg", P + "s03_chaine1.mp4", d["chaine1"], 1.0, 1.25, .15, .85, .6, .4),
        lambda: zoompan(P + "chaine2_169.jpg", P + "s05_chaine2.mp4", d["chaine2"], 1.28, 1.0, .65, .4, .35, .5),
        lambda: zoompan(P + "dome1_169.jpg", P + "s06_dome1.mp4", d["dome1"], 1.0, 1.32, .5, .33, .6, .0),
        lambda: zoompan(P + "dome2_169.jpg", P + "s07_dome2.mp4", d["dome2"], 1.0, 1.26, .7, .0, .5, .2),
        lambda: zoompan(P + "pariou3_169.jpg", P + "s09_pariou3.mp4", d["pariou3"], 1.0, 1.38, .5, .65, .3, .75),
        lambda: zoompan(P + "pariou2_169.jpg", P + "s10_pariou2.mp4", d["pariou2"], 1.25, 1.0, .2, .6, .5, .4),
        lambda: zoompan(P + "chaine3_169.jpg", P + "s11_chaine3.mp4", d["chaine3"], 1.3, 1.0, .9, .3, .0, .6),
        lambda: zoompan(P + "bouteille_169.jpg", P + "s12_outro.mp4", d["outro"], 2.45, 1.0, .5, .5, .5, .5),
        lambda: zoompan(P + "chaine1_169.jpg", P + "s13_credits.mp4", d["credits"], 1.0, 1.12, .5, .5, .5, .5,
                        extra=",gblur=sigma=14,eq=brightness=-0.30:saturation=0.75"),
        lambda: drone_clip(7.10, 1.75, 1.7, P + "dA.mp4"),
        lambda: drone_clip(9.05, 1.25, 1.7, P + "dA2.mp4"),
        lambda: drone_clip(10.45, 2.70, 1.7, P + "dB.mp4"),
        lambda: drone_clip(25.15, 1.50, 1.8, P + "dD1.mp4"),
        lambda: drone_clip(26.80, 2.10, 1.8, P + "dD2.mp4"),
    ]
    with ThreadPoolExecutor(4) as ex:
        list(ex.map(lambda f: f(), jobs))
    # scène « drone » : trois plans enchaînés en fondu court
    run(["ffmpeg", "-v", "error", "-y", "-i", P + "dA.mp4", "-i", P + "dA2.mp4", "-i", P + "dB.mp4",
         "-filter_complex",
         "[0][1]xfade=transition=fade:duration=0.25:offset=2.725[a];[a][2]xfade=transition=fade:duration=0.25:offset=4.575[b]",
         "-map", "[b]", "-t", str(d["drone"]), "-r", str(FPS), "-c:v", "mpeg4", "-q:v", "2",
         P + "s04_drone.mp4"])
    run(["ffmpeg", "-v", "error", "-y", "-i", P + "dD1.mp4", "-i", P + "dD2.mp4",
         "-filter_complex", "[0][1]xfade=transition=fade:duration=0.25:offset=2.45,tpad=stop_mode=clone:stop_duration=1[b]",
         "-map", "[b]", "-t", str(d["droneD"]), "-r", str(FPS), "-c:v", "mpeg4", "-q:v", "2", P + "s08_droneD.mp4"])
    print("scènes ok")


if __name__ == "__main__":
    main()
