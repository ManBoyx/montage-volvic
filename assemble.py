import glob, subprocess, sys
from plan import SCENES, TRANS, OFFSETS, TOTAL, FPS

files = sorted(glob.glob("work/s[0-9][0-9]_*.mp4"))
assert len(files) == len(SCENES), files
cmd = ["ffmpeg", "-v", "error", "-stats", "-y"]
for f in files:
    cmd += ["-i", f]
cmd += ["-i", "work/musique.wav"]
n = len(files)
parts, prev = [], "0:v"
for k, ((tr, dur), off) in enumerate(zip(TRANS, OFFSETS)):
    out = f"x{k+1}"
    parts.append(f"[{prev}][{k+1}:v]xfade=transition={tr}:duration={dur}:offset={off:.3f}[{out}]")
    prev = out
parts.append(f"[{prev}]eq=contrast=1.05:saturation=1.10:gamma=0.98,vignette=angle=0.6,"
             f"noise=alls=5:allf=t,subtitles=work/subs.ass,format=yuv420p[v]")
parts.append(f"[{n}:a]loudnorm=I=-16:TP=-1.5:LRA=9[a]")
cmd += ["-filter_complex", ";".join(parts), "-map", "[v]", "-map", "[a]",
        "-c:v", "libopenh264", "-b:v", "16M", "-maxrate", "24M", "-profile:v", "high", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-t", f"{TOTAL:.2f}", "-movflags", "+faststart", sys.argv[1]]
sys.exit(subprocess.run(cmd).returncode)
