# Musique d'ambiance composée pour le montage : numpy seulement.
# Progression Bm9 - Gmaj7 - Dmaj7 - A6, 72 bpm, un accord = 2 mesures.
import wave
import numpy as np
from plan import TOTAL, S, START

SR = 44100
LEN = TOTAL + 2.0
N = int(LEN * SR)
t = np.arange(N) / SR
rng = np.random.default_rng(7)

BEAT = 60 / 72
CH = 8 * BEAT                      # durée d'un accord
CHORDS = [                         # (notes du pad, fondamentale basse)
    ([54, 59, 62, 66, 73], 47),    # Bm9
    ([55, 59, 62, 66, 71], 43),    # Gmaj7
    ([57, 62, 66, 69, 73], 38),    # Dmaj7
    ([57, 61, 64, 69, 73], 45),    # A6
]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def smooth(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def ramp(t0, t1):
    return smooth((t - t0) / (t1 - t0))


def add(buf, start, sig, pan=0.5, gain=1.0):
    i = int(start * SR)
    if i >= N:
        return
    j = min(N, i + len(sig))
    s = sig[: j - i] * gain
    buf[0, i:j] += s * np.cos(pan * np.pi / 2)
    buf[1, i:j] += s * np.sin(pan * np.pi / 2)


def fft_band(x, lo, hi):
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0
    return np.fft.irfft(X, len(x))


wet = np.zeros((2, N))   # passera dans la réverbération
dry = np.zeros((2, N))

# ---- pad : accords qui se recouvrent -------------------------------------
n_ch = int(LEN / CH) + 1
for c in range(n_ch):
    notes, _ = CHORDS[c % 4]
    t0 = c * CH
    dur = CH + 2.6
    tt = np.arange(int(dur * SR)) / SR
    env = smooth(tt / 2.0) * smooth((dur - tt) / 2.6)
    for k, m in enumerate(notes):
        for det, pan in ((-3, 0.25 + 0.1 * (k % 3)), (+3, 0.75 - 0.1 * (k % 3))):
            f = hz(m) * 2 ** (det / 1200)
            vib = 1 + 0.0015 * np.sin(2 * np.pi * (0.2 + 0.03 * k) * tt + k)
            ph = 2 * np.pi * np.cumsum(f * vib) / SR
            sig = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph)
            add(wet, t0, sig * env, pan, 0.045)

# ---- basse ---------------------------------------------------------------
for c in range(n_ch):
    root = CHORDS[c % 4][1]
    t0 = c * CH
    tt = np.arange(int((CH + 0.8) * SR)) / SR
    env = smooth(tt / 0.4) * smooth((CH + 0.8 - tt) / 0.8)
    sig = np.sin(2 * np.pi * hz(root) * tt) + 0.25 * np.sin(4 * np.pi * hz(root) * tt)
    add(dry, t0, sig * env, 0.5, 0.26 * 1.0)
dry *= (ramp(12, 18) * (1 - ramp(LEN - 8, LEN - 2)))[None, :]

# ---- arpèges pincés ------------------------------------------------------
pattern = [0, 2, 4, 3, 2, 4, 3, 1]
step = BEAT / 2
pl = np.zeros((2, N))
for n in range(int(LEN / step)):
    t0 = n * step
    if t0 < 5.5 or t0 > LEN - 6:
        continue
    notes, _ = CHORDS[int(t0 // CH) % 4]
    m = notes[pattern[n % 8]] + 12
    tt = np.arange(int(1.6 * SR)) / SR
    f = hz(m)
    sig = (np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 6)
           + 0.25 * np.sin(6 * np.pi * f * tt) * np.exp(-tt * 9))
    sig *= np.exp(-tt * 3.2) * smooth(tt / 0.006)
    add(pl, t0, sig, 0.3 + 0.4 * (n % 2), 0.17)
level = 0.45 + 0.55 * ramp(START['chaine1'], START['drone'] + 8) - 0.35 * ramp(START['pariou2'] + 2, START['chaine3'] + 4)   # monte, puis s'apaise
pl *= (ramp(5.5, 10) * level * (1 - ramp(LEN - 9, LEN - 2)))[None, :]
wet += pl * 0.8
dry += pl * 0.35

# ---- pulsation douce + charleston ---------------------------------------
pulse = np.zeros((2, N))
for n in range(int(LEN / BEAT)):
    t0 = n * BEAT
    if t0 < START['drone'] or t0 > START['pariou2'] + 3:
        continue
    if n % 2 == 0:
        tt = np.arange(int(0.5 * SR)) / SR
        fr = 45 + 70 * np.exp(-tt * 22)
        sig = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 9)
        add(pulse, t0, sig, 0.5, 0.42)
    else:
        tt = np.arange(int(0.08 * SR)) / SR
        h = fft_band(rng.standard_normal(len(tt)), 6000, 16000) * np.exp(-tt * 55)
        add(pulse, t0 + BEAT / 2 * 0, h, 0.62, 0.9)
pulse *= (ramp(START['drone'], START['drone'] + 4) * (1 - ramp(START['pariou2'], START['pariou2'] + 4)))[None, :]
dry += pulse

# ---- goutte d'eau en ouverture ------------------------------------------
for t0, g in ((0.35, 0.5), (1.15, 0.22)):
    tt = np.arange(int(0.5 * SR)) / SR
    fr = 600 + 1400 * np.exp(-tt * 38)
    sig = np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-tt * 14) * smooth(tt / 0.002)
    add(wet, t0, sig, 0.5, g)
    add(dry, t0, sig, 0.5, g * 0.6)

# ---- whooshes sur les transitions ---------------------------------------
whoosh_at = [S[k] + 0.5 for k in range(1, len(S) - 1)]
for w0 in whoosh_at:
    L = 1.6
    tt = np.arange(int(L * SR)) / SR
    noise = rng.standard_normal(len(tt))
    bands = (fft_band(noise, 300, 1200), fft_band(noise, 1200, 4500), fft_band(noise, 4500, 11000))
    sig = sum(b * np.exp(-((tt - (0.45 + 0.2 * i)) ** 2) / (2 * (0.22 + 0.04 * i) ** 2)) * g
              for i, (b, g) in enumerate(zip(bands, (1.0, 0.7, 0.35))))
    add(wet, w0 - 0.2, sig, 0.5, 0.20)

# ---- réverbération (IR bruitée à décroissance exponentielle) -------------
ir_len = int(3.2 * SR)
tt = np.arange(ir_len) / SR
ir = [rng.standard_normal(ir_len) * np.exp(-tt * 1.8) for _ in range(2)]
ir = [fft_band(x, 120, 9000) for x in ir]
for x in ir:
    x[: int(0.02 * SR)] *= np.linspace(0, 1, int(0.02 * SR))
ir = [x / np.sqrt(np.sum(x * x)) for x in ir]
size = 1 << int(np.ceil(np.log2(N + ir_len)))
out = np.zeros((2, N))
for ch in range(2):
    conv = np.fft.irfft(np.fft.rfft(wet[ch], size) * np.fft.rfft(ir[ch], size), size)[:N]
    out[ch] = dry[ch] + 0.55 * wet[ch] + 0.9 * conv

# ---- finalisation --------------------------------------------------------
fade_out = 1 - ramp(TOTAL - 4.0, TOTAL + 0.6)
out *= fade_out[None, :]
out *= smooth(t / 0.15)[None, :]
out /= np.max(np.abs(out)) / 0.89
pcm = (out.T * 32767).astype("<i2")
with wave.open("work/musique.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print("ok", LEN, "s ; rms", float(np.sqrt(np.mean(out ** 2))))
